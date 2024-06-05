import unittest
from unittest.mock import patch, MagicMock
import boto3
from botocore.stub import Stubber
from reporting_transit import *

class TestTGWScript(unittest.TestCase):

    @patch('your_script_name.boto3.client')
    def test_get_caller_identity(self, mock_boto_client):
        sts_client = boto3.client('sts')
        with Stubber(sts_client) as stubber:
            expected_response = {'Account': '123456789012', 'UserId': 'ABCDEFGHIJKL', 'Arn': 'arn:aws:sts::123456789012:assumed-role/Admin/user'}
            stubber.add_response('get_caller_identity', expected_response)
            mock_boto_client.return_value = sts_client

            account_id = get_caller_identity(sts_client)
            self.assertEqual(account_id, '123456789012')

    @patch('your_script_name.boto3.client')
    def test_get_route_table_id(self, mock_boto_client):
        ec2_client = boto3.client('ec2')
        with Stubber(ec2_client) as stubber:
            expected_response = {
                'TransitGatewayRouteTables': [
                    {'TransitGatewayRouteTableId': 'tgw-rtb-0123456789abcdef0'}
                ]
            }
            stubber.add_response('describe_transit_gateway_route_tables', expected_response)
            mock_boto_client.return_value = ec2_client

            tgw_id = 'tgw-0123456789abcdef0'
            route_table_id = get_route_table_id(ec2_client, tgw_id)
            self.assertEqual(route_table_id, 'tgw-rtb-0123456789abcdef0')

    @patch('your_script_name.boto3.client')
    def test_get_route_tables(self, mock_boto_client):
        ec2_client = boto3.client('ec2')
        with Stubber(ec2_client) as stubber:
            describe_response = {
                'TransitGatewayRouteTables': [
                    {'TransitGatewayRouteTableId': 'tgw-rtb-0123456789abcdef0'}
                ]
            }
            search_response = {
                'Routes': [
                    {'DestinationCidrBlock': '10.0.0.0/16', 'Type': 'static', 'PrefixListId': 'pl-0123456789abcdef0'}
                ]
            }
            stubber.add_response('describe_transit_gateway_route_tables', describe_response)
            stubber.add_response('search_transit_gateway_routes', search_response)
            mock_boto_client.return_value = ec2_client

            tgw_id = 'tgw-0123456789abcdef0'
            routes = get_route_tables(ec2_client, tgw_id)
            self.assertEqual(len(routes), 1)
            self.assertEqual(routes[0]['DestinationCidrBlock'], '10.0.0.0/16')

if __name__ == '__main__':
    unittest.main()
