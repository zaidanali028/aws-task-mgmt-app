from fastapi import FastAPI
from app.routers.index import index_router  # Import your routers
from app.routers.admin import auth as admin_auth  # Import your routers
from app.routers.user import auth as user_auth  # Import your routers
from app.routers.admin import user_mgmt as admin_user_mgmt 
from app.routers.admin import task_mgmt as admin_task_mgmt
from app.routers.user import task_mgmt as user_task_mgmt
from mangum import Mangum
app = FastAPI()

# Include the index route
app.include_router(index_router)
app.include_router(index_router,prefix="/api/v1")



   
# Include the router with the '/api/v1/admin' prefix
app.include_router(admin_auth.router, prefix="/api/v1/admin/auth")
app.include_router(admin_user_mgmt.router, prefix="/api/v1/admin/user-mgmt")
app.include_router(admin_task_mgmt.router, prefix="/api/v1/admin/task-mgmt")

app.include_router(user_auth.router, prefix="/api/v1/user/auth")
app.include_router(user_task_mgmt.router, prefix="/api/v1/user/task-mgmt")

handler = Mangum(app)

# zip -r app.zip app/
