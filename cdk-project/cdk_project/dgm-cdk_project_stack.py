from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as aws_events,
    aws_events_targets as aws_events_targets,
    aws_iam as aws_iam,
    aws_dynamodb as aws_dynamodb,
    aws_cognito as aws_cognito,
    aws_ses as aws_ses,
)
from constructs import Construct
from utils import load_env


class CdkProjectStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load environment variables
        project_environment = load_env()

        # Lambda Layer
        self.layer = _lambda.LayerVersion(
            self,
            "TaskMgmtDependenciesLayer",
            code=_lambda.Code.from_asset("../lambda_layer/lambda_layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Shared dependencies for FastAPI and AWS SDK",
        )

        # Existing IAM Role
        existing_role = aws_iam.Role.from_role_arn(
            self,
            "taskMgmtApp",
            "arn:aws:iam::774305574116:role/taskMgmtApp",
            mutable=False,
        )

     

     

        # Main FastAPI Lambda Function
        self.fastapi_lambda = _lambda.Function(
            self,
            "FastAPILambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.main.handler",
            code=_lambda.Code.from_asset("../app/"),
            layers=[self.layer],
            role=existing_role,
            environment={
                **project_environment,
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "TASK_TABLE_NAME": self.task_table.table_name,
            },
        )

        # Grant permissions to FastAPI Lambda
        self.task_table.grant_read_write_data(self.fastapi_lambda)
        self.user_pool.grant(
            self.fastapi_lambda,
            "cognito-idp:AdminCreateUser",
            "cognito-idp:AdminSetUserPassword",
        )

        # EventBuses
        self.task_created_event_bus = aws_events.EventBus(
            self, "TaskCreatedEventBus", event_bus_name="TaskCreatedEventBus"
        )
        self.task_updated_event_bus = aws_events.EventBus(
            self, "TaskUpdatedEventBus", event_bus_name="TaskUpdatedEventBus"
        )
        self.user_created_event_bus = aws_events.EventBus(
            self, "UserCreatedEventBus", event_bus_name="UserCreatedEventBus"
        )

        # Listener for User Created Event
        user_created_listener = _lambda.Function(
            self,
            "UserCreatedListener",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../listeners/user_created"),
            layers=[self.layer],
            role=existing_role,
           
        )
        aws_events.Rule(
            self,
            "UserCreatedRule",
            event_bus=self.user_created_event_bus,
            event_pattern={
                "source": ["app.taskmgmt"],
                "detail_type": ["UserCreated"],
            },
            targets=[aws_events_targets.LambdaFunction(user_created_listener)],
        )

        # Listener for Task Created Event
        task_created_listener = _lambda.Function(
            self,
            "TaskCreatedListener",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../listeners/task_created"),
            layers=[self.layer],
            role=existing_role,
         
        )
        aws_events.Rule(
            self,
            "TaskCreatedRule",
            event_bus=self.task_created_event_bus,
            event_pattern={
                "source": ["app.taskmgmt"],
                "detail_type": ["TaskCreated"],
            },
            targets=[aws_events_targets.LambdaFunction(task_created_listener)],
        )

        # Listener for Task Updated Event
        task_updated_listener = _lambda.Function(
            self,
            "TaskUpdatedListener",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../listeners/task_updated"),
            layers=[self.layer],
            role=existing_role,
        )
        aws_events.Rule(
            self,
            "TaskUpdatedRule",
            event_bus=self.task_updated_event_bus,
            event_pattern={
                "source": ["app.taskmgmt"],
                "detail_type": ["TaskUpdated"],
            },
            targets=[aws_events_targets.LambdaFunction(task_updated_listener)],
        )

        # Reminder Lambda Function for Task Deadlines
        reminder_lambda = _lambda.Function(
            self,
            "TaskReminderLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../listeners/task_due"),
            layers=[self.layer],
            role=existing_role,
           
        )

        # EventBridge Rule to schedule the Reminder Lambda daily at 8 AM UTC
        aws_events.Rule(
            self,
            "DailyTaskReminderRule",
            schedule=aws_events.Schedule.cron(minute="0", hour="8"),
            targets=[aws_events_targets.LambdaFunction(reminder_lambda)],
        )
        
        
           # DynamoDB Table for Tasks
        self.task_table = aws_dynamodb.Table(
            self,
            "Tasks",
            partition_key=aws_dynamodb.Attribute(name="task_id", type=aws_dynamodb.AttributeType.STRING),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        ),
           # SES Email Identity
        self.email_identity = aws_ses.EmailIdentity(
            self,
            "EmailIdentity",
            identity=aws_ses.Identity.email("zaidanali028@gmail.com"),
        )
        

        # Cognito User Pool for Authentication
        self.user_pool = aws_cognito.UserPool(
            self,
            "UserPool",
           )