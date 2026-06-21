from sqlalchemy import Column, Integer, String, Date, Decimal, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import date

Base = declarative_base()

class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    
    tax_rate = Column(Decimal(5, 2), default=0)
    margin_percent = Column(Decimal(5, 2), default=0)
    
    total_cost_nma = Column(Decimal(14, 2), default=0)
    total_cost_cp = Column(Decimal(14, 2), default=0)
    total_cost_project = Column(Decimal(14, 2), default=0)
    pure_profit = Column(Decimal(14, 2), default=0)
    cost_price = Column(Decimal(14, 2), default=0)
    
    status = Column(String(30), default="создан")

class ProjectResourceDB(Base):
    __tablename__ = "project_resources"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    resource_name = Column(String(150))
    resource_type = Column(String(30))
    executor_id = Column(Integer, nullable=True)
    service_name = Column(String(150))
    
    start_date = Column(Date)
    end_date = Column(Date)
    hours_days = Column(Integer, default=0)
    
    cost_price = Column(Decimal(14, 2), default=0)
    margin_percent = Column(Decimal(5, 2), default=0)
    total_cost = Column(Decimal(14, 2), default=0)