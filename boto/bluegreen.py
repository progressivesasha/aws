import boto3

cfs = boto3.client('cloudformation')
asg = boto3.client('autoscaling', region_name='us-east-1')
ec2 = boto3.resource('ec2')
secgroup = ec2.SecurityGroup('independentsg')

def stack_create(color):
    cfstack = cfs.create_stack(
        StackName = 'REAXYS2-'+color.lower()+'-WEB-'+color.upper(),
        DisableRollback = False,
    )
    return cfstack

def asglc_create(color):
    asglc = asg.create_launch_configuration(
        LaunchConfigurationName = 'REAXYS2-RX2-FrontEnd-PROD-'+color.upper(),
        KeyName = 'string',
        ImageId = 'ami-9e2f0988',
        InstanceType = 't2.micro',
        SecurityGroups = [
            'independentsg',
        ],
    )
    return asglc

def asg_create(color):
    asgroup = asg.create_autoscaling_group(
        AutoScalingGroupName = 'REAXYS-'+color.lower()'-WEB-'+color.upper()+'-ReaxysWebASG-Q9WILFZOR75H',
        LaunchConfigurationName = 'REAXYS2-RX2-FrontEnd-PROD-'+color.upper(),
        MinSize = 1,
        MaxSize = 4,
        DesiredCapacity = 2,
    )
    return asgroup


# Reference: https://boto3.readthedocs.io/en/latest/reference/services/index.html
