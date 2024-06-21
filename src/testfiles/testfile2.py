
def to_json(data, account_name):
    filename = f'tgw_output-{account_name}.json'
    mypath = Path.home() / 'output' / account_name / filename
    mypath.parent.mkdir(parents=True, exist_ok=True)
    with open(mypath, 'w') as f:
        json.dump(data, f, indent=4)

def to_csv(data, account_name):
    rows = []
    for tgw_id, tgw_details in data.items():
        for attachment in tgw_details['Attachments']:
            for route in attachment['Routes']:
                rows.append({
                    'TGW ID': tgw_id,
                    'Owner': tgw_details['Owner'],
                    'State': tgw_details['State'],
                    'Attachment ID': attachment['AttachmentId'],
                    'Resource Type': attachment['ResourceType'],
                    'Attachment Owner': attachment['Owner'],
                    'Destination CIDR': route['DestinationCidrBlock'],
                    'Target Type': route['TargetType'],
                    'Prefix List': route['PrefixList']
                })
    df = pd.DataFrame(rows)
    folderpath = Path('output') / account_name
    folderpath.mkdir(parents=True, exist_ok=True)
    filename = folderpath / f'tgw_output-{account_name}.csv'
    df.to_csv(filename, index=False)
