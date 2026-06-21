from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models import ProjectDB, ProjectResourceDB
from calculators import recalculate_project, calculate_employee_cost, calculate_contractor_cost, calculate_equipment_cost

app = FastAPI(title="IT Project Cost API")

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_session():
    async with AsyncSessionLocal() as session:
        return session

@app.get("/api/projects")
async def get_projects():
    session = await get_session()
    result = await session.execute(select(ProjectDB))
    projects = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "total_cost_project": str(p.total_cost_project),
            "cost_price": str(p.cost_price)
        }
        for p in projects
    ]

@app.post("/api/projects")
async def create_project(name: str, start_date: str, end_date: str, tax_rate: float = 0, margin_percent: float = 0):
    session = await get_session()
    
    new_project = ProjectDB(
        name=name,
        start_date=start_date,
        end_date=end_date,
        tax_rate=tax_rate,
        margin_percent=margin_percent,
        status="создан"
    )
    
    session.add(new_project)
    await session.commit()
    await session.refresh(new_project)
    
    return {"id": new_project.id, "name": new_project.name, "message": "Проект создан"}

@app.post("/api/projects/{project_id}/resources")
async def add_resource(
    project_id: int,
    resource_name: str,
    resource_type: str,
    hours_days: int,
    cost_price_value: float = 0,
    base_salary: float = 0,
    price_per_unit: float = 0,
    tax_rate_input: float = 0,
    margin_percent: float = 0
):
    session = await get_session()
    
    final_cost_price = Decimal(0)
    
    if resource_type == "сотрудник":
        if cost_price_value == 0:
            final_cost_price = calculate_employee_cost(hours_days, Decimal(base_salary), Decimal(tax_rate_input))
        else:
            final_cost_price = Decimal(cost_price_value)
    elif resource_type == "исполнитель":
        if cost_price_value == 0:
            final_cost_price = calculate_contractor_cost(hours_days, Decimal(price_per_unit), Decimal(tax_rate_input))
        else:
            final_cost_price = Decimal(cost_price_value)
    elif resource_type == "оборудование":
        if cost_price_value == 0:
            final_cost_price = calculate_equipment_cost(hours_days, Decimal(price_per_unit))
        else:
            final_cost_price = Decimal(cost_price_value)
    
    final_total_cost = calculate_service_total_cost(final_cost_price, Decimal(margin_percent))
    
    new_res = ProjectResourceDB(
        project_id=project_id,
        resource_name=resource_name,
        resource_type=resource_type,
        hours_days=hours_days,
        cost_price=final_cost_price,
        margin_percent=margin_percent,
        total_cost=final_total_cost
    )
    
    session.add(new_res)
    
    all_res = await session.execute(select(ProjectResourceDB).where(ProjectResourceDB.project_id == project_id))
    resources_list = all_res.scalars().all()
    
    project = await session.get(ProjectDB, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    recalculate_project(project, resources_list)
    
    await session.commit()
    
    return {
        "message": "Ресурс добавлен и проект пересчитан",
        "new_cost_price": str(final_cost_price),
        "new_total_cost": str(final_total_cost)
    }

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: int):
    session = await get_session()
    
    project = await session.get(ProjectDB, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    resources = await session.execute(select(ProjectResourceDB).where(ProjectResourceDB.project_id == project_id))
    resources_list = resources.scalars().all()
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "total_cost_project": str(project.total_cost_project),
            "cost_price": str(project.cost_price),
            "pure_profit": str(project.pure_profit)
        },
        "resources": [
            {
                "name": r.resource_name,
                "type": r.resource_type,
                "cost": str(r.cost_price),
                "total": str(r.total_cost)
            }
            for r in resources_list
        ]
    }