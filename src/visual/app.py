from flask import Flask, jsonify, render_template
import boto3

app = Flask(__name__)

def get_transit_gateways():
    client = boto3.client('ec2')
    response = client.describe_transit_gateways()
    return response['TransitGateways']

@app.route('/api/transit_gateways')
def transit_gateways():
    tgw_data = get_transit_gateways()
    return jsonify(tgw_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
