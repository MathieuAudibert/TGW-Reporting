def to_csv(data, acc_name):
    try:
        rows = []

        for tgw_id, tgw_details in data.items():
            for attachment in tgw_details['Attachments']:
                for route in attachment.get('Routes', []):
                    rows.append({
                        'TGW id': tgw_id,
                        'Owner': tgw_details['Owner'],
                        'State': tgw_details['State'],
                        'AttachmentId': attachment['AttachmentId'],
                        'Resource Type': attachment['ResourceType'],
                        'Attachment Owner': attachment['Owner'],
                        'Destination CIDR': route['DestinationCidrBlock'],
                        'Target Type': route['TargetType'],
                        'Prefix List': route['PrefixList']
                    })
        
        df = pd.DataFrame(rows)
        folderpath = Path(f'output/{acc_name}')
        folderpath.mkdir(parents=True, exist_ok=True)

        filename = folderpath / f'tgw_output-{acc_name}.csv'
        df.to_csv(filename, index=False)
    
    except Exception as e:
        print(str(e))
        return None

