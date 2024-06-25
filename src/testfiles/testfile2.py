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
            for route in attachment.get('Routes', []):
                md_content += f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route['PrefixList']} |\n"
            md_content += "\n"
    
    with open(output_md_path, 'w') as f:
        f.write(md_content)
