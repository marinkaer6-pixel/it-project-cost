from decimal import Decimal
from typing import List
from models import ProjectResourceDB, ProjectDB

def calculate_employee_cost(days: int, monthly_salary: Decimal, tax_rate: Decimal) -> Decimal:
    if days == 0: return Decimal(0)
    daily_cost_with_tax = (monthly_salary + (monthly_salary * tax_rate / 100)) / Decimal(22)
    return days * daily_cost_with_tax

def calculate_contractor_cost(units: int, price_per_unit: Decimal, tax_rate: Decimal) -> Decimal:
    base_cost = units * price_per_unit
    tax_cost = base_cost * tax_rate / 100
    return base_cost + tax_cost

def calculate_equipment_cost(units: int, price_per_unit: Decimal) -> Decimal:
    return units * price_per_unit

def calculate_service_total_cost(cost_price: Decimal, margin_percent: Decimal) -> Decimal:
    return cost_price + (cost_price * margin_percent / 100)

def calculate_project_total_cost(sp: Decimal, tax_rate: Decimal) -> Decimal:
    return sp + (sp * tax_rate / 100)

def calculate_pure_profit(resources: List[ProjectResourceDB]) -> Decimal:
    total_profit = Decimal(0)
    for res in resources:
        diff = res.total_cost - res.cost_price
        total_profit += diff
    return total_profit

def recalculate_project(project: ProjectDB, resources: List[ProjectResourceDB]) -> dict:
    total_cost_price = Decimal(0)
    total_cost_with_margin = Decimal(0)
    
    for res in resources:
        total_cost_price += res.cost_price
        total_cost_with_margin += res.total_cost
        
    project.cost_price = total_cost_price
    project.total_cost_nma = total_cost_price
    project.total_cost_cp = total_cost_with_margin
    project.total_cost_project = calculate_project_total_cost(total_cost_with_margin, project.tax_rate)
    project.pure_profit = calculate_pure_profit(resources)
    
    return {
        "cost_price": str(project.cost_price),
        "total_cost_nma": str(project.total_cost_nma),
        "total_cost_cp": str(project.total_cost_cp),
        "total_cost_project": str(project.total_cost_project),
        "pure_profit": str(project.pure_profit)
    }