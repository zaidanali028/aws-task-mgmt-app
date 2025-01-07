import json
import boto3

# Initialize SES client
ses_client = boto3.client("ses", region_name="eu-west-1")

def handler(event, context):
    try:
        print("Received event:", json.dumps(event))  

        # Extract task details from the event
        detail = event.get("detail", {})
        recipient_email = detail.get("email", "recipient@example.com")  # Replace with actual email mapping
        title = detail.get("title", "No Title")
        description = detail.get("description", "No Description")
        deadline = detail.get("deadline", "No Deadline")
        task_status = detail.get("task_status", "No Status")
        assigned_to = detail.get("assigned_to", "No Assignee")

        # Email content
        subject = f"New Task Assigned: {title}"
        body_text = (
            f"Hello,\n\n"
            f"A new task has been assigned to you:\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Status: {task_status}\n\n"
            f"Please log in to the system to view more details.\n\n"
            f"#awsEventBridge"
        )

        # Sending email using SES
        response = ses_client.send_email(
            Source="zaidanali028@gmail.com",  # Verified email on SES
            Destination={"ToAddresses": [recipient_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}},
            },
        )
        print(f"Email sent successfully: {response}")
        return {"statusCode": 200, "body": "Task creation email sent successfully!"}

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
