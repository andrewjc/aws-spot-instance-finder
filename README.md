# aws-spot-instance-finder
Find the cheapest spot instance across any region

```
usage: finder.py [-h] [-c CPU] [-m MEM] [--region REGION] [--cheapest]
                 [--single] [--product PRODUCT]

AWS Spot Instance Finder

optional arguments:
  -h, --help         show this help message and exit
  -c CPU, --cpu CPU  Minimum number of vCPUs
  -m MEM, --mem MEM  Minimum amount of memory
  --region REGION    Specify single region, or 'all'
  --cheapest         Display a table of cheapest prices for all matching
                     instances
  --single           Display the single cheapest spot price matching the
                     instance requirements
  --product PRODUCT  The product to search for, defaults to 'Linux/UNIX'

Author: andrew.cranston@gmail.com
```

## Quick Usage ##

<b>Find the single cheapest price for an instance with more than 48 vCPUs and 256GB of ram:</b>

```
$ finder.py -c 48 -m 256 --single

AWS Spot Instance Finder
Finding single cheapest instance(s) with 32 vCPUs and 256gb ram.

Querying 18 regions...................
Query Complete!

| Instance Type   | Availability Zone   |   Price |   vCPUs |   Ram |
|-----------------+---------------------+---------+---------+-------|
| r5n.12xlarge    | us-east-2c          |  0.5017 |      48 |   384 |

...
```

<b>Display only the cheapest prices of instances more than 48 vCPUs and 256GB of ram:</b>

```
$ finder.py -c 48 -m 256 --cheapest

AWS Spot Instance Finder
Finding cheapest instance(s) with 32 vCPUs and 256gb ram.

Querying 18 regions...................
Query Complete!

| Instance Type   | Availability Zone   |   Price |   vCPUs |   Ram |
|-----------------+---------------------+---------+---------+-------|
| r5n.12xlarge    | us-east-2c          |  0.5017 |      48 |   384 |
| m5.24xlarge     | us-east-2b          |  0.9862 |      96 |   384 |
| i3en.12xlarge   | us-east-1a          |  1.6272 |      48 |   384 |
| i3en.metal      | us-east-1a          |  3.2544 |      96 |   768 |
| x1e.16xlarge    | us-east-1a          |  4.0032 |      64 |  1952 |
| r5n.24xlarge    | us-east-2c          |  1.0034 |      96 |   768 |
| r5d.24xlarge    | us-east-2c          |  1.0069 |      96 |   768 |
| x1.16xlarge     | us-east-1c          |  2.0007 |      64 |   976 |
| r5.metal        | us-east-2c          |  0.6689 |      96 |   768 |
| r5a.24xlarge    | ap-south-1a         |  1.394  |      96 |   768 |
| g3.16xlarge     | us-east-1a          |  1.368  |      64 |   488 |
| i3en.24xlarge   | us-east-1a          |  3.2544 |      96 |   768 |
| m5d.24xlarge    | us-east-2c          |  0.9578 |      96 |   384 |

```

<b>Display all instance prices with more than 48 vCPUs and 256GB of ram:</b>

```
$ finder.py -c 48 -m 256

AWS Spot Instance Finder
Finding all instance(s) with 32 vCPUs and 256gb ram.

Querying 18 regions...................
Query Complete!

| Instance Type   | Availability Zone   |   Price |   vCPUs |   Ram |
|-----------------+---------------------+---------+---------+-------|
| r5n.12xlarge    | us-east-2c          |  0.5017 |      48 |   384 |
| r5n.12xlarge    | us-east-2b          |  0.5017 |      48 |   384 |
...
| m5.24xlarge     | us-east-2b          |  0.9862 |      96 |   384 |
| m5.24xlarge     | us-east-2c          |  1.2018 |      96 |   384 |
| m5.24xlarge     | us-east-2a          |  1.2304 |      96 |   384 |

...
```


<b>Limit search of instance to particular region:</b>

```
$ finder.py -c 48 -m 256 --region ap-southeast-1

AWS Spot Instance Finder
Finding single cheapest instance(s) with 32 vCPUs and 256gb ram.

Querying 1 regions..
Query Complete!

| Instance Type   | Availability Zone   |   Price |   vCPUs |   Ram |
|-----------------+---------------------+---------+---------+-------|
| r5n.12xlarge    | ap-southeast-1c     |  0.8222 |      48 |   384 |

...
```

