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



# CRUD Operation: Create a new task
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_task(task: Task, token: str = Depends(oauth2_scheme)):
    try:
        # Verify the token first
        utils.verify_token(token,"Admins")
        # Generate task_id if not provided
        if not task.task_id:
            task.task_id = utils.generate_task_id()
        task.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert task into DynamoDB
        task_response=task_model.create_task(task)
        
        return {"task_id": task.task_id, "message": "Task created successfully.","task_data":task.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

# CRUD Operation: Update an existing task
@router.put("/tasks/{task_id}/{assigned_to}")
async def update_task(task_id: str, assigned_to:str,updated_task: Task, token: str = Depends(oauth2_scheme)):
    try:
        utils.verify_token(token,"Admins")
        # Update task in DynamoDB
        task_response=task_model.update_task(task_id,assigned_to, updated_task)
        return {"task_id": task_id, "message": "Task updated successfully.","task_data":task_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


# CRUD Operation: Get a task by task_id
@router.get("/tasks/{task_id}/{assigned_to}", response_model=Task)
async def get_task(task_id: str, assigned_to:str, token: str = Depends(oauth2_scheme)):
    try:
        utils.verify_token(token,"Admins")
        
        # Fetch task from DynamoDB
        task_response=task_model.get_task(task_id,assigned_to)
        return task_response
    except HTTPException as http_exc:
        # Specifically handle HTTPException
        raise http_exc  # This will allow FastAPI to generate the appropriate response

    except Exception as e:
        # Catch any other exceptions and include more detailed error handling
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


# CRUD Operation: Delete a task by task_id
@router.delete("/tasks/{task_id}/{assigned_to}")
async def delete_task(task_id: str, assigned_to:str, token: str = Depends(oauth2_scheme)):
    try:
        utils.verify_token(token,"Admins")
        
        # Delete task from DynamoDB
        task_response=task_model.delete_task(task_id,assigned_to)
        return task_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

# CRUD Operation: List all tasks (Optional)
@router.get("/tasks", response_model=List[Task])
async def list_tasks(token: str = Depends(oauth2_scheme)):
    try:
        utils.verify_token(token,"Admins")
        
        # Scan DynamoDB table to fetch all tasks (Consider using Query for better performance in production)
        task_response=task_model.get_all_tasks()
        return task_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")


# CRUD Operation: Specific user's task
@router.get("/tasks/{assigned_to}", response_model=List[Task])
async def list_my_tasks(assigned_to:str,token: str = Depends(oauth2_scheme)):
    try:
        utils.verify_token(token,"Admins")
        
        # Scan DynamoDB table to fetch all tasks (Consider using Query for better performance in production)
        task_response=task_model.get_tasks_by_user(assigned_to)
        return task_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")
