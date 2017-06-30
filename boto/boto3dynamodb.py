import boto3

# Get the service resources
dynamodb_instance = boto3.resource('dynamodb')
# ec2_instance = boto3.resource('ec2')

def table_create(table_name, hash_attr, range_attr):
    print ('Default read/write CapacityUnits == 5. You can\'t change them.')
    print ('Creating table...')
    # Create table
    table = dynamodb_instance.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': hash_attr,
                'KeyType': 'HASH'
            },
            {
                'AttributeName': range_attr,
                'KeyType': 'RANGE'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': hash_attr,
                'AttributeType': 'S'
            },
            {
                'AttributeName': range_attr,
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until table exists
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

    print ('Table %s created' % table_name)
    user_create(table_name)


# add user
def add_item(table_name, username, last_name, position):
    table = dynamodb_instance.Table(table_name)
    response = table.put_item(
        Item={
            hash_attr: username,
            range_attr: last_name,
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

def user_create(table_name):
    while True:
        check = input ('Do you want to add a user? (y/n)? ')
        if check == 'y':
            username = input ('Input the name: ')
            last_name = input ('Set the Lastname: ')
            position = input ('Set the position: ')
            print ('You\'ve created item now. Info: ')
            add_item(table_name, username, last_name, position)
            print ('Checking a scan_table function. Here it is:')
            print (scan_table(table_name))
            print (get_table_data(table_name))
        elif check == 'n':
            print ('exiting')
            break
        else:
            print ('wrong input')

            
table_name = input ('Input table name: ')
hash_attr = input ('Define hash attribute name: ')
range_attr = input ('Define range attribute name: ')
table_create(table_name, hash_attr, range_attr)
# Table deletion
# table = dynamodb_instance.Table('users')
# table.delete()
