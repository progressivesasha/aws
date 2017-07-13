#!/usr/bin/env python3

import boto3
from optparse import OptionParser

asg = boto3.client('autoscaling')
asgroup = asg.describe_auto_scaling_groups()

parser = OptionParser()
parser.add_option('-c', '--color', dest='color',
                  help='stack color')
parser.add_option('-d', '--desired-capacity', dest='desired_capacity',
                  default=1, type=int, # set default here
                  help='desired capacity for stack')
parser.add_option('--min', dest='min',
                  default=1, type=int, # set default here
                  help='minimal number of instances in stack')
parser.add_option('--max', dest='max',
                  default=3, type=int, # set default here
                  help='maximum number of instances in stack')

options, args = parser.parse_args()
print(options)

# Number in [brackets] depends on stack order, I've deployed green stack first, then blue.
# That's why in stack list it has [1] position.
# [green] has position[0] | blue -> [green] | [blue, green] has position[1]

asg_blue_name = asgroup.get('AutoScalingGroups', [{}])[0].get('AutoScalingGroupName', '') 
asg_green_name = asgroup.get('AutoScalingGroups', [{}])[1].get('AutoScalingGroupName', '')

def scaler(color):
    asgname = ''
    if color == 'green':
        asgname = asg_green_name
    elif color == 'blue':
        asgname = asg_blue_name
    new = asg.update_auto_scaling_group(
        AutoScalingGroupName = asgname,
        MinSize = options.min,
        MaxSize = options.max,
        DesiredCapacity = options.desired_capacity)
    print('Autoscaling group name: ', asgname)
    print('MinSize changed to %s' % options.min)
    print('MaxSize changed to %s' % options.max)
    print('DesiredCapacity changed to %s' % options.desired_capacity)
    return new

scaler(options.color)
