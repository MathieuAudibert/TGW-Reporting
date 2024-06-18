for tgw_id, tgw_details in data.items():
md_content += f"\n## Transit Gateway ID: {tgw_id}\n"
md_content += f"Owner: {tgw_details['Owner']} | State: {tgw_details['State']}\n\n"
for attachment in tgw_details['Attachments']:
md_content += f"### Attachment ID: {attachment['AttachmentId']} (Resource Type: {attachment['ResourceType']}, Owner: {attachment['Owner']})\n"
md_content += "| DestinationCidrBlock | TargetType | PrefixList |\n"
md_content += "|----------------------|------------|------------|\n"
for route in attachment['Routes']:
md_content += f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route.get('PrefixList', '')} |\n"
md_content += "\n"

python
Copier le code
with md_path.open('w') as f:
    f.write(md_content)
