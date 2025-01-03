import boto3
from botocore.exceptions import ClientError
from app.utils import utils
from typing import Optional
import boto3
from botocore.exceptions import ClientError
import time
from app.models import Task
from fastapi import HTTPException

# env vars
my_env_vars=utils.load_env()


# DynamoDB table setup
dynamodb = boto3.resource('dynamodb', region_name=my_env_vars.get("MY_AWS_REGION"))
table = dynamodb.Table(my_env_vars.get("DYNAMODB_TABLE_NAME"))





# Fetch All Tasks (using scan)
def get_all_tasks() -> Optional[list]:
    try:
        # Use scan to fetch all tasks from DynamoDB (not recommended for large tables)
        response = table.scan()
        
        if 'Items' not in response:
            raise HTTPException(status_code=404, detail="No tasks found")
        
        tasks = [Task(**task_data) for task_data in response['Items']]
        return tasks
    
    except ClientError as e:
        print(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")


# Create Task - Insert a new task
def create_task(task: Task) -> Optional[dict]:
    try:
      
        response = table.put_item(
            Item={
                'task_id': task.task_id,
                'title': task.title,
                'description': task.description,
                'assigned_to': task.assigned_to,
                'deadline': task.deadline,
                'task_status': task.task_status,
                'created_at': task.created_at
            }
        )
        return response
    except ClientError as e:
        print(f"Error creating task: {e}")
        return None

# Get Task - Fetch a task by task_id
def get_task(task_id: str,assigned_to:str) -> Optional[Task]:
    try:
        # Fetch task from DynamoDB
        response = table.get_item(  Key={
                'task_id': task_id,
                'assigned_to': assigned_to
            },)
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = response['Item']

        # Ensure all fields are present in the response data
        if not all(key in task_data for key in ["task_id", "title", "description", "assigned_to", "deadline", "task_status", "created_at"]):
            raise HTTPException(status_code=500, detail="Missing required fields in task data")
        
        # Create Task model from the DynamoDB response
        task = Task(**task_data)
        return task
    
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTPException for proper FastAPI error handling

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    except ClientError as e:
        print(f"Error getting task: {e}")
        return None

# Update Task - Update an existing task's details
def update_task(task_id: str, current_assigned_to: str, updated_task: Task) -> Optional[dict]:
    try:
        # Get the current item
        existing_task = table.get_item(
            Key={
                'task_id': task_id,
                'assigned_to': current_assigned_to
            }
        ).get('Item', None)
        
        if not existing_task:
            print("Task not found!")
            return None

        # Create a new item with updated 'assigned_to'
        new_task = existing_task.copy()
        new_task.update({
            'assigned_to': updated_task.assigned_to,
            'title': updated_task.title,
            'description': updated_task.description,
            'deadline': updated_task.deadline,
            'task_status': updated_task.task_status,
            'created_at': updated_task.created_at
        })

        table.put_item(Item=new_task)

        # Delete the old item
        table.delete_item(
            Key={
                'task_id': task_id,
                'assigned_to': current_assigned_to
            }
        )

        return new_task  # Return the new task details
    except ClientError as e:
        print(f"Error reassigning task: {e}")
        return None
# Delete Task - Remove a task from the database
def delete_task(task_id: str,assigned_to:str) -> Optional[dict]:
    try:
        response = table.delete_item(
            Key={
                'task_id': task_id,
                'assigned_to': assigned_to
            },
            ReturnValues="ALL_OLD"
            # The response will include the task attributes before it was deleted.
        )
        return response
    except ClientError as e:
        print(f"Error deleting task: {e}")

# Fetch Tasks Assigned to a Specific User (using query)
def get_tasks_by_user(assigned_to: str) -> Optional[list]:
    try:
        # Use query to fetch tasks assigned to a specific user
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('assigned_to').eq(assigned_to)
        )
        
        if 'Items' not in response:
            raise HTTPException(status_code=404, detail="No tasks found for this user")
        
        tasks = [Task(**task_data) for task_data in response['Items']]
        return tasks

    except ClientError as e:
        print(f"Error fetching tasks by user: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tasks by user")