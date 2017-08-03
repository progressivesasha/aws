#!/usr/bin/env python3

import boto3
import time
from optparse import OptionParser

asg = boto3.client('autoscaling')
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
cfs = boto3.client('cloudformation')
asgroup = asg.describe_auto_scaling_groups()

parser = OptionParser()
parser.add_option('-c', '--color', dest='color',
                  help='stack color')
parser.add_option('-s', '--shutdown', dest='instance_action', action='store_false',
                  help='shutdown instances in specified stack')
parser.add_option('-u', '--up', dest='instance_action', action='store_true',
                  help='set instances in specified stack running')
parser.add_option('-r', '--resume-processes', dest='resume', action='store_true',
                  help='resume processes suspended by shutdown() func')
options, args = parser.parse_args()
print(options)

stack_name = 'REAXYS2-'+options.color.lower()+'-WEB-'+options.color.upper()
cf_resources = cfs.list_stack_resources(StackName=stack_name)
stack_resources = cf_resources.get('StackResourceSummaries')

asg_name = [v for resource in stack_resources for k, v in resource.items() if k != 'LastUpdatedTimestamp'
            and 'REAXYS2-'+options.color.lower()+'-WEB-'+options.color.upper()+'-ReaxysWebASG' in v][0]

instances_list = [v for group in asgroup.get('AutoScalingGroups') for k, v in group.items()if k != 'CreatedTime'
                  and 'Instances' in k and ('AutoScalingGroupName', asg_name) in group.items()][0]

instance_ids = [v for instance in instances_list for k, v in instance.items() if 'InstanceId' in k]

current_min = [v for group in asgroup.get('AutoScalingGroups') for k, v in group.items()
               if k != 'CreatedTime' and 'MinSize' in k and ('AutoScalingGroupName', asg_name) in group.items()][0]

current_max = [v for group in asgroup.get('AutoScalingGroups') for k, v in group.items()
               if k != 'CreatedTime' and 'MaxSize' in k and ('AutoScalingGroupName', asg_name) in group.items()][0]

def main():
    print("AutoScaling Group name: ", asg_name)
    if options.instance_action == None:
        if options.resume == None:
            print('Specify arguments')
            return 0
        else:
            print('Resuming processes')
            resume()
    else:
        if options.resume == None:
            if options.instance_action == False:
                print("These instances state will be changed to 'stopped': ", instance_ids)
                check = input('Is it ok? y/n: ')
                if check == 'y':
                    shutdown()
                elif check == 'n':
                    print('Exiting')
                    return 0
                else:
                    print('Wrong input. Try again')
                    return 0
            elif options.instance_action == True:
                print("These instances state will be changed to 'running': ", instance_ids)
                check = input('Is it ok? y/n: ')
                if check == 'y':
                    run()
                elif check == 'n':
                    print('Exiting')
                    return 0
                else:
                    print('Wrong input. Try again')
                    return 0
        else:
            print('Wrong arguments')
            return 0

def resume():
    resume = asg.resume_processes(
        AutoScalingGroupName = asg_name)
    return resume

def check():
    not_passed = [i for i in instance_ids]
    check_count = 0
    if check_count < len(instance_ids):
        for iteration in range(20):
            for instance in range(len(instance_ids)):
                instance_status = [v for statuses in ec2_client.describe_instance_status(InstanceIds = instance_ids).get('InstanceStatuses') for k, v in statuses.items() if k == 'InstanceStatus' and ('InstanceId', instance_ids[instance]) in statuses.items()]
                system_status = [v for statuses in ec2_client.describe_instance_status(InstanceIds = instance_ids).get('InstanceStatuses') for k, v in statuses.items() if k == 'SystemStatus' and ('InstanceId', instance_ids[instance]) in statuses.items()]
                instance_status_value = [v for items in instance_status for k, v in items.items() if k == 'Status']
                system_status_value = [v for items in system_status for k, v in items.items() if k == 'Status']
                to_delete = instance_ids[instance]
                print('[+] ' + instance_ids[instance])
                if instance_status_value:
                    print('Instance status: {}'.format(instance_status_value))
                    print('System status: {}'.format(system_status_value))
                    if instance_status_value[0] == 'ok':
                        if system_status_value[0] == 'ok':
                            check_count += 1
                            not_passed.remove(to_delete)
                            print('Check count: {0}/{1}'.format(check_count, len(instance_ids)))
                else:
                    print('Waiting for instance status...')
                if len(not_passed) == 0 and check_count == len(instance_ids):
                    resume = asg.resume_processes(AutoScalingGroupName = asg_name)
                    print('All instances have passed status checks')
                    return resume
            time.sleep(30)
    if len(not_passed) > 0 and check_count < len(instances):
        print('Instances: {} have not passed status checks'.format(not_passed))
        print('All processes resumed - this instances will be terminated')
        resume = asg.resume_processes(AutoScalingGroupName = asg_name)
        return resume

def shutdown():
    suspend = asg.suspend_processes(
        AutoScalingGroupName = asg_name,
        ScalingProcesses = ['HealthCheck'])
    print('Instances {} state: stopping'.format(instance_ids))
    return suspend, ec2.instances.filter(InstanceIds=instance_ids).stop()

def run():
    ec2.instances.filter(InstanceIds=instance_ids).start()
    print('Please wait. Machines are bringing up')
    print('Instances {} state: running'.format(instance_ids))
    check()

main()
