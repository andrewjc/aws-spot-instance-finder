#!.env/bin/python3
# -*- coding: ascii -*-

__author__ = 'Andrew Cranston'
__copyright__ = 'Copyright 2019 Andrew Cranston'
__license__ = 'GPL-3.0'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Cranston'
__email__ = 'andrew.cranston@gmail.com'
__status__ = 'Dev'

import boto3
import requests
import urllib3
import argparse

from datetime import datetime
from collections import namedtuple
from tabulate import tabulate
from filecache import filecache

urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='AWS Spot Instance Finder', epilog='Author: andrew.cranston@gmail.com')
parser.add_argument('-c', '--cpu', type=int, default=32, help='Minimum number of vCPUs')
parser.add_argument('-m', '--mem', type=int, default=256, help='Minimum amount of memory')
parser.add_argument('--region', type=str, default='all', help='Specify single region, or \'all\'')
parser.add_argument('--cheapest', action='store_true', help='Display a table of cheapest prices for all matching instances')
parser.add_argument('--single', action='store_true', help='Display the single cheapest spot price matching the instance requirements')
parser.add_argument('--product', type=str, default='Linux/UNIX', help='The product to search for, defaults to \'Linux/UNIX\'')

args = parser.parse_args()

min_cores = args.cpu
min_ram = args.mem
product_desc = args.product
run_mode = 'single cheapest' if args.single else 'cheapest' if args.cheapest else 'all'
arg_regions = args.region.split(',')

print(f'AWS Spot Instance Finder')
print(f'Finding {run_mode} instance(s) with {min_cores} vCPUs and {min_ram}gb ram.\n')

@filecache(24 * 60 * 60)
def get_instance_types():
    req = requests.get('https://www.ec2instances.info/instances.json', verify=False)
    json_response = req.json()
    d = {}
    for i in json_response:
        d[i['instance_type']] = {
            'cores': i['vCPU'],
            'memory': i['memory']
        }
    return d

@filecache(24 * 60 * 60)
def get_aws_regions():
    botoclient = boto3.client('ec2', 'us-east-1', verify=False)
    regions = [region['RegionName'] for region in botoclient.describe_regions()['Regions']]
    return regions

def query_regions(instances, regions, cores, ram):
    instance_table = dict(filter(lambda elem: (int(elem[1]['cores']) > min_cores) and (int(elem[1]['memory']) > min_ram), all_instances.items()))
    instance_types = list(instance_table.keys())
    for x in instance_types:
        instance_table[x]['history'] = []
        instance_table[x]['name'] = x

    for x in regions:
        print(".", flush=True, end = '')
        testconn = boto3.client('ec2', region_name=x, verify=False)

        azquery = testconn.describe_availability_zones()
        azcount = len( azquery['AvailabilityZones'] )



        response = testconn.describe_spot_price_history(
            InstanceTypes=instance_types,
            ProductDescriptions=[product_desc],
            MaxResults=(len(instance_types) * azcount)
            )

        if response is not None and response['SpotPriceHistory'] is not None and len(response['SpotPriceHistory']) > 0:
            for x in response['SpotPriceHistory']:
                instance = x['InstanceType']
                if not any(entry['AvailabilityZone'] == x['AvailabilityZone'] for entry in instance_table[instance]['history']):
                    instance_table[instance]['history'].append(x)

    return instance_table

def get_all_results(instance_table):
    result_table = []
    for x in instance_table.values():
        x['history'].sort(key=lambda k: float(k['SpotPrice']))        
        if len(x['history']) > 0:
            for y in x['history']:
                
                cheap = [x['name'], y['AvailabilityZone'], y['SpotPrice'], x['cores'], x['memory']]
                result_table.append(cheap)
    return result_table

def get_cheapest_results(instance_table):
    result_table = []
    for x in instance_table.values():
        x['history'].sort(key=lambda k: float(k['SpotPrice']))
        if len(x['history']) > 0:
            best = x['history'][0]
            x['best'] = best
            
            cheap = [x['name'], best['AvailabilityZone'], best['SpotPrice'], x['cores'], x['memory']]
            result_table.append(cheap)
    return result_table

def get_single_cheapest(instance_table):
    result_table = []
    cheapest_so_far = None
    for x in instance_table.values():
        x['history'].sort(key=lambda k: float(k['SpotPrice']))
        if len(x['history']) > 0:
            best = x['history'][0]

            cheap = [x['name'], best['AvailabilityZone'], best['SpotPrice'], x['cores'], x['memory']]

            cheapest_so_far = cheap if cheapest_so_far is None or float(best['SpotPrice']) < float(cheapest_so_far[2]) else cheapest_so_far

    result_table.append(cheapest_so_far)
    return result_table

all_instances = get_instance_types()

regions = []
if arg_regions is None or len(arg_regions) == 1 and arg_regions[0] is 'all':    
    regions = get_aws_regions()
else:
    regions = arg_regions

print(f'Querying { len(regions) } regions.', end = '')

instance_table = query_regions(all_instances, regions, min_cores, min_ram)

print('\nQuery Complete!\n')

result_table = None

if run_mode == 'all':
    result_table = get_all_results(instance_table)

if run_mode == 'cheapest':
    result_table = get_cheapest_results(instance_table)

if run_mode == 'single cheapest':
    result_table = get_single_cheapest(instance_table)

print(tabulate(result_table, headers=['Instance Type', 'Availability Zone', 'Price', 'vCPUs', 'Ram'], tablefmt="orgtbl"))
print('\n')
