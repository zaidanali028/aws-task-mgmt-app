

from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam, aws_lambda,
    Stack,
   aws_events_targets,
   aws_events
)
from constructs import Construct
from utils import load_env

class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Lambda layer
        self.layer = _lambda.LayerVersion(
            self,
            "TaskMgmtDependenciesLayer",
            code=_lambda.Code.from_asset("../lambda_layer/lambda_layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Shared dependencies for FastAPI and AWS SDK"
        )


        # Existing Layer from Step 2
        layer = self.layer
        
        
        
         # Reference the existing IAM role 3
        existing_role = aws_iam.Role.from_role_arn(
            self,
            "taskMgmtApp",
            "arn:aws:iam::774305574116:role/taskMgmtApp",
            mutable=False
        )

       

        # EventBus 4
        self.event_bus = aws_events.EventBus(
            self, "TaskMgmtEventBus", event_bus_name="TaskMgmtEventBus"
        )
        
        # FastAPI Lambda function 5
        # from app.utils import utils
        # not working :(
            

        # not at the top to prevent circular import
        project_environment=load_env()
        self.fastapi_lambda = aws_lambda.Function(
            self,
            "FastAPILambdaFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="app.main.handler",
            code=aws_lambda.Code.from_asset("../app/"),
            layers=[layer],
            role=existing_role,
            environment=project_environment
        )
        
           # Listener Lambda function 6
        listener_lambda = aws_lambda.Function(
            self,
            "ListenerLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="handler.handler",
            code=aws_lambda.Code.from_asset("../listener"),
            layers=[self.layer],
            role=existing_role,
        )
        
        
          # Add rule to EventBus 7
        aws_events.Rule(
            self,
            "TaskCreatedRule",
            event_bus=self.event_bus,
            event_pattern={
                "source": ["app.taskmgmt"],
                "detail_type": ["UserCreated"],
            },
            targets=[aws_events_targets.LambdaFunction(listener_lambda)],
        )
