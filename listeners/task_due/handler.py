import json
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from typing import Optional

# Load environment variables
AWS_REGION = os.getenv("MY_AWS_REGION", "eu-west-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "Tasks")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

# Initialize DynamoDB and SES clients using loaded environment variables
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
ses_client = boto3.client('ses', region_name=AWS_REGION)

def parse_deadline(deadline_str):
    """
    Parses the deadline string into a datetime object.
    Supports ISO 8601 and MM/DD/YYYY formats.
    """
    formats = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(deadline_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {deadline_str}")

def get_email_for_user(user_id):
    """
    Fetches the email address of a user from Cognito based on user_id.
    """
    try:
        cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)
        response = cognito_client.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=user_id
        )
        email = next(
            (attr['Value'] for attr in response.get('UserAttributes', []) if attr['Name'] == 'email'),
            None
        )
        if not email:
            print(f"No email attribute found for user {user_id}.")
            return None
        return email
    except cognito_client.exceptions.UserNotFoundException:
        print(f"User with ID {user_id} not found in Cognito.")
        return None
    except Exception as e:
        print(f"Error retrieving email for user {user_id}: {str(e)}")
        return None

def get_all_tasks() -> Optional[list]:
    """
    Retrieves all tasks from the DynamoDB table.
    """
    try:
        response = table.scan()
        if 'Items' not in response or not response['Items']:
            raise HTTPException(status_code=404, detail="No tasks found")
        return response['Items']
    except ClientError as e:
        print(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")

def handler(event, context):
    """
    Lambda function handler to send task reminder emails.
    """
    try:
        print("Received event:", json.dumps(event))
        tasks = get_all_tasks()
        now = datetime.utcnow()
        for task in tasks:
            assigned_to = task.get("assigned_to")
            title = task.get("title", "No Title")
            description = task.get("description", "No Description")
            deadline_str = task.get("deadline")
            task_id = task.get("task_id", "No ID")
            if not deadline_str:
                print(f"Task {task_id} has no deadline. Skipping.")
                continue
            try:
                deadline = parse_deadline(deadline_str)
            except ValueError as ve:
                print(f"Invalid date format for task {task_id}: {ve}")
                continue
            days_remaining = (deadline - now).days
            if days_remaining in [1, 3, 5]:
                recipient_email = get_email_for_user(assigned_to)
                if not recipient_email:
                    print(f"No email for user {assigned_to}. Skipping.")
                    continue
                subject = f"Reminder: Task '{title}' is due in {days_remaining} day(s)"
                body_text = (
                    f"Hello,\n\n"
                    f"This is a reminder that the following task is due in {days_remaining} day(s):\n\n"
                    f"Title: {title}\n"
                    f"Description: {description}\n"
                    f"Task ID: {task_id}\n"
                    f"Deadline: {deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                    f"Best regards,\nTask Scheduler"
                )
                response = ses_client.send_email(
                    Source="zaidanali028@gmail.com",
                    Destination={"ToAddresses": [recipient_email]},
                    Message={
                        "Subject": {"Data": subject},
                        "Body": {"Text": {"Data": body_text}},
                    },
                )
                print(f"Email sent to {recipient_email}: {response}")
        return {"statusCode": 200, "body": "Reminder emails sent successfully!"}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
