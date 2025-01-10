from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam,
    Stack,
    aws_events_targets,
    aws_events
)
from constructs import Construct
from utils import load_env

class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Layer
        self.layer = _lambda.LayerVersion(
            self,
            "TaskMgmtDependenciesLayer",
            code=_lambda.Code.from_asset("../lambda_layer/lambda_layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Shared dependencies for FastAPI and AWS SDK"
        )

        # Existing IAM Role
        existing_role = aws_iam.Role.from_role_arn(
            self,
            "taskMgmtApp",
            "arn:aws:iam::774305574116:role/taskMgmtApp",
            mutable=False
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

        # Main FastAPI Lambda Function
        project_environment = load_env()
        self.fastapi_lambda = _lambda.Function(
            self,
            "FastAPILambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.main.handler",
            code=_lambda.Code.from_asset("../app/"),
            layers=[self.layer],
            role=existing_role,
            environment=project_environment
        )


# UPDATED: Added EventBridge Rules for Task Reminders

        # Reminder Lambda Function for Task Deadlines
        reminder_lambda = _lambda.Function(
            self,
            "TaskReminderLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../listeners/task_due"),
            layers=[self.layer],
            role=existing_role,
            environment=project_environment
        )

        # EventBridge Rule to schedule the Reminder Lambda daily at 8 AM UTC
        aws_events.Rule(
            self,
            "DailyTaskReminderRule",
            schedule=aws_events.Schedule.cron(minute="00", hour="14"),
            targets=[aws_events_targets.LambdaFunction(reminder_lambda)]
        )
