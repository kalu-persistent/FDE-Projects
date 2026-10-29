import re
from dataclasses import dataclass
from fastapi import Header,HTTPException
from sqlalchemy import select,text
from .database import SessionLocal
from .models import Employee
BLOCK_PATTERNS=[r"ignore (all|previous) instructions",r"reveal (the )?(system|developer) prompt",r"<script",r"\b(drop|truncate|alter)\s+table\b",r"\bunion\s+select\b",r"\.\./",r"file://",r"(?:password|secret|api[_ -]?key)\s*[:=]"]
@dataclass
class UserContext: id:int; name:str; role:str; employee_type:str
def content_gateway(q:str)->str:
    q=" ".join(q.strip().split())
    if not q or len(q)>2000: raise HTTPException(400,"Question must be 1-2000 characters")
    if any(re.search(p,q,re.I) for p in BLOCK_PATTERNS): raise HTTPException(400,"Request blocked by deterministic content gateway")
    return q
def get_user(x_user_id:int=Header(...,alias="X-User-Id")):
    with SessionLocal() as db: e=db.get(Employee,x_user_id)
    if not e: raise HTTPException(401,"Unknown demo user")
    return UserContext(e.id,e.name,e.role,e.employee_type)
def visible_employee_ids(user):
    if user.role in {"ADMIN","HR"}:
        with SessionLocal() as db: return list(db.scalars(select(Employee.id)).all())
    if user.employee_type!="manager": return [user.id]
    with SessionLocal() as db: return [r[0] for r in db.execute(text("WITH RECURSIVE t AS (SELECT id FROM employees WHERE id=:id UNION ALL SELECT e.id FROM employees e JOIN t ON e.manager_id=t.id) SELECT id FROM t"),{"id":user.id})]
def can_view_employee(user,target): return target in visible_employee_ids(user)
