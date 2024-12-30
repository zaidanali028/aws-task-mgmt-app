'''
# AWS CodePipeline Construct Library

<!--BEGIN STABILITY BANNER-->---


![End-of-Support](https://img.shields.io/badge/End--of--Support-critical.svg?style=for-the-badge)

> AWS CDK v1 has reached End-of-Support on 2023-06-01.
> This package is no longer being updated, and users should migrate to AWS CDK v2.
>
> For more information on how to migrate, see the [*Migrating to AWS CDK v2* guide](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html).

---
<!--END STABILITY BANNER-->

## Pipeline

To construct an empty Pipeline:

```python
# Construct an empty Pipeline
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline")
```

To give the Pipeline a nice, human-readable name:

```python
# Give the Pipeline a nice, human-readable name
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    pipeline_name="MyPipeline"
)
```

Be aware that in the default configuration, the `Pipeline` construct creates
an AWS Key Management Service (AWS KMS) Customer Master Key (CMK) for you to
encrypt the artifacts in the artifact bucket, which incurs a cost of
**$1/month**. This default configuration is necessary to allow cross-account
actions.

If you do not intend to perform cross-account deployments, you can disable
the creation of the Customer Master Keys by passing `crossAccountKeys: false`
when defining the Pipeline:

```python
# Don't create Customer Master Keys
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    cross_account_keys=False
)
```

If you want to enable key rotation for the generated KMS keys,
you can configure it by passing `enableKeyRotation: true` when creating the pipeline.
Note that key rotation will incur an additional cost of **$1/month**.

```python
# Enable key rotation for the generated KMS key
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    # ...
    enable_key_rotation=True
)
```

## Stages

You can provide Stages when creating the Pipeline:

```python
# Provide a Stage when creating a pipeline
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    stages=[codepipeline.StageProps(
        stage_name="Source",
        actions=[]
    )
    ]
)
```

Or append a Stage to an existing Pipeline:

```python
# Append a Stage to an existing Pipeline
# pipeline: codepipeline.Pipeline

source_stage = pipeline.add_stage(
    stage_name="Source",
    actions=[]
)
```

You can insert the new Stage at an arbitrary point in the Pipeline:

```python
# Insert a new Stage at an arbitrary point
# pipeline: codepipeline.Pipeline
# another_stage: codepipeline.IStage
# yet_another_stage: codepipeline.IStage


some_stage = pipeline.add_stage(
    stage_name="SomeStage",
    placement=codepipeline.StagePlacement(
        # note: you can only specify one of the below properties
        right_before=another_stage,
        just_after=yet_another_stage
    )
)
```

You can disable transition to a Stage:

```python
# Disable transition to a stage
# pipeline: codepipeline.Pipeline


some_stage = pipeline.add_stage(
    stage_name="SomeStage",
    transition_to_enabled=False,
    transition_disabled_reason="Manual transition only"
)
```

This is useful if you don't want every executions of the pipeline to flow into
this stage automatically. The transition can then be "manually" enabled later on.

## Actions

Actions live in a separate package, `@aws-cdk/aws-codepipeline-actions`.

To add an Action to a Stage, you can provide it when creating the Stage,
in the `actions` property,
or you can use the `IStage.addAction()` method to mutate an existing Stage:

```python
# Use the `IStage.addAction()` method to mutate an existing Stage.
# source_stage: codepipeline.IStage
# some_action: codepipeline.Action

source_stage.add_action(some_action)
```

## Custom Action Registration

To make your own custom CodePipeline Action requires registering the action provider. Look to the `JenkinsProvider` in `@aws-cdk/aws-codepipeline-actions` for an implementation example.

```python
# Make a custom CodePipeline Action
codepipeline.CustomActionRegistration(self, "GenericGitSourceProviderResource",
    category=codepipeline.ActionCategory.SOURCE,
    artifact_bounds=codepipeline.ActionArtifactBounds(min_inputs=0, max_inputs=0, min_outputs=1, max_outputs=1),
    provider="GenericGitSource",
    version="1",
    entity_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
    execution_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
    action_properties=[codepipeline.CustomActionProperty(
        name="Branch",
        required=True,
        key=False,
        secret=False,
        queryable=False,
        description="Git branch to pull",
        type="String"
    ), codepipeline.CustomActionProperty(
        name="GitUrl",
        required=True,
        key=False,
        secret=False,
        queryable=False,
        description="SSH git clone URL",
        type="String"
    )
    ]
)
```

## Cross-account CodePipelines

> Cross-account Pipeline actions require that the Pipeline has *not* been
> created with `crossAccountKeys: false`.

Most pipeline Actions accept an AWS resource object to operate on. For example:

* `S3DeployAction` accepts an `s3.IBucket`.
* `CodeBuildAction` accepts a `codebuild.IProject`.
* etc.

These resources can be either newly defined (`new s3.Bucket(...)`) or imported
(`s3.Bucket.fromBucketAttributes(...)`) and identify the resource that should
be changed.

These resources can be in different accounts than the pipeline itself. For
example, the following action deploys to an imported S3 bucket from a
different account:

```python
# Deploy an imported S3 bucket from a different account
# stage: codepipeline.IStage
# input: codepipeline.Artifact

stage.add_action(codepipeline_actions.S3DeployAction(
    bucket=s3.Bucket.from_bucket_attributes(self, "Bucket",
        account="123456789012"
    ),
    input=input,
    action_name="s3-deploy-action"
))
```

Actions that don't accept a resource object accept an explicit `account` parameter:

```python
# Actions that don't accept a resource objet accept an explicit `account` parameter
# stage: codepipeline.IStage
# template_path: codepipeline.ArtifactPath

stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
    account="123456789012",
    template_path=template_path,
    admin_permissions=False,
    stack_name=Stack.of(self).stack_name,
    action_name="cloudformation-create-update"
))
```

The `Pipeline` construct automatically defines an **IAM Role** for you in the
target account which the pipeline will assume to perform that action. This
Role will be defined in a **support stack** named
`<PipelineStackName>-support-<account>`, that will automatically be deployed
before the stack containing the pipeline.

If you do not want to use the generated role, you can also explicitly pass a
`role` when creating the action. In that case, the action will operate in the
account the role belongs to:

```python
# Explicitly pass in a `role` when creating an action.
# stage: codepipeline.IStage
# template_path: codepipeline.ArtifactPath

stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
    template_path=template_path,
    admin_permissions=False,
    stack_name=Stack.of(self).stack_name,
    action_name="cloudformation-create-update",
    # ...
    role=iam.Role.from_role_arn(self, "ActionRole", "...")
))
```

## Cross-region CodePipelines

Similar to how you set up a cross-account Action, the AWS resource object you
pass to actions can also be in different *Regions*. For example, the
following Action deploys to an imported S3 bucket from a different Region:

```python
# Deploy to an imported S3 bucket from a different Region.
# stage: codepipeline.IStage
# input: codepipeline.Artifact

stage.add_action(codepipeline_actions.S3DeployAction(
    bucket=s3.Bucket.from_bucket_attributes(self, "Bucket",
        region="us-west-1"
    ),
    input=input,
    action_name="s3-deploy-action"
))
```

Actions that don't take an AWS resource will accept an explicit `region`
parameter:

```python
# Actions that don't take an AWS resource will accept an explicit `region` parameter.
# stage: codepipeline.IStage
# template_path: codepipeline.ArtifactPath

stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
    template_path=template_path,
    admin_permissions=False,
    stack_name=Stack.of(self).stack_name,
    action_name="cloudformation-create-update",
    # ...
    region="us-west-1"
))
```

The `Pipeline` construct automatically defines a **replication bucket** for
you in the target region, which the pipeline will replicate artifacts to and
from. This Bucket will be defined in a **support stack** named
`<PipelineStackName>-support-<region>`, that will automatically be deployed
before the stack containing the pipeline.

If you don't want to use these support stacks, and already have buckets in
place to serve as replication buckets, you can supply these at Pipeline definition
time using the `crossRegionReplicationBuckets` parameter. Example:

```python
# Supply replication buckets for the Pipeline instead of using the generated support stack
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    # ...

    cross_region_replication_buckets={
        # note that a physical name of the replication Bucket must be known at synthesis time
        "us-west-1": s3.Bucket.from_bucket_attributes(self, "UsWest1ReplicationBucket",
            bucket_name="my-us-west-1-replication-bucket",
            # optional KMS key
            encryption_key=kms.Key.from_key_arn(self, "UsWest1ReplicationKey", "arn:aws:kms:us-west-1:123456789012:key/1234-5678-9012")
        )
    }
)
```

See [the AWS docs here](https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-cross-region.html)
for more information on cross-region CodePipelines.

### Creating an encrypted replication bucket

If you're passing a replication bucket created in a different stack,
like this:

```python
# Passing a replication bucket created in a different stack.
app = App()
replication_stack = Stack(app, "ReplicationStack",
    env=Environment(
        region="us-west-1"
    )
)
key = kms.Key(replication_stack, "ReplicationKey")
replication_bucket = s3.Bucket(replication_stack, "ReplicationBucket",
    # like was said above - replication buckets need a set physical name
    bucket_name=PhysicalName.GENERATE_IF_NEEDED,
    encryption_key=key
)

# later...
codepipeline.Pipeline(replication_stack, "Pipeline",
    cross_region_replication_buckets={
        "us-west-1": replication_bucket
    }
)
```

When trying to encrypt it
(and note that if any of the cross-region actions happen to be cross-account as well,
the bucket *has to* be encrypted - otherwise the pipeline will fail at runtime),
you cannot use a key directly - KMS keys don't have physical names,
and so you can't reference them across environments.

In this case, you need to use an alias in place of the key when creating the bucket:

```python
# Passing an encrypted replication bucket created in a different stack.
app = App()
replication_stack = Stack(app, "ReplicationStack",
    env=Environment(
        region="us-west-1"
    )
)
key = kms.Key(replication_stack, "ReplicationKey")
alias = kms.Alias(replication_stack, "ReplicationAlias",
    # aliasName is required
    alias_name=PhysicalName.GENERATE_IF_NEEDED,
    target_key=key
)
replication_bucket = s3.Bucket(replication_stack, "ReplicationBucket",
    bucket_name=PhysicalName.GENERATE_IF_NEEDED,
    encryption_key=alias
)
```

## Variables

The library supports the CodePipeline Variables feature.
Each action class that emits variables has a separate variables interface,
accessed as a property of the action instance called `variables`.
You instantiate the action class and assign it to a local variable;
when you want to use a variable in the configuration of a different action,
you access the appropriate property of the interface returned from `variables`,
which represents a single variable.
Example:

```python
# MyAction is some action type that produces variables, like EcrSourceAction
my_action = MyAction(
    # ...
    action_name="myAction"
)
OtherAction(
    # ...
    config=my_action.variables.my_variable,
    action_name="otherAction"
)
```

The namespace name that will be used will be automatically generated by the pipeline construct,
based on the stage and action name;
you can pass a custom name when creating the action instance:

```python
# MyAction is some action type that produces variables, like EcrSourceAction
my_action = MyAction(
    # ...
    variables_namespace="MyNamespace",
    action_name="myAction"
)
```

There are also global variables available,
not tied to any action;
these are accessed through static properties of the `GlobalVariables` class:

```python
# OtherAction is some action type that produces variables, like EcrSourceAction
OtherAction(
    # ...
    config=codepipeline.GlobalVariables.execution_id,
    action_name="otherAction"
)
```

Check the documentation of the `@aws-cdk/aws-codepipeline-actions`
for details on how to use the variables for each action class.

See the [CodePipeline documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-variables.html)
for more details on how to use the variables feature.

## Events

### Using a pipeline as an event target

A pipeline can be used as a target for a CloudWatch event rule:

```python
# A pipeline being used as a target for a CloudWatch event rule.
import aws_cdk.aws_events_targets as targets
import aws_cdk.aws_events as events

# pipeline: codepipeline.Pipeline


# kick off the pipeline every day
rule = events.Rule(self, "Daily",
    schedule=events.Schedule.rate(Duration.days(1))
)
rule.add_target(targets.CodePipeline(pipeline))
```

When a pipeline is used as an event target, the
"codepipeline:StartPipelineExecution" permission is granted to the AWS
CloudWatch Events service.

### Event sources

Pipelines emit CloudWatch events. To define event rules for events emitted by
the pipeline, stages or action, use the `onXxx` methods on the respective
construct:

```python
# Define event rules for events emitted by the pipeline
import aws_cdk.aws_events as events

# my_pipeline: codepipeline.Pipeline
# my_stage: codepipeline.IStage
# my_action: codepipeline.Action
# target: events.IRuleTarget

my_pipeline.on_state_change("MyPipelineStateChange", target=target)
my_stage.on_state_change("MyStageStateChange", target)
my_action.on_state_change("MyActionStateChange", target)
```

## CodeStar Notifications

To define CodeStar Notification rules for Pipelines, use one of the `notifyOnXxx()` methods.
They are very similar to `onXxx()` methods for CloudWatch events:

```python
# Define CodeStar Notification rules for Pipelines
import aws_cdk.aws_chatbot as chatbot

# pipeline: codepipeline.Pipeline

target = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
    slack_channel_configuration_name="YOUR_CHANNEL_NAME",
    slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
    slack_channel_id="YOUR_SLACK_CHANNEL_ID"
)
rule = pipeline.notify_on_execution_state_change("NotifyOnExecutionStateChange", target)
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk.aws_codestarnotifications as _aws_cdk_aws_codestarnotifications_391e8ded
import aws_cdk.aws_events as _aws_cdk_aws_events_efcdfa54
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_55f001a5
import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.ActionArtifactBounds",
    jsii_struct_bases=[],
    name_mapping={
        "max_inputs": "maxInputs",
        "max_outputs": "maxOutputs",
        "min_inputs": "minInputs",
        "min_outputs": "minOutputs",
    },
)
class ActionArtifactBounds:
    def __init__(
        self,
        *,
        max_inputs: jsii.Number,
        max_outputs: jsii.Number,
        min_inputs: jsii.Number,
        min_outputs: jsii.Number,
    ) -> None:
        '''Specifies the constraints on the number of input and output artifacts an action can have.

        The constraints for each action type are documented on the
        {@link https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html Pipeline Structure Reference} page.

        :param max_inputs: 
        :param max_outputs: 
        :param min_inputs: 
        :param min_outputs: 

        :exampleMetadata: fixture=action infused

        Example::

            # MyAction is some action type that produces variables, like EcrSourceAction
            my_action = MyAction(
                # ...
                action_name="myAction"
            )
            OtherAction(
                # ...
                config=my_action.variables.my_variable,
                action_name="otherAction"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49437c0971e28d40061501b41b10bef84bbde7bc57c839a7171d8affd27f2163)
            check_type(argname="argument max_inputs", value=max_inputs, expected_type=type_hints["max_inputs"])
            check_type(argname="argument max_outputs", value=max_outputs, expected_type=type_hints["max_outputs"])
            check_type(argname="argument min_inputs", value=min_inputs, expected_type=type_hints["min_inputs"])
            check_type(argname="argument min_outputs", value=min_outputs, expected_type=type_hints["min_outputs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_inputs": max_inputs,
            "max_outputs": max_outputs,
            "min_inputs": min_inputs,
            "min_outputs": min_outputs,
        }

    @builtins.property
    def max_inputs(self) -> jsii.Number:
        result = self._values.get("max_inputs")
        assert result is not None, "Required property 'max_inputs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def max_outputs(self) -> jsii.Number:
        result = self._values.get("max_outputs")
        assert result is not None, "Required property 'max_outputs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_inputs(self) -> jsii.Number:
        result = self._values.get("min_inputs")
        assert result is not None, "Required property 'min_inputs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_outputs(self) -> jsii.Number:
        result = self._values.get("min_outputs")
        assert result is not None, "Required property 'min_outputs' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionArtifactBounds(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.ActionBindOptions",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "role": "role"},
)
class ActionBindOptions:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> None:
        '''
        :param bucket: 
        :param role: 

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            import aws_cdk.aws_iam as iam
            import aws_cdk.aws_s3 as s3
            
            # bucket: s3.Bucket
            # role: iam.Role
            
            action_bind_options = codepipeline.ActionBindOptions(
                bucket=bucket,
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d95e267c604745fb56119c678b3c0dfb91677cacab5aef7f405e7c0dc87bc257)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "role": role,
        }

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_940a1ce0.IRole:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-codepipeline.ActionCategory")
class ActionCategory(enum.Enum):
    '''
    :exampleMetadata: fixture=action infused

    Example::

        # MyAction is some action type that produces variables, like EcrSourceAction
        my_action = MyAction(
            # ...
            action_name="myAction"
        )
        OtherAction(
            # ...
            config=my_action.variables.my_variable,
            action_name="otherAction"
        )
    '''

    SOURCE = "SOURCE"
    BUILD = "BUILD"
    TEST = "TEST"
    APPROVAL = "APPROVAL"
    DEPLOY = "DEPLOY"
    INVOKE = "INVOKE"


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.ActionConfig",
    jsii_struct_bases=[],
    name_mapping={"configuration": "configuration"},
)
class ActionConfig:
    def __init__(self, *, configuration: typing.Any = None) -> None:
        '''
        :param configuration: 

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            # configuration: Any
            
            action_config = codepipeline.ActionConfig(
                configuration=configuration
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aafaa1bf0422ec59bdd95cd4eb1d4a9364ad38b88b4ff99f0055b4140ef7b3e)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if configuration is not None:
            self._values["configuration"] = configuration

    @builtins.property
    def configuration(self) -> typing.Any:
        result = self._values.get("configuration")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.ActionProperties",
    jsii_struct_bases=[],
    name_mapping={
        "action_name": "actionName",
        "artifact_bounds": "artifactBounds",
        "category": "category",
        "provider": "provider",
        "account": "account",
        "inputs": "inputs",
        "outputs": "outputs",
        "owner": "owner",
        "region": "region",
        "resource": "resource",
        "role": "role",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "version": "version",
    },
)
class ActionProperties:
    def __init__(
        self,
        *,
        action_name: builtins.str,
        artifact_bounds: typing.Union[ActionArtifactBounds, typing.Dict[builtins.str, typing.Any]],
        category: ActionCategory,
        provider: builtins.str,
        account: typing.Optional[builtins.str] = None,
        inputs: typing.Optional[typing.Sequence["Artifact"]] = None,
        outputs: typing.Optional[typing.Sequence["Artifact"]] = None,
        owner: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        resource: typing.Optional[_aws_cdk_core_f4b25747.IResource] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_name: 
        :param artifact_bounds: 
        :param category: The category of the action. The category defines which action type the owner (the entity that performs the action) performs.
        :param provider: The service provider that the action calls.
        :param account: The account the Action is supposed to live in. For Actions backed by resources, this is inferred from the Stack {@link resource} is part of. However, some Actions, like the CloudFormation ones, are not backed by any resource, and they still might want to be cross-account. In general, a concrete Action class should specify either {@link resource}, or {@link account} - but not both.
        :param inputs: 
        :param outputs: 
        :param owner: 
        :param region: The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param resource: The optional resource that is backing this Action. This is used for automatically handling Actions backed by resources from a different account and/or region.
        :param role: 
        :param run_order: The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide. https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names
        :param version: 

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            import aws_cdk.aws_iam as iam
            import aws_cdk.core as cdk
            
            # artifact: codepipeline.Artifact
            # resource: cdk.Resource
            # role: iam.Role
            
            action_properties = codepipeline.ActionProperties(
                action_name="actionName",
                artifact_bounds=codepipeline.ActionArtifactBounds(
                    max_inputs=123,
                    max_outputs=123,
                    min_inputs=123,
                    min_outputs=123
                ),
                category=codepipeline.ActionCategory.SOURCE,
                provider="provider",
            
                # the properties below are optional
                account="account",
                inputs=[artifact],
                outputs=[artifact],
                owner="owner",
                region="region",
                resource=resource,
                role=role,
                run_order=123,
                variables_namespace="variablesNamespace",
                version="version"
            )
        '''
        if isinstance(artifact_bounds, dict):
            artifact_bounds = ActionArtifactBounds(**artifact_bounds)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f4cfd8eb0ae80afe471c2da4f2e9123b86c4807079be718470ed88f1fe6c053)
            check_type(argname="argument action_name", value=action_name, expected_type=type_hints["action_name"])
            check_type(argname="argument artifact_bounds", value=artifact_bounds, expected_type=type_hints["artifact_bounds"])
            check_type(argname="argument category", value=category, expected_type=type_hints["category"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument inputs", value=inputs, expected_type=type_hints["inputs"])
            check_type(argname="argument outputs", value=outputs, expected_type=type_hints["outputs"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument run_order", value=run_order, expected_type=type_hints["run_order"])
            check_type(argname="argument variables_namespace", value=variables_namespace, expected_type=type_hints["variables_namespace"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action_name": action_name,
            "artifact_bounds": artifact_bounds,
            "category": category,
            "provider": provider,
        }
        if account is not None:
            self._values["account"] = account
        if inputs is not None:
            self._values["inputs"] = inputs
        if outputs is not None:
            self._values["outputs"] = outputs
        if owner is not None:
            self._values["owner"] = owner
        if region is not None:
            self._values["region"] = region
        if resource is not None:
            self._values["resource"] = resource
        if role is not None:
            self._values["role"] = role
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def action_name(self) -> builtins.str:
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifact_bounds(self) -> ActionArtifactBounds:
        result = self._values.get("artifact_bounds")
        assert result is not None, "Required property 'artifact_bounds' is missing"
        return typing.cast(ActionArtifactBounds, result)

    @builtins.property
    def category(self) -> ActionCategory:
        '''The category of the action.

        The category defines which action type the owner
        (the entity that performs the action) performs.
        '''
        result = self._values.get("category")
        assert result is not None, "Required property 'category' is missing"
        return typing.cast(ActionCategory, result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''The service provider that the action calls.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The account the Action is supposed to live in.

        For Actions backed by resources,
        this is inferred from the Stack {@link resource} is part of.
        However, some Actions, like the CloudFormation ones,
        are not backed by any resource, and they still might want to be cross-account.
        In general, a concrete Action class should specify either {@link resource},
        or {@link account} - but not both.
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inputs(self) -> typing.Optional[typing.List["Artifact"]]:
        result = self._values.get("inputs")
        return typing.cast(typing.Optional[typing.List["Artifact"]], result)

    @builtins.property
    def outputs(self) -> typing.Optional[typing.List["Artifact"]]:
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.List["Artifact"]], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region the given Action resides in.

        Note that a cross-region Pipeline requires replication buckets to function correctly.
        You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property.
        If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets,
        that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        :default: the Action resides in the same region as the Pipeline
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource(self) -> typing.Optional[_aws_cdk_core_f4b25747.IResource]:
        '''The optional resource that is backing this Action.

        This is used for automatically handling Actions backed by
        resources from a different account and/or region.
        '''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.IResource], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide.

        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default: - a name will be generated, based on the stage and action names
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Artifact(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.Artifact"):
    '''An output artifact of an action.

    Artifacts can be used as input by some actions.

    :exampleMetadata: infused

    Example::

        # later:
        # project: codebuild.PipelineProject
        lambda_invoke_action = codepipeline_actions.LambdaInvokeAction(
            action_name="Lambda",
            lambda_=lambda_.Function(self, "Func",
                runtime=lambda_.Runtime.NODEJS_14_X,
                handler="index.handler",
                code=lambda_.Code.from_inline("""
                            const AWS = require('aws-sdk');
        
                            exports.handler = async function(event, context) {
                                const codepipeline = new AWS.CodePipeline();
                                await codepipeline.putJobSuccessResult({
                                    jobId: event['CodePipeline.job'].id,
                                    outputVariables: {
                                        MY_VAR: "some value",
                                    },
                                }).promise();
                            }
                        """)
            ),
            variables_namespace="MyNamespace"
        )
        source_output = codepipeline.Artifact()
        codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,
            environment_variables={
                "MyVar": codebuild.BuildEnvironmentVariable(
                    value=lambda_invoke_action.variable("MY_VAR")
                )
            }
        )
    '''

    def __init__(self, artifact_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param artifact_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2edd07d274634f766fff267d67eecee48019d0884972b001d42ea2960593d58)
            check_type(argname="argument artifact_name", value=artifact_name, expected_type=type_hints["artifact_name"])
        jsii.create(self.__class__, self, [artifact_name])

    @jsii.member(jsii_name="artifact")
    @builtins.classmethod
    def artifact(cls, name: builtins.str) -> "Artifact":
        '''A static factory method used to create instances of the Artifact class.

        Mainly meant to be used from ``decdk``.

        :param name: the (required) name of the Artifact.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fdfd021c480d32c1093a92cf683469e620a7e639046a7a28fdaf509ce0afb79)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("Artifact", jsii.sinvoke(cls, "artifact", [name]))

    @jsii.member(jsii_name="atPath")
    def at_path(self, file_name: builtins.str) -> "ArtifactPath":
        '''Returns an ArtifactPath for a file within this artifact.

        CfnOutput is in the form "::"

        :param file_name: The name of the file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bba6e9bee16bf93b686e614c794394bcf58cae233a630a37441474019de9d15)
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        return typing.cast("ArtifactPath", jsii.invoke(self, "atPath", [file_name]))

    @jsii.member(jsii_name="getMetadata")
    def get_metadata(self, key: builtins.str) -> typing.Any:
        '''Retrieve the metadata stored in this artifact under the given key.

        If there is no metadata stored under the given key,
        null will be returned.

        :param key: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f5b03f659c1db1d9d83621aa3fe7f5824e1a107aee0df03869ca3e0bbe8d321)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast(typing.Any, jsii.invoke(self, "getMetadata", [key]))

    @jsii.member(jsii_name="getParam")
    def get_param(
        self,
        json_file: builtins.str,
        key_name: builtins.str,
    ) -> builtins.str:
        '''Returns a token for a value inside a JSON file within this artifact.

        :param json_file: The JSON file name.
        :param key_name: The hash key.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e23b949c5346a804f686591a270d7030e82a3db64884865161f3f8efc981c19)
            check_type(argname="argument json_file", value=json_file, expected_type=type_hints["json_file"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "getParam", [json_file, key_name]))

    @jsii.member(jsii_name="setMetadata")
    def set_metadata(self, key: builtins.str, value: typing.Any) -> None:
        '''Add arbitrary extra payload to the artifact under a given key.

        This can be used by CodePipeline actions to communicate data between themselves.
        If metadata was already present under the given key,
        it will be overwritten with the new value.

        :param key: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc5dd1f6e7ef5ce0f269d73a32fd796caf9046c3d22a29e5c828c67674438b5a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "setMetadata", [key, value]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "toString", []))

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''The artifact attribute for the name of the S3 bucket where the artifact is stored.'''
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @builtins.property
    @jsii.member(jsii_name="objectKey")
    def object_key(self) -> builtins.str:
        '''The artifact attribute for The name of the .zip file that contains the artifact that is generated by AWS CodePipeline, such as 1ABCyZZ.zip.'''
        return typing.cast(builtins.str, jsii.get(self, "objectKey"))

    @builtins.property
    @jsii.member(jsii_name="s3Location")
    def s3_location(self) -> _aws_cdk_aws_s3_55f001a5.Location:
        '''Returns the location of the .zip file in S3 that this Artifact represents. Used by Lambda's ``CfnParametersCode`` when being deployed in a CodePipeline.'''
        return typing.cast(_aws_cdk_aws_s3_55f001a5.Location, jsii.get(self, "s3Location"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''The artifact attribute of the Amazon Simple Storage Service (Amazon S3) URL of the artifact, such as https://s3-us-west-2.amazonaws.com/artifactstorebucket-yivczw8jma0c/test/TemplateSo/1ABCyZZ.zip.'''
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="artifactName")
    def artifact_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactName"))


class ArtifactPath(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.ArtifactPath",
):
    '''A specific file within an output artifact.

    The most common use case for this is specifying the template file
    for a CloudFormation action.

    :exampleMetadata: lit=test/integ.cfn-template-from-repo.lit.ts infused

    Example::

        # Source stage: read from repository
        repo = codecommit.Repository(stack, "TemplateRepo",
            repository_name="template-repo"
        )
        source_output = codepipeline.Artifact("SourceArtifact")
        source = cpactions.CodeCommitSourceAction(
            action_name="Source",
            repository=repo,
            output=source_output,
            trigger=cpactions.CodeCommitTrigger.POLL
        )
        source_stage = {
            "stage_name": "Source",
            "actions": [source]
        }
        
        # Deployment stage: create and deploy changeset with manual approval
        stack_name = "OurStack"
        change_set_name = "StagedChangeSet"
        
        prod_stage = {
            "stage_name": "Deploy",
            "actions": [
                cpactions.CloudFormationCreateReplaceChangeSetAction(
                    action_name="PrepareChanges",
                    stack_name=stack_name,
                    change_set_name=change_set_name,
                    admin_permissions=True,
                    template_path=source_output.at_path("template.yaml"),
                    run_order=1
                ),
                cpactions.ManualApprovalAction(
                    action_name="ApproveChanges",
                    run_order=2
                ),
                cpactions.CloudFormationExecuteChangeSetAction(
                    action_name="ExecuteChanges",
                    stack_name=stack_name,
                    change_set_name=change_set_name,
                    run_order=3
                )
            ]
        }
        
        codepipeline.Pipeline(stack, "Pipeline",
            stages=[source_stage, prod_stage
            ]
        )
    '''

    def __init__(self, artifact: Artifact, file_name: builtins.str) -> None:
        '''
        :param artifact: -
        :param file_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e12a0f2b4d3abc9eb4dd8a50b401b04d20dec5a1a21309d1a54036d2a635e56d)
            check_type(argname="argument artifact", value=artifact, expected_type=type_hints["artifact"])
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        jsii.create(self.__class__, self, [artifact, file_name])

    @jsii.member(jsii_name="artifactPath")
    @builtins.classmethod
    def artifact_path(
        cls,
        artifact_name: builtins.str,
        file_name: builtins.str,
    ) -> "ArtifactPath":
        '''
        :param artifact_name: -
        :param file_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__566369c25dc33b8a0f2cdfaba4a57a1674455ba52b6cd443db74bee345c1803a)
            check_type(argname="argument artifact_name", value=artifact_name, expected_type=type_hints["artifact_name"])
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        return typing.cast("ArtifactPath", jsii.sinvoke(cls, "artifactPath", [artifact_name, file_name]))

    @builtins.property
    @jsii.member(jsii_name="artifact")
    def artifact(self) -> Artifact:
        return typing.cast(Artifact, jsii.get(self, "artifact"))

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnCustomActionType(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType",
):
    '''A CloudFormation ``AWS::CodePipeline::CustomActionType``.

    The ``AWS::CodePipeline::CustomActionType`` resource creates a custom action for activities that aren't included in the CodePipeline default actions, such as running an internally developed build process or a test suite. You can use these custom actions in the stage of a pipeline. For more information, see `Create and Add a Custom Action in AWS CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-custom-action.html>`_ in the *AWS CodePipeline User Guide* .

    :cloudformationResource: AWS::CodePipeline::CustomActionType
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codepipeline as codepipeline
        
        cfn_custom_action_type = codepipeline.CfnCustomActionType(self, "MyCfnCustomActionType",
            category="category",
            input_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                maximum_count=123,
                minimum_count=123
            ),
            output_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                maximum_count=123,
                minimum_count=123
            ),
            provider="provider",
            version="version",
        
            # the properties below are optional
            configuration_properties=[codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty(
                key=False,
                name="name",
                required=False,
                secret=False,
        
                # the properties below are optional
                description="description",
                queryable=False,
                type="type"
            )],
            settings=codepipeline.CfnCustomActionType.SettingsProperty(
                entity_url_template="entityUrlTemplate",
                execution_url_template="executionUrlTemplate",
                revision_url_template="revisionUrlTemplate",
                third_party_configuration_url="thirdPartyConfigurationUrl"
            ),
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        category: builtins.str,
        input_artifact_details: typing.Union[typing.Union["CfnCustomActionType.ArtifactDetailsProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
        output_artifact_details: typing.Union[typing.Union["CfnCustomActionType.ArtifactDetailsProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
        provider: builtins.str,
        version: builtins.str,
        configuration_properties: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnCustomActionType.ConfigurationPropertiesProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        settings: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnCustomActionType.SettingsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::CodePipeline::CustomActionType``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param category: The category of the custom action, such as a build action or a test action.
        :param input_artifact_details: The details of the input artifact for the action, such as its commit ID.
        :param output_artifact_details: The details of the output artifact of the action, such as its commit ID.
        :param provider: The provider of the service used in the custom action, such as CodeDeploy.
        :param version: The version identifier of the custom action.
        :param configuration_properties: The configuration properties for the custom action. .. epigraph:: You can refer to a name in the configuration properties of the custom action within the URL templates by following the format of {Config:name}, as long as the configuration property is both required and not secret. For more information, see `Create a Custom Action for a Pipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-custom-action.html>`_ .
        :param settings: URLs that provide users information about this custom action.
        :param tags: The tags for the custom action.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b97c1dd247aea8532e1bd6bc03a53a909902c2db4d6535790030356848640b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnCustomActionTypeProps(
            category=category,
            input_artifact_details=input_artifact_details,
            output_artifact_details=output_artifact_details,
            provider=provider,
            version=version,
            configuration_properties=configuration_properties,
            settings=settings,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8e330b3b8a34f8d7e36f547dde5f95051c07b0782784f5a78b8c64b2c39ea3f)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f6acebc8348182323be09e7e36b852add0a83c813a7e0f984fd41772c6f3860)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''The tags for the custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="category")
    def category(self) -> builtins.str:
        '''The category of the custom action, such as a build action or a test action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
        '''
        return typing.cast(builtins.str, jsii.get(self, "category"))

    @category.setter
    def category(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85aba90a3d0ab3f804acacf909d5ee5b57661aa3ed8064fbd498bfb84301c0eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "category", value)

    @builtins.property
    @jsii.member(jsii_name="inputArtifactDetails")
    def input_artifact_details(
        self,
    ) -> typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _aws_cdk_core_f4b25747.IResolvable]:
        '''The details of the input artifact for the action, such as its commit ID.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
        '''
        return typing.cast(typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _aws_cdk_core_f4b25747.IResolvable], jsii.get(self, "inputArtifactDetails"))

    @input_artifact_details.setter
    def input_artifact_details(
        self,
        value: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _aws_cdk_core_f4b25747.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__467ddb2c73ce4d8522b48f8b27695fbfc8201b8d465445a611e7c456ec7651cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputArtifactDetails", value)

    @builtins.property
    @jsii.member(jsii_name="outputArtifactDetails")
    def output_artifact_details(
        self,
    ) -> typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _aws_cdk_core_f4b25747.IResolvable]:
        '''The details of the output artifact of the action, such as its commit ID.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
        '''
        return typing.cast(typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _aws_cdk_core_f4b25747.IResolvable], jsii.get(self, "outputArtifactDetails"))

    @output_artifact_details.setter
    def output_artifact_details(
        self,
        value: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _aws_cdk_core_f4b25747.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99a5d79a11542631af9fab118778f9aca711a3e059200928a274791f467cecb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputArtifactDetails", value)

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        '''The provider of the service used in the custom action, such as CodeDeploy.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
        '''
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5843ffd71957c4b4e75a784a340cdcb79f0057db979b00181233add475fd73ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version identifier of the custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6415fa88f7bb064bcc3c44509d895676a63589b13508525a5fa462c66d860f13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="configurationProperties")
    def configuration_properties(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnCustomActionType.ConfigurationPropertiesProperty"]]]]:
        '''The configuration properties for the custom action.

        .. epigraph::

           You can refer to a name in the configuration properties of the custom action within the URL templates by following the format of {Config:name}, as long as the configuration property is both required and not secret. For more information, see `Create a Custom Action for a Pipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-custom-action.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnCustomActionType.ConfigurationPropertiesProperty"]]]], jsii.get(self, "configurationProperties"))

    @configuration_properties.setter
    def configuration_properties(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnCustomActionType.ConfigurationPropertiesProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__499b2d3dba84b2966125616c0dff272afab83b8007b83550794130475cc31438)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configurationProperties", value)

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnCustomActionType.SettingsProperty"]]:
        '''URLs that provide users information about this custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnCustomActionType.SettingsProperty"]], jsii.get(self, "settings"))

    @settings.setter
    def settings(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnCustomActionType.SettingsProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86d36b6dab88be8ad4e76e1e3476c14bc75d347b8fc3c8aab27d34f5fd222384)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "settings", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.ArtifactDetailsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "maximum_count": "maximumCount",
            "minimum_count": "minimumCount",
        },
    )
    class ArtifactDetailsProperty:
        def __init__(
            self,
            *,
            maximum_count: jsii.Number,
            minimum_count: jsii.Number,
        ) -> None:
            '''Returns information about the details of an artifact.

            :param maximum_count: The maximum number of artifacts allowed for the action type.
            :param minimum_count: The minimum number of artifacts allowed for the action type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                artifact_details_property = codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                    maximum_count=123,
                    minimum_count=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__1439a619a23e9709e7af30ae96e7cbd6d5e0965516099d1cb0d173849ffa6955)
                check_type(argname="argument maximum_count", value=maximum_count, expected_type=type_hints["maximum_count"])
                check_type(argname="argument minimum_count", value=minimum_count, expected_type=type_hints["minimum_count"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "maximum_count": maximum_count,
                "minimum_count": minimum_count,
            }

        @builtins.property
        def maximum_count(self) -> jsii.Number:
            '''The maximum number of artifacts allowed for the action type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-maximumcount
            '''
            result = self._values.get("maximum_count")
            assert result is not None, "Required property 'maximum_count' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def minimum_count(self) -> jsii.Number:
            '''The minimum number of artifacts allowed for the action type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-minimumcount
            '''
            result = self._values.get("minimum_count")
            assert result is not None, "Required property 'minimum_count' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactDetailsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "key": "key",
            "name": "name",
            "required": "required",
            "secret": "secret",
            "description": "description",
            "queryable": "queryable",
            "type": "type",
        },
    )
    class ConfigurationPropertiesProperty:
        def __init__(
            self,
            *,
            key: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
            name: builtins.str,
            required: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
            secret: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
            description: typing.Optional[builtins.str] = None,
            queryable: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            type: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The configuration properties for the custom action.

            .. epigraph::

               You can refer to a name in the configuration properties of the custom action within the URL templates by following the format of {Config:name}, as long as the configuration property is both required and not secret. For more information, see `Create a Custom Action for a Pipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-custom-action.html>`_ .

            :param key: Whether the configuration property is a key.
            :param name: The name of the action configuration property.
            :param required: Whether the configuration property is a required value.
            :param secret: Whether the configuration property is secret. Secrets are hidden from all calls except for ``GetJobDetails`` , ``GetThirdPartyJobDetails`` , ``PollForJobs`` , and ``PollForThirdPartyJobs`` . When updating a pipeline, passing * * * * * without changing any other values of the action preserves the previous value of the secret.
            :param description: The description of the action configuration property that is displayed to users.
            :param queryable: Indicates that the property is used with ``PollForJobs`` . When creating a custom action, an action can have up to one queryable property. If it has one, that property must be both required and not secret. If you create a pipeline with a custom action type, and that custom action contains a queryable property, the value for that configuration property is subject to other restrictions. The value must be less than or equal to twenty (20) characters. The value can contain only alphanumeric characters, underscores, and hyphens.
            :param type: The type of the configuration property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                configuration_properties_property = codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty(
                    key=False,
                    name="name",
                    required=False,
                    secret=False,
                
                    # the properties below are optional
                    description="description",
                    queryable=False,
                    type="type"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__ad1821cc0e55eff338d50046f5b1a19a662fcf01156cdeb53f57e5c171bb2f30)
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument required", value=required, expected_type=type_hints["required"])
                check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
                check_type(argname="argument description", value=description, expected_type=type_hints["description"])
                check_type(argname="argument queryable", value=queryable, expected_type=type_hints["queryable"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "key": key,
                "name": name,
                "required": required,
                "secret": secret,
            }
            if description is not None:
                self._values["description"] = description
            if queryable is not None:
                self._values["queryable"] = queryable
            if type is not None:
                self._values["type"] = type

        @builtins.property
        def key(
            self,
        ) -> typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]:
            '''Whether the configuration property is a key.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''The name of the action configuration property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def required(
            self,
        ) -> typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]:
            '''Whether the configuration property is a required value.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-required
            '''
            result = self._values.get("required")
            assert result is not None, "Required property 'required' is missing"
            return typing.cast(typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable], result)

        @builtins.property
        def secret(
            self,
        ) -> typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]:
            '''Whether the configuration property is secret.

            Secrets are hidden from all calls except for ``GetJobDetails`` , ``GetThirdPartyJobDetails`` , ``PollForJobs`` , and ``PollForThirdPartyJobs`` .

            When updating a pipeline, passing * * * * * without changing any other values of the action preserves the previous value of the secret.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-secret
            '''
            result = self._values.get("secret")
            assert result is not None, "Required property 'secret' is missing"
            return typing.cast(typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable], result)

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''The description of the action configuration property that is displayed to users.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def queryable(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Indicates that the property is used with ``PollForJobs`` .

            When creating a custom action, an action can have up to one queryable property. If it has one, that property must be both required and not secret.

            If you create a pipeline with a custom action type, and that custom action contains a queryable property, the value for that configuration property is subject to other restrictions. The value must be less than or equal to twenty (20) characters. The value can contain only alphanumeric characters, underscores, and hyphens.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-queryable
            '''
            result = self._values.get("queryable")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def type(self) -> typing.Optional[builtins.str]:
            '''The type of the configuration property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-type
            '''
            result = self._values.get("type")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConfigurationPropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.SettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "entity_url_template": "entityUrlTemplate",
            "execution_url_template": "executionUrlTemplate",
            "revision_url_template": "revisionUrlTemplate",
            "third_party_configuration_url": "thirdPartyConfigurationUrl",
        },
    )
    class SettingsProperty:
        def __init__(
            self,
            *,
            entity_url_template: typing.Optional[builtins.str] = None,
            execution_url_template: typing.Optional[builtins.str] = None,
            revision_url_template: typing.Optional[builtins.str] = None,
            third_party_configuration_url: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``Settings`` is a property of the ``AWS::CodePipeline::CustomActionType`` resource that provides URLs that users can access to view information about the CodePipeline custom action.

            :param entity_url_template: The URL returned to the CodePipeline console that provides a deep link to the resources of the external system, such as the configuration page for a CodeDeploy deployment group. This link is provided as part of the action display in the pipeline.
            :param execution_url_template: The URL returned to the CodePipeline console that contains a link to the top-level landing page for the external system, such as the console page for CodeDeploy. This link is shown on the pipeline view page in the CodePipeline console and provides a link to the execution entity of the external action.
            :param revision_url_template: The URL returned to the CodePipeline console that contains a link to the page where customers can update or change the configuration of the external action.
            :param third_party_configuration_url: The URL of a sign-up page where users can sign up for an external service and perform initial configuration of the action provided by that service.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                settings_property = codepipeline.CfnCustomActionType.SettingsProperty(
                    entity_url_template="entityUrlTemplate",
                    execution_url_template="executionUrlTemplate",
                    revision_url_template="revisionUrlTemplate",
                    third_party_configuration_url="thirdPartyConfigurationUrl"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b60390fcee5af2ad2918c79f29b14e48bd199ffda4949057f602bd61c857ac2e)
                check_type(argname="argument entity_url_template", value=entity_url_template, expected_type=type_hints["entity_url_template"])
                check_type(argname="argument execution_url_template", value=execution_url_template, expected_type=type_hints["execution_url_template"])
                check_type(argname="argument revision_url_template", value=revision_url_template, expected_type=type_hints["revision_url_template"])
                check_type(argname="argument third_party_configuration_url", value=third_party_configuration_url, expected_type=type_hints["third_party_configuration_url"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if entity_url_template is not None:
                self._values["entity_url_template"] = entity_url_template
            if execution_url_template is not None:
                self._values["execution_url_template"] = execution_url_template
            if revision_url_template is not None:
                self._values["revision_url_template"] = revision_url_template
            if third_party_configuration_url is not None:
                self._values["third_party_configuration_url"] = third_party_configuration_url

        @builtins.property
        def entity_url_template(self) -> typing.Optional[builtins.str]:
            '''The URL returned to the CodePipeline console that provides a deep link to the resources of the external system, such as the configuration page for a CodeDeploy deployment group.

            This link is provided as part of the action display in the pipeline.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-entityurltemplate
            '''
            result = self._values.get("entity_url_template")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def execution_url_template(self) -> typing.Optional[builtins.str]:
            '''The URL returned to the CodePipeline console that contains a link to the top-level landing page for the external system, such as the console page for CodeDeploy.

            This link is shown on the pipeline view page in the CodePipeline console and provides a link to the execution entity of the external action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-executionurltemplate
            '''
            result = self._values.get("execution_url_template")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def revision_url_template(self) -> typing.Optional[builtins.str]:
            '''The URL returned to the CodePipeline console that contains a link to the page where customers can update or change the configuration of the external action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-revisionurltemplate
            '''
            result = self._values.get("revision_url_template")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def third_party_configuration_url(self) -> typing.Optional[builtins.str]:
            '''The URL of a sign-up page where users can sign up for an external service and perform initial configuration of the action provided by that service.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-thirdpartyconfigurationurl
            '''
            result = self._values.get("third_party_configuration_url")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionTypeProps",
    jsii_struct_bases=[],
    name_mapping={
        "category": "category",
        "input_artifact_details": "inputArtifactDetails",
        "output_artifact_details": "outputArtifactDetails",
        "provider": "provider",
        "version": "version",
        "configuration_properties": "configurationProperties",
        "settings": "settings",
        "tags": "tags",
    },
)
class CfnCustomActionTypeProps:
    def __init__(
        self,
        *,
        category: builtins.str,
        input_artifact_details: typing.Union[typing.Union[CfnCustomActionType.ArtifactDetailsProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
        output_artifact_details: typing.Union[typing.Union[CfnCustomActionType.ArtifactDetailsProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
        provider: builtins.str,
        version: builtins.str,
        configuration_properties: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnCustomActionType.ConfigurationPropertiesProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        settings: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnCustomActionType.SettingsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnCustomActionType``.

        :param category: The category of the custom action, such as a build action or a test action.
        :param input_artifact_details: The details of the input artifact for the action, such as its commit ID.
        :param output_artifact_details: The details of the output artifact of the action, such as its commit ID.
        :param provider: The provider of the service used in the custom action, such as CodeDeploy.
        :param version: The version identifier of the custom action.
        :param configuration_properties: The configuration properties for the custom action. .. epigraph:: You can refer to a name in the configuration properties of the custom action within the URL templates by following the format of {Config:name}, as long as the configuration property is both required and not secret. For more information, see `Create a Custom Action for a Pipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-custom-action.html>`_ .
        :param settings: URLs that provide users information about this custom action.
        :param tags: The tags for the custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            cfn_custom_action_type_props = codepipeline.CfnCustomActionTypeProps(
                category="category",
                input_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                    maximum_count=123,
                    minimum_count=123
                ),
                output_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                    maximum_count=123,
                    minimum_count=123
                ),
                provider="provider",
                version="version",
            
                # the properties below are optional
                configuration_properties=[codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty(
                    key=False,
                    name="name",
                    required=False,
                    secret=False,
            
                    # the properties below are optional
                    description="description",
                    queryable=False,
                    type="type"
                )],
                settings=codepipeline.CfnCustomActionType.SettingsProperty(
                    entity_url_template="entityUrlTemplate",
                    execution_url_template="executionUrlTemplate",
                    revision_url_template="revisionUrlTemplate",
                    third_party_configuration_url="thirdPartyConfigurationUrl"
                ),
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__548578e0735fd41956f7f5be1cc6dd48a87943eb1cab1c1b7cb0ee04e0c21163)
            check_type(argname="argument category", value=category, expected_type=type_hints["category"])
            check_type(argname="argument input_artifact_details", value=input_artifact_details, expected_type=type_hints["input_artifact_details"])
            check_type(argname="argument output_artifact_details", value=output_artifact_details, expected_type=type_hints["output_artifact_details"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument configuration_properties", value=configuration_properties, expected_type=type_hints["configuration_properties"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "category": category,
            "input_artifact_details": input_artifact_details,
            "output_artifact_details": output_artifact_details,
            "provider": provider,
            "version": version,
        }
        if configuration_properties is not None:
            self._values["configuration_properties"] = configuration_properties
        if settings is not None:
            self._values["settings"] = settings
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def category(self) -> builtins.str:
        '''The category of the custom action, such as a build action or a test action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
        '''
        result = self._values.get("category")
        assert result is not None, "Required property 'category' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input_artifact_details(
        self,
    ) -> typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _aws_cdk_core_f4b25747.IResolvable]:
        '''The details of the input artifact for the action, such as its commit ID.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
        '''
        result = self._values.get("input_artifact_details")
        assert result is not None, "Required property 'input_artifact_details' is missing"
        return typing.cast(typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _aws_cdk_core_f4b25747.IResolvable], result)

    @builtins.property
    def output_artifact_details(
        self,
    ) -> typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _aws_cdk_core_f4b25747.IResolvable]:
        '''The details of the output artifact of the action, such as its commit ID.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
        '''
        result = self._values.get("output_artifact_details")
        assert result is not None, "Required property 'output_artifact_details' is missing"
        return typing.cast(typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _aws_cdk_core_f4b25747.IResolvable], result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''The provider of the service used in the custom action, such as CodeDeploy.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''The version identifier of the custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration_properties(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnCustomActionType.ConfigurationPropertiesProperty]]]]:
        '''The configuration properties for the custom action.

        .. epigraph::

           You can refer to a name in the configuration properties of the custom action within the URL templates by following the format of {Config:name}, as long as the configuration property is both required and not secret. For more information, see `Create a Custom Action for a Pipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-custom-action.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
        '''
        result = self._values.get("configuration_properties")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnCustomActionType.ConfigurationPropertiesProperty]]]], result)

    @builtins.property
    def settings(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnCustomActionType.SettingsProperty]]:
        '''URLs that provide users information about this custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
        '''
        result = self._values.get("settings")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnCustomActionType.SettingsProperty]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]]:
        '''The tags for the custom action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCustomActionTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnPipeline(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline",
):
    '''A CloudFormation ``AWS::CodePipeline::Pipeline``.

    The ``AWS::CodePipeline::Pipeline`` resource creates a CodePipeline pipeline that describes how software changes go through a release process. For more information, see `What Is CodePipeline? <https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html>`_ in the *AWS CodePipeline User Guide* .

    :cloudformationResource: AWS::CodePipeline::Pipeline
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codepipeline as codepipeline
        
        # configuration: Any
        
        cfn_pipeline = codepipeline.CfnPipeline(self, "MyCfnPipeline",
            role_arn="roleArn",
            stages=[codepipeline.CfnPipeline.StageDeclarationProperty(
                actions=[codepipeline.CfnPipeline.ActionDeclarationProperty(
                    action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                        category="category",
                        owner="owner",
                        provider="provider",
                        version="version"
                    ),
                    name="name",
        
                    # the properties below are optional
                    configuration=configuration,
                    input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                        name="name"
                    )],
                    namespace="namespace",
                    output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                        name="name"
                    )],
                    region="region",
                    role_arn="roleArn",
                    run_order=123
                )],
                name="name",
        
                # the properties below are optional
                blockers=[codepipeline.CfnPipeline.BlockerDeclarationProperty(
                    name="name",
                    type="type"
                )]
            )],
        
            # the properties below are optional
            artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                location="location",
                type="type",
        
                # the properties below are optional
                encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                    id="id",
                    type="type"
                )
            ),
            artifact_stores=[codepipeline.CfnPipeline.ArtifactStoreMapProperty(
                artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                    location="location",
                    type="type",
        
                    # the properties below are optional
                    encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                        id="id",
                        type="type"
                    )
                ),
                region="region"
            )],
            disable_inbound_stage_transitions=[codepipeline.CfnPipeline.StageTransitionProperty(
                reason="reason",
                stage_name="stageName"
            )],
            name="name",
            restart_execution_on_update=False,
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        role_arn: builtins.str,
        stages: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.StageDeclarationProperty", typing.Dict[builtins.str, typing.Any]]]]],
        artifact_store: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.ArtifactStoreProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        artifact_stores: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.ArtifactStoreMapProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        disable_inbound_stage_transitions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.StageTransitionProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::CodePipeline::Pipeline``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param role_arn: The Amazon Resource Name (ARN) for CodePipeline to use to either perform actions with no ``actionRoleArn`` , or to use to assume roles for actions with an ``actionRoleArn`` .
        :param stages: Represents information about a stage and its definition.
        :param artifact_store: The S3 bucket where artifacts for the pipeline are stored. .. epigraph:: You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .
        :param artifact_stores: A mapping of ``artifactStore`` objects and their corresponding AWS Regions. There must be an artifact store for the pipeline Region and for each cross-region action in the pipeline. .. epigraph:: You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .
        :param disable_inbound_stage_transitions: Represents the input of a ``DisableStageTransition`` action.
        :param name: The name of the pipeline.
        :param restart_execution_on_update: Indicates whether to rerun the CodePipeline pipeline after you update it.
        :param tags: Specifies the tags applied to the pipeline.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a90dbf085b8b42f0558df98c3942bd858deeeb90552c8a551b3b0bceac12e11)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnPipelineProps(
            role_arn=role_arn,
            stages=stages,
            artifact_store=artifact_store,
            artifact_stores=artifact_stores,
            disable_inbound_stage_transitions=disable_inbound_stage_transitions,
            name=name,
            restart_execution_on_update=restart_execution_on_update,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b67e712add9fd75144d32d50ba3653a6077dc093da68ff21675fc3777d663ca2)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__677855baaa5a899eb692a6eb70f5cce317e2c1e1d9c00ac922275ba9a5c58229)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrVersion")
    def attr_version(self) -> builtins.str:
        '''The version of the pipeline.

        .. epigraph::

           A new pipeline is always assigned a version number of 1. This number increments when a pipeline is updated.

        :cloudformationAttribute: Version
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrVersion"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''Specifies the tags applied to the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) for CodePipeline to use to either perform actions with no ``actionRoleArn`` , or to use to assume roles for actions with an ``actionRoleArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e7ed59bf70c8e4b92394ba62d5029dd2c03816a91f87777cca964dcbe49e95b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.StageDeclarationProperty"]]]:
        '''Represents information about a stage and its definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.StageDeclarationProperty"]]], jsii.get(self, "stages"))

    @stages.setter
    def stages(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.StageDeclarationProperty"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fcae7c0369d95f08bf8d31a33e277c30f238deb1652a631789cc35c043b47cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value)

    @builtins.property
    @jsii.member(jsii_name="artifactStore")
    def artifact_store(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreProperty"]]:
        '''The S3 bucket where artifacts for the pipeline are stored.

        .. epigraph::

           You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreProperty"]], jsii.get(self, "artifactStore"))

    @artifact_store.setter
    def artifact_store(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5be61728c138dba2c84426ae4bf816cd48816dd2ca8c5e076331481c8d6c7409)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactStore", value)

    @builtins.property
    @jsii.member(jsii_name="artifactStores")
    def artifact_stores(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreMapProperty"]]]]:
        '''A mapping of ``artifactStore`` objects and their corresponding AWS Regions.

        There must be an artifact store for the pipeline Region and for each cross-region action in the pipeline.
        .. epigraph::

           You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreMapProperty"]]]], jsii.get(self, "artifactStores"))

    @artifact_stores.setter
    def artifact_stores(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreMapProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b54aaeabf7470459a896f9114f2d21853371a712fa5fcf9b0bda9ba829e9214)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactStores", value)

    @builtins.property
    @jsii.member(jsii_name="disableInboundStageTransitions")
    def disable_inbound_stage_transitions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.StageTransitionProperty"]]]]:
        '''Represents the input of a ``DisableStageTransition`` action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.StageTransitionProperty"]]]], jsii.get(self, "disableInboundStageTransitions"))

    @disable_inbound_stage_transitions.setter
    def disable_inbound_stage_transitions(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.StageTransitionProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d30782e225fb6bb51bff4cc6515a7b7dca598ee7c748d111ed4660dfa4336618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableInboundStageTransitions", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7faa0e1c0f5c78ee074c0b51d023c79272c147e7fee07b2537f4b0842a0ff32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="restartExecutionOnUpdate")
    def restart_execution_on_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Indicates whether to rerun the CodePipeline pipeline after you update it.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "restartExecutionOnUpdate"))

    @restart_execution_on_update.setter
    def restart_execution_on_update(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbc0f73d640d69b4f0c1f085d44f64ce77ee064fe18227b524fbb8340e4a413d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartExecutionOnUpdate", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ActionDeclarationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "action_type_id": "actionTypeId",
            "name": "name",
            "configuration": "configuration",
            "input_artifacts": "inputArtifacts",
            "namespace": "namespace",
            "output_artifacts": "outputArtifacts",
            "region": "region",
            "role_arn": "roleArn",
            "run_order": "runOrder",
        },
    )
    class ActionDeclarationProperty:
        def __init__(
            self,
            *,
            action_type_id: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.ActionTypeIdProperty", typing.Dict[builtins.str, typing.Any]]],
            name: builtins.str,
            configuration: typing.Any = None,
            input_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.InputArtifactProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            namespace: typing.Optional[builtins.str] = None,
            output_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.OutputArtifactProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            region: typing.Optional[builtins.str] = None,
            role_arn: typing.Optional[builtins.str] = None,
            run_order: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Represents information about an action declaration.

            :param action_type_id: Specifies the action type and the provider of the action.
            :param name: The action declaration's name.
            :param configuration: The action's configuration. These are key-value pairs that specify input values for an action. For more information, see `Action Structure Requirements in CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements>`_ . For the list of configuration properties for the AWS CloudFormation action type in CodePipeline, see `Configuration Properties Reference <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-action-reference.html>`_ in the *AWS CloudFormation User Guide* . For template snippets with examples, see `Using Parameter Override Functions with CodePipeline Pipelines <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-parameter-override-functions.html>`_ in the *AWS CloudFormation User Guide* . The values can be represented in either JSON or YAML format. For example, the JSON configuration item format is as follows: *JSON:* ``"Configuration" : { Key : Value },``
            :param input_artifacts: The name or ID of the artifact consumed by the action, such as a test or build artifact. While the field is not a required parameter, most actions have an action configuration that requires a specified quantity of input artifacts. To refer to the action configuration specification by action provider, see the `Action structure reference <https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference.html>`_ in the *AWS CodePipeline User Guide* . .. epigraph:: For a CodeBuild action with multiple input artifacts, one of your input sources must be designated the PrimarySource. For more information, see the `CodeBuild action reference page <https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodeBuild.html>`_ in the *AWS CodePipeline User Guide* .
            :param namespace: The variable namespace associated with the action. All variables produced as output by this action fall under this namespace.
            :param output_artifacts: The name or ID of the result of the action declaration, such as a test or build artifact. While the field is not a required parameter, most actions have an action configuration that requires a specified quantity of output artifacts. To refer to the action configuration specification by action provider, see the `Action structure reference <https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference.html>`_ in the *AWS CodePipeline User Guide* .
            :param region: The action declaration's AWS Region, such as us-east-1.
            :param role_arn: The ARN of the IAM service role that performs the declared action. This is assumed through the roleArn for the pipeline.
            :param run_order: The order in which actions are run.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                # configuration: Any
                
                action_declaration_property = codepipeline.CfnPipeline.ActionDeclarationProperty(
                    action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                        category="category",
                        owner="owner",
                        provider="provider",
                        version="version"
                    ),
                    name="name",
                
                    # the properties below are optional
                    configuration=configuration,
                    input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                        name="name"
                    )],
                    namespace="namespace",
                    output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                        name="name"
                    )],
                    region="region",
                    role_arn="roleArn",
                    run_order=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b7794f1937a73d9b9e8be8b19671275bd670df968d81cb1a10979b429aa7d549)
                check_type(argname="argument action_type_id", value=action_type_id, expected_type=type_hints["action_type_id"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
                check_type(argname="argument input_artifacts", value=input_artifacts, expected_type=type_hints["input_artifacts"])
                check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
                check_type(argname="argument output_artifacts", value=output_artifacts, expected_type=type_hints["output_artifacts"])
                check_type(argname="argument region", value=region, expected_type=type_hints["region"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument run_order", value=run_order, expected_type=type_hints["run_order"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "action_type_id": action_type_id,
                "name": name,
            }
            if configuration is not None:
                self._values["configuration"] = configuration
            if input_artifacts is not None:
                self._values["input_artifacts"] = input_artifacts
            if namespace is not None:
                self._values["namespace"] = namespace
            if output_artifacts is not None:
                self._values["output_artifacts"] = output_artifacts
            if region is not None:
                self._values["region"] = region
            if role_arn is not None:
                self._values["role_arn"] = role_arn
            if run_order is not None:
                self._values["run_order"] = run_order

        @builtins.property
        def action_type_id(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ActionTypeIdProperty"]:
            '''Specifies the action type and the provider of the action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid
            '''
            result = self._values.get("action_type_id")
            assert result is not None, "Required property 'action_type_id' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ActionTypeIdProperty"], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''The action declaration's name.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def configuration(self) -> typing.Any:
            '''The action's configuration.

            These are key-value pairs that specify input values for an action. For more information, see `Action Structure Requirements in CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements>`_ . For the list of configuration properties for the AWS CloudFormation action type in CodePipeline, see `Configuration Properties Reference <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-action-reference.html>`_ in the *AWS CloudFormation User Guide* . For template snippets with examples, see `Using Parameter Override Functions with CodePipeline Pipelines <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-parameter-override-functions.html>`_ in the *AWS CloudFormation User Guide* .

            The values can be represented in either JSON or YAML format. For example, the JSON configuration item format is as follows:

            *JSON:*

            ``"Configuration" : { Key : Value },``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-configuration
            '''
            result = self._values.get("configuration")
            return typing.cast(typing.Any, result)

        @builtins.property
        def input_artifacts(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.InputArtifactProperty"]]]]:
            '''The name or ID of the artifact consumed by the action, such as a test or build artifact.

            While the field is not a required parameter, most actions have an action configuration that requires a specified quantity of input artifacts. To refer to the action configuration specification by action provider, see the `Action structure reference <https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference.html>`_ in the *AWS CodePipeline User Guide* .
            .. epigraph::

               For a CodeBuild action with multiple input artifacts, one of your input sources must be designated the PrimarySource. For more information, see the `CodeBuild action reference page <https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodeBuild.html>`_ in the *AWS CodePipeline User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts
            '''
            result = self._values.get("input_artifacts")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.InputArtifactProperty"]]]], result)

        @builtins.property
        def namespace(self) -> typing.Optional[builtins.str]:
            '''The variable namespace associated with the action.

            All variables produced as output by this action fall under this namespace.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-actiondeclaration-namespace
            '''
            result = self._values.get("namespace")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def output_artifacts(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.OutputArtifactProperty"]]]]:
            '''The name or ID of the result of the action declaration, such as a test or build artifact.

            While the field is not a required parameter, most actions have an action configuration that requires a specified quantity of output artifacts. To refer to the action configuration specification by action provider, see the `Action structure reference <https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference.html>`_ in the *AWS CodePipeline User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts
            '''
            result = self._values.get("output_artifacts")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.OutputArtifactProperty"]]]], result)

        @builtins.property
        def region(self) -> typing.Optional[builtins.str]:
            '''The action declaration's AWS Region, such as us-east-1.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-region
            '''
            result = self._values.get("region")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''The ARN of the IAM service role that performs the declared action.

            This is assumed through the roleArn for the pipeline.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def run_order(self) -> typing.Optional[jsii.Number]:
            '''The order in which actions are run.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-runorder
            '''
            result = self._values.get("run_order")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionDeclarationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ActionTypeIdProperty",
        jsii_struct_bases=[],
        name_mapping={
            "category": "category",
            "owner": "owner",
            "provider": "provider",
            "version": "version",
        },
    )
    class ActionTypeIdProperty:
        def __init__(
            self,
            *,
            category: builtins.str,
            owner: builtins.str,
            provider: builtins.str,
            version: builtins.str,
        ) -> None:
            '''Represents information about an action type.

            :param category: A category defines what kind of action can be taken in the stage, and constrains the provider type for the action. Valid categories are limited to one of the values below. - ``Source`` - ``Build`` - ``Test`` - ``Deploy`` - ``Invoke`` - ``Approval``
            :param owner: The creator of the action being called. There are three valid values for the ``Owner`` field in the action category section within your pipeline structure: ``AWS`` , ``ThirdParty`` , and ``Custom`` . For more information, see `Valid Action Types and Providers in CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#actions-valid-providers>`_ .
            :param provider: The provider of the service being called by the action. Valid providers are determined by the action category. For example, an action in the Deploy category type might have a provider of CodeDeploy, which would be specified as ``CodeDeploy`` . For more information, see `Valid Action Types and Providers in CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#actions-valid-providers>`_ .
            :param version: A string that describes the action version.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                action_type_id_property = codepipeline.CfnPipeline.ActionTypeIdProperty(
                    category="category",
                    owner="owner",
                    provider="provider",
                    version="version"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__3565bd42d3fa473f3aceed4033b614545cc5c6dc5d6a59c8c1a79336a5a0cf70)
                check_type(argname="argument category", value=category, expected_type=type_hints["category"])
                check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
                check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
                check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "category": category,
                "owner": owner,
                "provider": provider,
                "version": version,
            }

        @builtins.property
        def category(self) -> builtins.str:
            '''A category defines what kind of action can be taken in the stage, and constrains the provider type for the action.

            Valid categories are limited to one of the values below.

            - ``Source``
            - ``Build``
            - ``Test``
            - ``Deploy``
            - ``Invoke``
            - ``Approval``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-category
            '''
            result = self._values.get("category")
            assert result is not None, "Required property 'category' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner(self) -> builtins.str:
            '''The creator of the action being called.

            There are three valid values for the ``Owner`` field in the action category section within your pipeline structure: ``AWS`` , ``ThirdParty`` , and ``Custom`` . For more information, see `Valid Action Types and Providers in CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#actions-valid-providers>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-owner
            '''
            result = self._values.get("owner")
            assert result is not None, "Required property 'owner' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def provider(self) -> builtins.str:
            '''The provider of the service being called by the action.

            Valid providers are determined by the action category. For example, an action in the Deploy category type might have a provider of CodeDeploy, which would be specified as ``CodeDeploy`` . For more information, see `Valid Action Types and Providers in CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#actions-valid-providers>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-provider
            '''
            result = self._values.get("provider")
            assert result is not None, "Required property 'provider' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def version(self) -> builtins.str:
            '''A string that describes the action version.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-version
            '''
            result = self._values.get("version")
            assert result is not None, "Required property 'version' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionTypeIdProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ArtifactStoreMapProperty",
        jsii_struct_bases=[],
        name_mapping={"artifact_store": "artifactStore", "region": "region"},
    )
    class ArtifactStoreMapProperty:
        def __init__(
            self,
            *,
            artifact_store: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.ArtifactStoreProperty", typing.Dict[builtins.str, typing.Any]]],
            region: builtins.str,
        ) -> None:
            '''A mapping of ``artifactStore`` objects and their corresponding AWS Regions.

            There must be an artifact store for the pipeline Region and for each cross-region action in the pipeline.
            .. epigraph::

               You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

            :param artifact_store: Represents information about the S3 bucket where artifacts are stored for the pipeline. .. epigraph:: You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .
            :param region: The action declaration's AWS Region, such as us-east-1.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                artifact_store_map_property = codepipeline.CfnPipeline.ArtifactStoreMapProperty(
                    artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                        location="location",
                        type="type",
                
                        # the properties below are optional
                        encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                            id="id",
                            type="type"
                        )
                    ),
                    region="region"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a61d6272b695134faa6b72e0fc22d6aa31285ee6be658d0a787181fa02b3686a)
                check_type(argname="argument artifact_store", value=artifact_store, expected_type=type_hints["artifact_store"])
                check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "artifact_store": artifact_store,
                "region": region,
            }

        @builtins.property
        def artifact_store(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreProperty"]:
            '''Represents information about the S3 bucket where artifacts are stored for the pipeline.

            .. epigraph::

               You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-artifactstore
            '''
            result = self._values.get("artifact_store")
            assert result is not None, "Required property 'artifact_store' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ArtifactStoreProperty"], result)

        @builtins.property
        def region(self) -> builtins.str:
            '''The action declaration's AWS Region, such as us-east-1.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-region
            '''
            result = self._values.get("region")
            assert result is not None, "Required property 'region' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactStoreMapProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ArtifactStoreProperty",
        jsii_struct_bases=[],
        name_mapping={
            "location": "location",
            "type": "type",
            "encryption_key": "encryptionKey",
        },
    )
    class ArtifactStoreProperty:
        def __init__(
            self,
            *,
            location: builtins.str,
            type: builtins.str,
            encryption_key: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.EncryptionKeyProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''The S3 bucket where artifacts for the pipeline are stored.

            .. epigraph::

               You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

            :param location: The S3 bucket used for storing the artifacts for a pipeline. You can specify the name of an S3 bucket but not a folder in the bucket. A folder to contain the pipeline artifacts is created for you based on the name of the pipeline. You can use any S3 bucket in the same AWS Region as the pipeline to store your pipeline artifacts.
            :param type: The type of the artifact store, such as S3.
            :param encryption_key: The encryption key used to encrypt the data in the artifact store, such as an AWS Key Management Service ( AWS KMS) key. If this is undefined, the default key for Amazon S3 is used. To see an example artifact store encryption key field, see the example structure here: `AWS::CodePipeline::Pipeline <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                artifact_store_property = codepipeline.CfnPipeline.ArtifactStoreProperty(
                    location="location",
                    type="type",
                
                    # the properties below are optional
                    encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                        id="id",
                        type="type"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f393d37f4eeb1331c24bccf5966c23d8b07f6c507108791d5b3dbaf5b19a4e95)
                check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "location": location,
                "type": type,
            }
            if encryption_key is not None:
                self._values["encryption_key"] = encryption_key

        @builtins.property
        def location(self) -> builtins.str:
            '''The S3 bucket used for storing the artifacts for a pipeline.

            You can specify the name of an S3 bucket but not a folder in the bucket. A folder to contain the pipeline artifacts is created for you based on the name of the pipeline. You can use any S3 bucket in the same AWS Region as the pipeline to store your pipeline artifacts.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-location
            '''
            result = self._values.get("location")
            assert result is not None, "Required property 'location' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of the artifact store, such as S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def encryption_key(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.EncryptionKeyProperty"]]:
            '''The encryption key used to encrypt the data in the artifact store, such as an AWS Key Management Service ( AWS KMS) key.

            If this is undefined, the default key for Amazon S3 is used. To see an example artifact store encryption key field, see the example structure here: `AWS::CodePipeline::Pipeline <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey
            '''
            result = self._values.get("encryption_key")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.EncryptionKeyProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactStoreProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.BlockerDeclarationProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "type": "type"},
    )
    class BlockerDeclarationProperty:
        def __init__(self, *, name: builtins.str, type: builtins.str) -> None:
            '''Reserved for future use.

            :param name: Reserved for future use.
            :param type: Reserved for future use.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                blocker_declaration_property = codepipeline.CfnPipeline.BlockerDeclarationProperty(
                    name="name",
                    type="type"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b5c957574ae9f77327d277442bc9e9188ce33307604990cae118a2734ac6b9ac)
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "name": name,
                "type": type,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''Reserved for future use.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''Reserved for future use.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BlockerDeclarationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.EncryptionKeyProperty",
        jsii_struct_bases=[],
        name_mapping={"id": "id", "type": "type"},
    )
    class EncryptionKeyProperty:
        def __init__(self, *, id: builtins.str, type: builtins.str) -> None:
            '''Represents information about the key used to encrypt data in the artifact store, such as an AWS Key Management Service ( AWS KMS) key.

            ``EncryptionKey`` is a property of the `ArtifactStore <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html>`_ property type.

            :param id: The ID used to identify the key. For an AWS KMS key, you can use the key ID, the key ARN, or the alias ARN. .. epigraph:: Aliases are recognized only in the account that created the AWS KMS key. For cross-account actions, you can only use the key ID or key ARN to identify the key. Cross-account actions involve using the role from the other account (AccountB), so specifying the key ID will use the key from the other account (AccountB).
            :param type: The type of encryption key, such as an AWS KMS key. When creating or updating a pipeline, the value must be set to 'KMS'.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                encryption_key_property = codepipeline.CfnPipeline.EncryptionKeyProperty(
                    id="id",
                    type="type"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7a2cabd8548be0ffd77669f6b7f70733418a5f82aec7c37d13b81e715430966b)
                check_type(argname="argument id", value=id, expected_type=type_hints["id"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "id": id,
                "type": type,
            }

        @builtins.property
        def id(self) -> builtins.str:
            '''The ID used to identify the key.

            For an AWS KMS key, you can use the key ID, the key ARN, or the alias ARN.
            .. epigraph::

               Aliases are recognized only in the account that created the AWS KMS key. For cross-account actions, you can only use the key ID or key ARN to identify the key. Cross-account actions involve using the role from the other account (AccountB), so specifying the key ID will use the key from the other account (AccountB).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of encryption key, such as an AWS KMS key.

            When creating or updating a pipeline, the value must be set to 'KMS'.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionKeyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.InputArtifactProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name"},
    )
    class InputArtifactProperty:
        def __init__(self, *, name: builtins.str) -> None:
            '''Represents information about an artifact to be worked on, such as a test or build artifact.

            :param name: The name of the artifact to be worked on (for example, "My App"). Artifacts are the files that are worked on by actions in the pipeline. See the action configuration for each action for details about artifact parameters. For example, the S3 source action input artifact is a file name (or file path), and the files are generally provided as a ZIP file. Example artifact name: SampleApp_Windows.zip The input artifact of an action must exactly match the output artifact declared in a preceding action, but the input artifact does not have to be the next action in strict sequence from the action that provided the output artifact. Actions in parallel can declare different output artifacts, which are in turn consumed by different following actions.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                input_artifact_property = codepipeline.CfnPipeline.InputArtifactProperty(
                    name="name"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__4b1253085d1a223d5e047c0225c56d87a1c9335b09aa0ffa8d0b0bd2932b6ec5)
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "name": name,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''The name of the artifact to be worked on (for example, "My App").

            Artifacts are the files that are worked on by actions in the pipeline. See the action configuration for each action for details about artifact parameters. For example, the S3 source action input artifact is a file name (or file path), and the files are generally provided as a ZIP file. Example artifact name: SampleApp_Windows.zip

            The input artifact of an action must exactly match the output artifact declared in a preceding action, but the input artifact does not have to be the next action in strict sequence from the action that provided the output artifact. Actions in parallel can declare different output artifacts, which are in turn consumed by different following actions.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InputArtifactProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.OutputArtifactProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name"},
    )
    class OutputArtifactProperty:
        def __init__(self, *, name: builtins.str) -> None:
            '''Represents information about the output of an action.

            :param name: The name of the output of an artifact, such as "My App". The output artifact name must exactly match the input artifact declared for a downstream action. However, the downstream action's input artifact does not have to be the next action in strict sequence from the action that provided the output artifact. Actions in parallel can declare different output artifacts, which are in turn consumed by different following actions. Output artifact names must be unique within a pipeline.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                output_artifact_property = codepipeline.CfnPipeline.OutputArtifactProperty(
                    name="name"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__41aab9838a6fa3b04cc14585296b7aa276af8b5667ddec30a8e5784ff7da2e82)
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "name": name,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''The name of the output of an artifact, such as "My App".

            The output artifact name must exactly match the input artifact declared for a downstream action. However, the downstream action's input artifact does not have to be the next action in strict sequence from the action that provided the output artifact. Actions in parallel can declare different output artifacts, which are in turn consumed by different following actions.

            Output artifact names must be unique within a pipeline.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OutputArtifactProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.StageDeclarationProperty",
        jsii_struct_bases=[],
        name_mapping={"actions": "actions", "name": "name", "blockers": "blockers"},
    )
    class StageDeclarationProperty:
        def __init__(
            self,
            *,
            actions: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.ActionDeclarationProperty", typing.Dict[builtins.str, typing.Any]]]]],
            name: builtins.str,
            blockers: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnPipeline.BlockerDeclarationProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        ) -> None:
            '''Represents information about a stage and its definition.

            :param actions: The actions included in a stage.
            :param name: The name of the stage.
            :param blockers: Reserved for future use.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                # configuration: Any
                
                stage_declaration_property = codepipeline.CfnPipeline.StageDeclarationProperty(
                    actions=[codepipeline.CfnPipeline.ActionDeclarationProperty(
                        action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                            category="category",
                            owner="owner",
                            provider="provider",
                            version="version"
                        ),
                        name="name",
                
                        # the properties below are optional
                        configuration=configuration,
                        input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                            name="name"
                        )],
                        namespace="namespace",
                        output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                            name="name"
                        )],
                        region="region",
                        role_arn="roleArn",
                        run_order=123
                    )],
                    name="name",
                
                    # the properties below are optional
                    blockers=[codepipeline.CfnPipeline.BlockerDeclarationProperty(
                        name="name",
                        type="type"
                    )]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__30b3c4be72debca476d94038d3fb862cae82deb520b0ad68085a04aa7be9c46d)
                check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument blockers", value=blockers, expected_type=type_hints["blockers"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "actions": actions,
                "name": name,
            }
            if blockers is not None:
                self._values["blockers"] = blockers

        @builtins.property
        def actions(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ActionDeclarationProperty"]]]:
            '''The actions included in a stage.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-actions
            '''
            result = self._values.get("actions")
            assert result is not None, "Required property 'actions' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.ActionDeclarationProperty"]]], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''The name of the stage.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def blockers(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.BlockerDeclarationProperty"]]]]:
            '''Reserved for future use.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-blockers
            '''
            result = self._values.get("blockers")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnPipeline.BlockerDeclarationProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StageDeclarationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.StageTransitionProperty",
        jsii_struct_bases=[],
        name_mapping={"reason": "reason", "stage_name": "stageName"},
    )
    class StageTransitionProperty:
        def __init__(self, *, reason: builtins.str, stage_name: builtins.str) -> None:
            '''The name of the pipeline in which you want to disable the flow of artifacts from one stage to another.

            :param reason: The reason given to the user that a stage is disabled, such as waiting for manual approval or manual tests. This message is displayed in the pipeline console UI.
            :param stage_name: The name of the stage where you want to disable the inbound or outbound transition of artifacts.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                stage_transition_property = codepipeline.CfnPipeline.StageTransitionProperty(
                    reason="reason",
                    stage_name="stageName"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__9178a81eab86bfb46f1e96e57fb136b413d087f699093e3835a4ed28ddb85993)
                check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
                check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "reason": reason,
                "stage_name": stage_name,
            }

        @builtins.property
        def reason(self) -> builtins.str:
            '''The reason given to the user that a stage is disabled, such as waiting for manual approval or manual tests.

            This message is displayed in the pipeline console UI.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-reason
            '''
            result = self._values.get("reason")
            assert result is not None, "Required property 'reason' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def stage_name(self) -> builtins.str:
            '''The name of the stage where you want to disable the inbound or outbound transition of artifacts.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-stagename
            '''
            result = self._values.get("stage_name")
            assert result is not None, "Required property 'stage_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StageTransitionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CfnPipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "stages": "stages",
        "artifact_store": "artifactStore",
        "artifact_stores": "artifactStores",
        "disable_inbound_stage_transitions": "disableInboundStageTransitions",
        "name": "name",
        "restart_execution_on_update": "restartExecutionOnUpdate",
        "tags": "tags",
    },
)
class CfnPipelineProps:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        stages: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.StageDeclarationProperty, typing.Dict[builtins.str, typing.Any]]]]],
        artifact_store: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        artifact_stores: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreMapProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        disable_inbound_stage_transitions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.StageTransitionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnPipeline``.

        :param role_arn: The Amazon Resource Name (ARN) for CodePipeline to use to either perform actions with no ``actionRoleArn`` , or to use to assume roles for actions with an ``actionRoleArn`` .
        :param stages: Represents information about a stage and its definition.
        :param artifact_store: The S3 bucket where artifacts for the pipeline are stored. .. epigraph:: You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .
        :param artifact_stores: A mapping of ``artifactStore`` objects and their corresponding AWS Regions. There must be an artifact store for the pipeline Region and for each cross-region action in the pipeline. .. epigraph:: You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .
        :param disable_inbound_stage_transitions: Represents the input of a ``DisableStageTransition`` action.
        :param name: The name of the pipeline.
        :param restart_execution_on_update: Indicates whether to rerun the CodePipeline pipeline after you update it.
        :param tags: Specifies the tags applied to the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            # configuration: Any
            
            cfn_pipeline_props = codepipeline.CfnPipelineProps(
                role_arn="roleArn",
                stages=[codepipeline.CfnPipeline.StageDeclarationProperty(
                    actions=[codepipeline.CfnPipeline.ActionDeclarationProperty(
                        action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                            category="category",
                            owner="owner",
                            provider="provider",
                            version="version"
                        ),
                        name="name",
            
                        # the properties below are optional
                        configuration=configuration,
                        input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                            name="name"
                        )],
                        namespace="namespace",
                        output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                            name="name"
                        )],
                        region="region",
                        role_arn="roleArn",
                        run_order=123
                    )],
                    name="name",
            
                    # the properties below are optional
                    blockers=[codepipeline.CfnPipeline.BlockerDeclarationProperty(
                        name="name",
                        type="type"
                    )]
                )],
            
                # the properties below are optional
                artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                    location="location",
                    type="type",
            
                    # the properties below are optional
                    encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                        id="id",
                        type="type"
                    )
                ),
                artifact_stores=[codepipeline.CfnPipeline.ArtifactStoreMapProperty(
                    artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                        location="location",
                        type="type",
            
                        # the properties below are optional
                        encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                            id="id",
                            type="type"
                        )
                    ),
                    region="region"
                )],
                disable_inbound_stage_transitions=[codepipeline.CfnPipeline.StageTransitionProperty(
                    reason="reason",
                    stage_name="stageName"
                )],
                name="name",
                restart_execution_on_update=False,
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__399f399dd104b18405c6a406bc4582445dd4401bb75f9f7443c2ef988e2b4616)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stages", value=stages, expected_type=type_hints["stages"])
            check_type(argname="argument artifact_store", value=artifact_store, expected_type=type_hints["artifact_store"])
            check_type(argname="argument artifact_stores", value=artifact_stores, expected_type=type_hints["artifact_stores"])
            check_type(argname="argument disable_inbound_stage_transitions", value=disable_inbound_stage_transitions, expected_type=type_hints["disable_inbound_stage_transitions"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument restart_execution_on_update", value=restart_execution_on_update, expected_type=type_hints["restart_execution_on_update"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_arn": role_arn,
            "stages": stages,
        }
        if artifact_store is not None:
            self._values["artifact_store"] = artifact_store
        if artifact_stores is not None:
            self._values["artifact_stores"] = artifact_stores
        if disable_inbound_stage_transitions is not None:
            self._values["disable_inbound_stage_transitions"] = disable_inbound_stage_transitions
        if name is not None:
            self._values["name"] = name
        if restart_execution_on_update is not None:
            self._values["restart_execution_on_update"] = restart_execution_on_update
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) for CodePipeline to use to either perform actions with no ``actionRoleArn`` , or to use to assume roles for actions with an ``actionRoleArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stages(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.StageDeclarationProperty]]]:
        '''Represents information about a stage and its definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
        '''
        result = self._values.get("stages")
        assert result is not None, "Required property 'stages' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.StageDeclarationProperty]]], result)

    @builtins.property
    def artifact_store(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.ArtifactStoreProperty]]:
        '''The S3 bucket where artifacts for the pipeline are stored.

        .. epigraph::

           You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
        '''
        result = self._values.get("artifact_store")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.ArtifactStoreProperty]], result)

    @builtins.property
    def artifact_stores(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.ArtifactStoreMapProperty]]]]:
        '''A mapping of ``artifactStore`` objects and their corresponding AWS Regions.

        There must be an artifact store for the pipeline Region and for each cross-region action in the pipeline.
        .. epigraph::

           You must include either ``artifactStore`` or ``artifactStores`` in your pipeline, but you cannot use both. If you create a cross-region action in your pipeline, you must use ``artifactStores`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
        '''
        result = self._values.get("artifact_stores")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.ArtifactStoreMapProperty]]]], result)

    @builtins.property
    def disable_inbound_stage_transitions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.StageTransitionProperty]]]]:
        '''Represents the input of a ``DisableStageTransition`` action.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
        '''
        result = self._values.get("disable_inbound_stage_transitions")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.StageTransitionProperty]]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restart_execution_on_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Indicates whether to rerun the CodePipeline pipeline after you update it.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
        '''
        result = self._values.get("restart_execution_on_update")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]]:
        '''Specifies the tags applied to the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnWebhook(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook",
):
    '''A CloudFormation ``AWS::CodePipeline::Webhook``.

    The ``AWS::CodePipeline::Webhook`` resource creates and registers your webhook. After the webhook is created and registered, it triggers your pipeline to start every time an external event occurs. For more information, see `Migrate polling pipelines to use event-based change detection <https://docs.aws.amazon.com/codepipeline/latest/userguide/update-change-detection.html>`_ in the *AWS CodePipeline User Guide* .

    We strongly recommend that you use AWS Secrets Manager to store your credentials. If you use Secrets Manager, you must have already configured and stored your secret parameters in Secrets Manager. For more information, see `Using Dynamic References to Specify Template Values <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-secretsmanager>`_ .
    .. epigraph::

       When passing secret parameters, do not enter the value directly into the template. The value is rendered as plaintext and is therefore readable. For security reasons, do not use plaintext in your AWS CloudFormation template to store your credentials.

    :cloudformationResource: AWS::CodePipeline::Webhook
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codepipeline as codepipeline
        
        cfn_webhook = codepipeline.CfnWebhook(self, "MyCfnWebhook",
            authentication="authentication",
            authentication_configuration=codepipeline.CfnWebhook.WebhookAuthConfigurationProperty(
                allowed_ip_range="allowedIpRange",
                secret_token="secretToken"
            ),
            filters=[codepipeline.CfnWebhook.WebhookFilterRuleProperty(
                json_path="jsonPath",
        
                # the properties below are optional
                match_equals="matchEquals"
            )],
            target_action="targetAction",
            target_pipeline="targetPipeline",
            target_pipeline_version=123,
        
            # the properties below are optional
            name="name",
            register_with_third_party=False
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        authentication: builtins.str,
        authentication_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnWebhook.WebhookAuthConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
        filters: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnWebhook.WebhookFilterRuleProperty", typing.Dict[builtins.str, typing.Any]]]]],
        target_action: builtins.str,
        target_pipeline: builtins.str,
        target_pipeline_version: jsii.Number,
        name: typing.Optional[builtins.str] = None,
        register_with_third_party: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    ) -> None:
        '''Create a new ``AWS::CodePipeline::Webhook``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authentication: Supported options are GITHUB_HMAC, IP, and UNAUTHENTICATED. - For information about the authentication scheme implemented by GITHUB_HMAC, see `Securing your webhooks <https://docs.aws.amazon.com/https://developer.github.com/webhooks/securing/>`_ on the GitHub Developer website. - IP rejects webhooks trigger requests unless they originate from an IP address in the IP range whitelisted in the authentication configuration. - UNAUTHENTICATED accepts all webhook trigger requests regardless of origin.
        :param authentication_configuration: Properties that configure the authentication applied to incoming webhook trigger requests. The required properties depend on the authentication type. For GITHUB_HMAC, only the ``SecretToken`` property must be set. For IP, only the ``AllowedIPRange`` property must be set to a valid CIDR range. For UNAUTHENTICATED, no properties can be set.
        :param filters: A list of rules applied to the body/payload sent in the POST request to a webhook URL. All defined rules must pass for the request to be accepted and the pipeline started.
        :param target_action: The name of the action in a pipeline you want to connect to the webhook. The action must be from the source (first) stage of the pipeline.
        :param target_pipeline: The name of the pipeline you want to connect to the webhook.
        :param target_pipeline_version: The version number of the pipeline to be connected to the trigger request. Required: Yes Type: Integer Update requires: `No interruption <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt>`_
        :param name: The name of the webhook.
        :param register_with_third_party: Configures a connection between the webhook that was created and the external tool with events to be detected.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c8d9d5f4f9a49198aad5b142eaa884276e566098b502dce3967e5feb4f08b4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnWebhookProps(
            authentication=authentication,
            authentication_configuration=authentication_configuration,
            filters=filters,
            target_action=target_action,
            target_pipeline=target_pipeline,
            target_pipeline_version=target_pipeline_version,
            name=name,
            register_with_third_party=register_with_third_party,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adfbef8326040df1dbd08f423e63e33586552a9e175c72b9ae23e757028b85b1)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9125eef274c8839b695ab0bb898a622158fbbbaa622fa689d090d368703d9296)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrUrl")
    def attr_url(self) -> builtins.str:
        '''The webhook URL generated by AWS CodePipeline , such as ``https://eu-central-1.webhooks.aws/trigger123456`` .

        :cloudformationAttribute: Url
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrUrl"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> builtins.str:
        '''Supported options are GITHUB_HMAC, IP, and UNAUTHENTICATED.

        - For information about the authentication scheme implemented by GITHUB_HMAC, see `Securing your webhooks <https://docs.aws.amazon.com/https://developer.github.com/webhooks/securing/>`_ on the GitHub Developer website.
        - IP rejects webhooks trigger requests unless they originate from an IP address in the IP range whitelisted in the authentication configuration.
        - UNAUTHENTICATED accepts all webhook trigger requests regardless of origin.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
        '''
        return typing.cast(builtins.str, jsii.get(self, "authentication"))

    @authentication.setter
    def authentication(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d184be6798f66aedf8d276d1820b8232b0506376eed7b3bf668008e35494118)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authentication", value)

    @builtins.property
    @jsii.member(jsii_name="authenticationConfiguration")
    def authentication_configuration(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnWebhook.WebhookAuthConfigurationProperty"]:
        '''Properties that configure the authentication applied to incoming webhook trigger requests.

        The required properties depend on the authentication type. For GITHUB_HMAC, only the ``SecretToken`` property must be set. For IP, only the ``AllowedIPRange`` property must be set to a valid CIDR range. For UNAUTHENTICATED, no properties can be set.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnWebhook.WebhookAuthConfigurationProperty"], jsii.get(self, "authenticationConfiguration"))

    @authentication_configuration.setter
    def authentication_configuration(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnWebhook.WebhookAuthConfigurationProperty"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020c22776d77738198a58a11d9db16bbc79a0cc2054d3ed6dcd9deb56da4b36e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnWebhook.WebhookFilterRuleProperty"]]]:
        '''A list of rules applied to the body/payload sent in the POST request to a webhook URL.

        All defined rules must pass for the request to be accepted and the pipeline started.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnWebhook.WebhookFilterRuleProperty"]]], jsii.get(self, "filters"))

    @filters.setter
    def filters(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnWebhook.WebhookFilterRuleProperty"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59beb9cfa4c2bd7a6148d2a65f399ff5296c8ed2631244e3e7ddf3b5774b20ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filters", value)

    @builtins.property
    @jsii.member(jsii_name="targetAction")
    def target_action(self) -> builtins.str:
        '''The name of the action in a pipeline you want to connect to the webhook.

        The action must be from the source (first) stage of the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetAction"))

    @target_action.setter
    def target_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aa54d76ff17d2f580d3fe06f755f79870f7b66cb9af35e1d0b2d3f8b98fc97a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetAction", value)

    @builtins.property
    @jsii.member(jsii_name="targetPipeline")
    def target_pipeline(self) -> builtins.str:
        '''The name of the pipeline you want to connect to the webhook.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetPipeline"))

    @target_pipeline.setter
    def target_pipeline(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df31cb0950dcc7019fed9255ccfd416da54e68de3dab9e35e6821be8fdb65ec7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPipeline", value)

    @builtins.property
    @jsii.member(jsii_name="targetPipelineVersion")
    def target_pipeline_version(self) -> jsii.Number:
        '''The version number of the pipeline to be connected to the trigger request.

        Required: Yes

        Type: Integer

        Update requires: `No interruption <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt>`_

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
        '''
        return typing.cast(jsii.Number, jsii.get(self, "targetPipelineVersion"))

    @target_pipeline_version.setter
    def target_pipeline_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce0ccc4a2ccdc6d2ac4927888611da9fd8961815fc04a3bb7b5b23c53d09cdee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPipelineVersion", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the webhook.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e292a530fa7830506bbd9e980a007d747aa8a4bede6f8db2168e800ae367deb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="registerWithThirdParty")
    def register_with_third_party(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Configures a connection between the webhook that was created and the external tool with events to be detected.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "registerWithThirdParty"))

    @register_with_third_party.setter
    def register_with_third_party(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf9c9cefcf08d621e7ea50857911947e623004f927044dac20193452b87f9c48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "registerWithThirdParty", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook.WebhookAuthConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "allowed_ip_range": "allowedIpRange",
            "secret_token": "secretToken",
        },
    )
    class WebhookAuthConfigurationProperty:
        def __init__(
            self,
            *,
            allowed_ip_range: typing.Optional[builtins.str] = None,
            secret_token: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The authentication applied to incoming webhook trigger requests.

            :param allowed_ip_range: The property used to configure acceptance of webhooks in an IP address range. For IP, only the ``AllowedIPRange`` property must be set. This property must be set to a valid CIDR range.
            :param secret_token: The property used to configure GitHub authentication. For GITHUB_HMAC, only the ``SecretToken`` property must be set.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                webhook_auth_configuration_property = codepipeline.CfnWebhook.WebhookAuthConfigurationProperty(
                    allowed_ip_range="allowedIpRange",
                    secret_token="secretToken"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__58c2d6b94792e1f423293abe56c1c5bafe39c94c0480cb739ff7d8780e3518be)
                check_type(argname="argument allowed_ip_range", value=allowed_ip_range, expected_type=type_hints["allowed_ip_range"])
                check_type(argname="argument secret_token", value=secret_token, expected_type=type_hints["secret_token"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if allowed_ip_range is not None:
                self._values["allowed_ip_range"] = allowed_ip_range
            if secret_token is not None:
                self._values["secret_token"] = secret_token

        @builtins.property
        def allowed_ip_range(self) -> typing.Optional[builtins.str]:
            '''The property used to configure acceptance of webhooks in an IP address range.

            For IP, only the ``AllowedIPRange`` property must be set. This property must be set to a valid CIDR range.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-allowediprange
            '''
            result = self._values.get("allowed_ip_range")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secret_token(self) -> typing.Optional[builtins.str]:
            '''The property used to configure GitHub authentication.

            For GITHUB_HMAC, only the ``SecretToken`` property must be set.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-secrettoken
            '''
            result = self._values.get("secret_token")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WebhookAuthConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook.WebhookFilterRuleProperty",
        jsii_struct_bases=[],
        name_mapping={"json_path": "jsonPath", "match_equals": "matchEquals"},
    )
    class WebhookFilterRuleProperty:
        def __init__(
            self,
            *,
            json_path: builtins.str,
            match_equals: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The event criteria that specify when a webhook notification is sent to your URL.

            :param json_path: A JsonPath expression that is applied to the body/payload of the webhook. The value selected by the JsonPath expression must match the value specified in the ``MatchEquals`` field. Otherwise, the request is ignored. For more information, see `Java JsonPath implementation <https://docs.aws.amazon.com/https://github.com/json-path/JsonPath>`_ in GitHub.
            :param match_equals: The value selected by the ``JsonPath`` expression must match what is supplied in the ``MatchEquals`` field. Otherwise, the request is ignored. Properties from the target action configuration can be included as placeholders in this value by surrounding the action configuration key with curly brackets. For example, if the value supplied here is "refs/heads/{Branch}" and the target action has an action configuration property called "Branch" with a value of "main", the ``MatchEquals`` value is evaluated as "refs/heads/main". For a list of action configuration properties for built-in action types, see `Pipeline Structure Reference Action Requirements <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codepipeline as codepipeline
                
                webhook_filter_rule_property = codepipeline.CfnWebhook.WebhookFilterRuleProperty(
                    json_path="jsonPath",
                
                    # the properties below are optional
                    match_equals="matchEquals"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__22280a9993953e867a13984d2d51e6b2316ab7254d3baa896964cb85b5f6a31f)
                check_type(argname="argument json_path", value=json_path, expected_type=type_hints["json_path"])
                check_type(argname="argument match_equals", value=match_equals, expected_type=type_hints["match_equals"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "json_path": json_path,
            }
            if match_equals is not None:
                self._values["match_equals"] = match_equals

        @builtins.property
        def json_path(self) -> builtins.str:
            '''A JsonPath expression that is applied to the body/payload of the webhook.

            The value selected by the JsonPath expression must match the value specified in the ``MatchEquals`` field. Otherwise, the request is ignored. For more information, see `Java JsonPath implementation <https://docs.aws.amazon.com/https://github.com/json-path/JsonPath>`_ in GitHub.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-jsonpath
            '''
            result = self._values.get("json_path")
            assert result is not None, "Required property 'json_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def match_equals(self) -> typing.Optional[builtins.str]:
            '''The value selected by the ``JsonPath`` expression must match what is supplied in the ``MatchEquals`` field.

            Otherwise, the request is ignored. Properties from the target action configuration can be included as placeholders in this value by surrounding the action configuration key with curly brackets. For example, if the value supplied here is "refs/heads/{Branch}" and the target action has an action configuration property called "Branch" with a value of "main", the ``MatchEquals`` value is evaluated as "refs/heads/main". For a list of action configuration properties for built-in action types, see `Pipeline Structure Reference Action Requirements <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-matchequals
            '''
            result = self._values.get("match_equals")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WebhookFilterRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CfnWebhookProps",
    jsii_struct_bases=[],
    name_mapping={
        "authentication": "authentication",
        "authentication_configuration": "authenticationConfiguration",
        "filters": "filters",
        "target_action": "targetAction",
        "target_pipeline": "targetPipeline",
        "target_pipeline_version": "targetPipelineVersion",
        "name": "name",
        "register_with_third_party": "registerWithThirdParty",
    },
)
class CfnWebhookProps:
    def __init__(
        self,
        *,
        authentication: builtins.str,
        authentication_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnWebhook.WebhookAuthConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
        filters: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnWebhook.WebhookFilterRuleProperty, typing.Dict[builtins.str, typing.Any]]]]],
        target_action: builtins.str,
        target_pipeline: builtins.str,
        target_pipeline_version: jsii.Number,
        name: typing.Optional[builtins.str] = None,
        register_with_third_party: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    ) -> None:
        '''Properties for defining a ``CfnWebhook``.

        :param authentication: Supported options are GITHUB_HMAC, IP, and UNAUTHENTICATED. - For information about the authentication scheme implemented by GITHUB_HMAC, see `Securing your webhooks <https://docs.aws.amazon.com/https://developer.github.com/webhooks/securing/>`_ on the GitHub Developer website. - IP rejects webhooks trigger requests unless they originate from an IP address in the IP range whitelisted in the authentication configuration. - UNAUTHENTICATED accepts all webhook trigger requests regardless of origin.
        :param authentication_configuration: Properties that configure the authentication applied to incoming webhook trigger requests. The required properties depend on the authentication type. For GITHUB_HMAC, only the ``SecretToken`` property must be set. For IP, only the ``AllowedIPRange`` property must be set to a valid CIDR range. For UNAUTHENTICATED, no properties can be set.
        :param filters: A list of rules applied to the body/payload sent in the POST request to a webhook URL. All defined rules must pass for the request to be accepted and the pipeline started.
        :param target_action: The name of the action in a pipeline you want to connect to the webhook. The action must be from the source (first) stage of the pipeline.
        :param target_pipeline: The name of the pipeline you want to connect to the webhook.
        :param target_pipeline_version: The version number of the pipeline to be connected to the trigger request. Required: Yes Type: Integer Update requires: `No interruption <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt>`_
        :param name: The name of the webhook.
        :param register_with_third_party: Configures a connection between the webhook that was created and the external tool with events to be detected.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            cfn_webhook_props = codepipeline.CfnWebhookProps(
                authentication="authentication",
                authentication_configuration=codepipeline.CfnWebhook.WebhookAuthConfigurationProperty(
                    allowed_ip_range="allowedIpRange",
                    secret_token="secretToken"
                ),
                filters=[codepipeline.CfnWebhook.WebhookFilterRuleProperty(
                    json_path="jsonPath",
            
                    # the properties below are optional
                    match_equals="matchEquals"
                )],
                target_action="targetAction",
                target_pipeline="targetPipeline",
                target_pipeline_version=123,
            
                # the properties below are optional
                name="name",
                register_with_third_party=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4c528c1252da1be3d0ef8e263c9dbd4eaef33fb8879f8d5301ced25603b00eb)
            check_type(argname="argument authentication", value=authentication, expected_type=type_hints["authentication"])
            check_type(argname="argument authentication_configuration", value=authentication_configuration, expected_type=type_hints["authentication_configuration"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument target_action", value=target_action, expected_type=type_hints["target_action"])
            check_type(argname="argument target_pipeline", value=target_pipeline, expected_type=type_hints["target_pipeline"])
            check_type(argname="argument target_pipeline_version", value=target_pipeline_version, expected_type=type_hints["target_pipeline_version"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument register_with_third_party", value=register_with_third_party, expected_type=type_hints["register_with_third_party"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authentication": authentication,
            "authentication_configuration": authentication_configuration,
            "filters": filters,
            "target_action": target_action,
            "target_pipeline": target_pipeline,
            "target_pipeline_version": target_pipeline_version,
        }
        if name is not None:
            self._values["name"] = name
        if register_with_third_party is not None:
            self._values["register_with_third_party"] = register_with_third_party

    @builtins.property
    def authentication(self) -> builtins.str:
        '''Supported options are GITHUB_HMAC, IP, and UNAUTHENTICATED.

        - For information about the authentication scheme implemented by GITHUB_HMAC, see `Securing your webhooks <https://docs.aws.amazon.com/https://developer.github.com/webhooks/securing/>`_ on the GitHub Developer website.
        - IP rejects webhooks trigger requests unless they originate from an IP address in the IP range whitelisted in the authentication configuration.
        - UNAUTHENTICATED accepts all webhook trigger requests regardless of origin.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
        '''
        result = self._values.get("authentication")
        assert result is not None, "Required property 'authentication' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_configuration(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnWebhook.WebhookAuthConfigurationProperty]:
        '''Properties that configure the authentication applied to incoming webhook trigger requests.

        The required properties depend on the authentication type. For GITHUB_HMAC, only the ``SecretToken`` property must be set. For IP, only the ``AllowedIPRange`` property must be set to a valid CIDR range. For UNAUTHENTICATED, no properties can be set.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
        '''
        result = self._values.get("authentication_configuration")
        assert result is not None, "Required property 'authentication_configuration' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnWebhook.WebhookAuthConfigurationProperty], result)

    @builtins.property
    def filters(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnWebhook.WebhookFilterRuleProperty]]]:
        '''A list of rules applied to the body/payload sent in the POST request to a webhook URL.

        All defined rules must pass for the request to be accepted and the pipeline started.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
        '''
        result = self._values.get("filters")
        assert result is not None, "Required property 'filters' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnWebhook.WebhookFilterRuleProperty]]], result)

    @builtins.property
    def target_action(self) -> builtins.str:
        '''The name of the action in a pipeline you want to connect to the webhook.

        The action must be from the source (first) stage of the pipeline.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
        '''
        result = self._values.get("target_action")
        assert result is not None, "Required property 'target_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_pipeline(self) -> builtins.str:
        '''The name of the pipeline you want to connect to the webhook.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
        '''
        result = self._values.get("target_pipeline")
        assert result is not None, "Required property 'target_pipeline' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_pipeline_version(self) -> jsii.Number:
        '''The version number of the pipeline to be connected to the trigger request.

        Required: Yes

        Type: Integer

        Update requires: `No interruption <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt>`_

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
        '''
        result = self._values.get("target_pipeline_version")
        assert result is not None, "Required property 'target_pipeline_version' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the webhook.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def register_with_third_party(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Configures a connection between the webhook that was created and the external tool with events to be detected.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
        '''
        result = self._values.get("register_with_third_party")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnWebhookProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CommonActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
    },
)
class CommonActionProps:
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Common properties shared by all Actions.

        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            common_action_props = codepipeline.CommonActionProps(
                action_name="actionName",
            
                # the properties below are optional
                run_order=123,
                variables_namespace="variablesNamespace"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b982e6d6312c65f867c30c3d33be03ebdbbee534bb9f0b5163701d37c2dc2d7)
            check_type(argname="argument action_name", value=action_name, expected_type=type_hints["action_name"])
            check_type(argname="argument run_order", value=run_order, expected_type=type_hints["run_order"])
            check_type(argname="argument variables_namespace", value=variables_namespace, expected_type=type_hints["variables_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action_name": action_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CommonAwsActionProps",
    jsii_struct_bases=[CommonActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
    },
)
class CommonAwsActionProps(CommonActionProps):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    ) -> None:
        '''Common properties shared by all Actions whose {@link ActionProperties.owner} field is 'AWS' (or unset, as 'AWS' is the default).

        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            import aws_cdk.aws_iam as iam
            
            # role: iam.Role
            
            common_aws_action_props = codepipeline.CommonAwsActionProps(
                action_name="actionName",
            
                # the properties below are optional
                role=role,
                run_order=123,
                variables_namespace="variablesNamespace"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef056dde856e997c38b4d3a061132f8263bb2e8152145d6546afb3729a3035d2)
            check_type(argname="argument action_name", value=action_name, expected_type=type_hints["action_name"])
            check_type(argname="argument run_order", value=run_order, expected_type=type_hints["run_order"])
            check_type(argname="argument variables_namespace", value=variables_namespace, expected_type=type_hints["variables_namespace"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action_name": action_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonAwsActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CrossRegionSupport",
    jsii_struct_bases=[],
    name_mapping={"replication_bucket": "replicationBucket", "stack": "stack"},
)
class CrossRegionSupport:
    def __init__(
        self,
        *,
        replication_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        stack: _aws_cdk_core_f4b25747.Stack,
    ) -> None:
        '''An interface representing resources generated in order to support the cross-region capabilities of CodePipeline.

        You get instances of this interface from the {@link Pipeline#crossRegionSupport} property.

        :param replication_bucket: The replication Bucket used by CodePipeline to operate in this region. Belongs to {@link stack}.
        :param stack: The Stack that has been created to house the replication Bucket required for this region.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            import aws_cdk.aws_s3 as s3
            import aws_cdk.core as cdk
            
            # bucket: s3.Bucket
            # stack: cdk.Stack
            
            cross_region_support = codepipeline.CrossRegionSupport(
                replication_bucket=bucket,
                stack=stack
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45cbcc0f891a61e380a3f6eaa19f8c25e9892bcdea80438911b4aaad5c60611b)
            check_type(argname="argument replication_bucket", value=replication_bucket, expected_type=type_hints["replication_bucket"])
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "replication_bucket": replication_bucket,
            "stack": stack,
        }

    @builtins.property
    def replication_bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''The replication Bucket used by CodePipeline to operate in this region.

        Belongs to {@link stack}.
        '''
        result = self._values.get("replication_bucket")
        assert result is not None, "Required property 'replication_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def stack(self) -> _aws_cdk_core_f4b25747.Stack:
        '''The Stack that has been created to house the replication Bucket required for this  region.'''
        result = self._values.get("stack")
        assert result is not None, "Required property 'stack' is missing"
        return typing.cast(_aws_cdk_core_f4b25747.Stack, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossRegionSupport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CustomActionProperty",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "required": "required",
        "description": "description",
        "key": "key",
        "queryable": "queryable",
        "secret": "secret",
        "type": "type",
    },
)
class CustomActionProperty:
    def __init__(
        self,
        *,
        name: builtins.str,
        required: builtins.bool,
        description: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.bool] = None,
        queryable: typing.Optional[builtins.bool] = None,
        secret: typing.Optional[builtins.bool] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The creation attributes used for defining a configuration property of a custom Action.

        :param name: The name of the property. You use this name in the ``configuration`` attribute when defining your custom Action class.
        :param required: Whether this property is required.
        :param description: The description of the property. Default: the description will be empty
        :param key: Whether this property is a key. Default: false
        :param queryable: Whether this property is queryable. Note that only a single property of a custom Action can be queryable. Default: false
        :param secret: Whether this property is secret, like a password, or access key. Default: false
        :param type: The type of the property, like 'String', 'Number', or 'Boolean'. Default: 'String'

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            custom_action_property = codepipeline.CustomActionProperty(
                name="name",
                required=False,
            
                # the properties below are optional
                description="description",
                key=False,
                queryable=False,
                secret=False,
                type="type"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb0cb51d4ed66bc56ba70dafe8657d9fa1e2f0698d21d8d37e6a870db44653a5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument queryable", value=queryable, expected_type=type_hints["queryable"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "required": required,
        }
        if description is not None:
            self._values["description"] = description
        if key is not None:
            self._values["key"] = key
        if queryable is not None:
            self._values["queryable"] = queryable
        if secret is not None:
            self._values["secret"] = secret
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the property.

        You use this name in the ``configuration`` attribute when defining your custom Action class.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def required(self) -> builtins.bool:
        '''Whether this property is required.'''
        result = self._values.get("required")
        assert result is not None, "Required property 'required' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the property.

        :default: the description will be empty
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.bool]:
        '''Whether this property is a key.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-key
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def queryable(self) -> typing.Optional[builtins.bool]:
        '''Whether this property is queryable.

        Note that only a single property of a custom Action can be queryable.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-queryable
        '''
        result = self._values.get("queryable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.bool]:
        '''Whether this property is secret, like a password, or access key.

        :default: false
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of the property, like 'String', 'Number', or 'Boolean'.

        :default: 'String'
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomActionProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomActionRegistration(
    _aws_cdk_core_f4b25747.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.CustomActionRegistration",
):
    '''The resource representing registering a custom Action with CodePipeline.

    For the Action to be usable, it has to be registered for every region and every account it's used in.
    In addition to this class, you should most likely also provide your clients a class
    representing your custom Action, extending the Action class,
    and taking the ``actionProperties`` as properly typed, construction properties.

    :exampleMetadata: infused

    Example::

        # Make a custom CodePipeline Action
        codepipeline.CustomActionRegistration(self, "GenericGitSourceProviderResource",
            category=codepipeline.ActionCategory.SOURCE,
            artifact_bounds=codepipeline.ActionArtifactBounds(min_inputs=0, max_inputs=0, min_outputs=1, max_outputs=1),
            provider="GenericGitSource",
            version="1",
            entity_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
            execution_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
            action_properties=[codepipeline.CustomActionProperty(
                name="Branch",
                required=True,
                key=False,
                secret=False,
                queryable=False,
                description="Git branch to pull",
                type="String"
            ), codepipeline.CustomActionProperty(
                name="GitUrl",
                required=True,
                key=False,
                secret=False,
                queryable=False,
                description="SSH git clone URL",
                type="String"
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        artifact_bounds: typing.Union[ActionArtifactBounds, typing.Dict[builtins.str, typing.Any]],
        category: ActionCategory,
        provider: builtins.str,
        action_properties: typing.Optional[typing.Sequence[typing.Union[CustomActionProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        entity_url: typing.Optional[builtins.str] = None,
        execution_url: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param artifact_bounds: The artifact bounds of the Action.
        :param category: The category of the Action.
        :param provider: The provider of the Action. For example, ``'MyCustomActionProvider'``
        :param action_properties: The properties used for customizing the instance of your Action. Default: []
        :param entity_url: The URL shown for the entire Action in the Pipeline UI. Default: none
        :param execution_url: The URL shown for a particular execution of an Action in the Pipeline UI. Default: none
        :param version: The version of your Action. Default: '1'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__606777d998a7c0a503c51d4ed0e4616008f88170600debdead23a1e955371434)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CustomActionRegistrationProps(
            artifact_bounds=artifact_bounds,
            category=category,
            provider=provider,
            action_properties=action_properties,
            entity_url=entity_url,
            execution_url=execution_url,
            version=version,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.CustomActionRegistrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_bounds": "artifactBounds",
        "category": "category",
        "provider": "provider",
        "action_properties": "actionProperties",
        "entity_url": "entityUrl",
        "execution_url": "executionUrl",
        "version": "version",
    },
)
class CustomActionRegistrationProps:
    def __init__(
        self,
        *,
        artifact_bounds: typing.Union[ActionArtifactBounds, typing.Dict[builtins.str, typing.Any]],
        category: ActionCategory,
        provider: builtins.str,
        action_properties: typing.Optional[typing.Sequence[typing.Union[CustomActionProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        entity_url: typing.Optional[builtins.str] = None,
        execution_url: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties of registering a custom Action.

        :param artifact_bounds: The artifact bounds of the Action.
        :param category: The category of the Action.
        :param provider: The provider of the Action. For example, ``'MyCustomActionProvider'``
        :param action_properties: The properties used for customizing the instance of your Action. Default: []
        :param entity_url: The URL shown for the entire Action in the Pipeline UI. Default: none
        :param execution_url: The URL shown for a particular execution of an Action in the Pipeline UI. Default: none
        :param version: The version of your Action. Default: '1'

        :exampleMetadata: infused

        Example::

            # Make a custom CodePipeline Action
            codepipeline.CustomActionRegistration(self, "GenericGitSourceProviderResource",
                category=codepipeline.ActionCategory.SOURCE,
                artifact_bounds=codepipeline.ActionArtifactBounds(min_inputs=0, max_inputs=0, min_outputs=1, max_outputs=1),
                provider="GenericGitSource",
                version="1",
                entity_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
                execution_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
                action_properties=[codepipeline.CustomActionProperty(
                    name="Branch",
                    required=True,
                    key=False,
                    secret=False,
                    queryable=False,
                    description="Git branch to pull",
                    type="String"
                ), codepipeline.CustomActionProperty(
                    name="GitUrl",
                    required=True,
                    key=False,
                    secret=False,
                    queryable=False,
                    description="SSH git clone URL",
                    type="String"
                )
                ]
            )
        '''
        if isinstance(artifact_bounds, dict):
            artifact_bounds = ActionArtifactBounds(**artifact_bounds)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e144db048884d7cdd29246cbfada59cbaff708570d4e450ab672f1c3273387ce)
            check_type(argname="argument artifact_bounds", value=artifact_bounds, expected_type=type_hints["artifact_bounds"])
            check_type(argname="argument category", value=category, expected_type=type_hints["category"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument action_properties", value=action_properties, expected_type=type_hints["action_properties"])
            check_type(argname="argument entity_url", value=entity_url, expected_type=type_hints["entity_url"])
            check_type(argname="argument execution_url", value=execution_url, expected_type=type_hints["execution_url"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "artifact_bounds": artifact_bounds,
            "category": category,
            "provider": provider,
        }
        if action_properties is not None:
            self._values["action_properties"] = action_properties
        if entity_url is not None:
            self._values["entity_url"] = entity_url
        if execution_url is not None:
            self._values["execution_url"] = execution_url
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def artifact_bounds(self) -> ActionArtifactBounds:
        '''The artifact bounds of the Action.'''
        result = self._values.get("artifact_bounds")
        assert result is not None, "Required property 'artifact_bounds' is missing"
        return typing.cast(ActionArtifactBounds, result)

    @builtins.property
    def category(self) -> ActionCategory:
        '''The category of the Action.'''
        result = self._values.get("category")
        assert result is not None, "Required property 'category' is missing"
        return typing.cast(ActionCategory, result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''The provider of the Action.

        For example, ``'MyCustomActionProvider'``
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_properties(self) -> typing.Optional[typing.List[CustomActionProperty]]:
        '''The properties used for customizing the instance of your Action.

        :default: []
        '''
        result = self._values.get("action_properties")
        return typing.cast(typing.Optional[typing.List[CustomActionProperty]], result)

    @builtins.property
    def entity_url(self) -> typing.Optional[builtins.str]:
        '''The URL shown for the entire Action in the Pipeline UI.

        :default: none
        '''
        result = self._values.get("entity_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_url(self) -> typing.Optional[builtins.str]:
        '''The URL shown for a particular execution of an Action in the Pipeline UI.

        :default: none
        '''
        result = self._values.get("execution_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''The version of your Action.

        :default: '1'
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomActionRegistrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GlobalVariables(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.GlobalVariables",
):
    '''The CodePipeline variables that are global, not bound to a specific action.

    This class defines a bunch of static fields that represent the different variables.
    These can be used can be used in any action configuration.

    :exampleMetadata: fixture=action infused

    Example::

        # OtherAction is some action type that produces variables, like EcrSourceAction
        OtherAction(
            # ...
            config=codepipeline.GlobalVariables.execution_id,
            action_name="otherAction"
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="executionId")
    def EXECUTION_ID(cls) -> builtins.str:
        '''The identifier of the current pipeline execution.'''
        return typing.cast(builtins.str, jsii.sget(cls, "executionId"))


@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IAction")
class IAction(typing_extensions.Protocol):
    '''A Pipeline Action.

    If you want to implement this interface,
    consider extending the {@link Action} class,
    which contains some common logic.
    '''

    @builtins.property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> ActionProperties:
        '''The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.
        '''
        ...

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        stage: "IStage",
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> ActionConfig:
        '''The callback invoked when this Action is added to a Pipeline.

        :param scope: the Construct tree scope the Action can use if it needs to create any resources.
        :param stage: the {@link IStage} this Action is being added to.
        :param bucket: 
        :param role: 
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: the name to use for the new Event.
        :param target: the optional target for the Event.
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        ...


class _IActionProxy:
    '''A Pipeline Action.

    If you want to implement this interface,
    consider extending the {@link Action} class,
    which contains some common logic.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codepipeline.IAction"

    @builtins.property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> ActionProperties:
        '''The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.
        '''
        return typing.cast(ActionProperties, jsii.get(self, "actionProperties"))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        stage: "IStage",
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> ActionConfig:
        '''The callback invoked when this Action is added to a Pipeline.

        :param scope: the Construct tree scope the Action can use if it needs to create any resources.
        :param stage: the {@link IStage} this Action is being added to.
        :param bucket: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f087503a953ba2edbe5d7793bf17f96389a1bae9d4262b1f01e81dc775b31016)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        options = ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bind", [scope, stage, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: the name to use for the new Event.
        :param target: the optional target for the Event.
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4206f0ca4f896a913ee158e3f47f39ef60969140c494d4a737613d1768d1c46)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_events_efcdfa54.RuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [name, target, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAction).__jsii_proxy_class__ = lambda : _IActionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IPipeline")
class IPipeline(
    _aws_cdk_core_f4b25747.IResource,
    _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleSource,
    typing_extensions.Protocol,
):
    '''The abstract view of an AWS CodePipeline as required and used by Actions.

    It extends {@link events.IRuleTarget},
    so this interface can be used as a Target for CloudWatch Events.
    '''

    @builtins.property
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> builtins.str:
        '''The ARN of the Pipeline.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        '''The name of the Pipeline.

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["PipelineNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule triggered when the pipeline events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnExecutionStateChange``, ``notifyOnAnyStageStateChange``,
        ``notifyOnAnyActionStateChange`` and ``notifyOnAnyManualApprovalStateChange``
        to define rules for these specific event emitted.

        :param id: The id of the CodeStar notification rule.
        :param target: The target to register for the CodeStar Notifications destination.
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar notification rule associated with this build project.
        '''
        ...

    @jsii.member(jsii_name="notifyOnAnyActionStateChange")
    def notify_on_any_action_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Action execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="notifyOnAnyManualApprovalStateChange")
    def notify_on_any_manual_approval_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Manual approval" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="notifyOnAnyStageStateChange")
    def notify_on_any_stage_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Stage execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="notifyOnExecutionStateChange")
    def notify_on_execution_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Pipeline execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Define an event rule triggered by this CodePipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...


class _IPipelineProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleSource), # type: ignore[misc]
):
    '''The abstract view of an AWS CodePipeline as required and used by Actions.

    It extends {@link events.IRuleTarget},
    so this interface can be used as a Target for CloudWatch Events.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codepipeline.IPipeline"

    @builtins.property
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> builtins.str:
        '''The ARN of the Pipeline.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "pipelineArn"))

    @builtins.property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        '''The name of the Pipeline.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "pipelineName"))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["PipelineNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule triggered when the pipeline events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnExecutionStateChange``, ``notifyOnAnyStageStateChange``,
        ``notifyOnAnyActionStateChange`` and ``notifyOnAnyManualApprovalStateChange``
        to define rules for these specific event emitted.

        :param id: The id of the CodeStar notification rule.
        :param target: The target to register for the CodeStar Notifications destination.
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar notification rule associated with this build project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cf0c15116528a686f8c394f5c1545d39abc257be231189ee16551554a38481f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = PipelineNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyActionStateChange")
    def notify_on_any_action_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Action execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30dfe2e460caf15e7696a215cf589f57f80d864c1fb35fd5907148ce10911c2b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnAnyActionStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyManualApprovalStateChange")
    def notify_on_any_manual_approval_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Manual approval" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d5ace427a05f66fb5e1542bf5df15a967fa85df90e475dc9cdb8e873bd8db9)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnAnyManualApprovalStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyStageStateChange")
    def notify_on_any_stage_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Stage execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3106bdd30fa222d7b604f1ad650b6c3486e4323ed5418735ad62f5da41d537e0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnAnyStageStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnExecutionStateChange")
    def notify_on_execution_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Pipeline execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8026e92418b84e699517cdeb2938d952a6fc7db5c810ff3ac7ccaf6f3a0c9e4f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnExecutionStateChange", [id, target, options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Define an event rule triggered by this CodePipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e73dcfe5b09723a66441ad9c124ca0e7f197fa3baf0c51dbacf65f66406a0277)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abbe125ab463a0af83eb11fdcf4d887432390adb33c4a82db40b7990adcfc1a4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPipeline).__jsii_proxy_class__ = lambda : _IPipelineProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IStage")
class IStage(typing_extensions.Protocol):
    '''The abstract interface of a Pipeline Stage that is used by Actions.'''

    @builtins.property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[IAction]:
        '''The actions belonging to this stage.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> IPipeline:
        ...

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name of this Pipeline Stage.'''
        ...

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: IAction) -> None:
        '''
        :param action: -
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''
        :param name: -
        :param target: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        ...


class _IStageProxy:
    '''The abstract interface of a Pipeline Stage that is used by Actions.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codepipeline.IStage"

    @builtins.property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[IAction]:
        '''The actions belonging to this stage.'''
        return typing.cast(typing.List[IAction], jsii.get(self, "actions"))

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> IPipeline:
        return typing.cast(IPipeline, jsii.get(self, "pipeline"))

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name of this Pipeline Stage.'''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: IAction) -> None:
        '''
        :param action: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e74956085e7dc6b78603b31a0bcf3077efadbf7834ed283e27100c5acbeaac60)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
        return typing.cast(None, jsii.invoke(self, "addAction", [action]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''
        :param name: -
        :param target: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2cc4448fa5add30227d8058bdd32a268335e37f00d63d3ab55e324cda09b6f)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_events_efcdfa54.RuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [name, target, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStage).__jsii_proxy_class__ = lambda : _IStageProxy


@jsii.implements(IPipeline)
class Pipeline(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codepipeline.Pipeline",
):
    '''An AWS CodePipeline pipeline with its associated IAM role and S3 bucket.

    Example::

        # create a pipeline
        import aws_cdk.aws_codecommit as codecommit
        
        # add a source action to the stage
        # repo: codecommit.Repository
        # source_artifact: codepipeline.Artifact
        
        
        pipeline = codepipeline.Pipeline(self, "Pipeline")
        
        # add a stage
        source_stage = pipeline.add_stage(stage_name="Source")
        source_stage.add_action(codepipeline_actions.CodeCommitSourceAction(
            action_name="Source",
            output=source_artifact,
            repository=repo
        ))
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        artifact_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
        cross_account_keys: typing.Optional[builtins.bool] = None,
        cross_region_replication_buckets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_s3_55f001a5.IBucket]] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[builtins.bool] = None,
        reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        stages: typing.Optional[typing.Sequence[typing.Union["StageProps", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param artifact_bucket: The S3 bucket used by this Pipeline to store artifacts. Default: - A new S3 bucket will be created.
        :param cross_account_keys: Create KMS keys for cross-account deployments. This controls whether the pipeline is enabled for cross-account deployments. By default cross-account deployments are enabled, but this feature requires that KMS Customer Master Keys are created which have a cost of $1/month. If you do not need cross-account deployments, you can set this to ``false`` to not create those keys and save on that cost (the artifact bucket will be encrypted with an AWS-managed key). However, cross-account deployments will no longer be possible. Default: true
        :param cross_region_replication_buckets: A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a Stack containing an S3 Bucket in that region. Default: - None.
        :param enable_key_rotation: Enable KMS key rotation for the generated KMS keys. By default KMS key rotation is disabled, but will add an additional $1/month for each year the key exists when enabled. Default: - false (key rotation is disabled)
        :param pipeline_name: Name of the pipeline. Default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
        :param restart_execution_on_update: Indicates whether to rerun the AWS CodePipeline pipeline after you update it. Default: false
        :param reuse_cross_region_support_stacks: Reuse the same cross region support stack for all pipelines in the App. Default: - true (Use the same support stack for all pipelines in App)
        :param role: The IAM role to be assumed by this Pipeline. Default: a new IAM role will be created.
        :param stages: The list of Stages, in order, to create this Pipeline with. You can always add more Stages later by calling {@link Pipeline#addStage}. Default: - None.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f90b55f94a38352f916e0ab2a635da01beb113c2d8c149f21913828fd638773)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PipelineProps(
            artifact_bucket=artifact_bucket,
            cross_account_keys=cross_account_keys,
            cross_region_replication_buckets=cross_region_replication_buckets,
            enable_key_rotation=enable_key_rotation,
            pipeline_name=pipeline_name,
            restart_execution_on_update=restart_execution_on_update,
            reuse_cross_region_support_stacks=reuse_cross_region_support_stacks,
            role=role,
            stages=stages,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPipelineArn")
    @builtins.classmethod
    def from_pipeline_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        pipeline_arn: builtins.str,
    ) -> IPipeline:
        '''Import a pipeline into this app.

        :param scope: the scope into which to import this pipeline.
        :param id: the logical ID of the returned pipeline construct.
        :param pipeline_arn: The ARN of the pipeline (e.g. ``arn:aws:codepipeline:us-east-1:123456789012:MyDemoPipeline``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dee678410112d4f0f7990206ef3fd094e87a5e500ff5fb6ae80f0d93d6716ff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument pipeline_arn", value=pipeline_arn, expected_type=type_hints["pipeline_arn"])
        return typing.cast(IPipeline, jsii.sinvoke(cls, "fromPipelineArn", [scope, id, pipeline_arn]))

    @jsii.member(jsii_name="addStage")
    def add_stage(
        self,
        *,
        placement: typing.Optional[typing.Union["StagePlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        stage_name: builtins.str,
        actions: typing.Optional[typing.Sequence[IAction]] = None,
        transition_disabled_reason: typing.Optional[builtins.str] = None,
        transition_to_enabled: typing.Optional[builtins.bool] = None,
    ) -> IStage:
        '''Creates a new Stage, and adds it to this Pipeline.

        :param placement: 
        :param stage_name: The physical, human-readable name to assign to this Pipeline Stage.
        :param actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.
        :param transition_disabled_reason: The reason for disabling transition to this stage. Only applicable if ``transitionToEnabled`` is set to ``false``. Default: 'Transition disabled'
        :param transition_to_enabled: Whether to enable transition to this stage. Default: true

        :return: the newly created Stage
        '''
        props = StageOptions(
            placement=placement,
            stage_name=stage_name,
            actions=actions,
            transition_disabled_reason=transition_disabled_reason,
            transition_to_enabled=transition_to_enabled,
        )

        return typing.cast(IStage, jsii.invoke(self, "addStage", [props]))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
    ) -> None:
        '''Adds a statement to the pipeline role.

        :param statement: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcaf8ecf43e6c5be3722df6436b10b7b0350c3af3003e70362fd7fd5f9fe0214)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="bindAsNotificationRuleSource")
    def bind_as_notification_rule_source(
        self,
        _scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleSourceConfig:
        '''Returns a source configuration for notification rule.

        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60549b383bfd8f30c2555fe131ba32635ca7a19029f9587c7159f460bb22d76f)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleSourceConfig, jsii.invoke(self, "bindAsNotificationRuleSource", [_scope]))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["PipelineNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule triggered when the pipeline events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnExecutionStateChange``, ``notifyOnAnyStageStateChange``,
        ``notifyOnAnyActionStateChange`` and ``notifyOnAnyManualApprovalStateChange``
        to define rules for these specific event emitted.

        :param id: -
        :param target: -
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2701c843193d3ccc38731da37f5f25a885d1d0361587123e78f0f16ebee252)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = PipelineNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyActionStateChange")
    def notify_on_any_action_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Action execution" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63ac0ea05fd9a43a550eeca5f2a120f8909383315b1101d43cdb252b1302375d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnAnyActionStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyManualApprovalStateChange")
    def notify_on_any_manual_approval_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Manual approval" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14fc8598de0989a0a651e25a7223c8c8c10d57906be5e7da6f06b23444796afd)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnAnyManualApprovalStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyStageStateChange")
    def notify_on_any_stage_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Stage execution" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6acd9654be76a948bb0181c03367a720720edc87ca52e26d7571f22de47eec)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnAnyStageStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnExecutionStateChange")
    def notify_on_execution_state_change(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Define an notification rule triggered by the set of the "Pipeline execution" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a57f66d4cae51a72b8f4db6b4d8be092649e2ddcdb294390f801b9a182239f8c)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnExecutionStateChange", [id, target, options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule triggered by this CodePipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9fc488565bf936d319df3c65cd1792484ef2a172f6fb6cd3471cf9ecf9a4692)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed6bb219c997f3cc8e98fb086e022e15e99414d0b9939261db36c9b13df7d195)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [id, options]))

    @jsii.member(jsii_name="stage")
    def stage(self, stage_name: builtins.str) -> IStage:
        '''Access one of the pipeline's stages by stage name.

        :param stage_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2921a12b733ca52dd9bc0fe7b5cf641bce9de8cf749d2f7f815acfda0959e108)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        return typing.cast(IStage, jsii.invoke(self, "stage", [stage_name]))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''Validate the pipeline structure.

        Validation happens according to the rules documented at

        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#pipeline-requirements

        :override: true
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property
    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''Bucket used to store output artifacts.'''
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, jsii.get(self, "artifactBucket"))

    @builtins.property
    @jsii.member(jsii_name="crossRegionSupport")
    def cross_region_support(self) -> typing.Mapping[builtins.str, CrossRegionSupport]:
        '''Returns all of the {@link CrossRegionSupportStack}s that were generated automatically when dealing with Actions that reside in a different region than the Pipeline itself.'''
        return typing.cast(typing.Mapping[builtins.str, CrossRegionSupport], jsii.get(self, "crossRegionSupport"))

    @builtins.property
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> builtins.str:
        '''ARN of this pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "pipelineArn"))

    @builtins.property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        '''The name of the pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "pipelineName"))

    @builtins.property
    @jsii.member(jsii_name="pipelineVersion")
    def pipeline_version(self) -> builtins.str:
        '''The version of the pipeline.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "pipelineVersion"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_940a1ce0.IRole:
        '''The IAM role AWS CodePipeline will use to perform actions or assume roles for actions with a more specific IAM role.'''
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="stageCount")
    def stage_count(self) -> jsii.Number:
        '''Get the number of Stages in this Pipeline.'''
        return typing.cast(jsii.Number, jsii.get(self, "stageCount"))

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IStage]:
        '''Returns the stages that comprise the pipeline.

        **Note**: the returned array is a defensive copy,
        so adding elements to it has no effect.
        Instead, use the {@link addStage} method if you want to add more stages
        to the pipeline.
        '''
        return typing.cast(typing.List[IStage], jsii.get(self, "stages"))


@jsii.enum(jsii_type="@aws-cdk/aws-codepipeline.PipelineNotificationEvents")
class PipelineNotificationEvents(enum.Enum):
    '''The list of event types for AWS Codepipeline Pipeline.

    :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
    '''

    PIPELINE_EXECUTION_FAILED = "PIPELINE_EXECUTION_FAILED"
    '''Trigger notification when pipeline execution failed.'''
    PIPELINE_EXECUTION_CANCELED = "PIPELINE_EXECUTION_CANCELED"
    '''Trigger notification when pipeline execution canceled.'''
    PIPELINE_EXECUTION_STARTED = "PIPELINE_EXECUTION_STARTED"
    '''Trigger notification when pipeline execution started.'''
    PIPELINE_EXECUTION_RESUMED = "PIPELINE_EXECUTION_RESUMED"
    '''Trigger notification when pipeline execution resumed.'''
    PIPELINE_EXECUTION_SUCCEEDED = "PIPELINE_EXECUTION_SUCCEEDED"
    '''Trigger notification when pipeline execution succeeded.'''
    PIPELINE_EXECUTION_SUPERSEDED = "PIPELINE_EXECUTION_SUPERSEDED"
    '''Trigger notification when pipeline execution superseded.'''
    STAGE_EXECUTION_STARTED = "STAGE_EXECUTION_STARTED"
    '''Trigger notification when pipeline stage execution started.'''
    STAGE_EXECUTION_SUCCEEDED = "STAGE_EXECUTION_SUCCEEDED"
    '''Trigger notification when pipeline stage execution succeeded.'''
    STAGE_EXECUTION_RESUMED = "STAGE_EXECUTION_RESUMED"
    '''Trigger notification when pipeline stage execution resumed.'''
    STAGE_EXECUTION_CANCELED = "STAGE_EXECUTION_CANCELED"
    '''Trigger notification when pipeline stage execution canceled.'''
    STAGE_EXECUTION_FAILED = "STAGE_EXECUTION_FAILED"
    '''Trigger notification when pipeline stage execution failed.'''
    ACTION_EXECUTION_SUCCEEDED = "ACTION_EXECUTION_SUCCEEDED"
    '''Trigger notification when pipeline action execution succeeded.'''
    ACTION_EXECUTION_FAILED = "ACTION_EXECUTION_FAILED"
    '''Trigger notification when pipeline action execution failed.'''
    ACTION_EXECUTION_CANCELED = "ACTION_EXECUTION_CANCELED"
    '''Trigger notification when pipeline action execution canceled.'''
    ACTION_EXECUTION_STARTED = "ACTION_EXECUTION_STARTED"
    '''Trigger notification when pipeline action execution started.'''
    MANUAL_APPROVAL_FAILED = "MANUAL_APPROVAL_FAILED"
    '''Trigger notification when pipeline manual approval failed.'''
    MANUAL_APPROVAL_NEEDED = "MANUAL_APPROVAL_NEEDED"
    '''Trigger notification when pipeline manual approval needed.'''
    MANUAL_APPROVAL_SUCCEEDED = "MANUAL_APPROVAL_SUCCEEDED"
    '''Trigger notification when pipeline manual approval succeeded.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.PipelineNotifyOnOptions",
    jsii_struct_bases=[
        _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions
    ],
    name_mapping={
        "detail_type": "detailType",
        "enabled": "enabled",
        "notification_rule_name": "notificationRuleName",
        "events": "events",
    },
)
class PipelineNotifyOnOptions(
    _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions,
):
    def __init__(
        self,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
        events: typing.Sequence[PipelineNotificationEvents],
    ) -> None:
        '''Additional options to pass to the notification rule.

        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            pipeline_notify_on_options = codepipeline.PipelineNotifyOnOptions(
                events=[codepipeline.PipelineNotificationEvents.PIPELINE_EXECUTION_FAILED],
            
                # the properties below are optional
                detail_type=codestarnotifications.DetailType.BASIC,
                enabled=False,
                notification_rule_name="notificationRuleName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__751b9eb85a9c1708b1614ec32def63e8fbe0e589e469d802a6fce06945750f1f)
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument notification_rule_name", value=notification_rule_name, expected_type=type_hints["notification_rule_name"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "events": events,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if enabled is not None:
            self._values["enabled"] = enabled
        if notification_rule_name is not None:
            self._values["notification_rule_name"] = notification_rule_name

    @builtins.property
    def detail_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event as it would appear in AWS CloudWatch.
        FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :default: DetailType.FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''The status of the notification rule.

        If the enabled is set to DISABLED, notifications aren't sent for the notification rule.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notification_rule_name(self) -> typing.Optional[builtins.str]:
        '''The name for the notification rule.

        Notification rule names must be unique in your AWS account.

        :default: - generated from the ``id``
        '''
        result = self._values.get("notification_rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def events(self) -> typing.List[PipelineNotificationEvents]:
        '''A list of event types associated with this notification rule for CodePipeline Pipeline.

        For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api
        '''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[PipelineNotificationEvents], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineNotifyOnOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.PipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_bucket": "artifactBucket",
        "cross_account_keys": "crossAccountKeys",
        "cross_region_replication_buckets": "crossRegionReplicationBuckets",
        "enable_key_rotation": "enableKeyRotation",
        "pipeline_name": "pipelineName",
        "restart_execution_on_update": "restartExecutionOnUpdate",
        "reuse_cross_region_support_stacks": "reuseCrossRegionSupportStacks",
        "role": "role",
        "stages": "stages",
    },
)
class PipelineProps:
    def __init__(
        self,
        *,
        artifact_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
        cross_account_keys: typing.Optional[builtins.bool] = None,
        cross_region_replication_buckets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_s3_55f001a5.IBucket]] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[builtins.bool] = None,
        reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        stages: typing.Optional[typing.Sequence[typing.Union["StageProps", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param artifact_bucket: The S3 bucket used by this Pipeline to store artifacts. Default: - A new S3 bucket will be created.
        :param cross_account_keys: Create KMS keys for cross-account deployments. This controls whether the pipeline is enabled for cross-account deployments. By default cross-account deployments are enabled, but this feature requires that KMS Customer Master Keys are created which have a cost of $1/month. If you do not need cross-account deployments, you can set this to ``false`` to not create those keys and save on that cost (the artifact bucket will be encrypted with an AWS-managed key). However, cross-account deployments will no longer be possible. Default: true
        :param cross_region_replication_buckets: A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a Stack containing an S3 Bucket in that region. Default: - None.
        :param enable_key_rotation: Enable KMS key rotation for the generated KMS keys. By default KMS key rotation is disabled, but will add an additional $1/month for each year the key exists when enabled. Default: - false (key rotation is disabled)
        :param pipeline_name: Name of the pipeline. Default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
        :param restart_execution_on_update: Indicates whether to rerun the AWS CodePipeline pipeline after you update it. Default: false
        :param reuse_cross_region_support_stacks: Reuse the same cross region support stack for all pipelines in the App. Default: - true (Use the same support stack for all pipelines in App)
        :param role: The IAM role to be assumed by this Pipeline. Default: a new IAM role will be created.
        :param stages: The list of Stages, in order, to create this Pipeline with. You can always add more Stages later by calling {@link Pipeline#addStage}. Default: - None.

        :exampleMetadata: infused

        Example::

            # project: codebuild.PipelineProject
            
            repository = codecommit.Repository(self, "MyRepository",
                repository_name="MyRepository"
            )
            project = codebuild.PipelineProject(self, "MyProject")
            
            source_output = codepipeline.Artifact()
            source_action = codepipeline_actions.CodeCommitSourceAction(
                action_name="CodeCommit",
                repository=repository,
                output=source_output
            )
            build_action = codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=project,
                input=source_output,
                outputs=[codepipeline.Artifact()],  # optional
                execute_batch_build=True,  # optional, defaults to false
                combine_batch_build_artifacts=True
            )
            
            codepipeline.Pipeline(self, "MyPipeline",
                stages=[codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ), codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                )
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d2c9c55dd5d2f20736ad52bd9449bcc9d63b2711ce74c33baa02a1f31e747cf)
            check_type(argname="argument artifact_bucket", value=artifact_bucket, expected_type=type_hints["artifact_bucket"])
            check_type(argname="argument cross_account_keys", value=cross_account_keys, expected_type=type_hints["cross_account_keys"])
            check_type(argname="argument cross_region_replication_buckets", value=cross_region_replication_buckets, expected_type=type_hints["cross_region_replication_buckets"])
            check_type(argname="argument enable_key_rotation", value=enable_key_rotation, expected_type=type_hints["enable_key_rotation"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument restart_execution_on_update", value=restart_execution_on_update, expected_type=type_hints["restart_execution_on_update"])
            check_type(argname="argument reuse_cross_region_support_stacks", value=reuse_cross_region_support_stacks, expected_type=type_hints["reuse_cross_region_support_stacks"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument stages", value=stages, expected_type=type_hints["stages"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if artifact_bucket is not None:
            self._values["artifact_bucket"] = artifact_bucket
        if cross_account_keys is not None:
            self._values["cross_account_keys"] = cross_account_keys
        if cross_region_replication_buckets is not None:
            self._values["cross_region_replication_buckets"] = cross_region_replication_buckets
        if enable_key_rotation is not None:
            self._values["enable_key_rotation"] = enable_key_rotation
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name
        if restart_execution_on_update is not None:
            self._values["restart_execution_on_update"] = restart_execution_on_update
        if reuse_cross_region_support_stacks is not None:
            self._values["reuse_cross_region_support_stacks"] = reuse_cross_region_support_stacks
        if role is not None:
            self._values["role"] = role
        if stages is not None:
            self._values["stages"] = stages

    @builtins.property
    def artifact_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket]:
        '''The S3 bucket used by this Pipeline to store artifacts.

        :default: - A new S3 bucket will be created.
        '''
        result = self._values.get("artifact_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket], result)

    @builtins.property
    def cross_account_keys(self) -> typing.Optional[builtins.bool]:
        '''Create KMS keys for cross-account deployments.

        This controls whether the pipeline is enabled for cross-account deployments.

        By default cross-account deployments are enabled, but this feature requires
        that KMS Customer Master Keys are created which have a cost of $1/month.

        If you do not need cross-account deployments, you can set this to ``false`` to
        not create those keys and save on that cost (the artifact bucket will be
        encrypted with an AWS-managed key). However, cross-account deployments will
        no longer be possible.

        :default: true
        '''
        result = self._values.get("cross_account_keys")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_replication_buckets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_s3_55f001a5.IBucket]]:
        '''A map of region to S3 bucket name used for cross-region CodePipeline.

        For every Action that you specify targeting a different region than the Pipeline itself,
        if you don't provide an explicit Bucket for that region using this property,
        the construct will automatically create a Stack containing an S3 Bucket in that region.

        :default: - None.
        '''
        result = self._values.get("cross_region_replication_buckets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_s3_55f001a5.IBucket]], result)

    @builtins.property
    def enable_key_rotation(self) -> typing.Optional[builtins.bool]:
        '''Enable KMS key rotation for the generated KMS keys.

        By default KMS key rotation is disabled, but will add an additional $1/month
        for each year the key exists when enabled.

        :default: - false (key rotation is disabled)
        '''
        result = self._values.get("enable_key_rotation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        '''Name of the pipeline.

        :default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
        '''
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restart_execution_on_update(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to rerun the AWS CodePipeline pipeline after you update it.

        :default: false
        '''
        result = self._values.get("restart_execution_on_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def reuse_cross_region_support_stacks(self) -> typing.Optional[builtins.bool]:
        '''Reuse the same cross region support stack for all pipelines in the App.

        :default: - true (Use the same support stack for all pipelines in App)
        '''
        result = self._values.get("reuse_cross_region_support_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''The IAM role to be assumed by this Pipeline.

        :default: a new IAM role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def stages(self) -> typing.Optional[typing.List["StageProps"]]:
        '''The list of Stages, in order, to create this Pipeline with.

        You can always add more Stages later by calling {@link Pipeline#addStage}.

        :default: - None.
        '''
        result = self._values.get("stages")
        return typing.cast(typing.Optional[typing.List["StageProps"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.StagePlacement",
    jsii_struct_bases=[],
    name_mapping={"just_after": "justAfter", "right_before": "rightBefore"},
)
class StagePlacement:
    def __init__(
        self,
        *,
        just_after: typing.Optional[IStage] = None,
        right_before: typing.Optional[IStage] = None,
    ) -> None:
        '''Allows you to control where to place a new Stage when it's added to the Pipeline.

        Note that you can provide only one of the below properties -
        specifying more than one will result in a validation error.

        :param just_after: Inserts the new Stage as a child of the given Stage (changing its current child Stage, if it had one).
        :param right_before: Inserts the new Stage as a parent of the given Stage (changing its current parent Stage, if it had one).

        :see: #justAfter
        :exampleMetadata: infused

        Example::

            # Insert a new Stage at an arbitrary point
            # pipeline: codepipeline.Pipeline
            # another_stage: codepipeline.IStage
            # yet_another_stage: codepipeline.IStage
            
            
            some_stage = pipeline.add_stage(
                stage_name="SomeStage",
                placement=codepipeline.StagePlacement(
                    # note: you can only specify one of the below properties
                    right_before=another_stage,
                    just_after=yet_another_stage
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0619ed44577d805bbd71c337297fed809418b93c97e0bedc01899b6f462c51f0)
            check_type(argname="argument just_after", value=just_after, expected_type=type_hints["just_after"])
            check_type(argname="argument right_before", value=right_before, expected_type=type_hints["right_before"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if just_after is not None:
            self._values["just_after"] = just_after
        if right_before is not None:
            self._values["right_before"] = right_before

    @builtins.property
    def just_after(self) -> typing.Optional[IStage]:
        '''Inserts the new Stage as a child of the given Stage (changing its current child Stage, if it had one).'''
        result = self._values.get("just_after")
        return typing.cast(typing.Optional[IStage], result)

    @builtins.property
    def right_before(self) -> typing.Optional[IStage]:
        '''Inserts the new Stage as a parent of the given Stage (changing its current parent Stage, if it had one).'''
        result = self._values.get("right_before")
        return typing.cast(typing.Optional[IStage], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StagePlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.StageProps",
    jsii_struct_bases=[],
    name_mapping={
        "stage_name": "stageName",
        "actions": "actions",
        "transition_disabled_reason": "transitionDisabledReason",
        "transition_to_enabled": "transitionToEnabled",
    },
)
class StageProps:
    def __init__(
        self,
        *,
        stage_name: builtins.str,
        actions: typing.Optional[typing.Sequence[IAction]] = None,
        transition_disabled_reason: typing.Optional[builtins.str] = None,
        transition_to_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties of a Pipeline Stage.

        :param stage_name: The physical, human-readable name to assign to this Pipeline Stage.
        :param actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.
        :param transition_disabled_reason: The reason for disabling transition to this stage. Only applicable if ``transitionToEnabled`` is set to ``false``. Default: 'Transition disabled'
        :param transition_to_enabled: Whether to enable transition to this stage. Default: true

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codepipeline as codepipeline
            
            # action: codepipeline.Action
            
            stage_props = codepipeline.StageProps(
                stage_name="stageName",
            
                # the properties below are optional
                actions=[action],
                transition_disabled_reason="transitionDisabledReason",
                transition_to_enabled=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af751edd2e729b79dd24c0c8186ec89a121da03648858669aac7b6a664c65c5e)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument transition_disabled_reason", value=transition_disabled_reason, expected_type=type_hints["transition_disabled_reason"])
            check_type(argname="argument transition_to_enabled", value=transition_to_enabled, expected_type=type_hints["transition_to_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
        }
        if actions is not None:
            self._values["actions"] = actions
        if transition_disabled_reason is not None:
            self._values["transition_disabled_reason"] = transition_disabled_reason
        if transition_to_enabled is not None:
            self._values["transition_to_enabled"] = transition_to_enabled

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name to assign to this Pipeline Stage.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[IAction]]:
        '''The list of Actions to create this Stage with.

        You can always add more Actions later by calling {@link IStage#addAction}.
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[IAction]], result)

    @builtins.property
    def transition_disabled_reason(self) -> typing.Optional[builtins.str]:
        '''The reason for disabling transition to this stage.

        Only applicable
        if ``transitionToEnabled`` is set to ``false``.

        :default: 'Transition disabled'
        '''
        result = self._values.get("transition_disabled_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transition_to_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable transition to this stage.

        :default: true
        '''
        result = self._values.get("transition_to_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAction)
class Action(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-codepipeline.Action",
):
    '''Low-level class for generic CodePipeline Actions implementing the {@link IAction} interface.

    Contains some common logic that can be re-used by all {@link IAction} implementations.
    If you're writing your own Action class,
    feel free to extend this class.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        stage: IStage,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> ActionConfig:
        '''The callback invoked when this Action is added to a Pipeline.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c3f70ef09925618e26deb1a257cf4edf11c05f11012a5aa6741901b9bac9873)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        options = ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bind", [scope, stage, options]))

    @jsii.member(jsii_name="bound")
    @abc.abstractmethod
    def _bound(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        stage: IStage,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> ActionConfig:
        '''This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: -
        :param target: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcad290f2016f730ed17cfe0089eaf3b8726828c6d6c38d77ea05a34bf3a9279)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_events_efcdfa54.RuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [name, target, options]))

    @jsii.member(jsii_name="variableExpression")
    def _variable_expression(self, variable_name: builtins.str) -> builtins.str:
        '''
        :param variable_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0da0cc44862e6a9c7d093e09bda2c1ce0ab0dfb72dfc1a776984947aa7ad5481)
            check_type(argname="argument variable_name", value=variable_name, expected_type=type_hints["variable_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "variableExpression", [variable_name]))

    @builtins.property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> ActionProperties:
        '''The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.
        '''
        return typing.cast(ActionProperties, jsii.get(self, "actionProperties"))

    @builtins.property
    @jsii.member(jsii_name="providedActionProperties")
    @abc.abstractmethod
    def _provided_action_properties(self) -> ActionProperties:
        '''This is a renamed version of the {@link IAction.actionProperties} property.'''
        ...


class _ActionProxy(Action):
    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        stage: IStage,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> ActionConfig:
        '''This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fc6405848a27fdf315539fe1e733fa40b357f0a4ee5c6b30af5430bfe691bce)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        options = ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bound", [scope, stage, options]))

    @builtins.property
    @jsii.member(jsii_name="providedActionProperties")
    def _provided_action_properties(self) -> ActionProperties:
        '''This is a renamed version of the {@link IAction.actionProperties} property.'''
        return typing.cast(ActionProperties, jsii.get(self, "providedActionProperties"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Action).__jsii_proxy_class__ = lambda : _ActionProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codepipeline.StageOptions",
    jsii_struct_bases=[StageProps],
    name_mapping={
        "stage_name": "stageName",
        "actions": "actions",
        "transition_disabled_reason": "transitionDisabledReason",
        "transition_to_enabled": "transitionToEnabled",
        "placement": "placement",
    },
)
class StageOptions(StageProps):
    def __init__(
        self,
        *,
        stage_name: builtins.str,
        actions: typing.Optional[typing.Sequence[IAction]] = None,
        transition_disabled_reason: typing.Optional[builtins.str] = None,
        transition_to_enabled: typing.Optional[builtins.bool] = None,
        placement: typing.Optional[typing.Union[StagePlacement, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param stage_name: The physical, human-readable name to assign to this Pipeline Stage.
        :param actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.
        :param transition_disabled_reason: The reason for disabling transition to this stage. Only applicable if ``transitionToEnabled`` is set to ``false``. Default: 'Transition disabled'
        :param transition_to_enabled: Whether to enable transition to this stage. Default: true
        :param placement: 

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_stepfunctions as stepfunctions
            
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            input_artifact = codepipeline.Artifact()
            start_state = stepfunctions.Pass(self, "StartState")
            simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
                definition=start_state
            )
            step_function_action = codepipeline_actions.StepFunctionInvokeAction(
                action_name="Invoke",
                state_machine=simple_state_machine,
                state_machine_input=codepipeline_actions.StateMachineInput.file_path(input_artifact.at_path("assets/input.json"))
            )
            pipeline.add_stage(
                stage_name="StepFunctions",
                actions=[step_function_action]
            )
        '''
        if isinstance(placement, dict):
            placement = StagePlacement(**placement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e27a5a30ad9418c2d3a1fa9c78339e42d72516bb3945a6fed78e8ffed57d067)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument transition_disabled_reason", value=transition_disabled_reason, expected_type=type_hints["transition_disabled_reason"])
            check_type(argname="argument transition_to_enabled", value=transition_to_enabled, expected_type=type_hints["transition_to_enabled"])
            check_type(argname="argument placement", value=placement, expected_type=type_hints["placement"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
        }
        if actions is not None:
            self._values["actions"] = actions
        if transition_disabled_reason is not None:
            self._values["transition_disabled_reason"] = transition_disabled_reason
        if transition_to_enabled is not None:
            self._values["transition_to_enabled"] = transition_to_enabled
        if placement is not None:
            self._values["placement"] = placement

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name to assign to this Pipeline Stage.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[IAction]]:
        '''The list of Actions to create this Stage with.

        You can always add more Actions later by calling {@link IStage#addAction}.
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[IAction]], result)

    @builtins.property
    def transition_disabled_reason(self) -> typing.Optional[builtins.str]:
        '''The reason for disabling transition to this stage.

        Only applicable
        if ``transitionToEnabled`` is set to ``false``.

        :default: 'Transition disabled'
        '''
        result = self._values.get("transition_disabled_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transition_to_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable transition to this stage.

        :default: true
        '''
        result = self._values.get("transition_to_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def placement(self) -> typing.Optional[StagePlacement]:
        result = self._values.get("placement")
        return typing.cast(typing.Optional[StagePlacement], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Action",
    "ActionArtifactBounds",
    "ActionBindOptions",
    "ActionCategory",
    "ActionConfig",
    "ActionProperties",
    "Artifact",
    "ArtifactPath",
    "CfnCustomActionType",
    "CfnCustomActionTypeProps",
    "CfnPipeline",
    "CfnPipelineProps",
    "CfnWebhook",
    "CfnWebhookProps",
    "CommonActionProps",
    "CommonAwsActionProps",
    "CrossRegionSupport",
    "CustomActionProperty",
    "CustomActionRegistration",
    "CustomActionRegistrationProps",
    "GlobalVariables",
    "IAction",
    "IPipeline",
    "IStage",
    "Pipeline",
    "PipelineNotificationEvents",
    "PipelineNotifyOnOptions",
    "PipelineProps",
    "StageOptions",
    "StagePlacement",
    "StageProps",
]

publication.publish()

def _typecheckingstub__49437c0971e28d40061501b41b10bef84bbde7bc57c839a7171d8affd27f2163(
    *,
    max_inputs: jsii.Number,
    max_outputs: jsii.Number,
    min_inputs: jsii.Number,
    min_outputs: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d95e267c604745fb56119c678b3c0dfb91677cacab5aef7f405e7c0dc87bc257(
    *,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aafaa1bf0422ec59bdd95cd4eb1d4a9364ad38b88b4ff99f0055b4140ef7b3e(
    *,
    configuration: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f4cfd8eb0ae80afe471c2da4f2e9123b86c4807079be718470ed88f1fe6c053(
    *,
    action_name: builtins.str,
    artifact_bounds: typing.Union[ActionArtifactBounds, typing.Dict[builtins.str, typing.Any]],
    category: ActionCategory,
    provider: builtins.str,
    account: typing.Optional[builtins.str] = None,
    inputs: typing.Optional[typing.Sequence[Artifact]] = None,
    outputs: typing.Optional[typing.Sequence[Artifact]] = None,
    owner: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    resource: typing.Optional[_aws_cdk_core_f4b25747.IResource] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    run_order: typing.Optional[jsii.Number] = None,
    variables_namespace: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2edd07d274634f766fff267d67eecee48019d0884972b001d42ea2960593d58(
    artifact_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fdfd021c480d32c1093a92cf683469e620a7e639046a7a28fdaf509ce0afb79(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bba6e9bee16bf93b686e614c794394bcf58cae233a630a37441474019de9d15(
    file_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f5b03f659c1db1d9d83621aa3fe7f5824e1a107aee0df03869ca3e0bbe8d321(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e23b949c5346a804f686591a270d7030e82a3db64884865161f3f8efc981c19(
    json_file: builtins.str,
    key_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc5dd1f6e7ef5ce0f269d73a32fd796caf9046c3d22a29e5c828c67674438b5a(
    key: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e12a0f2b4d3abc9eb4dd8a50b401b04d20dec5a1a21309d1a54036d2a635e56d(
    artifact: Artifact,
    file_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__566369c25dc33b8a0f2cdfaba4a57a1674455ba52b6cd443db74bee345c1803a(
    artifact_name: builtins.str,
    file_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b97c1dd247aea8532e1bd6bc03a53a909902c2db4d6535790030356848640b(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    category: builtins.str,
    input_artifact_details: typing.Union[typing.Union[CfnCustomActionType.ArtifactDetailsProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
    output_artifact_details: typing.Union[typing.Union[CfnCustomActionType.ArtifactDetailsProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
    provider: builtins.str,
    version: builtins.str,
    configuration_properties: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnCustomActionType.ConfigurationPropertiesProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    settings: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnCustomActionType.SettingsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8e330b3b8a34f8d7e36f547dde5f95051c07b0782784f5a78b8c64b2c39ea3f(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f6acebc8348182323be09e7e36b852add0a83c813a7e0f984fd41772c6f3860(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85aba90a3d0ab3f804acacf909d5ee5b57661aa3ed8064fbd498bfb84301c0eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467ddb2c73ce4d8522b48f8b27695fbfc8201b8d465445a611e7c456ec7651cb(
    value: typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _aws_cdk_core_f4b25747.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99a5d79a11542631af9fab118778f9aca711a3e059200928a274791f467cecb3(
    value: typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _aws_cdk_core_f4b25747.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5843ffd71957c4b4e75a784a340cdcb79f0057db979b00181233add475fd73ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6415fa88f7bb064bcc3c44509d895676a63589b13508525a5fa462c66d860f13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__499b2d3dba84b2966125616c0dff272afab83b8007b83550794130475cc31438(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnCustomActionType.ConfigurationPropertiesProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86d36b6dab88be8ad4e76e1e3476c14bc75d347b8fc3c8aab27d34f5fd222384(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnCustomActionType.SettingsProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1439a619a23e9709e7af30ae96e7cbd6d5e0965516099d1cb0d173849ffa6955(
    *,
    maximum_count: jsii.Number,
    minimum_count: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1821cc0e55eff338d50046f5b1a19a662fcf01156cdeb53f57e5c171bb2f30(
    *,
    key: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
    name: builtins.str,
    required: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
    secret: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
    description: typing.Optional[builtins.str] = None,
    queryable: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60390fcee5af2ad2918c79f29b14e48bd199ffda4949057f602bd61c857ac2e(
    *,
    entity_url_template: typing.Optional[builtins.str] = None,
    execution_url_template: typing.Optional[builtins.str] = None,
    revision_url_template: typing.Optional[builtins.str] = None,
    third_party_configuration_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__548578e0735fd41956f7f5be1cc6dd48a87943eb1cab1c1b7cb0ee04e0c21163(
    *,
    category: builtins.str,
    input_artifact_details: typing.Union[typing.Union[CfnCustomActionType.ArtifactDetailsProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
    output_artifact_details: typing.Union[typing.Union[CfnCustomActionType.ArtifactDetailsProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
    provider: builtins.str,
    version: builtins.str,
    configuration_properties: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnCustomActionType.ConfigurationPropertiesProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    settings: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnCustomActionType.SettingsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a90dbf085b8b42f0558df98c3942bd858deeeb90552c8a551b3b0bceac12e11(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    role_arn: builtins.str,
    stages: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.StageDeclarationProperty, typing.Dict[builtins.str, typing.Any]]]]],
    artifact_store: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    artifact_stores: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreMapProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    disable_inbound_stage_transitions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.StageTransitionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    restart_execution_on_update: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b67e712add9fd75144d32d50ba3653a6077dc093da68ff21675fc3777d663ca2(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677855baaa5a899eb692a6eb70f5cce317e2c1e1d9c00ac922275ba9a5c58229(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7ed59bf70c8e4b92394ba62d5029dd2c03816a91f87777cca964dcbe49e95b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fcae7c0369d95f08bf8d31a33e277c30f238deb1652a631789cc35c043b47cc(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.StageDeclarationProperty]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5be61728c138dba2c84426ae4bf816cd48816dd2ca8c5e076331481c8d6c7409(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.ArtifactStoreProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b54aaeabf7470459a896f9114f2d21853371a712fa5fcf9b0bda9ba829e9214(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.ArtifactStoreMapProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d30782e225fb6bb51bff4cc6515a7b7dca598ee7c748d111ed4660dfa4336618(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnPipeline.StageTransitionProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7faa0e1c0f5c78ee074c0b51d023c79272c147e7fee07b2537f4b0842a0ff32(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbc0f73d640d69b4f0c1f085d44f64ce77ee064fe18227b524fbb8340e4a413d(
    value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7794f1937a73d9b9e8be8b19671275bd670df968d81cb1a10979b429aa7d549(
    *,
    action_type_id: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ActionTypeIdProperty, typing.Dict[builtins.str, typing.Any]]],
    name: builtins.str,
    configuration: typing.Any = None,
    input_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.InputArtifactProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    output_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.OutputArtifactProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    region: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    run_order: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3565bd42d3fa473f3aceed4033b614545cc5c6dc5d6a59c8c1a79336a5a0cf70(
    *,
    category: builtins.str,
    owner: builtins.str,
    provider: builtins.str,
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a61d6272b695134faa6b72e0fc22d6aa31285ee6be658d0a787181fa02b3686a(
    *,
    artifact_store: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreProperty, typing.Dict[builtins.str, typing.Any]]],
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f393d37f4eeb1331c24bccf5966c23d8b07f6c507108791d5b3dbaf5b19a4e95(
    *,
    location: builtins.str,
    type: builtins.str,
    encryption_key: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.EncryptionKeyProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c957574ae9f77327d277442bc9e9188ce33307604990cae118a2734ac6b9ac(
    *,
    name: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2cabd8548be0ffd77669f6b7f70733418a5f82aec7c37d13b81e715430966b(
    *,
    id: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b1253085d1a223d5e047c0225c56d87a1c9335b09aa0ffa8d0b0bd2932b6ec5(
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41aab9838a6fa3b04cc14585296b7aa276af8b5667ddec30a8e5784ff7da2e82(
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30b3c4be72debca476d94038d3fb862cae82deb520b0ad68085a04aa7be9c46d(
    *,
    actions: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ActionDeclarationProperty, typing.Dict[builtins.str, typing.Any]]]]],
    name: builtins.str,
    blockers: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.BlockerDeclarationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9178a81eab86bfb46f1e96e57fb136b413d087f699093e3835a4ed28ddb85993(
    *,
    reason: builtins.str,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__399f399dd104b18405c6a406bc4582445dd4401bb75f9f7443c2ef988e2b4616(
    *,
    role_arn: builtins.str,
    stages: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.StageDeclarationProperty, typing.Dict[builtins.str, typing.Any]]]]],
    artifact_store: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    artifact_stores: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.ArtifactStoreMapProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    disable_inbound_stage_transitions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnPipeline.StageTransitionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    restart_execution_on_update: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c8d9d5f4f9a49198aad5b142eaa884276e566098b502dce3967e5feb4f08b4(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    authentication: builtins.str,
    authentication_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnWebhook.WebhookAuthConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    filters: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnWebhook.WebhookFilterRuleProperty, typing.Dict[builtins.str, typing.Any]]]]],
    target_action: builtins.str,
    target_pipeline: builtins.str,
    target_pipeline_version: jsii.Number,
    name: typing.Optional[builtins.str] = None,
    register_with_third_party: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adfbef8326040df1dbd08f423e63e33586552a9e175c72b9ae23e757028b85b1(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9125eef274c8839b695ab0bb898a622158fbbbaa622fa689d090d368703d9296(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d184be6798f66aedf8d276d1820b8232b0506376eed7b3bf668008e35494118(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020c22776d77738198a58a11d9db16bbc79a0cc2054d3ed6dcd9deb56da4b36e(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnWebhook.WebhookAuthConfigurationProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59beb9cfa4c2bd7a6148d2a65f399ff5296c8ed2631244e3e7ddf3b5774b20ff(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnWebhook.WebhookFilterRuleProperty]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aa54d76ff17d2f580d3fe06f755f79870f7b66cb9af35e1d0b2d3f8b98fc97a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df31cb0950dcc7019fed9255ccfd416da54e68de3dab9e35e6821be8fdb65ec7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0ccc4a2ccdc6d2ac4927888611da9fd8961815fc04a3bb7b5b23c53d09cdee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e292a530fa7830506bbd9e980a007d747aa8a4bede6f8db2168e800ae367deb(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf9c9cefcf08d621e7ea50857911947e623004f927044dac20193452b87f9c48(
    value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c2d6b94792e1f423293abe56c1c5bafe39c94c0480cb739ff7d8780e3518be(
    *,
    allowed_ip_range: typing.Optional[builtins.str] = None,
    secret_token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22280a9993953e867a13984d2d51e6b2316ab7254d3baa896964cb85b5f6a31f(
    *,
    json_path: builtins.str,
    match_equals: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4c528c1252da1be3d0ef8e263c9dbd4eaef33fb8879f8d5301ced25603b00eb(
    *,
    authentication: builtins.str,
    authentication_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnWebhook.WebhookAuthConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    filters: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnWebhook.WebhookFilterRuleProperty, typing.Dict[builtins.str, typing.Any]]]]],
    target_action: builtins.str,
    target_pipeline: builtins.str,
    target_pipeline_version: jsii.Number,
    name: typing.Optional[builtins.str] = None,
    register_with_third_party: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b982e6d6312c65f867c30c3d33be03ebdbbee534bb9f0b5163701d37c2dc2d7(
    *,
    action_name: builtins.str,
    run_order: typing.Optional[jsii.Number] = None,
    variables_namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef056dde856e997c38b4d3a061132f8263bb2e8152145d6546afb3729a3035d2(
    *,
    action_name: builtins.str,
    run_order: typing.Optional[jsii.Number] = None,
    variables_namespace: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45cbcc0f891a61e380a3f6eaa19f8c25e9892bcdea80438911b4aaad5c60611b(
    *,
    replication_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    stack: _aws_cdk_core_f4b25747.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb0cb51d4ed66bc56ba70dafe8657d9fa1e2f0698d21d8d37e6a870db44653a5(
    *,
    name: builtins.str,
    required: builtins.bool,
    description: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.bool] = None,
    queryable: typing.Optional[builtins.bool] = None,
    secret: typing.Optional[builtins.bool] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__606777d998a7c0a503c51d4ed0e4616008f88170600debdead23a1e955371434(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    artifact_bounds: typing.Union[ActionArtifactBounds, typing.Dict[builtins.str, typing.Any]],
    category: ActionCategory,
    provider: builtins.str,
    action_properties: typing.Optional[typing.Sequence[typing.Union[CustomActionProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    entity_url: typing.Optional[builtins.str] = None,
    execution_url: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e144db048884d7cdd29246cbfada59cbaff708570d4e450ab672f1c3273387ce(
    *,
    artifact_bounds: typing.Union[ActionArtifactBounds, typing.Dict[builtins.str, typing.Any]],
    category: ActionCategory,
    provider: builtins.str,
    action_properties: typing.Optional[typing.Sequence[typing.Union[CustomActionProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    entity_url: typing.Optional[builtins.str] = None,
    execution_url: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f087503a953ba2edbe5d7793bf17f96389a1bae9d4262b1f01e81dc775b31016(
    scope: _aws_cdk_core_f4b25747.Construct,
    stage: IStage,
    *,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4206f0ca4f896a913ee158e3f47f39ef60969140c494d4a737613d1768d1c46(
    name: builtins.str,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cf0c15116528a686f8c394f5c1545d39abc257be231189ee16551554a38481f(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    events: typing.Sequence[PipelineNotificationEvents],
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30dfe2e460caf15e7696a215cf589f57f80d864c1fb35fd5907148ce10911c2b(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d5ace427a05f66fb5e1542bf5df15a967fa85df90e475dc9cdb8e873bd8db9(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3106bdd30fa222d7b604f1ad650b6c3486e4323ed5418735ad62f5da41d537e0(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8026e92418b84e699517cdeb2938d952a6fc7db5c810ff3ac7ccaf6f3a0c9e4f(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e73dcfe5b09723a66441ad9c124ca0e7f197fa3baf0c51dbacf65f66406a0277(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abbe125ab463a0af83eb11fdcf4d887432390adb33c4a82db40b7990adcfc1a4(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e74956085e7dc6b78603b31a0bcf3077efadbf7834ed283e27100c5acbeaac60(
    action: IAction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2cc4448fa5add30227d8058bdd32a268335e37f00d63d3ab55e324cda09b6f(
    name: builtins.str,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f90b55f94a38352f916e0ab2a635da01beb113c2d8c149f21913828fd638773(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    artifact_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
    cross_account_keys: typing.Optional[builtins.bool] = None,
    cross_region_replication_buckets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_s3_55f001a5.IBucket]] = None,
    enable_key_rotation: typing.Optional[builtins.bool] = None,
    pipeline_name: typing.Optional[builtins.str] = None,
    restart_execution_on_update: typing.Optional[builtins.bool] = None,
    reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    stages: typing.Optional[typing.Sequence[typing.Union[StageProps, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dee678410112d4f0f7990206ef3fd094e87a5e500ff5fb6ae80f0d93d6716ff(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    pipeline_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcaf8ecf43e6c5be3722df6436b10b7b0350c3af3003e70362fd7fd5f9fe0214(
    statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60549b383bfd8f30c2555fe131ba32635ca7a19029f9587c7159f460bb22d76f(
    _scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2701c843193d3ccc38731da37f5f25a885d1d0361587123e78f0f16ebee252(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    events: typing.Sequence[PipelineNotificationEvents],
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63ac0ea05fd9a43a550eeca5f2a120f8909383315b1101d43cdb252b1302375d(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14fc8598de0989a0a651e25a7223c8c8c10d57906be5e7da6f06b23444796afd(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6acd9654be76a948bb0181c03367a720720edc87ca52e26d7571f22de47eec(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a57f66d4cae51a72b8f4db6b4d8be092649e2ddcdb294390f801b9a182239f8c(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9fc488565bf936d319df3c65cd1792484ef2a172f6fb6cd3471cf9ecf9a4692(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6bb219c997f3cc8e98fb086e022e15e99414d0b9939261db36c9b13df7d195(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2921a12b733ca52dd9bc0fe7b5cf641bce9de8cf749d2f7f815acfda0959e108(
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751b9eb85a9c1708b1614ec32def63e8fbe0e589e469d802a6fce06945750f1f(
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
    events: typing.Sequence[PipelineNotificationEvents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d2c9c55dd5d2f20736ad52bd9449bcc9d63b2711ce74c33baa02a1f31e747cf(
    *,
    artifact_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
    cross_account_keys: typing.Optional[builtins.bool] = None,
    cross_region_replication_buckets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_s3_55f001a5.IBucket]] = None,
    enable_key_rotation: typing.Optional[builtins.bool] = None,
    pipeline_name: typing.Optional[builtins.str] = None,
    restart_execution_on_update: typing.Optional[builtins.bool] = None,
    reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    stages: typing.Optional[typing.Sequence[typing.Union[StageProps, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0619ed44577d805bbd71c337297fed809418b93c97e0bedc01899b6f462c51f0(
    *,
    just_after: typing.Optional[IStage] = None,
    right_before: typing.Optional[IStage] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af751edd2e729b79dd24c0c8186ec89a121da03648858669aac7b6a664c65c5e(
    *,
    stage_name: builtins.str,
    actions: typing.Optional[typing.Sequence[IAction]] = None,
    transition_disabled_reason: typing.Optional[builtins.str] = None,
    transition_to_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c3f70ef09925618e26deb1a257cf4edf11c05f11012a5aa6741901b9bac9873(
    scope: _aws_cdk_core_f4b25747.Construct,
    stage: IStage,
    *,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcad290f2016f730ed17cfe0089eaf3b8726828c6d6c38d77ea05a34bf3a9279(
    name: builtins.str,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_efcdfa54.IEventBus] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_efcdfa54.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0da0cc44862e6a9c7d093e09bda2c1ce0ab0dfb72dfc1a776984947aa7ad5481(
    variable_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fc6405848a27fdf315539fe1e733fa40b357f0a4ee5c6b30af5430bfe691bce(
    scope: _aws_cdk_core_f4b25747.Construct,
    stage: IStage,
    *,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e27a5a30ad9418c2d3a1fa9c78339e42d72516bb3945a6fed78e8ffed57d067(
    *,
    stage_name: builtins.str,
    actions: typing.Optional[typing.Sequence[IAction]] = None,
    transition_disabled_reason: typing.Optional[builtins.str] = None,
    transition_to_enabled: typing.Optional[builtins.bool] = None,
    placement: typing.Optional[typing.Union[StagePlacement, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
