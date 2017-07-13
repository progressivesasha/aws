import boto3
from botocore.exceptions import *

cfs = boto3.client('cloudformation')
asg = boto3.client('autoscaling')
ec2 = boto3.client('ec2')
vpcs = ec2.describe_vpcs()
avzs = ec2.describe_availability_zones()
vpc_id = vpcs.get('Vpcs', [{}])[0].get('VpcId', '')
avzones = avzs.get('AvailabilityZones', [{}])[0].get('ZoneName', '')

def sg_create(name, color):
    global sg_id
    try:
        secgroup = ec2.create_security_group(
            GroupName = name,
            Description = 'Security group for blue and green stacks'
            )
        sg_id = secgroup['GroupId']
        print('Security Group %s created in vpc %s.' % (sg_id, vpc_id))

        ingress = ec2.authorize_security_group_ingress(
            GroupId = sg_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '89.162.139.0/24'}]}
            ])
        print('Ingress Successfully Set %s' % ingress)
    except ClientError as e:
        print(e)
    asglc_create(color, sg_id)
    return sg_id

def stack_create(color):
    cfstack = cfs.create_stack(
        StackName = 'REAXYS2-'+color.lower()+'-WEB-'+color.upper(),
        DisableRollback = False,
    )

def asglc_create(color, sg_id):
    asglc = asg.create_launch_configuration(
        LaunchConfigurationName = 'REAXYS2-RX2-FrontEnd-PROD-'+color.upper(),
        KeyName = 'work_key',
        ImageId = 'ami-9e2f0988',
        InstanceType = 't2.micro',
        SecurityGroups = [
            sg_id,
        ],
    )
    print('Launch Configuration %s created' % asglc)
    asg_create(color)

def asg_create(color):
    try:
        asgroup = asg.create_auto_scaling_group(
            AutoScalingGroupName = 'REAXYS-'+color.lower()+'-WEB-'+color.upper()+'-ReaxysWebASG-Q9WILFZOR75H',
            LaunchConfigurationName = 'REAXYS2-RX2-FrontEnd-PROD-'+color.upper(),
            AvailabilityZones=[
                avzones
            ],
            MinSize = 1,
            MaxSize = 4,
            DesiredCapacity = 2,
        )
        print('AutoScaling Group %s created' % asgroup)
        #scaleup = 
    except Exception as e:
        print(e, '-- All created instances will be deleted.')
        remover(color)

        
def remover(color):
    deleteasg = asg.delete_auto_scaling_group(
        AutoScalingGroupName = 'REAXYS-'+color.lower()+'-WEB-'+color.upper()+'-ReaxysWebASG-Q9WILFZOR75H'
    )
    deletelc = asg.delete_launch_configuration(
        LaunchConfigurationName = 'REAXYS2-RX2-FrontEnd-PROD-'+color.upper()
    )
    deletesg = ec2.delete_security_group(
        GroupId = sg_id
    )
    return deleteasg, deletelc, deletesg

def creator():
    sgname = input('Input secgroup name: ')
    stack_color = input('Input stack color: ')
    if stack_color == '':
        print('input something')
    elif stack_color == 'green' | 'blue':
        sg_create(sgname, stack_color)
    else:
        print ('try green or blue')

while True:   
    action = input('What\'s next? (c)reate new / (d)elete existing / (u)pdate existing / (e)xit: ')
    if action == 'c':
        creator()
    elif action == 'd':
        color = input('Which stack to remove? green/blue: ')
        if color == '':
            print('input something')
        elif color == 'green' | 'blue':
            remover(color)
        else:
            print('wrong input')
        print('%s stack is being deleted now' % color)
    elif action == 'u':
        print('Not available')
    elif action == 'e':
        print('exiting')
        break;
    else:
        print('wrong input.')
    
# Reference: https://boto3.readthedocs.io/en/latest/reference/services/index.html
'''
exception handler:
    try:
    --code
    except ClientError as e:
        print('an error occured. all created instances will be deleted')
        print(e.response['Error']['Code'])
        remover(color, sg_id)
'''
