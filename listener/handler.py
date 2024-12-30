import json
import time
# ses_client = boto3.client("ses", region_name="us-east-1")  # Replace with your SES region
def handler(event, context):
    start_time = time.time()  # Record the start time
    print("Received event:", json.dumps(event))  # Log event
    end_time = time.time()  # Record the end time
    # Calculate and log the execution time
    execution_time = end_time - start_time
    print(f"Time taken for print statement: {execution_time:.6f} seconds")
    return {
        "statusCode": 200,
        "body": json.dumps("Event logged successfully")
    }