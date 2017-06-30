import boto3

# Get the service resources
dynamodb_instance = boto3.resource('dynamodb')
# ec2_instance = boto3.resource('ec2')

# Create table
table = dynamodb_instance.create_table(
    TableName='users',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'last_name',
            'KeyType': 'RANGE'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'last_name',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until table exists
table.meta.client.get_waiter('table_exists').wait(TableName='users')

# add user
def add_item(table_name, username, last_name, position):
    table = dynamodb_instance.Table(table_name)
    response = table.put_item(
        Item={
            'username': username,
            'last_name': last_name,
            'position': position
        }
    )
    return response

# Print data
def get_table_data(table_name):
    # Get some metadata about chosen table
    table = dynamodb_instance.Table(table_name)
    return {
        'num_items': table.item_count,
        'primary_key_name': table.key_schema[0],
        'status': table.table_status,
        'bytes_size': table.table_size_bytes,
        'global_secondary_indices': table.global_secondary_indexes
    }

def scan_table(table_name, filter_key=None, filter_value=None):
    """
    Perform a scan operation on table.
    Can specify filter_key (col name) and its value to be filtered.
    """
    table = dynamodb_instance.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.scan(FilterExpression=filtering_exp)
    else:
        response = table.scan()

    return response

print ('Table created')
username = input ('We need to add a user now. Input the name: ')
last_name = input ('Set your Lastname: ')
position = input ('Who do you work as? ')
print ('You\'ve created user now. Info: ')
print (add_item('users', username, last_name, position))
print ('Checking a scan_table function. Here it is:')
print (scan_table('users'))
print (get_table_data('users'))

# Table deletion
# table = dynamodb_instance.Table('users')
# table.delete()
