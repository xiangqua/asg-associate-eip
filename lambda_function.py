import json
import boto3
import random

client = boto3.client('ec2')

def unused_eip(instance_id):
    response = client.describe_addresses()
    unused_eips_id = []
    unused_eips_ip = []
    check = list(response['Addresses'])
    #print(check)
    if not check:
        print("Elastic IP does not exist | Exiting program.....")
        exit()

    for address in response['Addresses']:
        if 'InstanceId' in address:
            if instance_id == address['InstanceId']:
                print("instance already allocated eip")
                exit()

        if 'AssociationId' not in address:
            #print('Elastic IP {} is unused'.format(address['PublicIp']))
            unused_eips_ip.append("{}".format(address['PublicIp']))
            unused_eips_id.append("{}".format(address['AllocationId']))
    print("Free eip list: ",unused_eips_ip)
    return unused_eips_id

def allocate_eip():
    try:
        response = client.allocate_address(Domain='vpc',)
        print("allocate new eip:", json.dumps(response))
    except Exception as e:
        print(e)    


def association_eip(instance_id, allocation_id):
    try:
        response = client.associate_address(AllocationId=allocation_id, InstanceId=instance_id)
        print("Boto3 api associate_address response:", json.dumps(response))
        print(instance_id + " associate to " + allocation_id + " success")
    except Exception as e:
        print(e)

    
def lambda_handler(event, context):
    #print(event)
    for message in event['Records']:
        #print(message)
        body = message['body']
        #print(body)
        message_json = json.loads(body)
        instance_id = message_json['detail']['EC2InstanceId']
        print(instance_id," need allocated Elastic IP ")
        unused_eip_count=unused_eip(instance_id)
        if  unused_eip_count== None or unused_eip_count == []:
            print("There are no unused Elastic IP,manual allocated new one!")
            allocate_eip()
            unused_eip_count=unused_eip(instance_id)
            allocation_id = random.choice(unused_eip_count)
            association_eip(instance_id,allocation_id)            
        else:
            allocation_id = random.choice(unused_eip_count)
            association_eip(instance_id,allocation_id)
