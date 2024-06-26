#!/usr/bin/env python

import json
import pandas as pd
import boto3
from pathlib import Path
from typing import Dict, Any, List

def get_caller_identity(sts_client: boto3.client) -> str:
    res = sts_client.get_caller_identity()
    return res['Account']

def get_route_table_id(tgw_id: str, ec2_client: boto3.client) -> str:
    res = ec2_client.describe_transit_gateway_route_tables(
        Filters=[{
            'Name': 'transit-gateway-id',
            'Values': [tgw_id]
        }]
    )
    return res["TransitGatewayRouteTables"][0]["TransitGatewayRouteTableId"]

def get_route_tables(tgw_id: str, ec2_client: boto3.client) -> List[Dict[str, Any]]:
    rte_id = get_route_table_id(tgw_id, ec2_client)
    res = ec2_client.search_transit_gateway_routes(
        TransitGatewayRouteTableId=rte_id,
        Filters=[{"Name": "state", "Values": ["active"]}],
    )
    return [
        {
            "DestinationCidrBlock": route.get("DestinationCidrBlock", ""),
            "TargetType": route.get("TargetType", ""),
            "PrefixList": route.get("PrefixListId", ""),
        }
        for route in res.get("Routes", [])
    ]

def get_transit_gateways(ec2_client: boto3.client) -> Dict[str, Any]:
    res = ec2_client.describe_transit_gateways()
    transit_gateways = {}
    for tgw in res.get("TransitGateways", []):
        tgw_id = tgw["TransitGatewayId"]
        tgw_details = {
            "Owner": tgw["OwnerId"],
            "State": tgw["State"],
            "Attachments": [
                {
                    "AttachmentId": attachment["TransitGatewayAttachmentId"],
                    "ResourceType": attachment["ResourceType"],
                    "Owner": attachment["ResourceOwnerId"],
                    "Routes": get_route_tables(tgw_id, ec2_client),
                }
                for attachment in ec2_client.describe_transit_gateway_attachments(
                    Filters=[{"Name": "transit-gateway-id", "Values": [tgw_id]}]
                ).get("TransitGatewayAttachments", [])
            ]
        }
        transit_gateways[tgw_id] = tgw_details
    return transit_gateways

def to_json(data: Dict[str, Any], acc_name: str) -> None:
    folderpath = Path(f'output/{acc_name}')
    folderpath.mkdir(parents=True, exist_ok=True)
    filename = folderpath / f'tgw_output-{acc_name}.json'
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def to_csv(data: Dict[str, Any], acc_name: str) -> None:
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

def read_json_file(json_path: Path) -> Dict[str, Any]:
    with open(json_path, 'r') as f:
        return json.load(f)

def generate_markdown(json_data: Dict[str, Any], output_md_path: Path) -> None:
    md_content = f"""
# Reporting

## Routing
"""
    for tgw_id, tgw_details in json_data.items():
        md_content += f"\n### TGW id: {tgw_id}\n"
        md_content += f"**Owner:** {tgw_details['Owner']} | **State:** {tgw_details['State']}\n"
        for attachment in tgw_details['Attachments']:
            md_content += f"### Attachment ID: {attachment['AttachmentId']} | Resource Type: {attachment['ResourceType']} | Owner: {attachment['Owner']}\n"
            md_content += f"| Destination CIDR | Target Type | Prefix List |\n"
            md_content += f"| --- | --- | --- |\n"
            md_content += "\n".join(
                f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route['PrefixList']} |"
                for route in attachment.get('Routes', [])
            )
            md_content += "\n"
    with open(output_md_path, 'w') as f:
        f.write(md_content)

def main() -> None:
    try:
        boto_session = boto3.Session()
        sts_client = boto_session.client('sts')
        ec2_client = boto_session.client('ec2')
        acc_id = get_caller_identity(sts_client)
        print(acc_id)
        transit_gateways = get_transit_gateways(ec2_client)

        if transit_gateways:
            acc_name = boto_session.profile_name
            to_json(transit_gateways, acc_name)
            to_csv(transit_gateways, acc_name)

            script_dir = Path(__file__).parent.resolve()
            output_dir = script_dir / 'output'
            json_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.json'
            output_md_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.md'

            json_data = read_json_file(json_path)
            generate_markdown(json_data, output_md_path)

            print("\nReporting OK\n")
        else:
            print("No Transit Gateways found")

    except Exception as e:
        print("Reporting KO", str(e))

if __name__ == '__main__':
    main()
