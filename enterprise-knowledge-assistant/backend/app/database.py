from datetime import date,timedelta
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from .config import get_settings
from .models import Base,Employee,Attendance,LeaveBalance,Opening
engine=create_engine(get_settings().database_url,pool_pre_ping=True); SessionLocal=sessionmaker(engine,expire_on_commit=False)
def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Employee.id).limit(1)): return
        db.add_all([Employee(id=1,name="Asha Admin",role="ADMIN",employee_type="individual"),Employee(id=2,name="Hari HR",role="HR",employee_type="individual"),Employee(id=3,name="Meera Manager",role="EMPLOYEE",employee_type="manager"),Employee(id=4,name="Eva Engineer",role="EMPLOYEE",employee_type="individual",manager_id=3),Employee(id=5,name="Dev Analyst",role="EMPLOYEE",employee_type="individual",manager_id=3)])
        db.flush() # Persist parent rows before FK-dependent seed rows.
        for eid in range(1,6):
            db.add(LeaveBalance(employee_id=eid,annual_remaining=14,sick_remaining=7))
            for i in range(7): db.add(Attendance(employee_id=eid,day=date.today()-timedelta(days=i),status="PRESENT" if i%6 else "LEAVE"))
        db.add_all([Opening(title="Senior Python Engineer",skills="Python, FastAPI, PostgreSQL",status="OPEN"),Opening(title="LLM Engineer",skills="RAG, LangGraph, Pinecone",status="OPEN")]); db.commit()
