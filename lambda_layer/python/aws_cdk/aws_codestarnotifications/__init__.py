'''
# AWS CodeStarNotifications Construct Library

<!--BEGIN STABILITY BANNER-->---


![End-of-Support](https://img.shields.io/badge/End--of--Support-critical.svg?style=for-the-badge)

> AWS CDK v1 has reached End-of-Support on 2023-06-01.
> This package is no longer being updated, and users should migrate to AWS CDK v2.
>
> For more information on how to migrate, see the [*Migrating to AWS CDK v2* guide](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html).

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## NotificationRule

The `NotificationRule` construct defines an AWS CodeStarNotifications rule.
The rule specifies the events you want notifications about and the targets
(such as Amazon SNS topics or AWS Chatbot clients configured for Slack)
where you want to receive them.
Notification targets are objects that implement the `INotificationRuleTarget`
interface and notification source is object that implement the `INotificationRuleSource` interface.

## Notification Targets

This module includes classes that implement the `INotificationRuleTarget` interface for SNS and slack in AWS Chatbot.

The following targets are supported:

* `SNS`: specify event and notify to SNS topic.
* `AWS Chatbot`: specify event and notify to slack channel and only support `SlackChannelConfiguration`.

## Examples

```python
import aws_cdk.aws_codestarnotifications as notifications
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_sns as sns
import aws_cdk.aws_chatbot as chatbot


project = codebuild.PipelineProject(self, "MyProject")

topic = sns.Topic(self, "MyTopic1")

slack = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
    slack_channel_configuration_name="YOUR_CHANNEL_NAME",
    slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
    slack_channel_id="YOUR_SLACK_CHANNEL_ID"
)

rule = notifications.NotificationRule(self, "NotificationRule",
    source=project,
    events=["codebuild-project-build-state-succeeded", "codebuild-project-build-state-failed"
    ],
    targets=[topic]
)
rule.add_target(slack)
```

## Notification Source

This module includes classes that implement the `INotificationRuleSource` interface for AWS CodeBuild,
AWS CodePipeline and will support AWS CodeCommit, AWS CodeDeploy in future.

The following sources are supported:

* `AWS CodeBuild`: support codebuild project to trigger notification when event specified.
* `AWS CodePipeline`: support codepipeline to trigger notification when event specified.

## Events

For the complete list of supported event types for CodeBuild and CodePipeline, see:

* [Events for notification rules on build projects](https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-buildproject).
* [Events for notification rules on pipelines](https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline).
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

import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnNotificationRule(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codestarnotifications.CfnNotificationRule",
):
    '''A CloudFormation ``AWS::CodeStarNotifications::NotificationRule``.

    Creates a notification rule for a resource. The rule specifies the events you want notifications about and the targets (such as AWS Chatbot topics or AWS Chatbot clients configured for Slack) where you want to receive them.

    :cloudformationResource: AWS::CodeStarNotifications::NotificationRule
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codestarnotifications as codestarnotifications
        
        cfn_notification_rule = codestarnotifications.CfnNotificationRule(self, "MyCfnNotificationRule",
            detail_type="detailType",
            event_type_ids=["eventTypeIds"],
            name="name",
            resource="resource",
            targets=[codestarnotifications.CfnNotificationRule.TargetProperty(
                target_address="targetAddress",
                target_type="targetType"
            )],
        
            # the properties below are optional
            created_by="createdBy",
            event_type_id="eventTypeId",
            status="status",
            tags={
                "tags_key": "tags"
            },
            target_address="targetAddress"
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        detail_type: builtins.str,
        event_type_ids: typing.Sequence[builtins.str],
        name: builtins.str,
        resource: builtins.str,
        targets: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union["CfnNotificationRule.TargetProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]],
        created_by: typing.Optional[builtins.str] = None,
        event_type_id: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        target_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::CodeStarNotifications::NotificationRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param detail_type: The level of detail to include in the notifications for this resource. ``BASIC`` will include only the contents of the event as it would appear in Amazon CloudWatch. ``FULL`` will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.
        :param event_type_ids: A list of event types associated with this notification rule. For a complete list of event types and IDs, see `Notification concepts <https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api>`_ in the *Developer Tools Console User Guide* .
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account .
        :param resource: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Supported resources include pipelines in AWS CodePipeline , repositories in AWS CodeCommit , and build projects in AWS CodeBuild .
        :param targets: A list of Amazon Resource Names (ARNs) of Amazon Simple Notification Service topics and AWS Chatbot clients to associate with the notification rule.
        :param created_by: ``AWS::CodeStarNotifications::NotificationRule.CreatedBy``.
        :param event_type_id: ``AWS::CodeStarNotifications::NotificationRule.EventTypeId``.
        :param status: The status of the notification rule. The default value is ``ENABLED`` . If the status is set to ``DISABLED`` , notifications aren't sent for the notification rule.
        :param tags: A list of tags to apply to this notification rule. Key names cannot start with " ``aws`` ".
        :param target_address: ``AWS::CodeStarNotifications::NotificationRule.TargetAddress``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afd9fbc9994fa80bdf60737da78d9f087a32581b7f81c0b4c334c08663e60f9c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnNotificationRuleProps(
            detail_type=detail_type,
            event_type_ids=event_type_ids,
            name=name,
            resource=resource,
            targets=targets,
            created_by=created_by,
            event_type_id=event_type_id,
            status=status,
            tags=tags,
            target_address=target_address,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__099a82c08137cec0b43dbe5f7b1d1f05f11dbad5f4403f71ceb6110e60a1fd52)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c3ef9b2c426e96fe677cd4d4414d0a37f3f81ed3db98434f6136136c5935aff)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''A list of tags to apply to this notification rule.

        Key names cannot start with " ``aws`` ".

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="detailType")
    def detail_type(self) -> builtins.str:
        '''The level of detail to include in the notifications for this resource.

        ``BASIC`` will include only the contents of the event as it would appear in Amazon CloudWatch. ``FULL`` will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-detailtype
        '''
        return typing.cast(builtins.str, jsii.get(self, "detailType"))

    @detail_type.setter
    def detail_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1328d7a4da7ac6738932c8452e08a9f4e55096173b2312ae6ab2db86423b1938)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "detailType", value)

    @builtins.property
    @jsii.member(jsii_name="eventTypeIds")
    def event_type_ids(self) -> typing.List[builtins.str]:
        '''A list of event types associated with this notification rule.

        For a complete list of event types and IDs, see `Notification concepts <https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api>`_ in the *Developer Tools Console User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-eventtypeids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventTypeIds"))

    @event_type_ids.setter
    def event_type_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__473d075788634c1f35d0683a9d9e587ea4f2462911cccfe7dcae793c8ee67be7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventTypeIds", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names must be unique in your AWS account .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__142bd3ac8c2650fb09979c4507e9dab179ed76b9322f6eaee331ad6ba5770543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the resource to associate with the notification rule.

        Supported resources include pipelines in AWS CodePipeline , repositories in AWS CodeCommit , and build projects in AWS CodeBuild .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-resource
        '''
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @resource.setter
    def resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeeffb63d38d20cc300c45b3315533d9c340b49c13b122eee8cf79eb6582d934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resource", value)

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnNotificationRule.TargetProperty", _aws_cdk_core_f4b25747.IResolvable]]]:
        '''A list of Amazon Resource Names (ARNs) of Amazon Simple Notification Service topics and AWS Chatbot clients to associate with the notification rule.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-targets
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnNotificationRule.TargetProperty", _aws_cdk_core_f4b25747.IResolvable]]], jsii.get(self, "targets"))

    @targets.setter
    def targets(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnNotificationRule.TargetProperty", _aws_cdk_core_f4b25747.IResolvable]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c95c26691bebee88c7be548c1c6c93065d1b91cf9d25d5b018ba30362271d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targets", value)

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStarNotifications::NotificationRule.CreatedBy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-createdby
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ce894a7a6566797118e7e025c8afb3b619760fa0243fbfef148b299b0ee57f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value)

    @builtins.property
    @jsii.member(jsii_name="eventTypeId")
    def event_type_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStarNotifications::NotificationRule.EventTypeId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-eventtypeid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventTypeId"))

    @event_type_id.setter
    def event_type_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3da63eceaa33c3f0096dfc27beda96674cdc9db5157b4588066cea8c8255782)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventTypeId", value)

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''The status of the notification rule.

        The default value is ``ENABLED`` . If the status is set to ``DISABLED`` , notifications aren't sent for the notification rule.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-status
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @status.setter
    def status(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ee093cb8a1c33c860df75ca61d85a592b43f62f5d20c2a3ab1c008fccea3e4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value)

    @builtins.property
    @jsii.member(jsii_name="targetAddress")
    def target_address(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStarNotifications::NotificationRule.TargetAddress``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-targetaddress
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetAddress"))

    @target_address.setter
    def target_address(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d9806aa77ce61f06619c13a0820bc0f31ca983daf63d4d3875dde9fc13c4934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetAddress", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codestarnotifications.CfnNotificationRule.TargetProperty",
        jsii_struct_bases=[],
        name_mapping={"target_address": "targetAddress", "target_type": "targetType"},
    )
    class TargetProperty:
        def __init__(
            self,
            *,
            target_address: builtins.str,
            target_type: builtins.str,
        ) -> None:
            '''Information about the AWS Chatbot topics or AWS Chatbot clients associated with a notification rule.

            :param target_address: The Amazon Resource Name (ARN) of the AWS Chatbot topic or AWS Chatbot client.
            :param target_type: The target type. Can be an Amazon Simple Notification Service topic or AWS Chatbot client. - Amazon Simple Notification Service topics are specified as ``SNS`` . - AWS Chatbot clients are specified as ``AWSChatbotSlack`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestarnotifications-notificationrule-target.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codestarnotifications as codestarnotifications
                
                target_property = codestarnotifications.CfnNotificationRule.TargetProperty(
                    target_address="targetAddress",
                    target_type="targetType"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__ed22e756de55f94cf900263f2eaadbfd5bc3bf60675a721cd588d4bd11c7dd08)
                check_type(argname="argument target_address", value=target_address, expected_type=type_hints["target_address"])
                check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "target_address": target_address,
                "target_type": target_type,
            }

        @builtins.property
        def target_address(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the AWS Chatbot topic or AWS Chatbot client.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestarnotifications-notificationrule-target.html#cfn-codestarnotifications-notificationrule-target-targetaddress
            '''
            result = self._values.get("target_address")
            assert result is not None, "Required property 'target_address' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def target_type(self) -> builtins.str:
            '''The target type. Can be an Amazon Simple Notification Service topic or AWS Chatbot client.

            - Amazon Simple Notification Service topics are specified as ``SNS`` .
            - AWS Chatbot clients are specified as ``AWSChatbotSlack`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestarnotifications-notificationrule-target.html#cfn-codestarnotifications-notificationrule-target-targettype
            '''
            result = self._values.get("target_type")
            assert result is not None, "Required property 'target_type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codestarnotifications.CfnNotificationRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "detail_type": "detailType",
        "event_type_ids": "eventTypeIds",
        "name": "name",
        "resource": "resource",
        "targets": "targets",
        "created_by": "createdBy",
        "event_type_id": "eventTypeId",
        "status": "status",
        "tags": "tags",
        "target_address": "targetAddress",
    },
)
class CfnNotificationRuleProps:
    def __init__(
        self,
        *,
        detail_type: builtins.str,
        event_type_ids: typing.Sequence[builtins.str],
        name: builtins.str,
        resource: builtins.str,
        targets: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnNotificationRule.TargetProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]],
        created_by: typing.Optional[builtins.str] = None,
        event_type_id: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        target_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnNotificationRule``.

        :param detail_type: The level of detail to include in the notifications for this resource. ``BASIC`` will include only the contents of the event as it would appear in Amazon CloudWatch. ``FULL`` will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.
        :param event_type_ids: A list of event types associated with this notification rule. For a complete list of event types and IDs, see `Notification concepts <https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api>`_ in the *Developer Tools Console User Guide* .
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account .
        :param resource: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Supported resources include pipelines in AWS CodePipeline , repositories in AWS CodeCommit , and build projects in AWS CodeBuild .
        :param targets: A list of Amazon Resource Names (ARNs) of Amazon Simple Notification Service topics and AWS Chatbot clients to associate with the notification rule.
        :param created_by: ``AWS::CodeStarNotifications::NotificationRule.CreatedBy``.
        :param event_type_id: ``AWS::CodeStarNotifications::NotificationRule.EventTypeId``.
        :param status: The status of the notification rule. The default value is ``ENABLED`` . If the status is set to ``DISABLED`` , notifications aren't sent for the notification rule.
        :param tags: A list of tags to apply to this notification rule. Key names cannot start with " ``aws`` ".
        :param target_address: ``AWS::CodeStarNotifications::NotificationRule.TargetAddress``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            cfn_notification_rule_props = codestarnotifications.CfnNotificationRuleProps(
                detail_type="detailType",
                event_type_ids=["eventTypeIds"],
                name="name",
                resource="resource",
                targets=[codestarnotifications.CfnNotificationRule.TargetProperty(
                    target_address="targetAddress",
                    target_type="targetType"
                )],
            
                # the properties below are optional
                created_by="createdBy",
                event_type_id="eventTypeId",
                status="status",
                tags={
                    "tags_key": "tags"
                },
                target_address="targetAddress"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4eed0a7d017b65718edbd93d2df7bc324716eeff1ff1004d63f607f30a27121)
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument event_type_ids", value=event_type_ids, expected_type=type_hints["event_type_ids"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument event_type_id", value=event_type_id, expected_type=type_hints["event_type_id"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target_address", value=target_address, expected_type=type_hints["target_address"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "detail_type": detail_type,
            "event_type_ids": event_type_ids,
            "name": name,
            "resource": resource,
            "targets": targets,
        }
        if created_by is not None:
            self._values["created_by"] = created_by
        if event_type_id is not None:
            self._values["event_type_id"] = event_type_id
        if status is not None:
            self._values["status"] = status
        if tags is not None:
            self._values["tags"] = tags
        if target_address is not None:
            self._values["target_address"] = target_address

    @builtins.property
    def detail_type(self) -> builtins.str:
        '''The level of detail to include in the notifications for this resource.

        ``BASIC`` will include only the contents of the event as it would appear in Amazon CloudWatch. ``FULL`` will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-detailtype
        '''
        result = self._values.get("detail_type")
        assert result is not None, "Required property 'detail_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_type_ids(self) -> typing.List[builtins.str]:
        '''A list of event types associated with this notification rule.

        For a complete list of event types and IDs, see `Notification concepts <https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api>`_ in the *Developer Tools Console User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-eventtypeids
        '''
        result = self._values.get("event_type_ids")
        assert result is not None, "Required property 'event_type_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names must be unique in your AWS account .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the resource to associate with the notification rule.

        Supported resources include pipelines in AWS CodePipeline , repositories in AWS CodeCommit , and build projects in AWS CodeBuild .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-resource
        '''
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnNotificationRule.TargetProperty, _aws_cdk_core_f4b25747.IResolvable]]]:
        '''A list of Amazon Resource Names (ARNs) of Amazon Simple Notification Service topics and AWS Chatbot clients to associate with the notification rule.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-targets
        '''
        result = self._values.get("targets")
        assert result is not None, "Required property 'targets' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnNotificationRule.TargetProperty, _aws_cdk_core_f4b25747.IResolvable]]], result)

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStarNotifications::NotificationRule.CreatedBy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-createdby
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_type_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStarNotifications::NotificationRule.EventTypeId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-eventtypeid
        '''
        result = self._values.get("event_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''The status of the notification rule.

        The default value is ``ENABLED`` . If the status is set to ``DISABLED`` , notifications aren't sent for the notification rule.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-status
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of tags to apply to this notification rule.

        Key names cannot start with " ``aws`` ".

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def target_address(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStarNotifications::NotificationRule.TargetAddress``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-targetaddress
        '''
        result = self._values.get("target_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-codestarnotifications.DetailType")
class DetailType(enum.Enum):
    '''The level of detail to include in the notifications for this resource.'''

    BASIC = "BASIC"
    '''BASIC will include only the contents of the event as it would appear in AWS CloudWatch.'''
    FULL = "FULL"
    '''FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.'''


@jsii.interface(jsii_type="@aws-cdk/aws-codestarnotifications.INotificationRule")
class INotificationRule(_aws_cdk_core_f4b25747.IResource, typing_extensions.Protocol):
    '''Represents a notification rule.'''

    @builtins.property
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        '''The ARN of the notification rule (i.e. arn:aws:codestar-notifications:::notificationrule/01234abcde).

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: "INotificationRuleTarget") -> builtins.bool:
        '''Adds target to notification rule.

        :param target: The SNS topic or AWS Chatbot Slack target.

        :return: boolean - return true if it had any effect
        '''
        ...


class _INotificationRuleProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
):
    '''Represents a notification rule.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codestarnotifications.INotificationRule"

    @builtins.property
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        '''The ARN of the notification rule (i.e. arn:aws:codestar-notifications:::notificationrule/01234abcde).

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "notificationRuleArn"))

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: "INotificationRuleTarget") -> builtins.bool:
        '''Adds target to notification rule.

        :param target: The SNS topic or AWS Chatbot Slack target.

        :return: boolean - return true if it had any effect
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf15c00e22ddb8a5e39cc2d68f62dacd02a0df9ef33826beb3c4332246956e4)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        return typing.cast(builtins.bool, jsii.invoke(self, "addTarget", [target]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INotificationRule).__jsii_proxy_class__ = lambda : _INotificationRuleProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codestarnotifications.INotificationRuleSource")
class INotificationRuleSource(typing_extensions.Protocol):
    '''Represents a notification source The source that allows CodeBuild and CodePipeline to associate with this rule.'''

    @jsii.member(jsii_name="bindAsNotificationRuleSource")
    def bind_as_notification_rule_source(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "NotificationRuleSourceConfig":
        '''Returns a source configuration for notification rule.

        :param scope: -
        '''
        ...


class _INotificationRuleSourceProxy:
    '''Represents a notification source The source that allows CodeBuild and CodePipeline to associate with this rule.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codestarnotifications.INotificationRuleSource"

    @jsii.member(jsii_name="bindAsNotificationRuleSource")
    def bind_as_notification_rule_source(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "NotificationRuleSourceConfig":
        '''Returns a source configuration for notification rule.

        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20b8b275f189ccc2ff09accf5dee06390479275c6567082197cd63d48b224308)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("NotificationRuleSourceConfig", jsii.invoke(self, "bindAsNotificationRuleSource", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INotificationRuleSource).__jsii_proxy_class__ = lambda : _INotificationRuleSourceProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codestarnotifications.INotificationRuleTarget")
class INotificationRuleTarget(typing_extensions.Protocol):
    '''Represents a notification target That allows AWS Chatbot and SNS topic to associate with this rule target.'''

    @jsii.member(jsii_name="bindAsNotificationRuleTarget")
    def bind_as_notification_rule_target(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "NotificationRuleTargetConfig":
        '''Returns a target configuration for notification rule.

        :param scope: -
        '''
        ...


class _INotificationRuleTargetProxy:
    '''Represents a notification target That allows AWS Chatbot and SNS topic to associate with this rule target.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codestarnotifications.INotificationRuleTarget"

    @jsii.member(jsii_name="bindAsNotificationRuleTarget")
    def bind_as_notification_rule_target(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "NotificationRuleTargetConfig":
        '''Returns a target configuration for notification rule.

        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e20c45ecfd9408362a8d96e83c9807ae4314a628594f1a06a45e5a44b35c1dc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("NotificationRuleTargetConfig", jsii.invoke(self, "bindAsNotificationRuleTarget", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INotificationRuleTarget).__jsii_proxy_class__ = lambda : _INotificationRuleTargetProxy


@jsii.implements(INotificationRule)
class NotificationRule(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codestarnotifications.NotificationRule",
):
    '''A new notification rule.

    :resource: AWS::CodeStarNotifications::NotificationRule
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_codestarnotifications as notifications
        import aws_cdk.aws_codebuild as codebuild
        import aws_cdk.aws_sns as sns
        import aws_cdk.aws_chatbot as chatbot
        
        
        project = codebuild.PipelineProject(self, "MyProject")
        
        topic = sns.Topic(self, "MyTopic1")
        
        slack = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
            slack_channel_configuration_name="YOUR_CHANNEL_NAME",
            slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
            slack_channel_id="YOUR_SLACK_CHANNEL_ID"
        )
        
        rule = notifications.NotificationRule(self, "NotificationRule",
            source=project,
            events=["codebuild-project-build-state-succeeded", "codebuild-project-build-state-failed"
            ],
            targets=[topic]
        )
        rule.add_target(slack)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[builtins.str],
        source: INotificationRuleSource,
        targets: typing.Optional[typing.Sequence[INotificationRuleTarget]] = None,
        detail_type: typing.Optional[DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: A list of event types associated with this notification rule. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param source: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Currently, Supported sources include pipelines in AWS CodePipeline, build projects in AWS CodeBuild, and repositories in AWS CodeCommit in this L2 constructor.
        :param targets: The targets to register for the notification destination. Default: - No targets are added to the rule. Use ``addTarget()`` to add a target.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44cd51cd16c41e58bcfae3942a401921d806a23c62162a792e01a41e083d9b03)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NotificationRuleProps(
            events=events,
            source=source,
            targets=targets,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromNotificationRuleArn")
    @builtins.classmethod
    def from_notification_rule_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        notification_rule_arn: builtins.str,
    ) -> INotificationRule:
        '''Import an existing notification rule provided an ARN.

        :param scope: The parent creating construct.
        :param id: The construct's name.
        :param notification_rule_arn: Notification rule ARN (i.e. arn:aws:codestar-notifications:::notificationrule/01234abcde).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a06dff87da285389a28eba4fea6cfc17a3a5c96258fa4b30ec7e270c1c834e05)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument notification_rule_arn", value=notification_rule_arn, expected_type=type_hints["notification_rule_arn"])
        return typing.cast(INotificationRule, jsii.sinvoke(cls, "fromNotificationRuleArn", [scope, id, notification_rule_arn]))

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: INotificationRuleTarget) -> builtins.bool:
        '''Adds target to notification rule.

        :param target: The SNS topic or AWS Chatbot Slack target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb48dc113ab45841e434838dac865b16d7d8da7bea71a773c552204d78f96a19)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        return typing.cast(builtins.bool, jsii.invoke(self, "addTarget", [target]))

    @builtins.property
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        '''The ARN of the notification rule (i.e. arn:aws:codestar-notifications:::notificationrule/01234abcde).

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "notificationRuleArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codestarnotifications.NotificationRuleOptions",
    jsii_struct_bases=[],
    name_mapping={
        "detail_type": "detailType",
        "enabled": "enabled",
        "notification_rule_name": "notificationRuleName",
    },
)
class NotificationRuleOptions:
    def __init__(
        self,
        *,
        detail_type: typing.Optional[DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Standard set of options for ``notifyOnXxx`` codestar notification handler on construct.

        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            notification_rule_options = codestarnotifications.NotificationRuleOptions(
                detail_type=codestarnotifications.DetailType.BASIC,
                enabled=False,
                notification_rule_name="notificationRuleName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f48407bf3ebe283b8c61872ea5e14d9c18182077e17919c837c1bff567b99e10)
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument notification_rule_name", value=notification_rule_name, expected_type=type_hints["notification_rule_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if enabled is not None:
            self._values["enabled"] = enabled
        if notification_rule_name is not None:
            self._values["notification_rule_name"] = notification_rule_name

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event as it would appear in AWS CloudWatch.
        FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :default: DetailType.FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationRuleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codestarnotifications.NotificationRuleProps",
    jsii_struct_bases=[NotificationRuleOptions],
    name_mapping={
        "detail_type": "detailType",
        "enabled": "enabled",
        "notification_rule_name": "notificationRuleName",
        "events": "events",
        "source": "source",
        "targets": "targets",
    },
)
class NotificationRuleProps(NotificationRuleOptions):
    def __init__(
        self,
        *,
        detail_type: typing.Optional[DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
        events: typing.Sequence[builtins.str],
        source: INotificationRuleSource,
        targets: typing.Optional[typing.Sequence[INotificationRuleTarget]] = None,
    ) -> None:
        '''Properties for a new notification rule.

        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        :param events: A list of event types associated with this notification rule. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param source: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Currently, Supported sources include pipelines in AWS CodePipeline, build projects in AWS CodeBuild, and repositories in AWS CodeCommit in this L2 constructor.
        :param targets: The targets to register for the notification destination. Default: - No targets are added to the rule. Use ``addTarget()`` to add a target.

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_codestarnotifications as notifications
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_sns as sns
            import aws_cdk.aws_chatbot as chatbot
            
            
            project = codebuild.PipelineProject(self, "MyProject")
            
            topic = sns.Topic(self, "MyTopic1")
            
            slack = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
                slack_channel_configuration_name="YOUR_CHANNEL_NAME",
                slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
                slack_channel_id="YOUR_SLACK_CHANNEL_ID"
            )
            
            rule = notifications.NotificationRule(self, "NotificationRule",
                source=project,
                events=["codebuild-project-build-state-succeeded", "codebuild-project-build-state-failed"
                ],
                targets=[topic]
            )
            rule.add_target(slack)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ea85023a7f772a61577fd32f2221d993d003fdc427214063f66bfd43ad35823)
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument notification_rule_name", value=notification_rule_name, expected_type=type_hints["notification_rule_name"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "events": events,
            "source": source,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if enabled is not None:
            self._values["enabled"] = enabled
        if notification_rule_name is not None:
            self._values["notification_rule_name"] = notification_rule_name
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event as it would appear in AWS CloudWatch.
        FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :default: DetailType.FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

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
    def events(self) -> typing.List[builtins.str]:
        '''A list of event types associated with this notification rule.

        For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api
        '''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def source(self) -> INotificationRuleSource:
        '''The Amazon Resource Name (ARN) of the resource to associate with the notification rule.

        Currently, Supported sources include pipelines in AWS CodePipeline, build projects in AWS CodeBuild, and repositories in AWS CodeCommit in this L2 constructor.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestarnotifications-notificationrule.html#cfn-codestarnotifications-notificationrule-resource
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(INotificationRuleSource, result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationRuleTarget]]:
        '''The targets to register for the notification destination.

        :default: - No targets are added to the rule. Use ``addTarget()`` to add a target.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationRuleTarget]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codestarnotifications.NotificationRuleSourceConfig",
    jsii_struct_bases=[],
    name_mapping={"source_arn": "sourceArn"},
)
class NotificationRuleSourceConfig:
    def __init__(self, *, source_arn: builtins.str) -> None:
        '''Information about the Codebuild or CodePipeline associated with a notification source.

        :param source_arn: The Amazon Resource Name (ARN) of the notification source.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            notification_rule_source_config = codestarnotifications.NotificationRuleSourceConfig(
                source_arn="sourceArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd29f82dfe3e27c5ec57406d9b4dfc765a642065c5b174cc9d45a01196558e1e)
            check_type(argname="argument source_arn", value=source_arn, expected_type=type_hints["source_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_arn": source_arn,
        }

    @builtins.property
    def source_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the notification source.'''
        result = self._values.get("source_arn")
        assert result is not None, "Required property 'source_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationRuleSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codestarnotifications.NotificationRuleTargetConfig",
    jsii_struct_bases=[],
    name_mapping={"target_address": "targetAddress", "target_type": "targetType"},
)
class NotificationRuleTargetConfig:
    def __init__(
        self,
        *,
        target_address: builtins.str,
        target_type: builtins.str,
    ) -> None:
        '''Information about the SNS topic or AWS Chatbot client associated with a notification target.

        :param target_address: The Amazon Resource Name (ARN) of the Amazon SNS topic or AWS Chatbot client.
        :param target_type: The target type. Can be an Amazon SNS topic or AWS Chatbot client.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            notification_rule_target_config = codestarnotifications.NotificationRuleTargetConfig(
                target_address="targetAddress",
                target_type="targetType"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1459d5d9250ba2a6d61e9992954cfd9160ec30c48a4db9956fc9b4b56ad1c2a6)
            check_type(argname="argument target_address", value=target_address, expected_type=type_hints["target_address"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_address": target_address,
            "target_type": target_type,
        }

    @builtins.property
    def target_address(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the Amazon SNS topic or AWS Chatbot client.'''
        result = self._values.get("target_address")
        assert result is not None, "Required property 'target_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> builtins.str:
        '''The target type.

        Can be an Amazon SNS topic or AWS Chatbot client.
        '''
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationRuleTargetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnNotificationRule",
    "CfnNotificationRuleProps",
    "DetailType",
    "INotificationRule",
    "INotificationRuleSource",
    "INotificationRuleTarget",
    "NotificationRule",
    "NotificationRuleOptions",
    "NotificationRuleProps",
    "NotificationRuleSourceConfig",
    "NotificationRuleTargetConfig",
]

publication.publish()

def _typecheckingstub__afd9fbc9994fa80bdf60737da78d9f087a32581b7f81c0b4c334c08663e60f9c(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    detail_type: builtins.str,
    event_type_ids: typing.Sequence[builtins.str],
    name: builtins.str,
    resource: builtins.str,
    targets: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnNotificationRule.TargetProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]],
    created_by: typing.Optional[builtins.str] = None,
    event_type_id: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    target_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__099a82c08137cec0b43dbe5f7b1d1f05f11dbad5f4403f71ceb6110e60a1fd52(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c3ef9b2c426e96fe677cd4d4414d0a37f3f81ed3db98434f6136136c5935aff(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1328d7a4da7ac6738932c8452e08a9f4e55096173b2312ae6ab2db86423b1938(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__473d075788634c1f35d0683a9d9e587ea4f2462911cccfe7dcae793c8ee67be7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__142bd3ac8c2650fb09979c4507e9dab179ed76b9322f6eaee331ad6ba5770543(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeeffb63d38d20cc300c45b3315533d9c340b49c13b122eee8cf79eb6582d934(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c95c26691bebee88c7be548c1c6c93065d1b91cf9d25d5b018ba30362271d4(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnNotificationRule.TargetProperty, _aws_cdk_core_f4b25747.IResolvable]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ce894a7a6566797118e7e025c8afb3b619760fa0243fbfef148b299b0ee57f0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3da63eceaa33c3f0096dfc27beda96674cdc9db5157b4588066cea8c8255782(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ee093cb8a1c33c860df75ca61d85a592b43f62f5d20c2a3ab1c008fccea3e4a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d9806aa77ce61f06619c13a0820bc0f31ca983daf63d4d3875dde9fc13c4934(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed22e756de55f94cf900263f2eaadbfd5bc3bf60675a721cd588d4bd11c7dd08(
    *,
    target_address: builtins.str,
    target_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4eed0a7d017b65718edbd93d2df7bc324716eeff1ff1004d63f607f30a27121(
    *,
    detail_type: builtins.str,
    event_type_ids: typing.Sequence[builtins.str],
    name: builtins.str,
    resource: builtins.str,
    targets: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnNotificationRule.TargetProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]],
    created_by: typing.Optional[builtins.str] = None,
    event_type_id: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    target_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf15c00e22ddb8a5e39cc2d68f62dacd02a0df9ef33826beb3c4332246956e4(
    target: INotificationRuleTarget,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20b8b275f189ccc2ff09accf5dee06390479275c6567082197cd63d48b224308(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e20c45ecfd9408362a8d96e83c9807ae4314a628594f1a06a45e5a44b35c1dc(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44cd51cd16c41e58bcfae3942a401921d806a23c62162a792e01a41e083d9b03(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    events: typing.Sequence[builtins.str],
    source: INotificationRuleSource,
    targets: typing.Optional[typing.Sequence[INotificationRuleTarget]] = None,
    detail_type: typing.Optional[DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a06dff87da285389a28eba4fea6cfc17a3a5c96258fa4b30ec7e270c1c834e05(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    notification_rule_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb48dc113ab45841e434838dac865b16d7d8da7bea71a773c552204d78f96a19(
    target: INotificationRuleTarget,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f48407bf3ebe283b8c61872ea5e14d9c18182077e17919c837c1bff567b99e10(
    *,
    detail_type: typing.Optional[DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ea85023a7f772a61577fd32f2221d993d003fdc427214063f66bfd43ad35823(
    *,
    detail_type: typing.Optional[DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
    events: typing.Sequence[builtins.str],
    source: INotificationRuleSource,
    targets: typing.Optional[typing.Sequence[INotificationRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd29f82dfe3e27c5ec57406d9b4dfc765a642065c5b174cc9d45a01196558e1e(
    *,
    source_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1459d5d9250ba2a6d61e9992954cfd9160ec30c48a4db9956fc9b4b56ad1c2a6(
    *,
    target_address: builtins.str,
    target_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
