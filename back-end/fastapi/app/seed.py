"""Idempotently seed CDIS RBAC, optional admin and demo gallery records."""
import asyncio, os
from uuid import uuid4
from sqlalchemy import delete, select
from app.database import SessionLocal
from app.models import DemoChartDataset, DemoChartPoint, DemoStateMetric, DemoTableDataset, DemoTableRow, Permission, Role, User, user_roles
from app.security import hash_password
ROLE_PERMISSIONS = {"admin":["users:read","users:write","roles:manage"],"manager":["users:read"],"user":[]}
STATES = [("Mizoram","15"),("Tamil Nadu","33"),("Madhya Pradesh","23"),("Maharashtra","27"),("Chhattisgarh","22"),("Gujarat","24"),("Odisha","21"),("Andhra Pradesh","37"),("Karnataka","29"),("Goa","30"),("Kerala","32"),("Telangana","36"),("West Bengal","19"),("Puducherry","34"),("Arunachal Pradesh","12"),("Assam","18"),("Nagaland","13"),("Meghalaya","17"),("Manipur","14"),("Tripura","16"),("Uttar Pradesh","09"),("Rajasthan","08"),("Delhi","07"),("Haryana","06"),("Sikkim","11"),("Bihar","10"),("Jharkhand","20"),("Ladakh","38"),("Jammu and Kashmir","01"),("Himachal Pradesh","02"),("Punjab","03"),("Uttarakhand","05"),("Chandigarh","04"),("Lakshadweep","31"),("Andaman and Nicobar Islands","35"),("Dadra and Nagar Haveli and Daman and Diu","26")]
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun"]
CHARTS = [
("monthly-revenue","Monthly Revenue","bar","Single-series bar chart — revenue per month.",[(m,None,20000+i*9300) for i,m in enumerate(MONTHS)]),
("quarterly-sales-by-region","Quarterly Sales by Region","bar","Grouped bar chart — multiple series sharing the same labels.",[(q,r,5000+(i*4211)%35000) for i,q in enumerate(["Q1","Q2","Q3","Q4"]) for r in ["North","South","East","West"]]),
("website-traffic","Website Traffic","line","Single-series line chart — daily visits.",[(d,None,800+i*570) for i,d in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])]),
("revenue-vs-cost","Revenue vs. Cost","line","Multi-series line chart — two series sharing the same labels.",[(m,s,v) for i,m in enumerate(MONTHS) for s,v in [("Revenue",30000+i*8000),("Cost",15000+i*4500)]]),
("user-growth","User Growth","area","Area chart — cumulative users over time.",[(m,None,300+i*420) for i,m in enumerate(MONTHS)]),
("market-share","Market Share","pie","Pie chart — share of total by category.",[(n,None,10+i*6) for i,n in enumerate(["Product A","Product B","Product C","Product D","Other"])]),
("budget-allocation","Budget Allocation","donut","Donut chart — share of total budget by department.",[(n,None,12+i*4) for i,n in enumerate(["Engineering","Marketing","Sales","Operations","Support"])]),
("team-performance","Team Performance","radial","Radial chart — percentage completion per team.",[(n,None,55+i*10) for i,n in enumerate(["Frontend","Backend","QA","DevOps"])])]
def table_rows(slug):
    if slug == "orders": return [{"orderId":f"ORD-{1000+i}","customer":f"Customer {i+1}","amount":500+i*537,"status":["Pending","Shipped","Delivered","Cancelled"][i%4],"placedOn":f"2026-{i%9+1:02d}-{i%27+1:02d}"} for i in range(24)]
    if slug == "employees": return [{"name":f"Employee {i+1}","department":["Engineering","Marketing","Sales","Support","Operations"][i%5],"email":f"employee{i+1}@example.com","isActive":i%7 != 0} for i in range(18)]
    return [{"name":f"Product {i+1}","category":["Electronics","Apparel","Home & Kitchen","Sports","Books"][i%5],"price":199+i*1200,"stock":i*23%501,"rating":round(3+(i%20)/10,1)} for i in range(20)]
async def seed():
    async with SessionLocal() as db:
        permission_map = {}
        descriptions = {"users:read":"View user accounts","users:write":"Create, edit, or deactivate user accounts","roles:manage":"Assign or modify roles and permissions"}
        for key, description in descriptions.items():
            row = await db.scalar(select(Permission).where(Permission.key == key))
            if row is None: row = Permission(id=str(uuid4()),key=key,description=description); db.add(row)
            else: row.description = description
            permission_map[key] = row
        await db.flush()
        role_map = {}
        role_descriptions = {"admin":"Full administrative access","manager":"Can view user accounts","user":"Standard authenticated user, no elevated access"}
        for name, keys in ROLE_PERMISSIONS.items():
            role = await db.scalar(select(Role).where(Role.name == name))
            if role is None: role = Role(id=str(uuid4()),name=name,description=role_descriptions[name]); db.add(role)
            role.description = role_descriptions[name]
            role.permissions = [permission_map[key] for key in keys]
            role_map[name] = role
        email, password = os.getenv("SEED_ADMIN_EMAIL"), os.getenv("SEED_ADMIN_PASSWORD")
        if bool(email) != bool(password): raise RuntimeError("Set both SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD, or neither.")
        if email and password:
            user = await db.scalar(select(User).where(User.email == email.lower(), User.deleted_at.is_(None)))
            if user is None:
                user = User(
                    id=str(uuid4()),
                    email=email.lower(),
                    name=os.getenv("SEED_ADMIN_NAME") or "Administrator",
                    password_hash=hash_password(password),
                )
                db.add(user)
                await db.flush()

            # Avoid accessing an unloaded async ORM relationship here.
            # Query the join table directly so seed works for both new and
            # existing users without triggering implicit async lazy loading.
            admin_role_id = role_map["admin"].id
            assigned_role_id = await db.scalar(
                select(user_roles.c.roleId).where(
                    user_roles.c.userId == user.id,
                    user_roles.c.roleId == admin_role_id,
                )
            )
            if assigned_role_id is None:
                await db.execute(
                    user_roles.insert().values(userId=user.id, roleId=admin_role_id)
                )
        for i,(name,code) in enumerate(STATES):
            metric = await db.scalar(select(DemoStateMetric).where(DemoStateMetric.state_code == code))
            values = {"state_name":name,"project_count":i*17%151,"activity_intensity":i*29%101}
            if metric is None: db.add(DemoStateMetric(id=str(uuid4()),state_code=code,**values))
            else:
                for key,value in values.items(): setattr(metric,key,value)
        for slug,title,kind,description,points in CHARTS:
            dataset = await db.scalar(select(DemoChartDataset).where(DemoChartDataset.slug == slug))
            if dataset is None: dataset=DemoChartDataset(id=str(uuid4()),slug=slug,title=title,chart_type=kind,description=description); db.add(dataset); await db.flush()
            else: dataset.title,dataset.chart_type,dataset.description=title,kind,description
            await db.execute(delete(DemoChartPoint).where(DemoChartPoint.dataset_id == dataset.id))
            db.add_all([DemoChartPoint(id=str(uuid4()),dataset_id=dataset.id,label=label,series=series,value=value,sort_order=i) for i,(label,series,value) in enumerate(points)])
        for slug,title,description in [("orders","Orders","A typical e-commerce order list — id, customer, amount, status, date."),("employees","Employees","A typical HR/admin employee directory."),("products","Products","A typical product catalog — name, category, price, stock, rating.")]:
            dataset = await db.scalar(select(DemoTableDataset).where(DemoTableDataset.slug == slug))
            if dataset is None: dataset=DemoTableDataset(id=str(uuid4()),slug=slug,title=title,description=description); db.add(dataset); await db.flush()
            else: dataset.title,dataset.description=title,description
            await db.execute(delete(DemoTableRow).where(DemoTableRow.dataset_id == dataset.id))
            db.add_all([DemoTableRow(id=str(uuid4()),dataset_id=dataset.id,data=row,sort_order=i) for i,row in enumerate(table_rows(slug))])
        await db.commit()
    print("CDIS roles, permissions, admin and demo datasets seeded.")
if __name__ == "__main__": asyncio.run(seed())
