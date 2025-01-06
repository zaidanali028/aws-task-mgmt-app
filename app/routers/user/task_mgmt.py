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


# CRUD Operation: Update an existing task
@router.put("/tasks/{task_id}")
async def update_task(task_id: str, updated_task: Task, token: str = Depends(oauth2_scheme)):
    try:
        # Verify token and extract user info
        user_id = utils.verify_token(token, "TeamMembers").get('decoded_token').get('sub')

        # Retrieve the existing task from DynamoDB to check the 'assigned_to' field
        existing_task = task_model.get_task_by_id(task_id)  # Implement this function to get the task by ID
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if the current user is assigned to the task
        if existing_task.get('assigned_to') != user_id:  # Assuming 'username' is part of the token
            raise HTTPException(status_code=403, detail="You are not authorized to update this task")

        # Proceed with the task update
        task_response = task_model.update_task(task_id, updated_task)

        return {
            "task_id": task_id,
            "message": "Task updated successfully.",
            "task_data": task_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")