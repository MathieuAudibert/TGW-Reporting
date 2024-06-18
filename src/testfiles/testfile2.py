import json
import pandas as pd
from pathlib import Path
import subprocess

def read_json_file(json_path):
    with json_path.open('r') as f:
        return json.load(f)

def read_csv_file(csv_path):
    return pd.read_csv(csv_path)

def generate_markdown(json_data, csv_data, output_md_path):
    md_content = f"""
# Reporting Transit

## What is the Reporting Transit?

The Reporting Transit is a Python script designed to generate detailed reports on AWS Transit Gateways. It provides comprehensive information about transit gateways, their attachments, and associated routes, which can be vital for managing and auditing network infrastructure.

## Why Use It?

- **Centralized Information**: It consolidates data from multiple AWS accounts and regions into a single, coherent report.
- **Auditing**: Facilitates compliance and security audits by providing a clear overview of network configurations.
- **Troubleshooting**: Helps identify and resolve network issues by visualizing the transit gateway connections and routes.
- **Documentation**: Generates documentation that can be used for knowledge sharing and operational purposes.

## Key Features

- **Multi-Account Support**: Capable of assuming roles across different AWS accounts to gather comprehensive data.
- **Detailed Reports**: Provides detailed information about each transit gateway, including attachments and associated routes.
- **Multiple Output Formats**: Generates reports in JSON, CSV, and Markdown formats to suit different use cases and tools.
- **Automated**: Simplifies the process of collecting and reporting transit gateway data, saving time and reducing manual effort.

## Limitations

- **Permissions**: Requires appropriate permissions to access transit gateway information across all targeted AWS accounts and regions.
- **Regional Constraints**: Data is collected per region, which means the script must be run for each region where transit gateways are present.
- **Complexity**: The script assumes familiarity with AWS and Python, which might be a barrier for some users.

## Data

### JSON Output

The JSON output provides a detailed, structured view of the transit gateways, attachments, and routes.

<div style="border: 1px solid #ccc; padding: 10px; overflow: auto; max-height: 400px;">
    <pre style="white-space: pre-wrap; word-wrap: break-word;">{json.dumps(json_data, indent=4)}</pre>
</div>

### CSV Output

The CSV output provides a tabular view of the transit gateways, attachments, and routes, which can be easily imported into spreadsheets or databases.

<div style="border: 1px solid #ccc; padding: 10px; overflow: auto; max-height: 400px;">
    <pre style="white-space: pre-wrap; word-wrap: break-word;">{csv_data.to_csv(index=False)}</pre>
</div>

## Transit Gateway Routes
"""
    for tgw_id, tgw_details in json_data.items():
        md_content += f"\n## Transit Gateway ID: {tgw_id}\n"
        md_content += f"**Owner:** {tgw_details['Owner']} | **State:** {tgw_details['State']}\n\n"
        for attachment in tgw_details['Attachments']:
            md_content += f"### Attachment ID: {attachment['AttachmentId']} (Resource Type: {attachment['ResourceType']}, Owner: {attachment['Owner']})\n"
            md_content += "| DestinationCidrBlock | TargetType | PrefixList |\n"
            md_content += "|----------------------|------------|------------|\n"
            for route in tgw_details['Routes']:
                md_content += f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route.get('PrefixList', '')} |\n"
            md_content += "\n"

    with output_md_path.open('w') as f:
        f.write(md_content)

def main():
    account_name = 'group1'  # Replace this with the actual account name
    script_dir = Path(__file__).parent.resolve()
    output_dir = script_dir / 'output'

    json_path = output_dir / f'tgw_output-{account_name}.json'
    csv_path = output_dir / f'tgw_output-{account_name}.csv'
    output_md_path = output_dir / f'tgw_output-{account_name}.md'

    if not json_path.exists():
        print(f"JSON file not found: {json_path}")
        return

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return

    json_data = read_json_file(json_path)
    csv_data = read_csv_file(csv_path)

    generate_markdown(json_data, csv_data, output_md_path)
    print(f"Markdown file generated at {output_md_path}")

if __name__ == "__main__":
    main()
