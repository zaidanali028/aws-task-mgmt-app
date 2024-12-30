'''
# Amazon Elastic File System Construct Library

<!--BEGIN STABILITY BANNER-->---


![End-of-Support](https://img.shields.io/badge/End--of--Support-critical.svg?style=for-the-badge)

> AWS CDK v1 has reached End-of-Support on 2023-06-01.
> This package is no longer being updated, and users should migrate to AWS CDK v2.
>
> For more information on how to migrate, see the [*Migrating to AWS CDK v2* guide](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html).

---
<!--END STABILITY BANNER-->

[Amazon Elastic File System](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html) (Amazon EFS) provides a simple, scalable,
fully managed elastic NFS file system for use with AWS Cloud services and on-premises resources.
Amazon EFS provides file storage in the AWS Cloud. With Amazon EFS, you can create a file system,
mount the file system on an Amazon EC2 instance, and then read and write data to and from your file system.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## File Systems

Amazon EFS provides elastic, shared file storage that is POSIX-compliant. The file system you create
supports concurrent read and write access from multiple Amazon EC2 instances and is accessible from
all of the Availability Zones in the AWS Region where it is created. Learn more about [EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/creating-using.html)

### Create an Amazon EFS file system

A Virtual Private Cloud (VPC) is required to create an Amazon EFS file system.
The following example creates a file system that is encrypted at rest, running in `General Purpose`
performance mode, and `Bursting` throughput mode and does not transition files to the Infrequent
Access (IA) storage class.

```python
file_system = efs.FileSystem(self, "MyEfsFileSystem",
    vpc=ec2.Vpc(self, "VPC"),
    lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,  # files are not transitioned to infrequent access (IA) storage by default
    performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
    out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS
)
```

⚠️ An Amazon EFS file system's performance mode can't be changed after the file system has been created.
Updating this property will replace the file system.

Any file system that has been created outside the stack can be imported into your CDK app.

Use the `fromFileSystemAttributes()` API to import an existing file system.
Here is an example of giving a role write permissions on a file system.

```python
import aws_cdk.aws_iam as iam


imported_file_system = efs.FileSystem.from_file_system_attributes(self, "existingFS",
    file_system_id="fs-12345678",  # You can also use fileSystemArn instead of fileSystemId.
    security_group=ec2.SecurityGroup.from_security_group_id(self, "SG", "sg-123456789",
        allow_all_outbound=False
    )
)
```

### Permissions

If you need to grant file system permissions to another resource, you can use the `.grant()` API.
As an example, the following code gives `elasticfilesystem:ClientWrite` permissions to an IAM role.

```python
role = iam.Role(self, "Role",
    assumed_by=iam.AnyPrincipal()
)

file_system.grant(role, "elasticfilesystem:ClientWrite")
```

### Access Point

An access point is an application-specific view into an EFS file system that applies an operating
system user and group, and a file system path, to any file system request made through the access
point. The operating system user and group override any identity information provided by the NFS
client. The file system path is exposed as the access point's root directory. Applications using
the access point can only access data in its own directory and below. To learn more, see [Mounting a File System Using EFS Access Points](https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html).

Use the `addAccessPoint` API to create an access point from a fileSystem.

```python
file_system.add_access_point("AccessPoint")
```

By default, when you create an access point, the root(`/`) directory is exposed to the client
connecting to the access point. You can specify a custom path with the `path` property.

If `path` does not exist, it will be created with the settings defined in the `creationInfo`.
See [Creating Access Points](https://docs.aws.amazon.com/efs/latest/ug/create-access-point.html) for more details.

Any access point that has been created outside the stack can be imported into your CDK app.

Use the `fromAccessPointAttributes()` API to import an existing access point.

```python
efs.AccessPoint.from_access_point_attributes(self, "ap",
    access_point_id="fsap-1293c4d9832fo0912",
    file_system=efs.FileSystem.from_file_system_attributes(self, "efs",
        file_system_id="fs-099d3e2f",
        security_group=ec2.SecurityGroup.from_security_group_id(self, "sg", "sg-51530134")
    )
)
```

⚠️ Notice: When importing an Access Point using `fromAccessPointAttributes()`, you must make sure
the mount targets are deployed and their lifecycle state is `available`. Otherwise, you may encounter
the following error when deploying:

> EFS file system <ARN of efs> referenced by access point <ARN of access point of EFS> has
> mount targets created in all availability zones the function will execute in, but not all
> are in the available life cycle state yet. Please wait for them to become available and
> try the request again.

### Connecting

To control who can access the EFS, use the `.connections` attribute. EFS has
a fixed default port, so you don't need to specify the port:

```python
file_system.connections.allow_default_port_from(instance)
```

Learn more about [managing file system network accessibility](https://docs.aws.amazon.com/efs/latest/ug/manage-fs-access.html)

### Mounting the file system using User Data

After you create a file system, you can create mount targets. Then you can mount the file system on
EC2 instances, containers, and Lambda functions in your virtual private cloud (VPC).

The following example automatically mounts a file system during instance launch.

```python
file_system.connections.allow_default_port_from(instance)

instance.user_data.add_commands("yum check-update -y", "yum upgrade -y", "yum install -y amazon-efs-utils", "yum install -y nfs-utils", "file_system_id_1=" + file_system.file_system_id, "efs_mount_point_1=/mnt/efs/fs1", "mkdir -p \"${efs_mount_point_1}\"", "test -f \"/sbin/mount.efs\" && echo \"${file_system_id_1}:/ ${efs_mount_point_1} efs defaults,_netdev\" >> /etc/fstab || " + "echo \"${file_system_id_1}.efs." + Stack.of(self).region + ".amazonaws.com:/ ${efs_mount_point_1} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0\" >> /etc/fstab", "mount -a -t efs,nfs4 defaults")
```

Learn more about [mounting EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/mounting-fs.html)

### Deleting

Since file systems are stateful resources, by default the file system will not be deleted when your
stack is deleted.

You can configure the file system to be destroyed on stack deletion by setting a `removalPolicy`

```python
file_system = efs.FileSystem(self, "EfsFileSystem",
    vpc=ec2.Vpc(self, "VPC"),
    removal_policy=RemovalPolicy.DESTROY
)
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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_67de8e8d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_kms as _aws_cdk_aws_kms_e491a92b
import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.AccessPointAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "access_point_arn": "accessPointArn",
        "access_point_id": "accessPointId",
        "file_system": "fileSystem",
    },
)
class AccessPointAttributes:
    def __init__(
        self,
        *,
        access_point_arn: typing.Optional[builtins.str] = None,
        access_point_id: typing.Optional[builtins.str] = None,
        file_system: typing.Optional["IFileSystem"] = None,
    ) -> None:
        '''Attributes that can be specified when importing an AccessPoint.

        :param access_point_arn: The ARN of the AccessPoint One of this, or {@link accessPointId} is required. Default: - determined based on accessPointId
        :param access_point_id: The ID of the AccessPoint One of this, or {@link accessPointArn} is required. Default: - determined based on accessPointArn
        :param file_system: The EFS file system. Default: - no EFS file system

        :exampleMetadata: infused

        Example::

            efs.AccessPoint.from_access_point_attributes(self, "ap",
                access_point_id="fsap-1293c4d9832fo0912",
                file_system=efs.FileSystem.from_file_system_attributes(self, "efs",
                    file_system_id="fs-099d3e2f",
                    security_group=ec2.SecurityGroup.from_security_group_id(self, "sg", "sg-51530134")
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31d2dfd0f909a5229b20f9d28aaab1a43e0a4e83e4187b76f746d0a619e8eee2)
            check_type(argname="argument access_point_arn", value=access_point_arn, expected_type=type_hints["access_point_arn"])
            check_type(argname="argument access_point_id", value=access_point_id, expected_type=type_hints["access_point_id"])
            check_type(argname="argument file_system", value=file_system, expected_type=type_hints["file_system"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_point_arn is not None:
            self._values["access_point_arn"] = access_point_arn
        if access_point_id is not None:
            self._values["access_point_id"] = access_point_id
        if file_system is not None:
            self._values["file_system"] = file_system

    @builtins.property
    def access_point_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the AccessPoint One of this, or {@link accessPointId} is required.

        :default: - determined based on accessPointId
        '''
        result = self._values.get("access_point_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def access_point_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the AccessPoint One of this, or {@link accessPointArn} is required.

        :default: - determined based on accessPointArn
        '''
        result = self._values.get("access_point_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system(self) -> typing.Optional["IFileSystem"]:
        '''The EFS file system.

        :default: - no EFS file system
        '''
        result = self._values.get("file_system")
        return typing.cast(typing.Optional["IFileSystem"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.AccessPointOptions",
    jsii_struct_bases=[],
    name_mapping={
        "create_acl": "createAcl",
        "path": "path",
        "posix_user": "posixUser",
    },
)
class AccessPointOptions:
    def __init__(
        self,
        *,
        create_acl: typing.Optional[typing.Union["Acl", typing.Dict[builtins.str, typing.Any]]] = None,
        path: typing.Optional[builtins.str] = None,
        posix_user: typing.Optional[typing.Union["PosixUser", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Options to create an AccessPoint.

        :param create_acl: Specifies the POSIX IDs and permissions to apply when creating the access point's root directory. If the root directory specified by ``path`` does not exist, EFS creates the root directory and applies the permissions specified here. If the specified ``path`` does not exist, you must specify ``createAcl``. Default: - None. The directory specified by ``path`` must exist.
        :param path: Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system. Default: '/'
        :param posix_user: The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point. Specify this to enforce a user identity using an access point. Default: - user identity not enforced

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ec2 as ec2
            import aws_cdk.aws_efs as efs
            
            
            # create a new VPC
            vpc = ec2.Vpc(self, "VPC")
            
            # create a new Amazon EFS filesystem
            file_system = efs.FileSystem(self, "Efs", vpc=vpc)
            
            # create a new access point from the filesystem
            access_point = file_system.add_access_point("AccessPoint",
                # set /export/lambda as the root of the access point
                path="/export/lambda",
                # as /export/lambda does not exist in a new efs filesystem, the efs will create the directory with the following createAcl
                create_acl=efs.Acl(
                    owner_uid="1001",
                    owner_gid="1001",
                    permissions="750"
                ),
                # enforce the POSIX identity so lambda function will access with this identity
                posix_user=efs.PosixUser(
                    uid="1001",
                    gid="1001"
                )
            )
            
            fn = lambda_.Function(self, "MyLambda",
                # mount the access point to /mnt/msg in the lambda runtime environment
                filesystem=lambda_.FileSystem.from_efs_access_point(access_point, "/mnt/msg"),
                runtime=lambda_.Runtime.NODEJS_16_X,
                handler="index.handler",
                code=lambda_.Code.from_asset(path.join(__dirname, "lambda-handler")),
                vpc=vpc
            )
        '''
        if isinstance(create_acl, dict):
            create_acl = Acl(**create_acl)
        if isinstance(posix_user, dict):
            posix_user = PosixUser(**posix_user)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb8a6fa3f01a86dbf38812d3501fed43e43720b0f5703852b4a4c24e7db0b4b0)
            check_type(argname="argument create_acl", value=create_acl, expected_type=type_hints["create_acl"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument posix_user", value=posix_user, expected_type=type_hints["posix_user"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create_acl is not None:
            self._values["create_acl"] = create_acl
        if path is not None:
            self._values["path"] = path
        if posix_user is not None:
            self._values["posix_user"] = posix_user

    @builtins.property
    def create_acl(self) -> typing.Optional["Acl"]:
        '''Specifies the POSIX IDs and permissions to apply when creating the access point's root directory.

        If the
        root directory specified by ``path`` does not exist, EFS creates the root directory and applies the
        permissions specified here. If the specified ``path`` does not exist, you must specify ``createAcl``.

        :default: - None. The directory specified by ``path`` must exist.
        '''
        result = self._values.get("create_acl")
        return typing.cast(typing.Optional["Acl"], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system.

        :default: '/'
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_user(self) -> typing.Optional["PosixUser"]:
        '''The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point.

        Specify this to enforce a user identity using an access point.

        :default: - user identity not enforced

        :see: - `Enforcing a User Identity Using an Access Point <https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html>`_
        '''
        result = self._values.get("posix_user")
        return typing.cast(typing.Optional["PosixUser"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.AccessPointProps",
    jsii_struct_bases=[AccessPointOptions],
    name_mapping={
        "create_acl": "createAcl",
        "path": "path",
        "posix_user": "posixUser",
        "file_system": "fileSystem",
    },
)
class AccessPointProps(AccessPointOptions):
    def __init__(
        self,
        *,
        create_acl: typing.Optional[typing.Union["Acl", typing.Dict[builtins.str, typing.Any]]] = None,
        path: typing.Optional[builtins.str] = None,
        posix_user: typing.Optional[typing.Union["PosixUser", typing.Dict[builtins.str, typing.Any]]] = None,
        file_system: "IFileSystem",
    ) -> None:
        '''Properties for the AccessPoint.

        :param create_acl: Specifies the POSIX IDs and permissions to apply when creating the access point's root directory. If the root directory specified by ``path`` does not exist, EFS creates the root directory and applies the permissions specified here. If the specified ``path`` does not exist, you must specify ``createAcl``. Default: - None. The directory specified by ``path`` must exist.
        :param path: Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system. Default: '/'
        :param posix_user: The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point. Specify this to enforce a user identity using an access point. Default: - user identity not enforced
        :param file_system: The efs filesystem.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_efs as efs
            
            # file_system: efs.FileSystem
            
            access_point_props = efs.AccessPointProps(
                file_system=file_system,
            
                # the properties below are optional
                create_acl=efs.Acl(
                    owner_gid="ownerGid",
                    owner_uid="ownerUid",
                    permissions="permissions"
                ),
                path="path",
                posix_user=efs.PosixUser(
                    gid="gid",
                    uid="uid",
            
                    # the properties below are optional
                    secondary_gids=["secondaryGids"]
                )
            )
        '''
        if isinstance(create_acl, dict):
            create_acl = Acl(**create_acl)
        if isinstance(posix_user, dict):
            posix_user = PosixUser(**posix_user)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edffcc913a44b02d3629783b0707de959f82da0d0edf85e3fab22e0730d80bc4)
            check_type(argname="argument create_acl", value=create_acl, expected_type=type_hints["create_acl"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument posix_user", value=posix_user, expected_type=type_hints["posix_user"])
            check_type(argname="argument file_system", value=file_system, expected_type=type_hints["file_system"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "file_system": file_system,
        }
        if create_acl is not None:
            self._values["create_acl"] = create_acl
        if path is not None:
            self._values["path"] = path
        if posix_user is not None:
            self._values["posix_user"] = posix_user

    @builtins.property
    def create_acl(self) -> typing.Optional["Acl"]:
        '''Specifies the POSIX IDs and permissions to apply when creating the access point's root directory.

        If the
        root directory specified by ``path`` does not exist, EFS creates the root directory and applies the
        permissions specified here. If the specified ``path`` does not exist, you must specify ``createAcl``.

        :default: - None. The directory specified by ``path`` must exist.
        '''
        result = self._values.get("create_acl")
        return typing.cast(typing.Optional["Acl"], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system.

        :default: '/'
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_user(self) -> typing.Optional["PosixUser"]:
        '''The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point.

        Specify this to enforce a user identity using an access point.

        :default: - user identity not enforced

        :see: - `Enforcing a User Identity Using an Access Point <https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html>`_
        '''
        result = self._values.get("posix_user")
        return typing.cast(typing.Optional["PosixUser"], result)

    @builtins.property
    def file_system(self) -> "IFileSystem":
        '''The efs filesystem.'''
        result = self._values.get("file_system")
        assert result is not None, "Required property 'file_system' is missing"
        return typing.cast("IFileSystem", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.Acl",
    jsii_struct_bases=[],
    name_mapping={
        "owner_gid": "ownerGid",
        "owner_uid": "ownerUid",
        "permissions": "permissions",
    },
)
class Acl:
    def __init__(
        self,
        *,
        owner_gid: builtins.str,
        owner_uid: builtins.str,
        permissions: builtins.str,
    ) -> None:
        '''Permissions as POSIX ACL.

        :param owner_gid: Specifies the POSIX group ID to apply to the RootDirectory. Accepts values from 0 to 2^32 (4294967295).
        :param owner_uid: Specifies the POSIX user ID to apply to the RootDirectory. Accepts values from 0 to 2^32 (4294967295).
        :param permissions: Specifies the POSIX permissions to apply to the RootDirectory, in the format of an octal number representing the file's mode bits.

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ec2 as ec2
            import aws_cdk.aws_efs as efs
            
            
            # create a new VPC
            vpc = ec2.Vpc(self, "VPC")
            
            # create a new Amazon EFS filesystem
            file_system = efs.FileSystem(self, "Efs", vpc=vpc)
            
            # create a new access point from the filesystem
            access_point = file_system.add_access_point("AccessPoint",
                # set /export/lambda as the root of the access point
                path="/export/lambda",
                # as /export/lambda does not exist in a new efs filesystem, the efs will create the directory with the following createAcl
                create_acl=efs.Acl(
                    owner_uid="1001",
                    owner_gid="1001",
                    permissions="750"
                ),
                # enforce the POSIX identity so lambda function will access with this identity
                posix_user=efs.PosixUser(
                    uid="1001",
                    gid="1001"
                )
            )
            
            fn = lambda_.Function(self, "MyLambda",
                # mount the access point to /mnt/msg in the lambda runtime environment
                filesystem=lambda_.FileSystem.from_efs_access_point(access_point, "/mnt/msg"),
                runtime=lambda_.Runtime.NODEJS_16_X,
                handler="index.handler",
                code=lambda_.Code.from_asset(path.join(__dirname, "lambda-handler")),
                vpc=vpc
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd310f9f4745c0043bc0c8a6d1788656670a2f31bdef8b2f5f651ec9aa65039a)
            check_type(argname="argument owner_gid", value=owner_gid, expected_type=type_hints["owner_gid"])
            check_type(argname="argument owner_uid", value=owner_uid, expected_type=type_hints["owner_uid"])
            check_type(argname="argument permissions", value=permissions, expected_type=type_hints["permissions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner_gid": owner_gid,
            "owner_uid": owner_uid,
            "permissions": permissions,
        }

    @builtins.property
    def owner_gid(self) -> builtins.str:
        '''Specifies the POSIX group ID to apply to the RootDirectory.

        Accepts values from 0 to 2^32 (4294967295).
        '''
        result = self._values.get("owner_gid")
        assert result is not None, "Required property 'owner_gid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def owner_uid(self) -> builtins.str:
        '''Specifies the POSIX user ID to apply to the RootDirectory.

        Accepts values from 0 to 2^32 (4294967295).
        '''
        result = self._values.get("owner_uid")
        assert result is not None, "Required property 'owner_uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permissions(self) -> builtins.str:
        '''Specifies the POSIX permissions to apply to the RootDirectory, in the format of an octal number representing the file's mode bits.'''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Acl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnAccessPoint(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-efs.CfnAccessPoint",
):
    '''A CloudFormation ``AWS::EFS::AccessPoint``.

    The ``AWS::EFS::AccessPoint`` resource creates an EFS access point. An access point is an application-specific view into an EFS file system that applies an operating system user and group, and a file system path, to any file system request made through the access point. The operating system user and group override any identity information provided by the NFS client. The file system path is exposed as the access point's root directory. Applications using the access point can only access data in its own directory and below. To learn more, see `Mounting a file system using EFS access points <https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html>`_ .

    This operation requires permissions for the ``elasticfilesystem:CreateAccessPoint`` action.

    :cloudformationResource: AWS::EFS::AccessPoint
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_efs as efs
        
        cfn_access_point = efs.CfnAccessPoint(self, "MyCfnAccessPoint",
            file_system_id="fileSystemId",
        
            # the properties below are optional
            access_point_tags=[efs.CfnAccessPoint.AccessPointTagProperty(
                key="key",
                value="value"
            )],
            client_token="clientToken",
            posix_user=efs.CfnAccessPoint.PosixUserProperty(
                gid="gid",
                uid="uid",
        
                # the properties below are optional
                secondary_gids=["secondaryGids"]
            ),
            root_directory=efs.CfnAccessPoint.RootDirectoryProperty(
                creation_info=efs.CfnAccessPoint.CreationInfoProperty(
                    owner_gid="ownerGid",
                    owner_uid="ownerUid",
                    permissions="permissions"
                ),
                path="path"
            )
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        access_point_tags: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union["CfnAccessPoint.AccessPointTagProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
        client_token: typing.Optional[builtins.str] = None,
        posix_user: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnAccessPoint.PosixUserProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        root_directory: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnAccessPoint.RootDirectoryProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::EFS::AccessPoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param file_system_id: The ID of the EFS file system that the access point applies to. Accepts only the ID format for input when specifying a file system, for example ``fs-0123456789abcedf2`` .
        :param access_point_tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        :param client_token: The opaque string specified in the request to ensure idempotent creation.
        :param posix_user: The full POSIX identity, including the user ID, group ID, and secondary group IDs on the access point that is used for all file operations by NFS clients using the access point.
        :param root_directory: The directory on the Amazon EFS file system that the access point exposes as the root directory to NFS clients using the access point.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e62c8866f08bee7a6298d187937b428740c5fb81073889628c42065ed5b1f01f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAccessPointProps(
            file_system_id=file_system_id,
            access_point_tags=access_point_tags,
            client_token=client_token,
            posix_user=posix_user,
            root_directory=root_directory,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23e5ba755ac6cb8454d80188ca032203d2215f2d50a60413554edcdaf92d6037)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1db6beb3a5b6ed53e0fb88ef325f69677c52d37d4a8603219722364f73fd4a68)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrAccessPointId")
    def attr_access_point_id(self) -> builtins.str:
        '''The ID of the EFS access point.

        :cloudformationAttribute: AccessPointId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAccessPointId"))

    @builtins.property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the access point.

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''The ID of the EFS file system that the access point applies to.

        Accepts only the ID format for input when specifying a file system, for example ``fs-0123456789abcedf2`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-filesystemid
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13b416810e8a2ed633e71da04f508fab61d50fc98ffb59cc33044ec0a9b6d3ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileSystemId", value)

    @builtins.property
    @jsii.member(jsii_name="accessPointTags")
    def access_point_tags(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnAccessPoint.AccessPointTagProperty", _aws_cdk_core_f4b25747.IResolvable]]]]:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-accesspointtags
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnAccessPoint.AccessPointTagProperty", _aws_cdk_core_f4b25747.IResolvable]]]], jsii.get(self, "accessPointTags"))

    @access_point_tags.setter
    def access_point_tags(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnAccessPoint.AccessPointTagProperty", _aws_cdk_core_f4b25747.IResolvable]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af4149744b13897ad419fc20b2d0c81b39b2e4359341d70cf74e2207aba31d5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPointTags", value)

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> typing.Optional[builtins.str]:
        '''The opaque string specified in the request to ensure idempotent creation.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-clienttoken
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientToken"))

    @client_token.setter
    def client_token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a65468531dc8c72e6e8d318e82ab07b03911e3f6bdd209c6711932ba13eb0a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientToken", value)

    @builtins.property
    @jsii.member(jsii_name="posixUser")
    def posix_user(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.PosixUserProperty"]]:
        '''The full POSIX identity, including the user ID, group ID, and secondary group IDs on the access point that is used for all file operations by NFS clients using the access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-posixuser
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.PosixUserProperty"]], jsii.get(self, "posixUser"))

    @posix_user.setter
    def posix_user(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.PosixUserProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8741273e068b108ec5b5decadda430d6ce85deac79ecba6177dd3f3e66ae94c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "posixUser", value)

    @builtins.property
    @jsii.member(jsii_name="rootDirectory")
    def root_directory(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.RootDirectoryProperty"]]:
        '''The directory on the Amazon EFS file system that the access point exposes as the root directory to NFS clients using the access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-rootdirectory
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.RootDirectoryProperty"]], jsii.get(self, "rootDirectory"))

    @root_directory.setter
    def root_directory(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.RootDirectoryProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f736c9f478d4b2ad636c6af507655f572a9c7d1ee83cf797edc2ee3f5b0c762)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootDirectory", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnAccessPoint.AccessPointTagProperty",
        jsii_struct_bases=[],
        name_mapping={"key": "key", "value": "value"},
    )
    class AccessPointTagProperty:
        def __init__(
            self,
            *,
            key: typing.Optional[builtins.str] = None,
            value: typing.Optional[builtins.str] = None,
        ) -> None:
            '''A tag is a key-value pair attached to a file system.

            Allowed characters in the ``Key`` and ``Value`` properties are letters, white space, and numbers that can be represented in UTF-8, and the following characters: ``+ - = . _ : /``

            :param key: The tag key (String). The key can't start with ``aws:`` .
            :param value: The value of the tag key.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-accesspointtag.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                access_point_tag_property = efs.CfnAccessPoint.AccessPointTagProperty(
                    key="key",
                    value="value"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__130bd0a39fe0e98bccff8e80f76fc5e9127d6226a943cf47d92042b1ec59501e)
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if key is not None:
                self._values["key"] = key
            if value is not None:
                self._values["value"] = value

        @builtins.property
        def key(self) -> typing.Optional[builtins.str]:
            '''The tag key (String).

            The key can't start with ``aws:`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-accesspointtag.html#cfn-efs-accesspoint-accesspointtag-key
            '''
            result = self._values.get("key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def value(self) -> typing.Optional[builtins.str]:
            '''The value of the tag key.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-accesspointtag.html#cfn-efs-accesspoint-accesspointtag-value
            '''
            result = self._values.get("value")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AccessPointTagProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnAccessPoint.CreationInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "owner_gid": "ownerGid",
            "owner_uid": "ownerUid",
            "permissions": "permissions",
        },
    )
    class CreationInfoProperty:
        def __init__(
            self,
            *,
            owner_gid: builtins.str,
            owner_uid: builtins.str,
            permissions: builtins.str,
        ) -> None:
            '''Required if the ``RootDirectory`` > ``Path`` specified does not exist.

            Specifies the POSIX IDs and permissions to apply to the access point's ``RootDirectory`` > ``Path`` . If the access point root directory does not exist, EFS creates it with these settings when a client connects to the access point. When specifying ``CreationInfo`` , you must include values for all properties.

            Amazon EFS creates a root directory only if you have provided the CreationInfo: OwnUid, OwnGID, and permissions for the directory. If you do not provide this information, Amazon EFS does not create the root directory. If the root directory does not exist, attempts to mount using the access point will fail.
            .. epigraph::

               If you do not provide ``CreationInfo`` and the specified ``RootDirectory`` does not exist, attempts to mount the file system using the access point will fail.

            :param owner_gid: Specifies the POSIX group ID to apply to the ``RootDirectory`` . Accepts values from 0 to 2^32 (4294967295).
            :param owner_uid: Specifies the POSIX user ID to apply to the ``RootDirectory`` . Accepts values from 0 to 2^32 (4294967295).
            :param permissions: Specifies the POSIX permissions to apply to the ``RootDirectory`` , in the format of an octal number representing the file's mode bits.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-creationinfo.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                creation_info_property = efs.CfnAccessPoint.CreationInfoProperty(
                    owner_gid="ownerGid",
                    owner_uid="ownerUid",
                    permissions="permissions"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__0fef521b72f6014f8cb111464419bde5c2f6c9b6f6ad3a31d5bb876f1649444d)
                check_type(argname="argument owner_gid", value=owner_gid, expected_type=type_hints["owner_gid"])
                check_type(argname="argument owner_uid", value=owner_uid, expected_type=type_hints["owner_uid"])
                check_type(argname="argument permissions", value=permissions, expected_type=type_hints["permissions"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "owner_gid": owner_gid,
                "owner_uid": owner_uid,
                "permissions": permissions,
            }

        @builtins.property
        def owner_gid(self) -> builtins.str:
            '''Specifies the POSIX group ID to apply to the ``RootDirectory`` .

            Accepts values from 0 to 2^32 (4294967295).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-creationinfo.html#cfn-efs-accesspoint-creationinfo-ownergid
            '''
            result = self._values.get("owner_gid")
            assert result is not None, "Required property 'owner_gid' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner_uid(self) -> builtins.str:
            '''Specifies the POSIX user ID to apply to the ``RootDirectory`` .

            Accepts values from 0 to 2^32 (4294967295).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-creationinfo.html#cfn-efs-accesspoint-creationinfo-owneruid
            '''
            result = self._values.get("owner_uid")
            assert result is not None, "Required property 'owner_uid' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def permissions(self) -> builtins.str:
            '''Specifies the POSIX permissions to apply to the ``RootDirectory`` , in the format of an octal number representing the file's mode bits.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-creationinfo.html#cfn-efs-accesspoint-creationinfo-permissions
            '''
            result = self._values.get("permissions")
            assert result is not None, "Required property 'permissions' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CreationInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnAccessPoint.PosixUserProperty",
        jsii_struct_bases=[],
        name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
    )
    class PosixUserProperty:
        def __init__(
            self,
            *,
            gid: builtins.str,
            uid: builtins.str,
            secondary_gids: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point.

            :param gid: The POSIX group ID used for all file system operations using this access point.
            :param uid: The POSIX user ID used for all file system operations using this access point.
            :param secondary_gids: Secondary POSIX group IDs used for all file system operations using this access point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-posixuser.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                posix_user_property = efs.CfnAccessPoint.PosixUserProperty(
                    gid="gid",
                    uid="uid",
                
                    # the properties below are optional
                    secondary_gids=["secondaryGids"]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__c8af579207a8f1f6b6bbb33d4d9e58eef02ceb239703eb80864a992e6faf602d)
                check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
                check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
                check_type(argname="argument secondary_gids", value=secondary_gids, expected_type=type_hints["secondary_gids"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "gid": gid,
                "uid": uid,
            }
            if secondary_gids is not None:
                self._values["secondary_gids"] = secondary_gids

        @builtins.property
        def gid(self) -> builtins.str:
            '''The POSIX group ID used for all file system operations using this access point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-posixuser.html#cfn-efs-accesspoint-posixuser-gid
            '''
            result = self._values.get("gid")
            assert result is not None, "Required property 'gid' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def uid(self) -> builtins.str:
            '''The POSIX user ID used for all file system operations using this access point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-posixuser.html#cfn-efs-accesspoint-posixuser-uid
            '''
            result = self._values.get("uid")
            assert result is not None, "Required property 'uid' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def secondary_gids(self) -> typing.Optional[typing.List[builtins.str]]:
            '''Secondary POSIX group IDs used for all file system operations using this access point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-posixuser.html#cfn-efs-accesspoint-posixuser-secondarygids
            '''
            result = self._values.get("secondary_gids")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PosixUserProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnAccessPoint.RootDirectoryProperty",
        jsii_struct_bases=[],
        name_mapping={"creation_info": "creationInfo", "path": "path"},
    )
    class RootDirectoryProperty:
        def __init__(
            self,
            *,
            creation_info: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnAccessPoint.CreationInfoProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Specifies the directory on the Amazon EFS file system that the access point provides access to.

            The access point exposes the specified file system path as the root directory of your file system to applications using the access point. NFS clients using the access point can only access data in the access point's ``RootDirectory`` and it's subdirectories.

            :param creation_info: (Optional) Specifies the POSIX IDs and permissions to apply to the access point's ``RootDirectory`` . If the ``RootDirectory`` > ``Path`` specified does not exist, EFS creates the root directory using the ``CreationInfo`` settings when a client connects to an access point. When specifying the ``CreationInfo`` , you must provide values for all properties. .. epigraph:: If you do not provide ``CreationInfo`` and the specified ``RootDirectory`` > ``Path`` does not exist, attempts to mount the file system using the access point will fail.
            :param path: Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system. A path can have up to four subdirectories. If the specified path does not exist, you are required to provide the ``CreationInfo`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-rootdirectory.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                root_directory_property = efs.CfnAccessPoint.RootDirectoryProperty(
                    creation_info=efs.CfnAccessPoint.CreationInfoProperty(
                        owner_gid="ownerGid",
                        owner_uid="ownerUid",
                        permissions="permissions"
                    ),
                    path="path"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__18da55ebe9d19e35cd04aee1b89e63c19a3a8f45697bd5ec5ec437d3d8bb512e)
                check_type(argname="argument creation_info", value=creation_info, expected_type=type_hints["creation_info"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if creation_info is not None:
                self._values["creation_info"] = creation_info
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def creation_info(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.CreationInfoProperty"]]:
            '''(Optional) Specifies the POSIX IDs and permissions to apply to the access point's ``RootDirectory`` .

            If the ``RootDirectory`` > ``Path`` specified does not exist, EFS creates the root directory using the ``CreationInfo`` settings when a client connects to an access point. When specifying the ``CreationInfo`` , you must provide values for all properties.
            .. epigraph::

               If you do not provide ``CreationInfo`` and the specified ``RootDirectory`` > ``Path`` does not exist, attempts to mount the file system using the access point will fail.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-rootdirectory.html#cfn-efs-accesspoint-rootdirectory-creationinfo
            '''
            result = self._values.get("creation_info")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnAccessPoint.CreationInfoProperty"]], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system.

            A path can have up to four subdirectories. If the specified path does not exist, you are required to provide the ``CreationInfo`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-accesspoint-rootdirectory.html#cfn-efs-accesspoint-rootdirectory-path
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RootDirectoryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.CfnAccessPointProps",
    jsii_struct_bases=[],
    name_mapping={
        "file_system_id": "fileSystemId",
        "access_point_tags": "accessPointTags",
        "client_token": "clientToken",
        "posix_user": "posixUser",
        "root_directory": "rootDirectory",
    },
)
class CfnAccessPointProps:
    def __init__(
        self,
        *,
        file_system_id: builtins.str,
        access_point_tags: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnAccessPoint.AccessPointTagProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
        client_token: typing.Optional[builtins.str] = None,
        posix_user: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.PosixUserProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        root_directory: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.RootDirectoryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnAccessPoint``.

        :param file_system_id: The ID of the EFS file system that the access point applies to. Accepts only the ID format for input when specifying a file system, for example ``fs-0123456789abcedf2`` .
        :param access_point_tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        :param client_token: The opaque string specified in the request to ensure idempotent creation.
        :param posix_user: The full POSIX identity, including the user ID, group ID, and secondary group IDs on the access point that is used for all file operations by NFS clients using the access point.
        :param root_directory: The directory on the Amazon EFS file system that the access point exposes as the root directory to NFS clients using the access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_efs as efs
            
            cfn_access_point_props = efs.CfnAccessPointProps(
                file_system_id="fileSystemId",
            
                # the properties below are optional
                access_point_tags=[efs.CfnAccessPoint.AccessPointTagProperty(
                    key="key",
                    value="value"
                )],
                client_token="clientToken",
                posix_user=efs.CfnAccessPoint.PosixUserProperty(
                    gid="gid",
                    uid="uid",
            
                    # the properties below are optional
                    secondary_gids=["secondaryGids"]
                ),
                root_directory=efs.CfnAccessPoint.RootDirectoryProperty(
                    creation_info=efs.CfnAccessPoint.CreationInfoProperty(
                        owner_gid="ownerGid",
                        owner_uid="ownerUid",
                        permissions="permissions"
                    ),
                    path="path"
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf0f5f1b672012093431efe6e1a6a29ef2351e15ae2a01beb8b352e0bc64391)
            check_type(argname="argument file_system_id", value=file_system_id, expected_type=type_hints["file_system_id"])
            check_type(argname="argument access_point_tags", value=access_point_tags, expected_type=type_hints["access_point_tags"])
            check_type(argname="argument client_token", value=client_token, expected_type=type_hints["client_token"])
            check_type(argname="argument posix_user", value=posix_user, expected_type=type_hints["posix_user"])
            check_type(argname="argument root_directory", value=root_directory, expected_type=type_hints["root_directory"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "file_system_id": file_system_id,
        }
        if access_point_tags is not None:
            self._values["access_point_tags"] = access_point_tags
        if client_token is not None:
            self._values["client_token"] = client_token
        if posix_user is not None:
            self._values["posix_user"] = posix_user
        if root_directory is not None:
            self._values["root_directory"] = root_directory

    @builtins.property
    def file_system_id(self) -> builtins.str:
        '''The ID of the EFS file system that the access point applies to.

        Accepts only the ID format for input when specifying a file system, for example ``fs-0123456789abcedf2`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-filesystemid
        '''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_point_tags(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnAccessPoint.AccessPointTagProperty, _aws_cdk_core_f4b25747.IResolvable]]]]:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-accesspointtags
        '''
        result = self._values.get("access_point_tags")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnAccessPoint.AccessPointTagProperty, _aws_cdk_core_f4b25747.IResolvable]]]], result)

    @builtins.property
    def client_token(self) -> typing.Optional[builtins.str]:
        '''The opaque string specified in the request to ensure idempotent creation.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-clienttoken
        '''
        result = self._values.get("client_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_user(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnAccessPoint.PosixUserProperty]]:
        '''The full POSIX identity, including the user ID, group ID, and secondary group IDs on the access point that is used for all file operations by NFS clients using the access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-posixuser
        '''
        result = self._values.get("posix_user")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnAccessPoint.PosixUserProperty]], result)

    @builtins.property
    def root_directory(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnAccessPoint.RootDirectoryProperty]]:
        '''The directory on the Amazon EFS file system that the access point exposes as the root directory to NFS clients using the access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-accesspoint.html#cfn-efs-accesspoint-rootdirectory
        '''
        result = self._values.get("root_directory")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnAccessPoint.RootDirectoryProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAccessPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnFileSystem(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-efs.CfnFileSystem",
):
    '''A CloudFormation ``AWS::EFS::FileSystem``.

    The ``AWS::EFS::FileSystem`` resource creates a new, empty file system in Amazon Elastic File System ( Amazon EFS ). You must create a mount target ( `AWS::EFS::MountTarget <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html>`_ ) to mount your EFS file system on an Amazon EC2 or other AWS cloud compute resource.

    :cloudformationResource: AWS::EFS::FileSystem
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_efs as efs
        
        # file_system_policy: Any
        
        cfn_file_system = efs.CfnFileSystem(self, "MyCfnFileSystem",
            availability_zone_name="availabilityZoneName",
            backup_policy=efs.CfnFileSystem.BackupPolicyProperty(
                status="status"
            ),
            bypass_policy_lockout_safety_check=False,
            encrypted=False,
            file_system_policy=file_system_policy,
            file_system_tags=[efs.CfnFileSystem.ElasticFileSystemTagProperty(
                key="key",
                value="value"
            )],
            kms_key_id="kmsKeyId",
            lifecycle_policies=[efs.CfnFileSystem.LifecyclePolicyProperty(
                transition_to_ia="transitionToIa",
                transition_to_primary_storage_class="transitionToPrimaryStorageClass"
            )],
            performance_mode="performanceMode",
            provisioned_throughput_in_mibps=123,
            throughput_mode="throughputMode"
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        availability_zone_name: typing.Optional[builtins.str] = None,
        backup_policy: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnFileSystem.BackupPolicyProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        bypass_policy_lockout_safety_check: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        file_system_policy: typing.Any = None,
        file_system_tags: typing.Optional[typing.Sequence[typing.Union["CfnFileSystem.ElasticFileSystemTagProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        lifecycle_policies: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnFileSystem.LifecyclePolicyProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        performance_mode: typing.Optional[builtins.str] = None,
        provisioned_throughput_in_mibps: typing.Optional[jsii.Number] = None,
        throughput_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::EFS::FileSystem``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param availability_zone_name: Used to create a file system that uses One Zone storage classes. It specifies the AWS Availability Zone in which to create the file system. Use the format ``us-east-1a`` to specify the Availability Zone. For more information about One Zone storage classes, see `Using EFS storage classes <https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html>`_ in the *Amazon EFS User Guide* . .. epigraph:: One Zone storage classes are not available in all Availability Zones in AWS Regions where Amazon EFS is available.
        :param backup_policy: Use the ``BackupPolicy`` to turn automatic backups on or off for the file system.
        :param bypass_policy_lockout_safety_check: (Optional) A boolean that specifies whether or not to bypass the ``FileSystemPolicy`` lockout safety check. The lockout safety check determines whether the policy in the request will lock out, or prevent, the IAM principal that is making the request from making future ``PutFileSystemPolicy`` requests on this file system. Set ``BypassPolicyLockoutSafetyCheck`` to ``True`` only when you intend to prevent the IAM principal that is making the request from making subsequent ``PutFileSystemPolicy`` requests on this file system. The default value is ``False`` .
        :param encrypted: A Boolean value that, if true, creates an encrypted file system. When creating an encrypted file system, you have the option of specifying a KmsKeyId for an existing AWS KMS key . If you don't specify a KMS key , then the default KMS key for Amazon EFS , ``/aws/elasticfilesystem`` , is used to protect the encrypted file system.
        :param file_system_policy: The ``FileSystemPolicy`` for the EFS file system. A file system policy is an IAM resource policy used to control NFS access to an EFS file system. For more information, see `Using IAM to control NFS access to Amazon EFS <https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html>`_ in the *Amazon EFS User Guide* .
        :param file_system_tags: Use to create one or more tags associated with the file system. Each tag is a user-defined key-value pair. Name your file system on creation by including a ``"Key":"Name","Value":"{value}"`` key-value pair. Each key must be unique. For more information, see `Tagging AWS resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in the *AWS General Reference Guide* .
        :param kms_key_id: The ID of the AWS KMS key to be used to protect the encrypted file system. This parameter is only required if you want to use a nondefault KMS key . If this parameter is not specified, the default KMS key for Amazon EFS is used. This ID can be in one of the following formats: - Key ID - A unique identifier of the key, for example ``1234abcd-12ab-34cd-56ef-1234567890ab`` . - ARN - An Amazon Resource Name (ARN) for the key, for example ``arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab`` . - Key alias - A previously created display name for a key, for example ``alias/projectKey1`` . - Key alias ARN - An ARN for a key alias, for example ``arn:aws:kms:us-west-2:444455556666:alias/projectKey1`` . If ``KmsKeyId`` is specified, the ``Encrypted`` parameter must be set to true.
        :param lifecycle_policies: An array of ``LifecyclePolicy`` objects that define the file system's ``LifecycleConfiguration`` object. A ``LifecycleConfiguration`` object informs EFS lifecycle management and intelligent tiering of the following: - When to move files in the file system from primary storage to the IA storage class. - When to move files that are in IA storage to primary storage. .. epigraph:: Amazon EFS requires that each ``LifecyclePolicy`` object have only a single transition. This means that in a request body, ``LifecyclePolicies`` needs to be structured as an array of ``LifecyclePolicy`` objects, one object for each transition, ``TransitionToIA`` , ``TransitionToPrimaryStorageClass`` . See the example requests in the following section for more information.
        :param performance_mode: The performance mode of the file system. We recommend ``generalPurpose`` performance mode for most file systems. File systems using the ``maxIO`` performance mode can scale to higher levels of aggregate throughput and operations per second with a tradeoff of slightly higher latencies for most file operations. The performance mode can't be changed after the file system has been created. .. epigraph:: The ``maxIO`` mode is not supported on file systems using One Zone storage classes.
        :param provisioned_throughput_in_mibps: The throughput, measured in MiB/s, that you want to provision for a file system that you're creating. Valid values are 1-1024. Required if ``ThroughputMode`` is set to ``provisioned`` . The upper limit for throughput is 1024 MiB/s. To increase this limit, contact AWS Support . For more information, see `Amazon EFS quotas that you can increase <https://docs.aws.amazon.com/efs/latest/ug/limits.html#soft-limits>`_ in the *Amazon EFS User Guide* .
        :param throughput_mode: Specifies the throughput mode for the file system. The mode can be ``bursting`` , ``provisioned`` , or ``elastic`` . If you set ``ThroughputMode`` to ``provisioned`` , you must also set a value for ``ProvisionedThroughputInMibps`` . After you create the file system, you can decrease your file system's throughput in Provisioned Throughput mode or change between the throughput modes, with certain time restrictions. For more information, see `Specifying throughput with provisioned mode <https://docs.aws.amazon.com/efs/latest/ug/performance.html#provisioned-throughput>`_ in the *Amazon EFS User Guide* . Default is ``bursting`` .
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fea9eb820ccdf52ff60762b22d92c3b0961441cf73274573242bc46f6b9799eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnFileSystemProps(
            availability_zone_name=availability_zone_name,
            backup_policy=backup_policy,
            bypass_policy_lockout_safety_check=bypass_policy_lockout_safety_check,
            encrypted=encrypted,
            file_system_policy=file_system_policy,
            file_system_tags=file_system_tags,
            kms_key_id=kms_key_id,
            lifecycle_policies=lifecycle_policies,
            performance_mode=performance_mode,
            provisioned_throughput_in_mibps=provisioned_throughput_in_mibps,
            throughput_mode=throughput_mode,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cdd7d09c9ed0724e3c2a2b57c9b4cb1e4ce79e5cfa64d660d5c6a47b68f3431)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41e4dd4167cdea01666410a5f2f58b025d85e35402976413bee3055e71b26619)
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
        '''The Amazon Resource Name (ARN) of the EFS file system.

        Example: ``arn:aws:elasticfilesystem:us-west-2:1111333322228888:file-system/fs-0123456789abcdef8``

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="attrFileSystemId")
    def attr_file_system_id(self) -> builtins.str:
        '''The ID of the EFS file system.

        For example: ``fs-abcdef0123456789a``

        :cloudformationAttribute: FileSystemId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrFileSystemId"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''Use to create one or more tags associated with the file system.

        Each tag is a user-defined key-value pair. Name your file system on creation by including a ``"Key":"Name","Value":"{value}"`` key-value pair. Each key must be unique. For more information, see `Tagging AWS resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in the *AWS General Reference Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystemtags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemPolicy")
    def file_system_policy(self) -> typing.Any:
        '''The ``FileSystemPolicy`` for the EFS file system.

        A file system policy is an IAM resource policy used to control NFS access to an EFS file system. For more information, see `Using IAM to control NFS access to Amazon EFS <https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html>`_ in the *Amazon EFS User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystempolicy
        '''
        return typing.cast(typing.Any, jsii.get(self, "fileSystemPolicy"))

    @file_system_policy.setter
    def file_system_policy(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c627d1d9c33ffa42a2b8e7be8b89ae0f703e70e099d8d002238e3c22f58bc96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileSystemPolicy", value)

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(self) -> typing.Optional[builtins.str]:
        '''Used to create a file system that uses One Zone storage classes.

        It specifies the AWS Availability Zone in which to create the file system. Use the format ``us-east-1a`` to specify the Availability Zone. For more information about One Zone storage classes, see `Using EFS storage classes <https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html>`_ in the *Amazon EFS User Guide* .
        .. epigraph::

           One Zone storage classes are not available in all Availability Zones in AWS Regions where Amazon EFS is available.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-availabilityzonename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneName"))

    @availability_zone_name.setter
    def availability_zone_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c5a414248495e9b1143202bff021dd0aa08cc762845ce18cd922ea93c461fb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZoneName", value)

    @builtins.property
    @jsii.member(jsii_name="backupPolicy")
    def backup_policy(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnFileSystem.BackupPolicyProperty"]]:
        '''Use the ``BackupPolicy`` to turn automatic backups on or off for the file system.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-backuppolicy
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnFileSystem.BackupPolicyProperty"]], jsii.get(self, "backupPolicy"))

    @backup_policy.setter
    def backup_policy(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnFileSystem.BackupPolicyProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8430a2d295efc4590d0c05f0dc4b573f9ee59afb74a94903d3ccad4f0f07c331)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupPolicy", value)

    @builtins.property
    @jsii.member(jsii_name="bypassPolicyLockoutSafetyCheck")
    def bypass_policy_lockout_safety_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''(Optional) A boolean that specifies whether or not to bypass the ``FileSystemPolicy`` lockout safety check.

        The lockout safety check determines whether the policy in the request will lock out, or prevent, the IAM principal that is making the request from making future ``PutFileSystemPolicy`` requests on this file system. Set ``BypassPolicyLockoutSafetyCheck`` to ``True`` only when you intend to prevent the IAM principal that is making the request from making subsequent ``PutFileSystemPolicy`` requests on this file system. The default value is ``False`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-bypasspolicylockoutsafetycheck
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "bypassPolicyLockoutSafetyCheck"))

    @bypass_policy_lockout_safety_check.setter
    def bypass_policy_lockout_safety_check(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73e51da86fabcb025a0c62a61f63d06e10c2a8a1e81121c664f4a97724ac97d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bypassPolicyLockoutSafetyCheck", value)

    @builtins.property
    @jsii.member(jsii_name="encrypted")
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''A Boolean value that, if true, creates an encrypted file system.

        When creating an encrypted file system, you have the option of specifying a KmsKeyId for an existing AWS KMS key . If you don't specify a KMS key , then the default KMS key for Amazon EFS , ``/aws/elasticfilesystem`` , is used to protect the encrypted file system.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-encrypted
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0e7f14112a6f6e2431ddf12e846dfd47d6d9ebb0b480ee132f6451878a87272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encrypted", value)

    @builtins.property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the AWS KMS key to be used to protect the encrypted file system.

        This parameter is only required if you want to use a nondefault KMS key . If this parameter is not specified, the default KMS key for Amazon EFS is used. This ID can be in one of the following formats:

        - Key ID - A unique identifier of the key, for example ``1234abcd-12ab-34cd-56ef-1234567890ab`` .
        - ARN - An Amazon Resource Name (ARN) for the key, for example ``arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab`` .
        - Key alias - A previously created display name for a key, for example ``alias/projectKey1`` .
        - Key alias ARN - An ARN for a key alias, for example ``arn:aws:kms:us-west-2:444455556666:alias/projectKey1`` .

        If ``KmsKeyId`` is specified, the ``Encrypted`` parameter must be set to true.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fb381b67b0c21e5d8f12de88dbfeb66640ec4333e4ed7d0d9b7565df0209750)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="lifecyclePolicies")
    def lifecycle_policies(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnFileSystem.LifecyclePolicyProperty"]]]]:
        '''An array of ``LifecyclePolicy`` objects that define the file system's ``LifecycleConfiguration`` object.

        A ``LifecycleConfiguration`` object informs EFS lifecycle management and intelligent tiering of the following:

        - When to move files in the file system from primary storage to the IA storage class.
        - When to move files that are in IA storage to primary storage.

        .. epigraph::

           Amazon EFS requires that each ``LifecyclePolicy`` object have only a single transition. This means that in a request body, ``LifecyclePolicies`` needs to be structured as an array of ``LifecyclePolicy`` objects, one object for each transition, ``TransitionToIA`` , ``TransitionToPrimaryStorageClass`` . See the example requests in the following section for more information.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-lifecyclepolicies
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnFileSystem.LifecyclePolicyProperty"]]]], jsii.get(self, "lifecyclePolicies"))

    @lifecycle_policies.setter
    def lifecycle_policies(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnFileSystem.LifecyclePolicyProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a18998e585540c914630cb9579accb0a2e14450c880e520efbfaa82f2a53c25b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lifecyclePolicies", value)

    @builtins.property
    @jsii.member(jsii_name="performanceMode")
    def performance_mode(self) -> typing.Optional[builtins.str]:
        '''The performance mode of the file system.

        We recommend ``generalPurpose`` performance mode for most file systems. File systems using the ``maxIO`` performance mode can scale to higher levels of aggregate throughput and operations per second with a tradeoff of slightly higher latencies for most file operations. The performance mode can't be changed after the file system has been created.
        .. epigraph::

           The ``maxIO`` mode is not supported on file systems using One Zone storage classes.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-performancemode
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "performanceMode"))

    @performance_mode.setter
    def performance_mode(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df981c4eb3c389ea4bd8e7da4424d8187e5fd2e241e45394a483b825bd0aa65b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performanceMode", value)

    @builtins.property
    @jsii.member(jsii_name="provisionedThroughputInMibps")
    def provisioned_throughput_in_mibps(self) -> typing.Optional[jsii.Number]:
        '''The throughput, measured in MiB/s, that you want to provision for a file system that you're creating.

        Valid values are 1-1024. Required if ``ThroughputMode`` is set to ``provisioned`` . The upper limit for throughput is 1024 MiB/s. To increase this limit, contact AWS Support . For more information, see `Amazon EFS quotas that you can increase <https://docs.aws.amazon.com/efs/latest/ug/limits.html#soft-limits>`_ in the *Amazon EFS User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-provisionedthroughputinmibps
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "provisionedThroughputInMibps"))

    @provisioned_throughput_in_mibps.setter
    def provisioned_throughput_in_mibps(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__690b8d52e663680a1787a47bbc298ad6783075236e2da513b492252bbb1035d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provisionedThroughputInMibps", value)

    @builtins.property
    @jsii.member(jsii_name="throughputMode")
    def throughput_mode(self) -> typing.Optional[builtins.str]:
        '''Specifies the throughput mode for the file system.

        The mode can be ``bursting`` , ``provisioned`` , or ``elastic`` . If you set ``ThroughputMode`` to ``provisioned`` , you must also set a value for ``ProvisionedThroughputInMibps`` . After you create the file system, you can decrease your file system's throughput in Provisioned Throughput mode or change between the throughput modes, with certain time restrictions. For more information, see `Specifying throughput with provisioned mode <https://docs.aws.amazon.com/efs/latest/ug/performance.html#provisioned-throughput>`_ in the *Amazon EFS User Guide* .

        Default is ``bursting`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-throughputmode
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "throughputMode"))

    @throughput_mode.setter
    def throughput_mode(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abf59665a8a919c7fbf31b08a5d59ceeec324f663c3c9b25e2581e6b87025c24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "throughputMode", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnFileSystem.BackupPolicyProperty",
        jsii_struct_bases=[],
        name_mapping={"status": "status"},
    )
    class BackupPolicyProperty:
        def __init__(self, *, status: builtins.str) -> None:
            '''The backup policy turns automatic backups for the file system on or off.

            :param status: Set the backup policy status for the file system. - *``ENABLED``* - Turns automatic backups on for the file system. - *``DISABLED``* - Turns automatic backups off for the file system.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-backuppolicy.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                backup_policy_property = efs.CfnFileSystem.BackupPolicyProperty(
                    status="status"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__c3fe5d84a7c5ee1607effd44bb4bd24fe479a5fe89395f15c85f233d4dbc54aa)
                check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "status": status,
            }

        @builtins.property
        def status(self) -> builtins.str:
            '''Set the backup policy status for the file system.

            - *``ENABLED``* - Turns automatic backups on for the file system.
            - *``DISABLED``* - Turns automatic backups off for the file system.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-backuppolicy.html#cfn-efs-filesystem-backuppolicy-status
            '''
            result = self._values.get("status")
            assert result is not None, "Required property 'status' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BackupPolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnFileSystem.ElasticFileSystemTagProperty",
        jsii_struct_bases=[],
        name_mapping={"key": "key", "value": "value"},
    )
    class ElasticFileSystemTagProperty:
        def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
            '''A tag is a key-value pair attached to a file system.

            Allowed characters in the ``Key`` and ``Value`` properties are letters, white space, and numbers that can be represented in UTF-8, and the following characters: ``+ - = . _ : /``

            :param key: The tag key (String). The key can't start with ``aws:`` .
            :param value: The value of the tag key.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-elasticfilesystemtag.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                elastic_file_system_tag_property = efs.CfnFileSystem.ElasticFileSystemTagProperty(
                    key="key",
                    value="value"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__d59c6edcaac2f072b18a6fa229d0a535bd11d208c6550cac454073f8bf71f815)
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "key": key,
                "value": value,
            }

        @builtins.property
        def key(self) -> builtins.str:
            '''The tag key (String).

            The key can't start with ``aws:`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-elasticfilesystemtag.html#cfn-efs-filesystem-elasticfilesystemtag-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''The value of the tag key.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-elasticfilesystemtag.html#cfn-efs-filesystem-elasticfilesystemtag-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ElasticFileSystemTagProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-efs.CfnFileSystem.LifecyclePolicyProperty",
        jsii_struct_bases=[],
        name_mapping={
            "transition_to_ia": "transitionToIa",
            "transition_to_primary_storage_class": "transitionToPrimaryStorageClass",
        },
    )
    class LifecyclePolicyProperty:
        def __init__(
            self,
            *,
            transition_to_ia: typing.Optional[builtins.str] = None,
            transition_to_primary_storage_class: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Describes a policy used by EFS lifecycle management and EFS Intelligent-Tiering that specifies when to transition files into and out of the file system's Infrequent Access (IA) storage class.

            For more information, see `EFS Intelligent‐Tiering and EFS Lifecycle Management <https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html>`_ .
            .. epigraph::

               - Each ``LifecyclePolicy`` object can have only a single transition. This means that in a request body, ``LifecyclePolicies`` must be structured as an array of ``LifecyclePolicy`` objects, one object for each transition, ``TransitionToIA`` , ``TransitionToPrimaryStorageClass`` .
               - See the AWS::EFS::FileSystem examples for the correct ``LifecyclePolicy`` structure. Do not use the syntax shown on this page.

            :param transition_to_ia: Describes the period of time that a file is not accessed, after which it transitions to IA storage. Metadata operations such as listing the contents of a directory don't count as file access events.
            :param transition_to_primary_storage_class: Describes when to transition a file from IA storage to primary storage. Metadata operations such as listing the contents of a directory don't count as file access events.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-lifecyclepolicy.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_efs as efs
                
                lifecycle_policy_property = efs.CfnFileSystem.LifecyclePolicyProperty(
                    transition_to_ia="transitionToIa",
                    transition_to_primary_storage_class="transitionToPrimaryStorageClass"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6fc98193b7297b128504a2d76d224f7f6b1a028e52f61d2e4df2941151a79b10)
                check_type(argname="argument transition_to_ia", value=transition_to_ia, expected_type=type_hints["transition_to_ia"])
                check_type(argname="argument transition_to_primary_storage_class", value=transition_to_primary_storage_class, expected_type=type_hints["transition_to_primary_storage_class"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if transition_to_ia is not None:
                self._values["transition_to_ia"] = transition_to_ia
            if transition_to_primary_storage_class is not None:
                self._values["transition_to_primary_storage_class"] = transition_to_primary_storage_class

        @builtins.property
        def transition_to_ia(self) -> typing.Optional[builtins.str]:
            '''Describes the period of time that a file is not accessed, after which it transitions to IA storage.

            Metadata operations such as listing the contents of a directory don't count as file access events.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-lifecyclepolicy.html#cfn-efs-filesystem-lifecyclepolicy-transitiontoia
            '''
            result = self._values.get("transition_to_ia")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def transition_to_primary_storage_class(self) -> typing.Optional[builtins.str]:
            '''Describes when to transition a file from IA storage to primary storage.

            Metadata operations such as listing the contents of a directory don't count as file access events.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-lifecyclepolicy.html#cfn-efs-filesystem-lifecyclepolicy-transitiontoprimarystorageclass
            '''
            result = self._values.get("transition_to_primary_storage_class")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LifecyclePolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.CfnFileSystemProps",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone_name": "availabilityZoneName",
        "backup_policy": "backupPolicy",
        "bypass_policy_lockout_safety_check": "bypassPolicyLockoutSafetyCheck",
        "encrypted": "encrypted",
        "file_system_policy": "fileSystemPolicy",
        "file_system_tags": "fileSystemTags",
        "kms_key_id": "kmsKeyId",
        "lifecycle_policies": "lifecyclePolicies",
        "performance_mode": "performanceMode",
        "provisioned_throughput_in_mibps": "provisionedThroughputInMibps",
        "throughput_mode": "throughputMode",
    },
)
class CfnFileSystemProps:
    def __init__(
        self,
        *,
        availability_zone_name: typing.Optional[builtins.str] = None,
        backup_policy: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnFileSystem.BackupPolicyProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        bypass_policy_lockout_safety_check: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        file_system_policy: typing.Any = None,
        file_system_tags: typing.Optional[typing.Sequence[typing.Union[CfnFileSystem.ElasticFileSystemTagProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        lifecycle_policies: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnFileSystem.LifecyclePolicyProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        performance_mode: typing.Optional[builtins.str] = None,
        provisioned_throughput_in_mibps: typing.Optional[jsii.Number] = None,
        throughput_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnFileSystem``.

        :param availability_zone_name: Used to create a file system that uses One Zone storage classes. It specifies the AWS Availability Zone in which to create the file system. Use the format ``us-east-1a`` to specify the Availability Zone. For more information about One Zone storage classes, see `Using EFS storage classes <https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html>`_ in the *Amazon EFS User Guide* . .. epigraph:: One Zone storage classes are not available in all Availability Zones in AWS Regions where Amazon EFS is available.
        :param backup_policy: Use the ``BackupPolicy`` to turn automatic backups on or off for the file system.
        :param bypass_policy_lockout_safety_check: (Optional) A boolean that specifies whether or not to bypass the ``FileSystemPolicy`` lockout safety check. The lockout safety check determines whether the policy in the request will lock out, or prevent, the IAM principal that is making the request from making future ``PutFileSystemPolicy`` requests on this file system. Set ``BypassPolicyLockoutSafetyCheck`` to ``True`` only when you intend to prevent the IAM principal that is making the request from making subsequent ``PutFileSystemPolicy`` requests on this file system. The default value is ``False`` .
        :param encrypted: A Boolean value that, if true, creates an encrypted file system. When creating an encrypted file system, you have the option of specifying a KmsKeyId for an existing AWS KMS key . If you don't specify a KMS key , then the default KMS key for Amazon EFS , ``/aws/elasticfilesystem`` , is used to protect the encrypted file system.
        :param file_system_policy: The ``FileSystemPolicy`` for the EFS file system. A file system policy is an IAM resource policy used to control NFS access to an EFS file system. For more information, see `Using IAM to control NFS access to Amazon EFS <https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html>`_ in the *Amazon EFS User Guide* .
        :param file_system_tags: Use to create one or more tags associated with the file system. Each tag is a user-defined key-value pair. Name your file system on creation by including a ``"Key":"Name","Value":"{value}"`` key-value pair. Each key must be unique. For more information, see `Tagging AWS resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in the *AWS General Reference Guide* .
        :param kms_key_id: The ID of the AWS KMS key to be used to protect the encrypted file system. This parameter is only required if you want to use a nondefault KMS key . If this parameter is not specified, the default KMS key for Amazon EFS is used. This ID can be in one of the following formats: - Key ID - A unique identifier of the key, for example ``1234abcd-12ab-34cd-56ef-1234567890ab`` . - ARN - An Amazon Resource Name (ARN) for the key, for example ``arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab`` . - Key alias - A previously created display name for a key, for example ``alias/projectKey1`` . - Key alias ARN - An ARN for a key alias, for example ``arn:aws:kms:us-west-2:444455556666:alias/projectKey1`` . If ``KmsKeyId`` is specified, the ``Encrypted`` parameter must be set to true.
        :param lifecycle_policies: An array of ``LifecyclePolicy`` objects that define the file system's ``LifecycleConfiguration`` object. A ``LifecycleConfiguration`` object informs EFS lifecycle management and intelligent tiering of the following: - When to move files in the file system from primary storage to the IA storage class. - When to move files that are in IA storage to primary storage. .. epigraph:: Amazon EFS requires that each ``LifecyclePolicy`` object have only a single transition. This means that in a request body, ``LifecyclePolicies`` needs to be structured as an array of ``LifecyclePolicy`` objects, one object for each transition, ``TransitionToIA`` , ``TransitionToPrimaryStorageClass`` . See the example requests in the following section for more information.
        :param performance_mode: The performance mode of the file system. We recommend ``generalPurpose`` performance mode for most file systems. File systems using the ``maxIO`` performance mode can scale to higher levels of aggregate throughput and operations per second with a tradeoff of slightly higher latencies for most file operations. The performance mode can't be changed after the file system has been created. .. epigraph:: The ``maxIO`` mode is not supported on file systems using One Zone storage classes.
        :param provisioned_throughput_in_mibps: The throughput, measured in MiB/s, that you want to provision for a file system that you're creating. Valid values are 1-1024. Required if ``ThroughputMode`` is set to ``provisioned`` . The upper limit for throughput is 1024 MiB/s. To increase this limit, contact AWS Support . For more information, see `Amazon EFS quotas that you can increase <https://docs.aws.amazon.com/efs/latest/ug/limits.html#soft-limits>`_ in the *Amazon EFS User Guide* .
        :param throughput_mode: Specifies the throughput mode for the file system. The mode can be ``bursting`` , ``provisioned`` , or ``elastic`` . If you set ``ThroughputMode`` to ``provisioned`` , you must also set a value for ``ProvisionedThroughputInMibps`` . After you create the file system, you can decrease your file system's throughput in Provisioned Throughput mode or change between the throughput modes, with certain time restrictions. For more information, see `Specifying throughput with provisioned mode <https://docs.aws.amazon.com/efs/latest/ug/performance.html#provisioned-throughput>`_ in the *Amazon EFS User Guide* . Default is ``bursting`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_efs as efs
            
            # file_system_policy: Any
            
            cfn_file_system_props = efs.CfnFileSystemProps(
                availability_zone_name="availabilityZoneName",
                backup_policy=efs.CfnFileSystem.BackupPolicyProperty(
                    status="status"
                ),
                bypass_policy_lockout_safety_check=False,
                encrypted=False,
                file_system_policy=file_system_policy,
                file_system_tags=[efs.CfnFileSystem.ElasticFileSystemTagProperty(
                    key="key",
                    value="value"
                )],
                kms_key_id="kmsKeyId",
                lifecycle_policies=[efs.CfnFileSystem.LifecyclePolicyProperty(
                    transition_to_ia="transitionToIa",
                    transition_to_primary_storage_class="transitionToPrimaryStorageClass"
                )],
                performance_mode="performanceMode",
                provisioned_throughput_in_mibps=123,
                throughput_mode="throughputMode"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d452d278cc61aa7b50bcd54214530c05d86f040151f093342063ed26bbe81634)
            check_type(argname="argument availability_zone_name", value=availability_zone_name, expected_type=type_hints["availability_zone_name"])
            check_type(argname="argument backup_policy", value=backup_policy, expected_type=type_hints["backup_policy"])
            check_type(argname="argument bypass_policy_lockout_safety_check", value=bypass_policy_lockout_safety_check, expected_type=type_hints["bypass_policy_lockout_safety_check"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument file_system_policy", value=file_system_policy, expected_type=type_hints["file_system_policy"])
            check_type(argname="argument file_system_tags", value=file_system_tags, expected_type=type_hints["file_system_tags"])
            check_type(argname="argument kms_key_id", value=kms_key_id, expected_type=type_hints["kms_key_id"])
            check_type(argname="argument lifecycle_policies", value=lifecycle_policies, expected_type=type_hints["lifecycle_policies"])
            check_type(argname="argument performance_mode", value=performance_mode, expected_type=type_hints["performance_mode"])
            check_type(argname="argument provisioned_throughput_in_mibps", value=provisioned_throughput_in_mibps, expected_type=type_hints["provisioned_throughput_in_mibps"])
            check_type(argname="argument throughput_mode", value=throughput_mode, expected_type=type_hints["throughput_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability_zone_name is not None:
            self._values["availability_zone_name"] = availability_zone_name
        if backup_policy is not None:
            self._values["backup_policy"] = backup_policy
        if bypass_policy_lockout_safety_check is not None:
            self._values["bypass_policy_lockout_safety_check"] = bypass_policy_lockout_safety_check
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if file_system_policy is not None:
            self._values["file_system_policy"] = file_system_policy
        if file_system_tags is not None:
            self._values["file_system_tags"] = file_system_tags
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if lifecycle_policies is not None:
            self._values["lifecycle_policies"] = lifecycle_policies
        if performance_mode is not None:
            self._values["performance_mode"] = performance_mode
        if provisioned_throughput_in_mibps is not None:
            self._values["provisioned_throughput_in_mibps"] = provisioned_throughput_in_mibps
        if throughput_mode is not None:
            self._values["throughput_mode"] = throughput_mode

    @builtins.property
    def availability_zone_name(self) -> typing.Optional[builtins.str]:
        '''Used to create a file system that uses One Zone storage classes.

        It specifies the AWS Availability Zone in which to create the file system. Use the format ``us-east-1a`` to specify the Availability Zone. For more information about One Zone storage classes, see `Using EFS storage classes <https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html>`_ in the *Amazon EFS User Guide* .
        .. epigraph::

           One Zone storage classes are not available in all Availability Zones in AWS Regions where Amazon EFS is available.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-availabilityzonename
        '''
        result = self._values.get("availability_zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def backup_policy(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnFileSystem.BackupPolicyProperty]]:
        '''Use the ``BackupPolicy`` to turn automatic backups on or off for the file system.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-backuppolicy
        '''
        result = self._values.get("backup_policy")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnFileSystem.BackupPolicyProperty]], result)

    @builtins.property
    def bypass_policy_lockout_safety_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''(Optional) A boolean that specifies whether or not to bypass the ``FileSystemPolicy`` lockout safety check.

        The lockout safety check determines whether the policy in the request will lock out, or prevent, the IAM principal that is making the request from making future ``PutFileSystemPolicy`` requests on this file system. Set ``BypassPolicyLockoutSafetyCheck`` to ``True`` only when you intend to prevent the IAM principal that is making the request from making subsequent ``PutFileSystemPolicy`` requests on this file system. The default value is ``False`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-bypasspolicylockoutsafetycheck
        '''
        result = self._values.get("bypass_policy_lockout_safety_check")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''A Boolean value that, if true, creates an encrypted file system.

        When creating an encrypted file system, you have the option of specifying a KmsKeyId for an existing AWS KMS key . If you don't specify a KMS key , then the default KMS key for Amazon EFS , ``/aws/elasticfilesystem`` , is used to protect the encrypted file system.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-encrypted
        '''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def file_system_policy(self) -> typing.Any:
        '''The ``FileSystemPolicy`` for the EFS file system.

        A file system policy is an IAM resource policy used to control NFS access to an EFS file system. For more information, see `Using IAM to control NFS access to Amazon EFS <https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html>`_ in the *Amazon EFS User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystempolicy
        '''
        result = self._values.get("file_system_policy")
        return typing.cast(typing.Any, result)

    @builtins.property
    def file_system_tags(
        self,
    ) -> typing.Optional[typing.List[CfnFileSystem.ElasticFileSystemTagProperty]]:
        '''Use to create one or more tags associated with the file system.

        Each tag is a user-defined key-value pair. Name your file system on creation by including a ``"Key":"Name","Value":"{value}"`` key-value pair. Each key must be unique. For more information, see `Tagging AWS resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in the *AWS General Reference Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystemtags
        '''
        result = self._values.get("file_system_tags")
        return typing.cast(typing.Optional[typing.List[CfnFileSystem.ElasticFileSystemTagProperty]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the AWS KMS key to be used to protect the encrypted file system.

        This parameter is only required if you want to use a nondefault KMS key . If this parameter is not specified, the default KMS key for Amazon EFS is used. This ID can be in one of the following formats:

        - Key ID - A unique identifier of the key, for example ``1234abcd-12ab-34cd-56ef-1234567890ab`` .
        - ARN - An Amazon Resource Name (ARN) for the key, for example ``arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab`` .
        - Key alias - A previously created display name for a key, for example ``alias/projectKey1`` .
        - Key alias ARN - An ARN for a key alias, for example ``arn:aws:kms:us-west-2:444455556666:alias/projectKey1`` .

        If ``KmsKeyId`` is specified, the ``Encrypted`` parameter must be set to true.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifecycle_policies(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnFileSystem.LifecyclePolicyProperty]]]]:
        '''An array of ``LifecyclePolicy`` objects that define the file system's ``LifecycleConfiguration`` object.

        A ``LifecycleConfiguration`` object informs EFS lifecycle management and intelligent tiering of the following:

        - When to move files in the file system from primary storage to the IA storage class.
        - When to move files that are in IA storage to primary storage.

        .. epigraph::

           Amazon EFS requires that each ``LifecyclePolicy`` object have only a single transition. This means that in a request body, ``LifecyclePolicies`` needs to be structured as an array of ``LifecyclePolicy`` objects, one object for each transition, ``TransitionToIA`` , ``TransitionToPrimaryStorageClass`` . See the example requests in the following section for more information.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-lifecyclepolicies
        '''
        result = self._values.get("lifecycle_policies")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnFileSystem.LifecyclePolicyProperty]]]], result)

    @builtins.property
    def performance_mode(self) -> typing.Optional[builtins.str]:
        '''The performance mode of the file system.

        We recommend ``generalPurpose`` performance mode for most file systems. File systems using the ``maxIO`` performance mode can scale to higher levels of aggregate throughput and operations per second with a tradeoff of slightly higher latencies for most file operations. The performance mode can't be changed after the file system has been created.
        .. epigraph::

           The ``maxIO`` mode is not supported on file systems using One Zone storage classes.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-performancemode
        '''
        result = self._values.get("performance_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provisioned_throughput_in_mibps(self) -> typing.Optional[jsii.Number]:
        '''The throughput, measured in MiB/s, that you want to provision for a file system that you're creating.

        Valid values are 1-1024. Required if ``ThroughputMode`` is set to ``provisioned`` . The upper limit for throughput is 1024 MiB/s. To increase this limit, contact AWS Support . For more information, see `Amazon EFS quotas that you can increase <https://docs.aws.amazon.com/efs/latest/ug/limits.html#soft-limits>`_ in the *Amazon EFS User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-provisionedthroughputinmibps
        '''
        result = self._values.get("provisioned_throughput_in_mibps")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def throughput_mode(self) -> typing.Optional[builtins.str]:
        '''Specifies the throughput mode for the file system.

        The mode can be ``bursting`` , ``provisioned`` , or ``elastic`` . If you set ``ThroughputMode`` to ``provisioned`` , you must also set a value for ``ProvisionedThroughputInMibps`` . After you create the file system, you can decrease your file system's throughput in Provisioned Throughput mode or change between the throughput modes, with certain time restrictions. For more information, see `Specifying throughput with provisioned mode <https://docs.aws.amazon.com/efs/latest/ug/performance.html#provisioned-throughput>`_ in the *Amazon EFS User Guide* .

        Default is ``bursting`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-throughputmode
        '''
        result = self._values.get("throughput_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnMountTarget(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-efs.CfnMountTarget",
):
    '''A CloudFormation ``AWS::EFS::MountTarget``.

    The ``AWS::EFS::MountTarget`` resource is an Amazon EFS resource that creates a mount target for an EFS file system. You can then mount the file system on Amazon EC2 instances or other resources by using the mount target.

    :cloudformationResource: AWS::EFS::MountTarget
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_efs as efs
        
        cfn_mount_target = efs.CfnMountTarget(self, "MyCfnMountTarget",
            file_system_id="fileSystemId",
            security_groups=["securityGroups"],
            subnet_id="subnetId",
        
            # the properties below are optional
            ip_address="ipAddress"
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        security_groups: typing.Sequence[builtins.str],
        subnet_id: builtins.str,
        ip_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::EFS::MountTarget``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param file_system_id: The ID of the file system for which to create the mount target.
        :param security_groups: Up to five VPC security group IDs, of the form ``sg-xxxxxxxx`` . These must be for the same VPC as subnet specified.
        :param subnet_id: The ID of the subnet to add the mount target in. For file systems that use One Zone storage classes, use the subnet that is associated with the file system's Availability Zone.
        :param ip_address: Valid IPv4 address within the address range of the specified subnet.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa05dafb8813747da25c5c74e3d4e3f7f0b3bb19544dc3215eb99fbaad99ee7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnMountTargetProps(
            file_system_id=file_system_id,
            security_groups=security_groups,
            subnet_id=subnet_id,
            ip_address=ip_address,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef2cefbb784feb3896a02884f29ec9d7867360cef52622ca2287a936159828d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8abb74bc99ebcb904c6ddde294e4b9f1851e66d259a4bf3b255790a1e1487f0)
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
        '''The ID of the Amazon EFS file system that the mount target provides access to.

        Example: ``fs-0123456789111222a``

        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property
    @jsii.member(jsii_name="attrIpAddress")
    def attr_ip_address(self) -> builtins.str:
        '''The IPv4 address of the mount target.

        Example: 192.0.2.0

        :cloudformationAttribute: IpAddress
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrIpAddress"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''The ID of the file system for which to create the mount target.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-filesystemid
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd95cb1b660377ac5b6c5a6ef5a6849e51f353de1c64e2c5ee9d04549e8349fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileSystemId", value)

    @builtins.property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        '''Up to five VPC security group IDs, of the form ``sg-xxxxxxxx`` .

        These must be for the same VPC as subnet specified.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-securitygroups
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0c38cab14d9120924ee08ed8a79f9f48482e3e9dade2a0e7e009faf5474167a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroups", value)

    @builtins.property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        '''The ID of the subnet to add the mount target in.

        For file systems that use One Zone storage classes, use the subnet that is associated with the file system's Availability Zone.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-subnetid
        '''
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a561fff3665a19c75b853583c37d9fc01cafb96b56841b2f8a802fd6471af6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetId", value)

    @builtins.property
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> typing.Optional[builtins.str]:
        '''Valid IPv4 address within the address range of the specified subnet.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-ipaddress
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipAddress"))

    @ip_address.setter
    def ip_address(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94159faf88cb9bc110e818fc904943e54c72c10e46eab9e69f21c7021ce57a7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipAddress", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.CfnMountTargetProps",
    jsii_struct_bases=[],
    name_mapping={
        "file_system_id": "fileSystemId",
        "security_groups": "securityGroups",
        "subnet_id": "subnetId",
        "ip_address": "ipAddress",
    },
)
class CfnMountTargetProps:
    def __init__(
        self,
        *,
        file_system_id: builtins.str,
        security_groups: typing.Sequence[builtins.str],
        subnet_id: builtins.str,
        ip_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnMountTarget``.

        :param file_system_id: The ID of the file system for which to create the mount target.
        :param security_groups: Up to five VPC security group IDs, of the form ``sg-xxxxxxxx`` . These must be for the same VPC as subnet specified.
        :param subnet_id: The ID of the subnet to add the mount target in. For file systems that use One Zone storage classes, use the subnet that is associated with the file system's Availability Zone.
        :param ip_address: Valid IPv4 address within the address range of the specified subnet.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_efs as efs
            
            cfn_mount_target_props = efs.CfnMountTargetProps(
                file_system_id="fileSystemId",
                security_groups=["securityGroups"],
                subnet_id="subnetId",
            
                # the properties below are optional
                ip_address="ipAddress"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88cb86671d700ae1b843a22e6bc420a8f848ee6ceed3ff82e81802f64cbbd424)
            check_type(argname="argument file_system_id", value=file_system_id, expected_type=type_hints["file_system_id"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
            check_type(argname="argument ip_address", value=ip_address, expected_type=type_hints["ip_address"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "file_system_id": file_system_id,
            "security_groups": security_groups,
            "subnet_id": subnet_id,
        }
        if ip_address is not None:
            self._values["ip_address"] = ip_address

    @builtins.property
    def file_system_id(self) -> builtins.str:
        '''The ID of the file system for which to create the mount target.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-filesystemid
        '''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_groups(self) -> typing.List[builtins.str]:
        '''Up to five VPC security group IDs, of the form ``sg-xxxxxxxx`` .

        These must be for the same VPC as subnet specified.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-securitygroups
        '''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_id(self) -> builtins.str:
        '''The ID of the subnet to add the mount target in.

        For file systems that use One Zone storage classes, use the subnet that is associated with the file system's Availability Zone.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-subnetid
        '''
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip_address(self) -> typing.Optional[builtins.str]:
        '''Valid IPv4 address within the address range of the specified subnet.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-ipaddress
        '''
        result = self._values.get("ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnMountTargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.FileSystemAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "security_group": "securityGroup",
        "file_system_arn": "fileSystemArn",
        "file_system_id": "fileSystemId",
    },
)
class FileSystemAttributes:
    def __init__(
        self,
        *,
        security_group: _aws_cdk_aws_ec2_67de8e8d.ISecurityGroup,
        file_system_arn: typing.Optional[builtins.str] = None,
        file_system_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties that describe an existing EFS file system.

        :param security_group: The security group of the file system.
        :param file_system_arn: The File System's Arn. Default: - determined based on fileSystemId
        :param file_system_id: The File System's ID. Default: - determined based on fileSystemArn

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_iam as iam
            
            
            imported_file_system = efs.FileSystem.from_file_system_attributes(self, "existingFS",
                file_system_id="fs-12345678",  # You can also use fileSystemArn instead of fileSystemId.
                security_group=ec2.SecurityGroup.from_security_group_id(self, "SG", "sg-123456789",
                    allow_all_outbound=False
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6182bc59f9073581131df0c99f223f7b26f8ae63ae4bb83284df32a9f9407497)
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument file_system_arn", value=file_system_arn, expected_type=type_hints["file_system_arn"])
            check_type(argname="argument file_system_id", value=file_system_id, expected_type=type_hints["file_system_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "security_group": security_group,
        }
        if file_system_arn is not None:
            self._values["file_system_arn"] = file_system_arn
        if file_system_id is not None:
            self._values["file_system_id"] = file_system_id

    @builtins.property
    def security_group(self) -> _aws_cdk_aws_ec2_67de8e8d.ISecurityGroup:
        '''The security group of the file system.'''
        result = self._values.get("security_group")
        assert result is not None, "Required property 'security_group' is missing"
        return typing.cast(_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup, result)

    @builtins.property
    def file_system_arn(self) -> typing.Optional[builtins.str]:
        '''The File System's Arn.

        :default: - determined based on fileSystemId
        '''
        result = self._values.get("file_system_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_id(self) -> typing.Optional[builtins.str]:
        '''The File System's ID.

        :default: - determined based on fileSystemArn
        '''
        result = self._values.get("file_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSystemAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.FileSystemProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "enable_automatic_backups": "enableAutomaticBackups",
        "encrypted": "encrypted",
        "file_system_name": "fileSystemName",
        "kms_key": "kmsKey",
        "lifecycle_policy": "lifecyclePolicy",
        "out_of_infrequent_access_policy": "outOfInfrequentAccessPolicy",
        "performance_mode": "performanceMode",
        "provisioned_throughput_per_second": "provisionedThroughputPerSecond",
        "removal_policy": "removalPolicy",
        "security_group": "securityGroup",
        "throughput_mode": "throughputMode",
        "vpc_subnets": "vpcSubnets",
    },
)
class FileSystemProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_67de8e8d.IVpc,
        enable_automatic_backups: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        file_system_name: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        lifecycle_policy: typing.Optional["LifecyclePolicy"] = None,
        out_of_infrequent_access_policy: typing.Optional["OutOfInfrequentAccessPolicy"] = None,
        performance_mode: typing.Optional["PerformanceMode"] = None,
        provisioned_throughput_per_second: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
        removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup] = None,
        throughput_mode: typing.Optional["ThroughputMode"] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties of EFS FileSystem.

        :param vpc: VPC to launch the file system in.
        :param enable_automatic_backups: Whether to enable automatic backups for the file system. Default: false
        :param encrypted: Defines if the data at rest in the file system is encrypted or not. Default: - If your application has the '
        :param file_system_name: The file system's name. Default: - CDK generated name
        :param kms_key: The KMS key used for encryption. This is required to encrypt the data at rest if @encrypted is set to true. Default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        :param lifecycle_policy: A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class. Default: - None. EFS will not transition files to the IA storage class.
        :param out_of_infrequent_access_policy: A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class. Default: - None. EFS will not transition files from IA storage to primary storage.
        :param performance_mode: The performance mode that the file system will operate under. An Amazon EFS file system's performance mode can't be changed after the file system has been created. Updating this property will replace the file system. Default: PerformanceMode.GENERAL_PURPOSE
        :param provisioned_throughput_per_second: Provisioned throughput for the file system. This is a required property if the throughput mode is set to PROVISIONED. Must be at least 1MiB/s. Default: - none, errors out
        :param removal_policy: The removal policy to apply to the file system. Default: RemovalPolicy.RETAIN
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic
        :param throughput_mode: Enum to mention the throughput mode of the file system. Default: ThroughputMode.BURSTING
        :param vpc_subnets: Which subnets to place the mount target in the VPC. Default: - the Vpc default strategy if not specified

        :exampleMetadata: infused

        Example::

            file_system = efs.FileSystem(self, "MyEfsFileSystem",
                vpc=ec2.Vpc(self, "VPC"),
                lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,  # files are not transitioned to infrequent access (IA) storage by default
                performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
                out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS
            )
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_67de8e8d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2391729261906e7b78bd044383f555ad2b4129f3e3dcddd67394de066c78c65a)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument enable_automatic_backups", value=enable_automatic_backups, expected_type=type_hints["enable_automatic_backups"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument file_system_name", value=file_system_name, expected_type=type_hints["file_system_name"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument lifecycle_policy", value=lifecycle_policy, expected_type=type_hints["lifecycle_policy"])
            check_type(argname="argument out_of_infrequent_access_policy", value=out_of_infrequent_access_policy, expected_type=type_hints["out_of_infrequent_access_policy"])
            check_type(argname="argument performance_mode", value=performance_mode, expected_type=type_hints["performance_mode"])
            check_type(argname="argument provisioned_throughput_per_second", value=provisioned_throughput_per_second, expected_type=type_hints["provisioned_throughput_per_second"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument throughput_mode", value=throughput_mode, expected_type=type_hints["throughput_mode"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if enable_automatic_backups is not None:
            self._values["enable_automatic_backups"] = enable_automatic_backups
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if file_system_name is not None:
            self._values["file_system_name"] = file_system_name
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if lifecycle_policy is not None:
            self._values["lifecycle_policy"] = lifecycle_policy
        if out_of_infrequent_access_policy is not None:
            self._values["out_of_infrequent_access_policy"] = out_of_infrequent_access_policy
        if performance_mode is not None:
            self._values["performance_mode"] = performance_mode
        if provisioned_throughput_per_second is not None:
            self._values["provisioned_throughput_per_second"] = provisioned_throughput_per_second
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group is not None:
            self._values["security_group"] = security_group
        if throughput_mode is not None:
            self._values["throughput_mode"] = throughput_mode
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_67de8e8d.IVpc:
        '''VPC to launch the file system in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_67de8e8d.IVpc, result)

    @builtins.property
    def enable_automatic_backups(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable automatic backups for the file system.

        :default: false
        '''
        result = self._values.get("enable_automatic_backups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.bool]:
        '''Defines if the data at rest in the file system is encrypted or not.

        :default: - If your application has the '

        :aws-cdk: /aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.
        :link: https://docs.aws.amazon.com/cdk/latest/guide/featureflags.html
        '''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def file_system_name(self) -> typing.Optional[builtins.str]:
        '''The file system's name.

        :default: - CDK generated name
        '''
        result = self._values.get("file_system_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey]:
        '''The KMS key used for encryption.

        This is required to encrypt the data at rest if @encrypted is set to true.

        :default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey], result)

    @builtins.property
    def lifecycle_policy(self) -> typing.Optional["LifecyclePolicy"]:
        '''A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class.

        :default: - None. EFS will not transition files to the IA storage class.
        '''
        result = self._values.get("lifecycle_policy")
        return typing.cast(typing.Optional["LifecyclePolicy"], result)

    @builtins.property
    def out_of_infrequent_access_policy(
        self,
    ) -> typing.Optional["OutOfInfrequentAccessPolicy"]:
        '''A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class.

        :default: - None. EFS will not transition files from IA storage to primary storage.
        '''
        result = self._values.get("out_of_infrequent_access_policy")
        return typing.cast(typing.Optional["OutOfInfrequentAccessPolicy"], result)

    @builtins.property
    def performance_mode(self) -> typing.Optional["PerformanceMode"]:
        '''The performance mode that the file system will operate under.

        An Amazon EFS file system's performance mode can't be changed after the file system has been created.
        Updating this property will replace the file system.

        :default: PerformanceMode.GENERAL_PURPOSE
        '''
        result = self._values.get("performance_mode")
        return typing.cast(typing.Optional["PerformanceMode"], result)

    @builtins.property
    def provisioned_throughput_per_second(
        self,
    ) -> typing.Optional[_aws_cdk_core_f4b25747.Size]:
        '''Provisioned throughput for the file system.

        This is a required property if the throughput mode is set to PROVISIONED.
        Must be at least 1MiB/s.

        :default: - none, errors out
        '''
        result = self._values.get("provisioned_throughput_per_second")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Size], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy]:
        '''The removal policy to apply to the file system.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]:
        '''Security Group to assign to this file system.

        :default: - creates new security group which allows all outbound traffic
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup], result)

    @builtins.property
    def throughput_mode(self) -> typing.Optional["ThroughputMode"]:
        '''Enum to mention the throughput mode of the file system.

        :default: ThroughputMode.BURSTING
        '''
        result = self._values.get("throughput_mode")
        return typing.cast(typing.Optional["ThroughputMode"], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection]:
        '''Which subnets to place the mount target in the VPC.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-efs.IAccessPoint")
class IAccessPoint(_aws_cdk_core_f4b25747.IResource, typing_extensions.Protocol):
    '''Represents an EFS AccessPoint.'''

    @builtins.property
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''The ARN of the AccessPoint.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="accessPointId")
    def access_point_id(self) -> builtins.str:
        '''The ID of the AccessPoint.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> "IFileSystem":
        '''The EFS file system.'''
        ...


class _IAccessPointProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
):
    '''Represents an EFS AccessPoint.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-efs.IAccessPoint"

    @builtins.property
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''The ARN of the AccessPoint.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property
    @jsii.member(jsii_name="accessPointId")
    def access_point_id(self) -> builtins.str:
        '''The ID of the AccessPoint.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointId"))

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> "IFileSystem":
        '''The EFS file system.'''
        return typing.cast("IFileSystem", jsii.get(self, "fileSystem"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccessPoint).__jsii_proxy_class__ = lambda : _IAccessPointProxy


@jsii.interface(jsii_type="@aws-cdk/aws-efs.IFileSystem")
class IFileSystem(
    _aws_cdk_aws_ec2_67de8e8d.IConnectable,
    _aws_cdk_core_f4b25747.IResource,
    typing_extensions.Protocol,
):
    '''Represents an Amazon EFS file system.'''

    @builtins.property
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        '''The ARN of the file system.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''The ID of the file system, assigned by Amazon EFS.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="mountTargetsAvailable")
    def mount_targets_available(self) -> _aws_cdk_core_f4b25747.IDependable:
        '''Dependable that can be depended upon to ensure the mount targets of the filesystem are ready.'''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the actions defined in actions to the given grantee on this File System resource.

        :param grantee: -
        :param actions: -
        '''
        ...


class _IFileSystemProxy(
    jsii.proxy_for(_aws_cdk_aws_ec2_67de8e8d.IConnectable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
):
    '''Represents an Amazon EFS file system.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-efs.IFileSystem"

    @builtins.property
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        '''The ARN of the file system.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemArn"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''The ID of the file system, assigned by Amazon EFS.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @builtins.property
    @jsii.member(jsii_name="mountTargetsAvailable")
    def mount_targets_available(self) -> _aws_cdk_core_f4b25747.IDependable:
        '''Dependable that can be depended upon to ensure the mount targets of the filesystem are ready.'''
        return typing.cast(_aws_cdk_core_f4b25747.IDependable, jsii.get(self, "mountTargetsAvailable"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the actions defined in actions to the given grantee on this File System resource.

        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8b9eb5699055264b11dc6386b4c013d7b3af0a8aa288c4bf4e18461a308b084)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFileSystem).__jsii_proxy_class__ = lambda : _IFileSystemProxy


@jsii.enum(jsii_type="@aws-cdk/aws-efs.LifecyclePolicy")
class LifecyclePolicy(enum.Enum):
    '''EFS Lifecycle Policy, if a file is not accessed for given days, it will move to EFS Infrequent Access.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-lifecyclepolicies
    :exampleMetadata: infused

    Example::

        file_system = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=ec2.Vpc(self, "VPC"),
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,  # files are not transitioned to infrequent access (IA) storage by default
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
            out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS
        )
    '''

    AFTER_7_DAYS = "AFTER_7_DAYS"
    '''After 7 days of not being accessed.'''
    AFTER_14_DAYS = "AFTER_14_DAYS"
    '''After 14 days of not being accessed.'''
    AFTER_30_DAYS = "AFTER_30_DAYS"
    '''After 30 days of not being accessed.'''
    AFTER_60_DAYS = "AFTER_60_DAYS"
    '''After 60 days of not being accessed.'''
    AFTER_90_DAYS = "AFTER_90_DAYS"
    '''After 90 days of not being accessed.'''


@jsii.enum(jsii_type="@aws-cdk/aws-efs.OutOfInfrequentAccessPolicy")
class OutOfInfrequentAccessPolicy(enum.Enum):
    '''EFS Out Of Infrequent Access Policy, if a file is accessed given times, it will move back to primary storage class.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-lifecyclepolicy.html#cfn-efs-filesystem-lifecyclepolicy-transitiontoprimarystorageclass
    :exampleMetadata: infused

    Example::

        file_system = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=ec2.Vpc(self, "VPC"),
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,  # files are not transitioned to infrequent access (IA) storage by default
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
            out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS
        )
    '''

    AFTER_1_ACCESS = "AFTER_1_ACCESS"
    '''After 1 access.'''


@jsii.enum(jsii_type="@aws-cdk/aws-efs.PerformanceMode")
class PerformanceMode(enum.Enum):
    '''EFS Performance mode.

    :see: https://docs.aws.amazon.com/efs/latest/ug/performance.html#performancemodes
    :exampleMetadata: infused

    Example::

        file_system = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=ec2.Vpc(self, "VPC"),
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,  # files are not transitioned to infrequent access (IA) storage by default
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
            out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS
        )
    '''

    GENERAL_PURPOSE = "GENERAL_PURPOSE"
    '''General Purpose is ideal for latency-sensitive use cases, like web serving environments, content management systems, home directories, and general file serving.

    Recommended for the majority of Amazon EFS file systems.
    '''
    MAX_IO = "MAX_IO"
    '''File systems in the Max I/O mode can scale to higher levels of aggregate throughput and operations per second.

    This scaling is done with a tradeoff
    of slightly higher latencies for file metadata operations.
    Highly parallelized applications and workloads, such as big data analysis,
    media processing, and genomics analysis, can benefit from this mode.
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-efs.PosixUser",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
)
class PosixUser:
    def __init__(
        self,
        *,
        gid: builtins.str,
        uid: builtins.str,
        secondary_gids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Represents the PosixUser.

        :param gid: The POSIX group ID used for all file system operations using this access point.
        :param uid: The POSIX user ID used for all file system operations using this access point.
        :param secondary_gids: Secondary POSIX group IDs used for all file system operations using this access point. Default: - None

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ec2 as ec2
            import aws_cdk.aws_efs as efs
            
            
            # create a new VPC
            vpc = ec2.Vpc(self, "VPC")
            
            # create a new Amazon EFS filesystem
            file_system = efs.FileSystem(self, "Efs", vpc=vpc)
            
            # create a new access point from the filesystem
            access_point = file_system.add_access_point("AccessPoint",
                # set /export/lambda as the root of the access point
                path="/export/lambda",
                # as /export/lambda does not exist in a new efs filesystem, the efs will create the directory with the following createAcl
                create_acl=efs.Acl(
                    owner_uid="1001",
                    owner_gid="1001",
                    permissions="750"
                ),
                # enforce the POSIX identity so lambda function will access with this identity
                posix_user=efs.PosixUser(
                    uid="1001",
                    gid="1001"
                )
            )
            
            fn = lambda_.Function(self, "MyLambda",
                # mount the access point to /mnt/msg in the lambda runtime environment
                filesystem=lambda_.FileSystem.from_efs_access_point(access_point, "/mnt/msg"),
                runtime=lambda_.Runtime.NODEJS_16_X,
                handler="index.handler",
                code=lambda_.Code.from_asset(path.join(__dirname, "lambda-handler")),
                vpc=vpc
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cba347ea413fd8937262ff7e748fa10bb9ee4969c4f156658c67708c19e04e0c)
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument secondary_gids", value=secondary_gids, expected_type=type_hints["secondary_gids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gid": gid,
            "uid": uid,
        }
        if secondary_gids is not None:
            self._values["secondary_gids"] = secondary_gids

    @builtins.property
    def gid(self) -> builtins.str:
        '''The POSIX group ID used for all file system operations using this access point.'''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> builtins.str:
        '''The POSIX user ID used for all file system operations using this access point.'''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secondary_gids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Secondary POSIX group IDs used for all file system operations using this access point.

        :default: - None
        '''
        result = self._values.get("secondary_gids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PosixUser(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-efs.ThroughputMode")
class ThroughputMode(enum.Enum):
    '''EFS Throughput mode.

    :see: https://docs.aws.amazon.com/efs/latest/ug/performance.html#throughput-modes
    '''

    BURSTING = "BURSTING"
    '''This mode on Amazon EFS scales as the size of the file system in the standard storage class grows.'''
    PROVISIONED = "PROVISIONED"
    '''This mode can instantly provision the throughput of the file system (in MiB/s) independent of the amount of data stored.'''


@jsii.implements(IAccessPoint)
class AccessPoint(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-efs.AccessPoint",
):
    '''Represents the AccessPoint.

    :exampleMetadata: infused

    Example::

        efs.AccessPoint.from_access_point_attributes(self, "ap",
            access_point_id="fsap-1293c4d9832fo0912",
            file_system=efs.FileSystem.from_file_system_attributes(self, "efs",
                file_system_id="fs-099d3e2f",
                security_group=ec2.SecurityGroup.from_security_group_id(self, "sg", "sg-51530134")
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        file_system: IFileSystem,
        create_acl: typing.Optional[typing.Union[Acl, typing.Dict[builtins.str, typing.Any]]] = None,
        path: typing.Optional[builtins.str] = None,
        posix_user: typing.Optional[typing.Union[PosixUser, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param file_system: The efs filesystem.
        :param create_acl: Specifies the POSIX IDs and permissions to apply when creating the access point's root directory. If the root directory specified by ``path`` does not exist, EFS creates the root directory and applies the permissions specified here. If the specified ``path`` does not exist, you must specify ``createAcl``. Default: - None. The directory specified by ``path`` must exist.
        :param path: Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system. Default: '/'
        :param posix_user: The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point. Specify this to enforce a user identity using an access point. Default: - user identity not enforced
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bfaf5991e048872f26df3c8055d79b68136bb642f4170131634ecf20e7a6d82)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AccessPointProps(
            file_system=file_system,
            create_acl=create_acl,
            path=path,
            posix_user=posix_user,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccessPointAttributes")
    @builtins.classmethod
    def from_access_point_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_point_arn: typing.Optional[builtins.str] = None,
        access_point_id: typing.Optional[builtins.str] = None,
        file_system: typing.Optional[IFileSystem] = None,
    ) -> IAccessPoint:
        '''Import an existing Access Point by attributes.

        :param scope: -
        :param id: -
        :param access_point_arn: The ARN of the AccessPoint One of this, or {@link accessPointId} is required. Default: - determined based on accessPointId
        :param access_point_id: The ID of the AccessPoint One of this, or {@link accessPointArn} is required. Default: - determined based on accessPointArn
        :param file_system: The EFS file system. Default: - no EFS file system
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dacc699deea3d03e593ea2d932e19fe7c7ef8a1d2f2d0e54803fd256bc68bb8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AccessPointAttributes(
            access_point_arn=access_point_arn,
            access_point_id=access_point_id,
            file_system=file_system,
        )

        return typing.cast(IAccessPoint, jsii.sinvoke(cls, "fromAccessPointAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromAccessPointId")
    @builtins.classmethod
    def from_access_point_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        access_point_id: builtins.str,
    ) -> IAccessPoint:
        '''Import an existing Access Point by id.

        :param scope: -
        :param id: -
        :param access_point_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2bb6a6c6521e61c7f1eae3b44253b5ee796571afde759aa34bf4c3c9cdb33a8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument access_point_id", value=access_point_id, expected_type=type_hints["access_point_id"])
        return typing.cast(IAccessPoint, jsii.sinvoke(cls, "fromAccessPointId", [scope, id, access_point_id]))

    @builtins.property
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''The ARN of the Access Point.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property
    @jsii.member(jsii_name="accessPointId")
    def access_point_id(self) -> builtins.str:
        '''The ID of the Access Point.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointId"))

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> IFileSystem:
        '''The file system of the access point.'''
        return typing.cast(IFileSystem, jsii.get(self, "fileSystem"))


@jsii.implements(IFileSystem)
class FileSystem(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-efs.FileSystem",
):
    '''The Elastic File System implementation of IFileSystem.

    It creates a new, empty file system in Amazon Elastic File System (Amazon EFS).
    It also creates mount target (AWS::EFS::MountTarget) implicitly to mount the
    EFS file system on an Amazon Elastic Compute Cloud (Amazon EC2) instance or another resource.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
    :resource: AWS::EFS::FileSystem
    :exampleMetadata: infused

    Example::

        file_system = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=ec2.Vpc(self, "VPC"),
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,  # files are not transitioned to infrequent access (IA) storage by default
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
            out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_67de8e8d.IVpc,
        enable_automatic_backups: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        file_system_name: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        lifecycle_policy: typing.Optional[LifecyclePolicy] = None,
        out_of_infrequent_access_policy: typing.Optional[OutOfInfrequentAccessPolicy] = None,
        performance_mode: typing.Optional[PerformanceMode] = None,
        provisioned_throughput_per_second: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
        removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup] = None,
        throughput_mode: typing.Optional[ThroughputMode] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Constructor for creating a new EFS FileSystem.

        :param scope: -
        :param id: -
        :param vpc: VPC to launch the file system in.
        :param enable_automatic_backups: Whether to enable automatic backups for the file system. Default: false
        :param encrypted: Defines if the data at rest in the file system is encrypted or not. Default: - If your application has the '
        :param file_system_name: The file system's name. Default: - CDK generated name
        :param kms_key: The KMS key used for encryption. This is required to encrypt the data at rest if @encrypted is set to true. Default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        :param lifecycle_policy: A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class. Default: - None. EFS will not transition files to the IA storage class.
        :param out_of_infrequent_access_policy: A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class. Default: - None. EFS will not transition files from IA storage to primary storage.
        :param performance_mode: The performance mode that the file system will operate under. An Amazon EFS file system's performance mode can't be changed after the file system has been created. Updating this property will replace the file system. Default: PerformanceMode.GENERAL_PURPOSE
        :param provisioned_throughput_per_second: Provisioned throughput for the file system. This is a required property if the throughput mode is set to PROVISIONED. Must be at least 1MiB/s. Default: - none, errors out
        :param removal_policy: The removal policy to apply to the file system. Default: RemovalPolicy.RETAIN
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic
        :param throughput_mode: Enum to mention the throughput mode of the file system. Default: ThroughputMode.BURSTING
        :param vpc_subnets: Which subnets to place the mount target in the VPC. Default: - the Vpc default strategy if not specified
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92d3d4536d6792ea5ce0b682a41a05a6102543d5c2c01914607492a470109264)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FileSystemProps(
            vpc=vpc,
            enable_automatic_backups=enable_automatic_backups,
            encrypted=encrypted,
            file_system_name=file_system_name,
            kms_key=kms_key,
            lifecycle_policy=lifecycle_policy,
            out_of_infrequent_access_policy=out_of_infrequent_access_policy,
            performance_mode=performance_mode,
            provisioned_throughput_per_second=provisioned_throughput_per_second,
            removal_policy=removal_policy,
            security_group=security_group,
            throughput_mode=throughput_mode,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromFileSystemAttributes")
    @builtins.classmethod
    def from_file_system_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        security_group: _aws_cdk_aws_ec2_67de8e8d.ISecurityGroup,
        file_system_arn: typing.Optional[builtins.str] = None,
        file_system_id: typing.Optional[builtins.str] = None,
    ) -> IFileSystem:
        '''Import an existing File System from the given properties.

        :param scope: -
        :param id: -
        :param security_group: The security group of the file system.
        :param file_system_arn: The File System's Arn. Default: - determined based on fileSystemId
        :param file_system_id: The File System's ID. Default: - determined based on fileSystemArn
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95b9b09f3d3626a7f035e9c01b439af172394ba3c18db23b27052cd421e00492)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = FileSystemAttributes(
            security_group=security_group,
            file_system_arn=file_system_arn,
            file_system_id=file_system_id,
        )

        return typing.cast(IFileSystem, jsii.sinvoke(cls, "fromFileSystemAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addAccessPoint")
    def add_access_point(
        self,
        id: builtins.str,
        *,
        create_acl: typing.Optional[typing.Union[Acl, typing.Dict[builtins.str, typing.Any]]] = None,
        path: typing.Optional[builtins.str] = None,
        posix_user: typing.Optional[typing.Union[PosixUser, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> AccessPoint:
        '''create access point from this filesystem.

        :param id: -
        :param create_acl: Specifies the POSIX IDs and permissions to apply when creating the access point's root directory. If the root directory specified by ``path`` does not exist, EFS creates the root directory and applies the permissions specified here. If the specified ``path`` does not exist, you must specify ``createAcl``. Default: - None. The directory specified by ``path`` must exist.
        :param path: Specifies the path on the EFS file system to expose as the root directory to NFS clients using the access point to access the EFS file system. Default: '/'
        :param posix_user: The full POSIX identity, including the user ID, group ID, and any secondary group IDs, on the access point that is used for all file system operations performed by NFS clients using the access point. Specify this to enforce a user identity using an access point. Default: - user identity not enforced
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edd1ecc72ee90a35213180a9406dba42ccd8a6483c2cd3e704bac04b8da943ca)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        access_point_options = AccessPointOptions(
            create_acl=create_acl, path=path, posix_user=posix_user
        )

        return typing.cast(AccessPoint, jsii.invoke(self, "addAccessPoint", [id, access_point_options]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the actions defined in actions to the given grantee on this File System resource.

        :param grantee: Principal to grant right to.
        :param actions: The actions to grant.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f502ece663ee7a29a3417f9feef2576e171ed274f1b4e39025dbd49f73eb301)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_PORT")
    def DEFAULT_PORT(cls) -> jsii.Number:
        '''The default port File System listens on.'''
        return typing.cast(jsii.Number, jsii.sget(cls, "DEFAULT_PORT"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_67de8e8d.Connections:
        '''The security groups/rules used to allow network connections to the file system.'''
        return typing.cast(_aws_cdk_aws_ec2_67de8e8d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        '''The ARN of the file system.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemArn"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''The ID of the file system, assigned by Amazon EFS.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @builtins.property
    @jsii.member(jsii_name="mountTargetsAvailable")
    def mount_targets_available(self) -> _aws_cdk_core_f4b25747.IDependable:
        '''Dependable that can be depended upon to ensure the mount targets of the filesystem are ready.'''
        return typing.cast(_aws_cdk_core_f4b25747.IDependable, jsii.get(self, "mountTargetsAvailable"))


__all__ = [
    "AccessPoint",
    "AccessPointAttributes",
    "AccessPointOptions",
    "AccessPointProps",
    "Acl",
    "CfnAccessPoint",
    "CfnAccessPointProps",
    "CfnFileSystem",
    "CfnFileSystemProps",
    "CfnMountTarget",
    "CfnMountTargetProps",
    "FileSystem",
    "FileSystemAttributes",
    "FileSystemProps",
    "IAccessPoint",
    "IFileSystem",
    "LifecyclePolicy",
    "OutOfInfrequentAccessPolicy",
    "PerformanceMode",
    "PosixUser",
    "ThroughputMode",
]

publication.publish()

def _typecheckingstub__31d2dfd0f909a5229b20f9d28aaab1a43e0a4e83e4187b76f746d0a619e8eee2(
    *,
    access_point_arn: typing.Optional[builtins.str] = None,
    access_point_id: typing.Optional[builtins.str] = None,
    file_system: typing.Optional[IFileSystem] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb8a6fa3f01a86dbf38812d3501fed43e43720b0f5703852b4a4c24e7db0b4b0(
    *,
    create_acl: typing.Optional[typing.Union[Acl, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
    posix_user: typing.Optional[typing.Union[PosixUser, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edffcc913a44b02d3629783b0707de959f82da0d0edf85e3fab22e0730d80bc4(
    *,
    create_acl: typing.Optional[typing.Union[Acl, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
    posix_user: typing.Optional[typing.Union[PosixUser, typing.Dict[builtins.str, typing.Any]]] = None,
    file_system: IFileSystem,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd310f9f4745c0043bc0c8a6d1788656670a2f31bdef8b2f5f651ec9aa65039a(
    *,
    owner_gid: builtins.str,
    owner_uid: builtins.str,
    permissions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e62c8866f08bee7a6298d187937b428740c5fb81073889628c42065ed5b1f01f(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    file_system_id: builtins.str,
    access_point_tags: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnAccessPoint.AccessPointTagProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
    client_token: typing.Optional[builtins.str] = None,
    posix_user: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.PosixUserProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    root_directory: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.RootDirectoryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23e5ba755ac6cb8454d80188ca032203d2215f2d50a60413554edcdaf92d6037(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1db6beb3a5b6ed53e0fb88ef325f69677c52d37d4a8603219722364f73fd4a68(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b416810e8a2ed633e71da04f508fab61d50fc98ffb59cc33044ec0a9b6d3ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af4149744b13897ad419fc20b2d0c81b39b2e4359341d70cf74e2207aba31d5a(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnAccessPoint.AccessPointTagProperty, _aws_cdk_core_f4b25747.IResolvable]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a65468531dc8c72e6e8d318e82ab07b03911e3f6bdd209c6711932ba13eb0a2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8741273e068b108ec5b5decadda430d6ce85deac79ecba6177dd3f3e66ae94c1(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnAccessPoint.PosixUserProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f736c9f478d4b2ad636c6af507655f572a9c7d1ee83cf797edc2ee3f5b0c762(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnAccessPoint.RootDirectoryProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__130bd0a39fe0e98bccff8e80f76fc5e9127d6226a943cf47d92042b1ec59501e(
    *,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fef521b72f6014f8cb111464419bde5c2f6c9b6f6ad3a31d5bb876f1649444d(
    *,
    owner_gid: builtins.str,
    owner_uid: builtins.str,
    permissions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8af579207a8f1f6b6bbb33d4d9e58eef02ceb239703eb80864a992e6faf602d(
    *,
    gid: builtins.str,
    uid: builtins.str,
    secondary_gids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18da55ebe9d19e35cd04aee1b89e63c19a3a8f45697bd5ec5ec437d3d8bb512e(
    *,
    creation_info: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.CreationInfoProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf0f5f1b672012093431efe6e1a6a29ef2351e15ae2a01beb8b352e0bc64391(
    *,
    file_system_id: builtins.str,
    access_point_tags: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnAccessPoint.AccessPointTagProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
    client_token: typing.Optional[builtins.str] = None,
    posix_user: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.PosixUserProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    root_directory: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnAccessPoint.RootDirectoryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fea9eb820ccdf52ff60762b22d92c3b0961441cf73274573242bc46f6b9799eb(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    availability_zone_name: typing.Optional[builtins.str] = None,
    backup_policy: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnFileSystem.BackupPolicyProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    bypass_policy_lockout_safety_check: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    encrypted: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    file_system_policy: typing.Any = None,
    file_system_tags: typing.Optional[typing.Sequence[typing.Union[CfnFileSystem.ElasticFileSystemTagProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    kms_key_id: typing.Optional[builtins.str] = None,
    lifecycle_policies: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnFileSystem.LifecyclePolicyProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    performance_mode: typing.Optional[builtins.str] = None,
    provisioned_throughput_in_mibps: typing.Optional[jsii.Number] = None,
    throughput_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cdd7d09c9ed0724e3c2a2b57c9b4cb1e4ce79e5cfa64d660d5c6a47b68f3431(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e4dd4167cdea01666410a5f2f58b025d85e35402976413bee3055e71b26619(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c627d1d9c33ffa42a2b8e7be8b89ae0f703e70e099d8d002238e3c22f58bc96(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c5a414248495e9b1143202bff021dd0aa08cc762845ce18cd922ea93c461fb0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8430a2d295efc4590d0c05f0dc4b573f9ee59afb74a94903d3ccad4f0f07c331(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnFileSystem.BackupPolicyProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e51da86fabcb025a0c62a61f63d06e10c2a8a1e81121c664f4a97724ac97d0(
    value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0e7f14112a6f6e2431ddf12e846dfd47d6d9ebb0b480ee132f6451878a87272(
    value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fb381b67b0c21e5d8f12de88dbfeb66640ec4333e4ed7d0d9b7565df0209750(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a18998e585540c914630cb9579accb0a2e14450c880e520efbfaa82f2a53c25b(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnFileSystem.LifecyclePolicyProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df981c4eb3c389ea4bd8e7da4424d8187e5fd2e241e45394a483b825bd0aa65b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__690b8d52e663680a1787a47bbc298ad6783075236e2da513b492252bbb1035d3(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf59665a8a919c7fbf31b08a5d59ceeec324f663c3c9b25e2581e6b87025c24(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3fe5d84a7c5ee1607effd44bb4bd24fe479a5fe89395f15c85f233d4dbc54aa(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d59c6edcaac2f072b18a6fa229d0a535bd11d208c6550cac454073f8bf71f815(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fc98193b7297b128504a2d76d224f7f6b1a028e52f61d2e4df2941151a79b10(
    *,
    transition_to_ia: typing.Optional[builtins.str] = None,
    transition_to_primary_storage_class: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d452d278cc61aa7b50bcd54214530c05d86f040151f093342063ed26bbe81634(
    *,
    availability_zone_name: typing.Optional[builtins.str] = None,
    backup_policy: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnFileSystem.BackupPolicyProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    bypass_policy_lockout_safety_check: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    encrypted: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    file_system_policy: typing.Any = None,
    file_system_tags: typing.Optional[typing.Sequence[typing.Union[CfnFileSystem.ElasticFileSystemTagProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    kms_key_id: typing.Optional[builtins.str] = None,
    lifecycle_policies: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnFileSystem.LifecyclePolicyProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    performance_mode: typing.Optional[builtins.str] = None,
    provisioned_throughput_in_mibps: typing.Optional[jsii.Number] = None,
    throughput_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa05dafb8813747da25c5c74e3d4e3f7f0b3bb19544dc3215eb99fbaad99ee7(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    file_system_id: builtins.str,
    security_groups: typing.Sequence[builtins.str],
    subnet_id: builtins.str,
    ip_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef2cefbb784feb3896a02884f29ec9d7867360cef52622ca2287a936159828d1(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8abb74bc99ebcb904c6ddde294e4b9f1851e66d259a4bf3b255790a1e1487f0(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd95cb1b660377ac5b6c5a6ef5a6849e51f353de1c64e2c5ee9d04549e8349fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c38cab14d9120924ee08ed8a79f9f48482e3e9dade2a0e7e009faf5474167a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a561fff3665a19c75b853583c37d9fc01cafb96b56841b2f8a802fd6471af6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94159faf88cb9bc110e818fc904943e54c72c10e46eab9e69f21c7021ce57a7c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88cb86671d700ae1b843a22e6bc420a8f848ee6ceed3ff82e81802f64cbbd424(
    *,
    file_system_id: builtins.str,
    security_groups: typing.Sequence[builtins.str],
    subnet_id: builtins.str,
    ip_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6182bc59f9073581131df0c99f223f7b26f8ae63ae4bb83284df32a9f9407497(
    *,
    security_group: _aws_cdk_aws_ec2_67de8e8d.ISecurityGroup,
    file_system_arn: typing.Optional[builtins.str] = None,
    file_system_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2391729261906e7b78bd044383f555ad2b4129f3e3dcddd67394de066c78c65a(
    *,
    vpc: _aws_cdk_aws_ec2_67de8e8d.IVpc,
    enable_automatic_backups: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    file_system_name: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    lifecycle_policy: typing.Optional[LifecyclePolicy] = None,
    out_of_infrequent_access_policy: typing.Optional[OutOfInfrequentAccessPolicy] = None,
    performance_mode: typing.Optional[PerformanceMode] = None,
    provisioned_throughput_per_second: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
    removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup] = None,
    throughput_mode: typing.Optional[ThroughputMode] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8b9eb5699055264b11dc6386b4c013d7b3af0a8aa288c4bf4e18461a308b084(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cba347ea413fd8937262ff7e748fa10bb9ee4969c4f156658c67708c19e04e0c(
    *,
    gid: builtins.str,
    uid: builtins.str,
    secondary_gids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bfaf5991e048872f26df3c8055d79b68136bb642f4170131634ecf20e7a6d82(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    file_system: IFileSystem,
    create_acl: typing.Optional[typing.Union[Acl, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
    posix_user: typing.Optional[typing.Union[PosixUser, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dacc699deea3d03e593ea2d932e19fe7c7ef8a1d2f2d0e54803fd256bc68bb8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_point_arn: typing.Optional[builtins.str] = None,
    access_point_id: typing.Optional[builtins.str] = None,
    file_system: typing.Optional[IFileSystem] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2bb6a6c6521e61c7f1eae3b44253b5ee796571afde759aa34bf4c3c9cdb33a8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    access_point_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92d3d4536d6792ea5ce0b682a41a05a6102543d5c2c01914607492a470109264(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_67de8e8d.IVpc,
    enable_automatic_backups: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    file_system_name: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    lifecycle_policy: typing.Optional[LifecyclePolicy] = None,
    out_of_infrequent_access_policy: typing.Optional[OutOfInfrequentAccessPolicy] = None,
    performance_mode: typing.Optional[PerformanceMode] = None,
    provisioned_throughput_per_second: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
    removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup] = None,
    throughput_mode: typing.Optional[ThroughputMode] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95b9b09f3d3626a7f035e9c01b439af172394ba3c18db23b27052cd421e00492(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    security_group: _aws_cdk_aws_ec2_67de8e8d.ISecurityGroup,
    file_system_arn: typing.Optional[builtins.str] = None,
    file_system_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd1ecc72ee90a35213180a9406dba42ccd8a6483c2cd3e704bac04b8da943ca(
    id: builtins.str,
    *,
    create_acl: typing.Optional[typing.Union[Acl, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
    posix_user: typing.Optional[typing.Union[PosixUser, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f502ece663ee7a29a3417f9feef2576e171ed274f1b4e39025dbd49f73eb301(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
