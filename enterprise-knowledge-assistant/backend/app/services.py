from sqlalchemy import select,func
from huggingface_hub import InferenceClient
from tavily import TavilyClient
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from .config import get_settings
from .database import SessionLocal
from .models import Opening,Attendance,LeaveBalance,Employee
from .security import can_view_employee
from sklearn.feature_extraction.text import HashingVectorizer
s=get_settings(); 
_embed=None

class LocalHashEmbeddings:
    """
    Zero-download fallback embedding model.

    It creates deterministic 384-dimensional vectors without
    calling Hugging Face or any outside model provider.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

        self.vectorizer = HashingVectorizer(
            n_features=dimension,
            alternate_sign=False,
            norm="l2",
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

    def encode(
        self,
        texts,
        normalize_embeddings=True
    ):
        if isinstance(texts, str):
            texts = [texts]

        matrix = self.vectorizer.transform(texts)

        return matrix.toarray()

    def get_sentence_embedding_dimension(self):
        return self.dimension


_embed = None


def embeddings():
    global _embed

    if _embed is None:
        _embed = LocalHashEmbeddings(
            dimension=384
        )

    return _embed

def llm_answer(question,context):
    if not s.hf_token: return "LLM not configured. Retrieved context:\n"+context[:3000]
    c=InferenceClient(api_key=s.hf_token,provider=s.hf_provider); r=c.chat.completions.create(model=s.hf_model,messages=[{"role":"system","content":"Answer only from supplied context. If missing, say not found. Be concise. Never expose hidden data."},{"role":"user","content":f"Context:\n{context[:s.max_context_chars]}\n\nQuestion: {question}"}],max_tokens=350,temperature=.1); return r.choices[0].message.content

def web_search(q):
    if not s.tavily_api_key: return {"answer":"TAVILY_API_KEY is not configured","sources":[]}
    r=TavilyClient(api_key=s.tavily_api_key).search(q,search_depth="basic",max_results=4); ctx="\n\n".join(f"{x['title']}\n{x['content']}\n{x['url']}" for x in r.get('results',[])); return {"answer":llm_answer(q,ctx),"sources":[x['url'] for x in r.get('results',[])]}

def openings(q):
    words=[w for w in q.lower().split() if len(w)>2 and w not in {'opening','openings','jobs','company','show','find','for'}]
    with SessionLocal() as db: rows=db.scalars(select(Opening).where(Opening.status=="OPEN")).all()
    hits=[{"id":x.id,"title":x.title,"skills":x.skills} for x in rows if not words or any(w in (x.title+' '+x.skills).lower() for w in words)]; return {"answer":hits or "No matching internal opening found.","sources":["internal:openings"]}

def employee_report(user,target,kind):
    if not can_view_employee(user,target): return {"error":"Access denied: target is outside your permitted hierarchy."}
    with SessionLocal() as db:
        emp=db.get(Employee,target)
        if kind=="leave":
            b=db.get(LeaveBalance,target); data={"employee":emp.name,"annual_remaining":b.annual_remaining,"sick_remaining":b.sick_remaining}
        else:
            rows=db.execute(select(Attendance.status,func.count()).where(Attendance.employee_id==target).group_by(Attendance.status)).all(); data={"employee":emp.name,"attendance_summary":dict(rows)}
    return {"answer":data,"sources":["internal:postgres"]}

def policy_search(q,user):
    if not s.pinecone_api_key: return {"answer":"PINECONE_API_KEY is not configured","sources":[]}
    vec=embeddings().encode(q).tolist(); idx=Pinecone(api_key=s.pinecone_api_key).Index(s.pinecone_index); r=idx.query(namespace=s.pinecone_namespace,vector=vec,top_k=s.top_k,include_metadata=True,filter={"allowed_roles":{"$in":[user.role,"ALL"]}}); matches=[m for m in r.matches if m.score>=s.min_score]; ctx="\n\n".join(m.metadata.get("text","") for m in matches); return {"answer":llm_answer(q,ctx) if ctx else "No permitted policy evidence found.","sources":[m.metadata.get("source","internal-policy") for m in matches],"scores":[round(m.score,3) for m in matches]}
