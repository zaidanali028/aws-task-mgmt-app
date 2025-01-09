import hmac
import hashlib
import base64
import jwt
from fastapi import  HTTPException,status
from dotenv import load_dotenv
import app.consts as constants
import random
import string
import uuid
from app.utils.CognitoAuthenticator import CognitoAuthenticator
import jwt
from typing import Dict
import json
import boto3

load_dotenv()

def load_env():
    # AWS Cognito configuration
    MY_AWS_REGION = constants.MY_AWS_REGION
    COGNITO_USER_POOL_ID = constants.COGNITO_USER_POOL_ID
    COGNITO_APP_CLIENT_ID = constants.COGNITO_APP_CLIENT_ID
    COGNITO_APP_CLIENT_SECRET = constants.COGNITO_APP_CLIENT_SECRET
    DYNAMODB_TABLE_NAME=constants.DYNAMODB_TABLE_NAME
    EVENT_BUS_NAME=constants.EVENT_BUS_NAME
    COGNITO_APP_CLIENT_SECRET2=constants.COGNITO_APP_CLIENT_SECRET2

    # raise the values as a dictionary
    return {
        "MY_AWS_REGION": MY_AWS_REGION,
        "COGNITO_USER_POOL_ID": COGNITO_USER_POOL_ID,
        "COGNITO_APP_CLIENT_ID": COGNITO_APP_CLIENT_ID,
        "COGNITO_APP_CLIENT_SECRET": COGNITO_APP_CLIENT_SECRET,
        "DYNAMODB_TABLE_NAME":DYNAMODB_TABLE_NAME,
        "EVENT_BUS_NAME":EVENT_BUS_NAME,
        "COGNITO_APP_CLIENT_SECRET2":COGNITO_APP_CLIENT_SECRET2
    }
    



# password generator (random)
def generate_random_password(length=12):
    """
    Generate a random password that meets basic security requirements.
    
    Args:
        length (int): Desired length of the password (minimum 8). Default is 12.
        
    raises:
        str: A securely generated random password.
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")
    
    # Define character pools
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+"
    
    # Ensure the password contains at least one of each character type
    all_characters = lower + upper + digits + symbols
    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(symbols),
    ]
    
    # Fill the remaining length with random choices from all character pools
    password += random.choices(all_characters, k=length - len(password))
    
    # Shuffle to ensure randomness
    random.shuffle(password)
    
    return ''.join(password)


    
def generate_secret_hash(client_id: str, client_secret: str, email: str) -> str:
    message = email + client_id
    secret_hash = hmac.new(client_secret.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(secret_hash.digest()).decode()




# Function to verify JWT and check if the user belongs to the required group
# TeamMembers or Admins
def verify_token(token: str, user_group: str) -> dict:
    """
    Verify a token and return the decoded token if valid.

    Args:
    - token (str): The token to verify.
    - user_group (str): The user group to check.

    Returns:
    - dict: The decoded token if valid, otherwise raises an exception.
    """

    auth = CognitoAuthenticator(
        pool_region=constants.MY_AWS_REGION,
        pool_id=constants.COGNITO_USER_POOL_ID,
        client_id=constants.COGNITO_APP_CLIENT_ID
    )

    try:
        # Verify the token
        token_verified = auth.verify_token(token)
        
        if not token_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Decode the JWT token
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Check if user belongs to the specified group
        user_groups = decoded_token.get('cognito:groups', [])
        if user_group not in user_groups:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User is not an {user_group}")

        if token_verified:
            return {"decoded_token":decoded_token,"verified":True}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown exeption")

  





# Generate a UUID for task_id if not provided
def generate_task_id() -> str:
    return str(uuid.uuid4())  # Generate a unique UUID


# Event emission after user is created using event bridge

eventbridge = boto3.client('events', region_name=constants.MY_AWS_REGION)

def publish_user_created_event(email:str, given_name:str, family_name:str,user_password:str):
    # Define event details
    event_detail = {
        "email": email,
        "given_name": given_name,
        "family_name": family_name,
        "user_password": user_password
        
    }
    
    # Publish the event to EventBridge
    response = eventbridge.put_events(
        Entries=[
            {
                'Source': 'app.taskmgmt',  # Event source identifier
                'DetailType': 'UserCreated',         # Event type
                'Detail': json.dumps(event_detail),  # Event data
                'EventBusName': 'UserCreatedEventBus'           # Event bus (use "default" for now)
            }
        ]
    )
    print(f"Event emitted: {response}")
    return response


def publish_task_created_event(
    title: str, description: str, assigned_to: str, deadline: str, task_status: str, email: str
):
    """
    Publish an event to EventBridge for task creation.

    Args:
        title (str): Title of the task.
        description (str): Description of the task.
        assigned_to (str): ID of the assignee.
        deadline (str): Deadline of the task in ISO format.
        task_status (str): Status of the task.
        email (str): Email of the assignee or recipient for notification.
    """
    # Define event details
    event_detail = {
        "title": title,
        "description": description,
        "assigned_to": assigned_to,
        "deadline": deadline,
        "task_status": task_status,
        "email": email,
    }

    # Publish the event to EventBridge
    response = eventbridge.put_events(
        Entries=[
            {
                "Source": "app.taskmgmt",  # Event source identifier
                "DetailType": "TaskCreated",  # Event type
                "Detail": json.dumps(event_detail),  # Event data
                "EventBusName": "TaskCreatedEventBus",  # Event bus name
            }
        ]
    )
    print(f"Task created event emitted: {event_detail,response}")
    return response

def publish_task_updated_event(
    title: str, updated_fields: dict, email: str
):
    """
    Publish an event to EventBridge for task updates.

    Args:
        title (str): Title of the task.
        updated_fields (dict): A dictionary of updated fields and their new values.
        email (str): Email of the recipient for notification.
    """
    # Define event details
    event_detail = {
        "title": title,
        "updated_fields": updated_fields,
        "email": email,
    }

    # Publish the event to EventBridge
    response = eventbridge.put_events(
        Entries=[
            {
                "Source": "app.taskmgmt",  # Event source identifier
                "DetailType": "TaskUpdated",  # Event type
                "Detail": json.dumps(event_detail),  # Event data
                "EventBusName": "TaskUpdatedEventBus",  # Event bus name
            }
        ]
    )
    print(f"Task updated event emitted: {response}")
    return response
