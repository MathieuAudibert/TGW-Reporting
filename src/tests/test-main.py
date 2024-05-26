import unittest
import json
from unittest.mock import MagicMock, patch
from reporting_transit import get_attachment_cidr, get_route_tables, get_caller_identity, get_transit_gateways

class TestMain(unittest.TestCase):
    
    @patch('reporting_transit.sts_client.get_caller_identity')
    def test_get_caller_identity(self, mock_get_caller_identity):
        sts_client_response = {
            'Account': '123456789012'
        }
        mock_get_caller_identity.return_value = sts_client_response
        account_id = get_caller_identity()
        self.assertEqual(account_id, '123456789012')
    
    @patch('reporting_transit.ec2_client.describe_vpcs')
    def test_get_attachment_cidr_vpc(self, mock_describe_vpcs):
        mock_describe_vpcs.return_value = {
            'Vpcs': [{'VpcId': 'vpc-123', 'CidrBlock': 'cidr1'}]
        }
        
        attachment = {'TransitGatewayAttachmentId': 'attachment_id', 'ResourceType': 'vpc'}
        cidr = get_attachment_cidr(attachment)
        
        self.assertEqual(cidr, ['cidr1'])

    @patch('reporting_transit.ec2_client.describe_vpn_connections')
    def test_get_attachment_cidr_vpn(self, mock_describe_vpn_connections):
        mock_describe_vpn_connections.return_value = {
            'VpnConnections': [{
                'CustomerGatewayConfiguration': json.dumps({
                    'tunnels': [{'outside_ip_address': 'vpn-ip'}]
                })
            }]
        }
        
        attachment = {'TransitGatewayAttachmentId': 'vpn-123', 'ResourceType': 'vpn'}
        cidr = get_attachment_cidr(attachment)
        
        self.assertEqual(cidr, ['vpn-ip'])

    @patch('reporting_transit.botoSession.client')
    def test_get_attachment_cidr_direct_connect(self, mock_boto_session_client):
        mock_direct_connect_client = MagicMock()
        mock_direct_connect_client.describe_direct_connect_gateways.return_value = {
            'directConnectGateways': [{'directConnectGatewayId': 'direct-connect-id'}]
        }
        mock_boto_session_client.return_value = mock_direct_connect_client
        
        attachment = {'TransitGatewayAttachmentId': 'direct-connect-id', 'ResourceType': 'direct-connect-gateway'}
        cidr = get_attachment_cidr(attachment)
        
        self.assertEqual(cidr, ['direct-connect-id'])

    @patch('reporting_transit.ec2_client.describe_transit_gateway_route_tables')
    def test_get_route_tables(self, mock_describe_transit_gateway_route_tables):
        mock_describe_transit_gateway_route_tables.return_value = {
            'TransitGatewayRouteTables': [
                {
                    'Routes': [
                        {
                            'DestinationCidrBlock': '10.0.0.0/16',
                            'State': 'active'
                        },
                        {
                            'DestinationCidrBlock': '192.168.0.0/24',
                            'State': 'blackhole'
                        }
                    ]
                }
            ]
        }
        
        routes = get_route_tables('tgw-123')
        
        self.assertIsNotNone(routes)
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]['DestinationCidrBlock'], '10.0.0.0/16')
        self.assertEqual(routes[0]['State'], 'active')
        self.assertEqual(routes[1]['DestinationCidrBlock'], '192.168.0.0/24')
        self.assertEqual(routes[1]['State'], 'blackhole')
    
    @patch('reporting_transit.ec2_client.describe_transit_gateways')
    @patch('reporting_transit.ec2_client.describe_transit_gateway_attachments')
    def test_get_transit_gateways(self, mock_describe_transit_gateway_attachments, mock_describe_transit_gateways):
        ec2_client_tgw_response = {
            'TransitGateways': [
                {
                    'TransitGatewayId': 'tgw-123',
                    'OwnerId': 'owner_id',
                    'State': 'available'
                }
            ]
        }
        ec2_client_attachment_response = {
            'TransitGatewayAttachments': [
                {
                    'TransitGatewayAttachmentId': 'attachment_id',
                    'ResourceType': 'vpc',
                    'ResourceId': 'vpc-123'
                }
            ]
        }

        mock_describe_transit_gateways.return_value = ec2_client_tgw_response
        mock_describe_transit_gateway_attachments.return_value = ec2_client_attachment_response

        with patch('reporting_transit.get_attachment_cidr', return_value=['cidr1']), \
             patch('reporting_transit.get_route_tables', return_value=[
                {
                    'DestinationCidrBlock': '10.0.0.0/16',
                    'State': 'active'
                },
                {
                    'DestinationCidrBlock': '192.168.0.0/24',
                    'State': 'blackhole'
                }
             ]):
            transit_gateways = get_transit_gateways('123456789012', 'us-east-1')
            self.assertEqual(len(transit_gateways), 1)
            self.assertIn('tgw-123', transit_gateways)
            tgw_details = transit_gateways['tgw-123']
            self.assertEqual(tgw_details['Owner'], 'owner_id')
            self.assertEqual(tgw_details['State'], 'available')
            self.assertEqual(len(tgw_details['Attachments']), 1)
            attachment = tgw_details['Attachments'][0]
            self.assertEqual(attachment['AttachmentId'], 'attachment_id')
            self.assertEqual(attachment['ResourceType'], 'vpc')
            self.assertEqual(attachment['Cidr'], ['cidr1'])
            self.assertEqual(len(tgw_details['Routes']), 2)
            self.assertEqual(tgw_details['Routes'][0]['DestinationCidrBlock'], '10.0.0.0/16')
            self.assertEqual(tgw_details['Routes'][0]['State'], 'active')
            self.assertEqual(tgw_details['Routes'][1]['DestinationCidrBlock'], '192.168.0.0/24')
            self.assertEqual(tgw_details['Routes'][1]['State'], 'blackhole')

if __name__ == '__main__':
    unittest.main()
