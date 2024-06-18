Let's simplify and debug the `to_md` function. Here is the revised version to ensure it correctly writes the markdown content:

```python
import json
import pandas as pd
from pathlib import Path

def to_md(data, account_name):
    # Define the output directory and file path
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f'tgw_output-{account_name}.md'
    
    # Prepare the markdown content
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

```json
{json.dumps(data, indent=4)}
```

## Transit Gateway Routes
"""
    
    # Add the transit gateway routes information
    for tgw_id, tgw_details in data.items():
        md_content += f"\n## Transit Gateway ID: {tgw_id}\n"
        md_content += f"**Owner:** {tgw_details['Owner']} | **State:** {tgw_details['State']}\n\n"
        for attachment in tgw_details['Attachments']:
            md_content += f"### Attachment ID: {attachment['AttachmentId']} (Resource Type: {attachment['ResourceType']}, Owner: {attachment['Owner']})\n"
            md_content += "| DestinationCidrBlock | TargetType | PrefixList |\n"
            md_content += "|----------------------|------------|------------|\n"
            for route in attachment.get('Routes', []):
                md_content += f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route.get('PrefixList', '')} |\n"
            md_content += "\n"

    # Write the markdown content to the file
    with md_path.open('w') as f:
        f.write(md_content)

# Sample function call (you need to replace this with actual data and account name)
if __name__ == "__main__":
    sample_data = {
        "tgw-12345678": {
            "Owner": "123456789012",
            "State": "available",
            "Attachments": [
                {
                    "AttachmentId": "tgw-attach-1",
                    "ResourceType": "vpc",
                    "Owner": "123456789012",
                    "Routes": [
                        {
                            "DestinationCidrBlock": "10.0.0.0/16",
                            "TargetType": "vpc",
                            "PrefixList": "pl-1234"
                        }
                    ]
                }
            ]
        }
    }
    account_name = "example-account"
    to_md(sample_data, account_name)
```

### Explanation:
1. **Import Necessary Libraries**: We import `json`, `pandas`, and `Path` from `pathlib`.
2. **Define the Output Directory and File Path**: We create an output directory if it doesn't exist and define the file path for the markdown file.
3. **Prepare the Markdown Content**: We generate the markdown content with sections for the overview, features, limitations, and data.
4. **Add Transit Gateway Routes Information**: We iterate through the data dictionary, appending information about each transit gateway and its routes.
5. **Write the Markdown Content to the File**: We open the file in write mode and save the content.

This script will generate a markdown file containing the transit gateway routes information. It includes proper handling of nested data and ensures the file structure is correct.
