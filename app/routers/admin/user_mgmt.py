import boto3
from fastapi import APIRouter, HTTPException,status
import app.utils.utils as utils
from app.models import TeamMember
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Initialize OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 
my_env_vars=utils.load_env()


router = APIRouter()

@router.post("/create-team-member",)
async def create_team_member(team_member: TeamMember, token: str = Depends(oauth2_scheme)):
    # Verify the token first
    decoded_token=utils.verify_token(token, "Admins")
    
    cognito_client = boto3.client('cognito-idp', region_name=my_env_vars.get("MY_AWS_REGION"))
    

    try:
        
        # Create user in Cognito
        response = cognito_client.admin_create_user(
            UserPoolId=my_env_vars.get("COGNITO_USER_POOL_ID"),
            Username=team_member.email,
            UserAttributes=[
                {'Name': 'email', 'Value': team_member.email},
                {'Name': 'given_name', 'Value': team_member.given_name},
                {'Name': 'family_name', 'Value': team_member.family_name},
            ],
            # MessageAction='SUPPRESS',  # Disable sending welcome email
            TemporaryPassword=utils.generate_random_password()

        )
        
        # Extract the created user's username
        created_username = response['User']['Username']

        # Confirm the user to avoid forcing a password reset
        cognito_client.admin_update_user_attributes(
            UserPoolId=my_env_vars.get("COGNITO_USER_POOL_ID"),
            Username=created_username,
            UserAttributes=[
                {'Name': 'email_verified', 'Value': 'true'}
            ]
        )

        # Add the user to the "TeamMembers" group
        # Extracting the Username
        username = response.get("User", {}).get("Username")
        cognito_client.admin_add_user_to_group(
            UserPoolId=my_env_vars.get("COGNITO_USER_POOL_ID"),
            Username=username,
            GroupName="TeamMembers",
        )

        return {"message": "Team member created successfully!","response":response}
    
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))