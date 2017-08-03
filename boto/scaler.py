#!/usr/bin/env python3

import boto3
from optparse import OptionParser

cfs = boto3.client('cloudformation')
asg = boto3.client('autoscaling')
asgroup = asg.describe_auto_scaling_groups()

parser = OptionParser()
parser.add_option('-c', '--color', dest='color',
                  help='stack color')
parser.add_option('-d', '--desired-capacity', dest='desired_capacity',
                  type=int, help='desired capacity for stack')
parser.add_option('--min', dest='min', type=int,
                  help='minimal number of instances in stack')
parser.add_option('--max', dest='max', type=int,
                  help='maximum number of instances in stack')
options, args = parser.parse_args()
print(options)

stack_name = 'REAXYS2-'+options.color.lower()+'-WEB-'+options.color.upper()
cf_resources = cfs.list_stack_resources(StackName=stack_name)
stack_resources = cf_resources.get('StackResourceSummaries')

asg_name = [v for resource in stack_resources for k, v in resource.items() if k != 'LastUpdatedTimestamp'
            and 'REAXYS2-'+options.color.lower()+'-WEB-'+options.color.upper()+'-ReaxysWebASG' in v][0]

current_min = [v for group in asgroup.get('AutoScalingGroups') for k, v in group.items()
               if k != 'CreatedTime' and 'MinSize' in k and ('AutoScalingGroupName', asg_name) in group.items()][0]

current_max = [v for group in asgroup.get('AutoScalingGroups') for k, v in group.items()
               if k != 'CreatedTime' and 'MaxSize' in k and ('AutoScalingGroupName', asg_name) in group.items()][0]

current_descap = [v for group in asgroup.get('AutoScalingGroups') for k, v in group.items()
                  if k != 'CreatedTime' and 'DesiredCapacity' in k
                  and ('AutoScalingGroupName', asg_name) in group.items()][0]


def scaler(color):
    if not options.min:
        if not options.max:
            if not options.desired_capacity:
                minsize = current_min
                maxsize = current_max
                descap = current_descap
            else:
                minsize = current_min
                maxsize = current_max
                descap = options.desired_capacity
        else:
            if not options.desired_capacity:
                minsize = current_min
                descap = current_descap
                maxsize = options.max
            else:
                minsize = current_min
                maxsize = options.max
                descap = options.desired_capacity
    else:
        if not options.max:
            if not options.desired_capacity:
                maxsize = current_max
                descap = current_descap
                minsize = options.min
            else:
                maxsize = current_max
                minsize = options.min
                descap = options.desired_capacity
        else:
            if not options.desired_capacity:
                descap = current_descap
                minsize = options.min
                maxsize = options.max
            else:
                minsize = options.min
                maxsize = options.max
                descap = options.desired_capacity
    
    print('Stack Name: ', stack_name)
    print('Autoscaling group name: ', asg_name)
    print("MinSize '{0}' ==> '{1}'".format(current_min, minsize))
    print("MaxSize '{0}' ==> '{1}'".format(current_max, maxsize))
    print("DesiredCapacity '{0}' ==> '{1}'".format(current_descap, descap))
    check = input('Is it right? y/n: ').lower()
    if check == 'y':
        new = asg.update_auto_scaling_group(
            AutoScalingGroupName = asg_name,
            MinSize = minsize,
            MaxSize = maxsize,
            DesiredCapacity = descap)
        print('Autoscaling group updated')
        return new
    elif check == 'n':
        print('Exiting')
        return 0
    else:
        print('Wrong input. Try again')
        return 0

scaler(options.color)
current_resource = cfs.describe_stack_resource(StackName=stack_name, LogicalResourceId = 'ReaxysWebASG')
