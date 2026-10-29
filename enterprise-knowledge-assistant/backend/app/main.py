import os
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from .database import init_db,SessionLocal
from .security import get_user,content_gateway,UserContext
from .graph import graph
from .models import Approval
from .router import detect_intent,extract_employee_id
from .config import get_settings
from .ingest import ingest_all_documents
s=get_settings()
if s.langsmith_tracing: os.environ.update({"LANGSMITH_TRACING":"true","LANGSMITH_API_KEY":s.langsmith_api_key,"LANGSMITH_PROJECT":s.langsmith_project})
@asynccontextmanager
async def lifespan(app): init_db(); yield
app=FastAPI(title="Permission-Aware Enterprise Knowledge Assistant",version="1.1.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=s.cors_origin_list,allow_credentials=False,allow_methods=["GET","POST","OPTIONS"],allow_headers=["Content-Type","X-User-Id"])
class Ask(BaseModel): question:str

class Decision(BaseModel): approved:bool

class IngestRequest(BaseModel):
    root_folder: str = "data/documents"
@app.get('/health')
def health(): return {"status":"ok"}

@app.get('/users')
def users(): return [{"id":1,"name":"Asha Admin","role":"ADMIN"},{"id":2,"name":"Hari HR","role":"HR"},{"id":3,"name":"Meera Manager","role":"EMPLOYEE / Manager"},{"id":4,"name":"Eva Engineer","role":"EMPLOYEE"},{"id":5,"name":"Dev Analyst","role":"EMPLOYEE"}]

@app.post('/query')
def query(body:Ask,user:UserContext=Depends(get_user)):
    q=content_gateway(body.question); intent=detect_intent(q)
    target=extract_employee_id(q,user.id)
    if user.role=="HR" and intent.value in {"attendance","leave_balance"} and target!=user.id:
        with SessionLocal() as db: a=Approval(requester_id=user.id,action=intent.value,payload=q); db.add(a); db.commit(); db.refresh(a)
        return {"status":"approval_required","approval_id":a.id,"intent":intent.value,"answer":f"Admin approval required. Approval request #{a.id} was created.","sources":[]}
    out=graph.invoke({"question":q,"user":user}); return {"intent":out['intent'],**out['result']}

@app.post('/approvals/{approval_id}')
def decide(approval_id:int,body:Decision,user:UserContext=Depends(get_user)):
    if user.role!="ADMIN": raise HTTPException(403,"Only ADMIN may approve")
    with SessionLocal() as db:
        a=db.get(Approval,approval_id)
        if not a: raise HTTPException(404,"Approval not found")
        a.approved=body.approved; db.commit()
    return {"approval_id":approval_id,"approved":body.approved}

@app.get('/approvals')
def approvals(user:UserContext=Depends(get_user)):
    if user.role!="ADMIN": raise HTTPException(403,"Only ADMIN may list approvals")
    with SessionLocal() as db: rows=db.scalars(select(Approval).order_by(Approval.id.desc())).all()
    return [{"id":a.id,"requester":a.requester_id,"action":a.action,"payload":a.payload,"approved":a.approved} for a in rows]


@app.post("/ingestion/run")
def run_ingestion(
    body: IngestRequest,
    user: UserContext = Depends(get_user)
):
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN may run ingestion"
        )

    try:
        return ingest_all_documents(
            documents_folder=body.root_folder
        )

    except RuntimeError as exception:
        raise HTTPException(
            status_code=400,
            detail=str(exception)
        ) from exception