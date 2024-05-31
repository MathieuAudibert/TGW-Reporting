#!bin/usr/env/ python

import json
import boto3
import pandas as pd
import pathlib as Path
import subprocess

a = input('AWS profile used :')
subprocess.run([f"set AWS_PROFILE=", a])

botoSession = boto3.Session()
dc_client = botoSession.client('directconnect')
sts_client = boto3.client('sts')
ec2_client = boto3.client('ec2')

def get_caller_identity():
    try:
        res = sts_client.get_caller_identity()
        account_id = res['Account']
        return account_id
    except Exception as e:
        print(str(e))
        return None

def get_route_table_id(tgw_id):
    try:
        res = ...
        rt_id = ...
        return rt_id
    except Exception as e:
        print(str(e))
        return None
    
def get_route_tables(tgw_id):
    try:
        res = ec2_client.search_transit_gateway_routes(
            TransitGatewayRouteTableId = get_route_table_id(tgw_id),
            Filter = [
                {
                    'Name': 'transit-gateway-id',
                    'Values': [tgw_id]
                }
            ]
        )

        routes = []
        for route in res['Routes']:
            routes.append(
                {
                    'DestinationCidrBlock': route['DestinationCidrBlock'],
                    'TargetType': route['Type'], 
                    'PrefixList': route['PrefixListId']
                }
            )

        return routes
    except Exception as e:
        print(str(e))
        return None
    
def get_transit_gateways(account_id, region):
    try:
        res = ec2_client.describe_transit_gateways()
        transit_gateways = {}
        for tgw in res['TransitGateways']:
            tgw_id = tgw['TransitGatewayId']
            tgw_details =
            {
                'Owner': tgw['OwnerId'],
                'State': tgw['State']
            }

            attachments = ec2_client.describe_transit_gateway_attachments(
                Filters=[
                    {
                        'Name': 'transit-gateway-id',
                        'Values': [tgw_id]
                    }
                ]
            )

            attachment_info = []
            for attachment in attachments['TransitGatewayAttachments']:
                attachment_info.append(
                    {
                        'AttachmentId': attachment['TransitGatewayAttachmentId'],
                        'ResourceType': attachment['ResourceType'],
                        'Owner': attachment['ResourceOwnerId']
                    }
                )

            tgw_details['Routes'] = get_route_tables(tgw_id)
            tgw_details['Attachments'] = attachment_info

            transit_gateways[tgw_id]= tgw_details
        return transit_gateways
    except Exception as e:
        print(str(e))
        return None
    
def to_json(data, account_name):
    filename = 'tgw_output-'+ account_name + '.json'
    home_path = str(Path.home())
    mypath = Path(home_path, filename)

    with open(mypath, 'w')as f:
        json.dump(data, f, indent=4)

def to_csv(data, account_name):
    rows = []
    for tgw_id, tgw_details in data.items():
        for route_table in tgw_details['Routes']:
            for route in route_table['Routes']:
                rows.append({
                    'TGW id': tgw_id,
                    'Owner': tgw_details['Owner'],
                    'State': tgw_details['State'],
                    'AttachmentId': tgw_details['AttachmentId'],
                    'Resource Type': tgw_details['ResourceType'],
                    'Attachment Owner': tgw_details['ResourceOwnerId'],
                    'RT': route['DestinationCidrBlock']
                })
    df = pd.DataFrame(rows)
    folderpath = Path(f'output/{account_name}')
    folderpath.mkdir(parents=True, esxist_ok=True)

    nomfich = folderpath / f'tgw_output-{account_name}.csv'
    df.to_csv(nomfich, index=False)

def to_md(data, account_name):
    rows = []
    for tgw_id, tgw_details in data.items():
        for route_table in tgw_details['Routes']:
            for route in route_table['Routes']:
                rows.append({
                    'TGW id': tgw_id,
                    'Owner': tgw_details['Owner'],
                    'State': tgw_details['State'],
                    'AttachmentId': tgw_details['AttachmentId'],
                    'Resource Type': tgw_details['ResourceType'],
                    'Attachment Owner': tgw_details['ResourceOwnerId'],
                    'RT': route['DestinationCidrBlock']
                })
    df = pd.DataFrame(rows)
    folderpath = Path(f'output/{account_name}')
    folderpath.mkdir(parents=True, esxist_ok=True)

    nomfich = folderpath / f'tgw_output-{account_name}.md'
    df.to_markdown(nomfich, index=False)

def main():
    try:
        region = botoSession.region_name
        account_id = get_caller_identity()
        transit_gateways = get_transit_gateways(account_id, region)

        tgw_rpstate = True
        to_json_rpstate = True
        to_csv_rpstate = True
        to_md_rpstate = True

        if transit_gateways:
            account_name = botoSession.profile_name
            print("\n TGW OK \n")

            try: 
                to_json(transit_gateways, account_name)
                print("\n TO JSON OK \n")

            except Exception as e:
                print("TO JSON KO")
                to_json_rpstate=False
            
            try: 
                to_csv(transit_gateways, account_name)
                print("\n TO CVS OK \n")

            except Exception as e:
                print("TO CSV KO")
                to_csv_rpstate=False

            try: 
                to_md(transit_gateways, account_name)
                print("\n TO MD OK \n")

            except Exception as e:
                print("TO MD KO")
                to_md_rpstate=False
        else:
            print("\n TGW KO \n")
            tgw_rpstate=False
        
        if (tgw_rpstate!=False) of ((to_json_rpstate and to_csv_rpstate and to_md_rpstate)!=False):
            print("\n Reporting OK \n")
    
    except Exception as e:
        print("Reporting KO", " ", str(e))

if __name__ == "__main__":
    main()