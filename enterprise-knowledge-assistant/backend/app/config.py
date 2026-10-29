from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_env:str="dev"; database_url:str="postgresql+psycopg://assistant:assistant@postgres:5432/assistant"
    hf_token:str=""; hf_model:str="Qwen/Qwen2.5-7B-Instruct"; hf_provider:str="auto"
    embedding_model:str="sentence-transformers/all-MiniLM-L6-v2"
    pinecone_api_key:str=""; pinecone_index:str="enterprise-kb"; pinecone_namespace:str="company"
    tavily_api_key:str=""; langsmith_tracing:bool=False; langsmith_api_key:str=""; langsmith_project:str="enterprise-knowledge-assistant"
    top_k:int=5; max_context_chars:int=9000; min_score:float=.25
    cors_origins:str="http://localhost:3000,http://127.0.0.1:3000"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    @property
    def cors_origin_list(self): return [x.strip() for x in self.cors_origins.split(',') if x.strip()]
@lru_cache
def get_settings(): return Settings()
