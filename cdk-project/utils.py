import consts as constants
from dotenv import load_dotenv



load_dotenv()

def load_env():
    # AWS Cognito configuration
    MY_AWS_REGION = constants.MY_AWS_REGION
    COGNITO_USER_POOL_ID = constants.COGNITO_USER_POOL_ID
    COGNITO_APP_CLIENT_ID = constants.COGNITO_APP_CLIENT_ID
    COGNITO_APP_CLIENT_SECRET = constants.COGNITO_APP_CLIENT_SECRET
    DYNAMODB_TABLE_NAME=constants.DYNAMODB_TABLE_NAME
    EVENT_BUS_NAME=constants.EVENT_BUS_NAME

    # raise the values as a dictionary
    return {
        "MY_AWS_REGION": MY_AWS_REGION,
        "COGNITO_USER_POOL_ID": COGNITO_USER_POOL_ID,
        "COGNITO_APP_CLIENT_ID": COGNITO_APP_CLIENT_ID,
        "COGNITO_APP_CLIENT_SECRET": COGNITO_APP_CLIENT_SECRET,
        "DYNAMODB_TABLE_NAME":DYNAMODB_TABLE_NAME,
        "EVENT_BUS_NAME":EVENT_BUS_NAME
    }
    

