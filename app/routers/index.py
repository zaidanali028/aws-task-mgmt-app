from fastapi import APIRouter

# Create an instance of APIRouter
index_router = APIRouter()

# Define the default route at the base URL "/"
@index_router.get("/")
async def read_root():
    return {"message": "Official Task API"}
