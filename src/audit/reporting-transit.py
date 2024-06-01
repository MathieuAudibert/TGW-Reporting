#!/usr/bin/python

import json
import os
import boto3

botoSession = boto3.Session()
sts_client = botoSession.client('sts')
ec2_client = botoSession.client('ec2')

def get_caller_identity():
    """
    Get the id of the AWS account you are using
    """
    try:
        res = sts_client.get_caller_identity()
        account_id = res['Account']
        return account_id
    except Exception as e:
        print(str(e))
        return None

def get_attachment_cidr(attachment):
    """
    Return a list of the attachment CIDR for each type of attachment
    """
    attachment_id = attachment['TransitGatewayAttachmentId']
    cidrs = []
    
    try:
        if attachment['ResourceType'] == 'vpc':
            res = ec2_client.describe_vpcs(VpcIds=[attachment_id])
            if res['Vpcs']:
                for vpc in res['Vpcs']:
                    cidrs.append(vpc['CidrBlock'])
        elif attachment['ResourceType'] == 'vpn':
            res = ec2_client.describe_vpn_connections(VpnConnectionIds=[attachment_id])
            if res['VpnConnections']:
                for vpn in res['VpnConnections']:
                    tunnels = json.loads(vpn['CustomerGatewayConfiguration']).get('tunnels', [])
                    for tunnel in tunnels:
                        cidrs.append(tunnel.get('outside_ip_address', ""))
        elif attachment['ResourceType'] == 'peering':
            res = ec2_client.describe_transit_gateway_peering_attachments(TransitGatewayAttachmentIds=[attachment_id])
            if res['TransitGatewayPeeringAttachments']:
                for peering in res['TransitGatewayPeeringAttachments']:
                    peering_cidrs = peering.get('AccepterTgwInfo', {}).get('TransitGatewayCidrBlocks', [])
                    cidrs.extend(peering_cidrs)
        elif attachment['ResourceType'] == 'direct-connect-gateway':
            dc_client = botoSession.client('directconnect')
            res = dc_client.describe_direct_connect_gateways(directConnectGatewayIds=[attachment_id])
            if res['directConnectGateways']:
                for dcg in res['directConnectGateways']:
                    cidrs.append(dcg.get('directConnectGatewayId', ''))
        else:
            cidrs.append('')
    except Exception as e:
        print(str(e))
        cidrs.append('Error')

    return cidrs

def get_route_tables(tgw_id):
    """
    Returns a list of the routes destination of each TGW
    """
    try:
        res = ec2_client.describe_transit_gateway_route_tables(
            Filters=[{
                'Name': 'transit-gateway-id',
                'Values': [tgw_id]
            }]
        )

        routes_info = []
        for route_table in res['TransitGatewayRouteTables']:
            for route in route_table['Routes']:
                routes_info.append({
                    'DestinationCidrBlock': route.get('DestinationCidrBlock', ''),
                    'State': route.get('State', '')
                })
        return routes_info
    except Exception as e:
        print(str(e))
        return []

def get_transit_gateways(account_id, region):
    """
    Main function of the reporting. Creates the list of information required
    """
    botoSession = boto3.Session(region_name=region)
    ec2_client = botoSession.client('ec2')
    
    try:
        res = ec2_client.describe_transit_gateways()
        transit_gateways = {}
        for tgw in res['TransitGateways']:
            tgw_id = tgw['TransitGatewayId']
            tgw_details = {
                'Owner': tgw['OwnerId'],
                'State': tgw['State']
            }

            attachments = ec2_client.describe_transit_gateway_attachments(
                Filters=[{
                    'Name': 'transit-gateway-id',
                    'Values': [tgw_id]
                }]
            )

            attachment_info = []
            for attachment in attachments['TransitGatewayAttachments']:
                cidrs = get_attachment_cidr(attachment)
                attachment_info.append({
                    'AttachmentId': attachment['TransitGatewayAttachmentId'],
                    'ResourceType': attachment['ResourceType'],
                    'Owner': attachment['ResourceOwnerId'],
                    'Cidr': cidrs
                })

            tgw_details['Attachments'] = attachment_info
            tgw_details['Routes'] = get_route_tables(tgw_id)
            transit_gateways[tgw_id] = tgw_details
            
        return transit_gateways
    except Exception as e:
        print(str(e))
        return None

def create_folder(account_name):
    """
    Creates a folder in the /output-file for each account. Better clarity
    """
    newpath = f"output-files/{account_name}"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

def to_json(data, account_id, account_name):
    """
    Creates the output file in json
    """
    folder_path = create_folder(account_name)
    with open(f'{folder_path}/output-{account_name}.json', 'w') as f:
        json.dump({account_name: {'AccountId': account_id, 'TransitGateways': data}}, f, indent=4)

def to_r(data, account_id, account_name):
    """
    Creates the output file in R
    """
    filename = f"{account_name}/output-{account_name}.R"
    with open(filename, 'w') as f:
        f.write(f'# Transit Gateway Report for AWS Account {account_id}\n\n')
        f.write('library(jsonlite)\n\n')
        
        # Convert the data to a JSON string
        json_data = json.dumps(data, indent=4)
        
        f.write(f'report_data <- fromJSON(\'{json_data}\')\n')
        f.write('print(report_data)\n')
    
    print(f"R report saved to {filename}")

def main():
    """
    Run the script
    """
    
    region = botoSession.region_name
    account_id = get_caller_identity()
    if not account_id:
        print("No AWS account existing")
        return

    try: 
        transit_gateways = get_transit_gateways(account_id, region)
        if transit_gateways:
            account_name = botoSession.profile_name if botoSession.profile_name else "default"

            folder_path = create_folder(account_name)

            try:
                to_json(transit_gateways, account_id, folder_path)
                print("to_json OK")
                
                to_r(transit_gateways, account_id, folder_path)
                print("to_r OK")
            
            except Exception as e:
                print(str(e))
                print("to_json or to_r KO")
                
        else:
            print("No tgw found, TGW KO") 
    
        print("Transit Gateway Report OK")
    
    except Exception as e:
        print(str(e))
        return "Transit Gateway Report KO"

if __name__ == "__main__":
    main()
