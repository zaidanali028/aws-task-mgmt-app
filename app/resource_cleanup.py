import boto3

# Initialize the client for ELBv2 (Application Load Balancer)
elb_client = boto3.client('elbv2')

# Specify the ARN of the ALB you want to delete
load_balancer_arn = "arn:aws:elasticloadbalancing:eu-west-1:774305574116:loadbalancer/app/ec2-ecr-alb/c9e0ec9ca3cdb594"  # Replace with your ALB ARN

# Delete the ALB
try:
    elb_client.delete_load_balancer(
        LoadBalancerArn=load_balancer_arn
    )
    print(f"Successfully deleted the ALB with ARN: {load_balancer_arn}")
except Exception as e:
    print(f"Error deleting ALB: {e}")
