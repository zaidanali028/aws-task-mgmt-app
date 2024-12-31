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
        
        # emit event using event bridge
        event_response=utils.publish_user_created_event(team_member.email,team_member.given_name,team_member.family_name)

        return {"message": "Team member created successfully!","response":response,"event_response":event_response}
    
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
    
@router.get("/users", summary="Get all users excluding the logged-in user/admin")
async def get_all_users(token: str = Depends(oauth2_scheme)):
    """
    Fetches all users from the 'TeamMembers' group in Cognito, excluding the logged-in user.
    Returns their names and usernames.
    """
    # Verify the token and extract user details
    decoded_token = utils.verify_token(token, 'Admins')
    logged_in_user_username = decoded_token.get('decoded_token', {}).get("username")
    
    if not logged_in_user_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to retrieve the logged-in user's username."
        )

    cognito_client = boto3.client('cognito-idp', region_name=my_env_vars.get("MY_AWS_REGION"))

    try:
        user_pool_id = my_env_vars.get("COGNITO_USER_POOL_ID")
        users = []
        pagination_token = None

        # Fetch users in the "TeamMembers" group
        while True:
            if pagination_token:
                response = cognito_client.list_users_in_group(
                    UserPoolId=user_pool_id,
                    GroupName="TeamMembers",
                    NextToken=pagination_token
                )
            else:
                response = cognito_client.list_users_in_group(
                    UserPoolId=user_pool_id,
                    GroupName="TeamMembers"
                )
            
            for user in response.get('Users', []):
                username = user.get("Username")
                if username != logged_in_user_username:
                    # Extract desired attributes
                    given_name = next(
                        (attr['Value'] for attr in user.get('Attributes', []) if attr['Name'] == 'given_name'), "N/A"
                    )
                    family_name = next(
                        (attr['Value'] for attr in user.get('Attributes', []) if attr['Name'] == 'family_name'), "N/A"
                    )
                    users.append({"username": username, "name": f"{given_name} {family_name}"})
            
            # Check if more pages are available
            pagination_token = response.get('NextToken')
            if not pagination_token:
                break
        
        return {"users": users}

    except cognito_client.exceptions.ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The TeamMembers group or user pool was not found."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )