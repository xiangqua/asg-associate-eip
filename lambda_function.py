import json
import boto3
import random

def unused_eip():
    client = boto3.client('ec2')
    response = client.describe_addresses()
    unused_eips = []

    check = list(response['Addresses'])
    if not check:
        print("Elastic IP does not exist | Exiting program.....")
        exit()

    for address in response['Addresses']:
        #if 'AssociationId' in address:
            #print('Elastic IP  is associated with instance' )
        if 'AssociationId' not  in address:
            print('Elastic IP {} is unused'.format(address['PublicIp']))
            unused_eips.append("{}".format(address['AllocationId']))
            return unused_eips
        else:
            print("allocate new eip...")
            
def association_eip(instance_id, allocation_id):
    client = boto3.client('ec2')
    response = client.associate_address(
        AllocationId= allocation_id,
        InstanceId= instance_id
    )
    print('Change eip to  instance id: %s' % instance_id)

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    instance_id = message['detail']['EC2InstanceId']
    allocation_id = random.choice(unused_eip())
    association_eip(instance_id,allocation_id)
