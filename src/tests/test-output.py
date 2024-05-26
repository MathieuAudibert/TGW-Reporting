import unittest
from unittest.mock import MagicMock, patch
import json
import os
from reporting_transit import create_folder, to_json, main

class TestOutputFiles(unittest.TestCase):
    
    @patch('reporting_transit.create_folder')
    @patch('reporting_transit.get_transit_gateways')
    @patch('reporting_transit.get_caller_identity')
    @patch('reporting_transit.botoSession')
    def test_output_json(self, mock_boto_session, mock_get_caller_identity, mock_get_transit_gateways, mock_create_folder):
        mock_boto_session.region_name = 'us-east-1'
        mock_boto_session.profile_name = 'default'
        mock_get_caller_identity.return_value = '123456789012'
        mock_get_transit_gateways.return_value = {
            'tgw-123': {
                'Owner': 'owner_id',
                'State': 'available',
                'Attachments': [
                    {
                        'AttachmentId': 'attachment_id',
                        'ResourceType': 'vpc',
                        'Owner': 'owner_id',
                        'Cidr': ['cidr1']
                    }
                ],
                'Routes': [
                    {
                        'DestinationCidrBlock': '10.0.0.0/16',
                        'State': 'active'
                    }
                ]
            }
        }
        
        mock_create_folder.return_value = 'output-files/default'
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            main()
        
            mock_file.assert_called_with('output-files/default/output-default.json', 'w')
            handle = mock_file()
            
            handle.write.assert_called_once()
            written_data = handle.write.call_args[0][0]
            data = json.loads(written_data)
            
            self.assertIn('default', data)
            self.assertEqual(data['default']['AccountId'], '123456789012')
            self.assertIn('tgw-123', data['default']['TransitGateways'])
            tgw = data['default']['TransitGateways']['tgw-123']
            self.assertEqual(tgw['Owner'], 'owner_id')
            self.assertEqual(tgw['State'], 'available')
            self.assertEqual(len(tgw['Attachments']), 1)
            self.assertEqual(tgw['Attachments'][0]['Cidr'], ['cidr1'])
            self.assertEqual(len(tgw['Routes']), 1)
            self.assertEqual(tgw['Routes'][0]['DestinationCidrBlock'], '10.0.0.0/16')

if __name__ == '__main__':
    unittest.main()
