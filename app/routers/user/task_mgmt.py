import boto3
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import Task, TeamMember
from app.utils import utils
from fastapi.security import OAuth2PasswordBearer
import uuid
from typing import List
from app.db import task as task_model
import time
my_env_vars=utils.load_env()

# Initialize FastAPI OAuth2 password bearer for security (e.g., authentication)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=my_env_vars.get("MY_AWS_REGION"))
table = dynamodb.Table(my_env_vars.get("MY_AWS_REGION"))


# APIRouter setup
router = APIRouter()


# CRUD Operation: Specific user's task
@router.get("/tasks/{assigned_to}", response_model=List[Task])
async def list_my_tasks(assigned_to:str,token: str = Depends(oauth2_scheme)):
    try:
        utils.verify_token(token,"TeamMembers")
        
        # Scan DynamoDB table to fetch all tasks (Consider using Query for better performance in production)
        task_response=task_model.get_tasks_by_user(assigned_to)
        return task_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")
