import unittest
from unittest.mock import MagicMock, patch
from reporting_transit import get_attachment_cidr, get_table_routes, get_caller_identity, get_transit_gateways

class TestMain(unittest.TestCase):
    
    def test_get_caller_identity(self):
        sts_client_response = {
            'Account': '123456789012'
        }

        with patch('your_script.sts_client.get_caller_identity', return_value=sts_client_response):
            account_id = get_caller_identity()
            self.assertEqual(account_id, '123456789012')
    
    @patch('reporting_transit.ec2_client.describe_vpcs')
    def test_get_attachment_cidr_vpc(self, describe_vpcs_mock):
        describe_vpcs_mock.return_value = {
            'Vpcs': [{'VpcId': 'vpc-123', 'CidrBlock': 'cidr1'}]
        }
        
        attachment = {'ResourceId': 'vpc-123', 'ResourceType': 'vpc'}
        cidr = get_attachment_cidr(attachment)
        
        self.assertEqual(cidr, 'cidr1')

    @patch('reporting_transit.ec2_client.describe_vpn_connections')
    def test_get_attachment_cidr_vpn(self, describe_vpn_connections_mock):
        describe_vpn_connections_mock.return_value = {
            'VpnConnections': [{
                'CustomerGatewayConfiguration': {
                    'Tunnels': [{'OutsideIpAddress': 'vpn-ip'}]
                }
            }]
        }
        
        attachment = {'ResourceId': 'vpn-123', 'ResourceType': 'vpn'}
        cidr = get_attachment_cidr(attachment)
        
        self.assertEqual(cidr, 'vpn-ip')

    @patch('reporting_transit.ec2_client.describe_direct_connect_gateways')
    def test_get_attachment_cidr_direct_connect(self, describe_direct_connect_gateways_mock):
        describe_direct_connect_gateways_mock.return_value = {
            'DirectConnectGateways': [{'DirectConnectGatewayId': 'direct-connect-id'}]
        }
        
        attachment = {'ResourceId': 'direct-connect-id', 'ResourceType': 'direct-connect-gateway'}
        cidr = get_attachment_cidr(attachment)
        
        self.assertEqual(cidr, 'direct-connect-id')

    @patch('reporting_transit.ec2_client.describe_transit_gateway_route_tables')
    def test_get_table_routes(self, describe_transit_gateway_route_tables_mock):
        describe_transit_gateway_route_tables_mock.return_value = {
            'TransitGatewayRouteTables': [
                {
                    'Routes': [
                        {
                            'DestinationCidrBlock': '10.0.0.0/16',
                            'TargetType': 'transit-gateway',
                            'Target': {
                                'TransitGatewayId': 'tgw-123'
                            }
                        },
                        {
                            'DestinationCidrBlock': '192.168.0.0/24',
                            'TargetType': 'local',
                            'Target': {}
                        }
                    ]
                }
            ]
        }
        
        routes = get_table_routes('tgw-123')
        
        self.assertIsNotNone(routes)
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]['DestinationCidrBlock'], '10.0.0.0/16')
        self.assertEqual(routes[0]['TargetType'], 'transit-gateway')
        self.assertEqual(routes[0]['Target'], 'tgw-123')
        self.assertEqual(routes[1]['DestinationCidrBlock'], '192.168.0.0/24')
        self.assertEqual(routes[1]['TargetType'], 'local')
        self.assertEqual(routes[1]['Target'], 'N/A')
    
    @patch('reporting_transit.ec2_client.describe_transit_gateway_route_tables')
    def test_get_transit_gateways(self):
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

        with patch('your_script.ec2_client.describe_transit_gateways', return_value=ec2_client_tgw_response), \
            patch('your_script.ec2_client.describe_transit_gateway_attachments', return_value=ec2_client_attachment_response):
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
            self.assertEqual(attachment['Cidr'], 'cidr1')

if __name__ == '__main__':
    unittest.main()
