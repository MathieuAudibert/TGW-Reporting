#!/usr/bin/env python

import json
import boto3
import pandas as pd
from pathlib import Path

def get_caller_identity():
    sts_client = boto3.client('sts')
    try: 
        res = sts_client.get_caller_identity()
        acc_id = res['Account']
        return acc_id
    except Exception as e:
        print(str(e))
        return None

def get_route_table_id(tgw_id):
    ec2_client = boto3.client('ec2')

    try:
        res = ec2_client.describe_transit_gateway_route_tables(
            Filters=[
                {
                    'Name': 'transit-gateway-id',
                    'Values': [tgw_id]
                }
            ]
        )

        if res['TransitGatewayRouteTables']:
            rte_id = res['TransitGatewayRouteTables'][0]['TransitGatewayRouteTableId']
            return rte_id
        else: 
            print('No route table found for the TGW')
            return None 
    except Exception as e:
        print(str(e))
        return None
    
def get_route_tables(tgw_id):
    ec2_client = boto3.client('ec2')

    try:
        rte_id = get_route_table_id(tgw_id)
        if not rte_id:
            return []
        
        res = ec2_client.search_transit_gateway_routes(
            TransitGatewayRouteTableId=rte_id,
            Filters=[
                {
                    'Name': 'State',
                    'Values': ['active']
                }
            ]
        )

        return [
            {
                'DestinationCidrBlock': route.get('DestinationCidrBlock', ''),
                'TargetType': route.get('TargetType', ''),
                'PrefixList': route.get('PrefixListId', ''),
            }
            for route in res.get('Routes', [])
        ]
    
    except Exception as e:
        print(str(e))
        return []

def get_transit_gateways():
    ec2_client = boto3.client('ec2')

    try:
        res = ec2_client.describe_transit_gateways()
        transit_gateways = {}

        for tgw in res.get('TransitGateways', []):
            tgw_id = tgw['TransitGatewayId']
            tgw_details = {
                'Owner': tgw['OwnerId'],
                'State': tgw['State'],
                'Attachments': [
                    {
                        'AttachmentId': attachment['TransitGatewayAttachmentId'],
                        'ResourceType': attachment['ResourceType'],
                        'Owner': attachment['ResourceOwnerId'],
                        'Routes': get_route_tables(tgw_id)
                    }
                    for attachment in ec2_client.describe_transit_gateway_attachments(
                        Filters=[
                            {
                                'Name': 'transit-gateway-id',
                                'Values': [tgw_id]
                            }
                        ]
                    ).get('TransitGatewayAttachments', [])
                ]
            }
            transit_gateways[tgw_id] = tgw_details
        
        return transit_gateways
    
    except Exception as e:
        print(str(e))
        return None
    
def to_json(data, acc_name):
    folderpath = Path(f'output/{acc_name}')
    folderpath.mkdir(parents=True, exist_ok=True)
    filename = folderpath / f'tgw_output-{acc_name}.json'

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def to_csv(data, acc_name):
    try: 
        rows = [
            {
                'TGW id': tgw_id,
                'Owner': tgw_details['Owner'],
                'State': tgw_details['State'],
                'AttachmentId': attachment['AttachmentId'],
                'Resource Type': attachment['ResourceType'],
                'Attachment Owner': attachment['Owner'],
                'Destination CIDR': route['DestinationCidrBlock'],
                'Target Type': route['TargetType'],
                'Prefix List': route['PrefixList']
            }
            for tgw_id, tgw_details in data.items()
            for attachment in tgw_details['Attachments']
            for route in attachment['Routes']
        ]
        
        df = pd.DataFrame(rows)
        folderpath = Path(f'output/{acc_name}')
        folderpath.mkdir(parents=True, exist_ok=True)

        filename = folderpath / f'tgw_output-{acc_name}.csv'
        df.to_csv(filename, index=False)
    
    except Exception as e:
        print(str(e))
        return None

#--------------------------------------------------------------------------
# Generate doc and outputs

def read_json_file(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)
    
def generate_markdown(json_data, output_md_path):
    md_content = f"""
# Reporting blablabla

# Routing
"""
    for tgw_id, tgw_details in json_data.items():
        md_content += f"\n ## TGW id: {tgw_id}\n"
        md_content += f"**Owner:** {tgw_details['Owner']} | **State:** {tgw_details['State']}\n \n"
        for attachment in tgw_details['Attachments']:
            md_content += f"## Attachment ID: {attachment['AttachmentId']} | Resource Type: {attachment['ResourceType']} | Owner: {attachment['Owner']}\n"
            md_content += f"| Destination CIDR | Target Type | Prefix List |\n"
            md_content += f"| --- | --- | --- |\n"
            md_content += "\n".join(
                f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route['PrefixList']} |"
                for route in attachment.get('Routes', [])
            )
            md_content += "\n"
    
    with open(output_md_path, 'w') as f:
        f.write(md_content)
    
def main():
    try:
        botoSession = boto3.Session()
        region = botoSession.region_name
        acc_id = get_caller_identity()
        print(acc_id, region)
        transit_gateways = get_transit_gateways()

        tgw_res = True
        to_json_res = True
        to_csv_res = True

        if transit_gateways:
            acc_name = botoSession.profile_name
            print("\n TGW OK \n")

            try:
                to_json(transit_gateways, acc_name)
                print("\n TO JSON OK \n")
            except Exception as e:
                print("TO JSON KO")
                to_json_res = False 
            
            try:
                to_csv(transit_gateways, acc_name)
                print("\n TO CSV OK \n")
            except Exception as e:
                print("TO CSV KO")
                to_csv_res = False
            
            script_dir = Path(__file__).parent.resolve()
            output_dir = script_dir / 'output'

            json_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.json'
            csv_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.csv'
            output_md_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.md'

            if not json_path.exists():
                print(f"No Json file: {json_path}")
                return 
            
            if not csv_path.exists():
                print(f"No CSV file: {csv_path}")
                return
            
            json_data = read_json_file(json_path)
            generate_markdown(json_data, output_md_path)

        else:
            print("TGW KO")
            tgw_res = False
        
        if tgw_res and to_json_res and to_csv_res:
            print("\n Reporting OK \n")

    except Exception as e: 
        print("Reporting KO", " ", str(e))

if __name__ == '__main__':
    main()
