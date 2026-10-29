from datetime import date,datetime
from sqlalchemy import String,Integer,Date,DateTime,ForeignKey,Text,Boolean
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
class Base(DeclarativeBase): pass
class Employee(Base):
    __tablename__="employees"; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(100)); role:Mapped[str]=mapped_column(String(20)); employee_type:Mapped[str]=mapped_column(String(20),default="individual"); manager_id:Mapped[int|None]=mapped_column(ForeignKey("employees.id"),nullable=True)
class Attendance(Base):
    __tablename__="attendance"; id:Mapped[int]=mapped_column(primary_key=True); employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id")); day:Mapped[date]=mapped_column(Date); status:Mapped[str]=mapped_column(String(20))
class LeaveBalance(Base):
    __tablename__="leave_balances"; employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"),primary_key=True); annual_remaining:Mapped[int]=mapped_column(Integer,default=18); sick_remaining:Mapped[int]=mapped_column(Integer,default=8)
class Opening(Base):
    __tablename__="openings"; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(120)); skills:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(20),default="OPEN")
class Approval(Base):
    __tablename__="approvals"; id:Mapped[int]=mapped_column(primary_key=True); requester_id:Mapped[int]=mapped_column(Integer); action:Mapped[str]=mapped_column(String(80)); payload:Mapped[str]=mapped_column(Text); approved:Mapped[bool|None]=mapped_column(Boolean,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class IngestedDocument(Base):
    __tablename__ = "ingested_documents"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    source_path: Mapped[str] = mapped_column(
        String(500),
        index=True
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        index=True
    )

    acl_key: Mapped[str] = mapped_column(
        String(100)
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="COMPLETED"
    )

    indexed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )