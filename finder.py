#!./env/bin/python3

import boto3
import requests
import pandas as pd
from datetime import datetime
from collections import namedtuple
from boto.pyami.config import Config
from tabulate import tabulate


min_cores = 96
min_ram = 256
max_expected_azs = 4

option_show_all = False
option_show_best = True

botoclient = boto3.client('ec2', 'us-east-1', verify=False)
regions = [region['RegionName'] for region in botoclient.describe_regions()['Regions']]

req = requests.get('https://www.ec2instances.info/instances.json', verify=False)
json_response = req.json()
d = {}
for i in json_response:
    d[i['instance_type']] = {
        'cores': i['vCPU'],
        'memory': i['memory']
    }

instance_table = dict(filter(lambda elem: (int(elem[1]['cores']) > min_cores), d.items()))
instance_table = dict(filter(lambda elem: (int(elem[1]['memory']) > min_ram), d.items()))
instance_types = list(instance_table.keys())
for x in instance_types:
    instance_table[x]['history'] = []

regions = ['us-east-1']

for x in regions:
    testconn = boto3.client('ec2', region_name=x, verify=False)
    response = testconn.describe_spot_price_history(
        InstanceTypes=instance_types,
        ProductDescriptions=['Linux/UNIX'],
        MaxResults=(len(instance_types) * max_expected_azs)
        )

    if response is not None and response['SpotPriceHistory'] is not None and len(response['SpotPriceHistory']) > 0:
        for x in response['SpotPriceHistory']:
            instance = x['InstanceType']
            if not any(entry['AvailabilityZone'] == x['AvailabilityZone'] for entry in instance_table[instance]['history']):
                instance_table[instance]['history'].append(x)


# Loop through each instance and find the cheapest instance price
for x in instance_table.values():
    x['history'].sort(key=lambda k: float(k['SpotPrice']))
    if len(x['history']) > 0:
        x['best'] = x['history'][0]
