#!/usr/bin/env python

import os
from dotenv import load_dotenv
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import yaml
from pprint import pprint

# Load environment variables from .env file
load_dotenv()

# Get environment variables
base_url = os.getenv('UDM_URL')
username = os.getenv('UDM_USERNAME')
password = os.getenv('UDM_PASSWORD')

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
headers = {"Accept": "application/json","Content-Type": "application/json"}
data = {'username': username, 'password': password}

s = requests.Session()
r_login = s.post(f'{base_url}:443/api/auth/login', headers=headers, json=data, verify=False, timeout=1)
r_systems = s.get(f'{base_url}/proxy/network/api/s/default/stat/sta', headers=headers, verify=False, timeout=1)


networks = {}
for system in r_systems.json()["data"]:
    network = system["network"]
    name = system["hostname"]
    vlan = system["gw_vlan"]
    ip = system["ip"]
    if "name" in system:
        name = system["name"]
    if network not in networks.keys():
        networks[network] = {
            "vlan": vlan,
            "hosts": []
        }
    networks[network]["hosts"].append({
        "ip": ip,
        "name": name
    })
    
pprint(networks)



ansible_inventory = {'all': {'children': {}}}
for network_name, network in networks.items():
    hosts = network["hosts"]
    ansible_inventory['all']['children'][network_name] = {
        'hosts': {},
        'vars': {
            'vlan': network["vlan"]
        }
    }
    for host in hosts:
        ansible_inventory['all']['children'][network_name]['hosts'][host['name']] = {
            'ansible_host': host['ip']
        }

# Save to a YAML file
with open('inventory.yaml', 'w') as yaml_file:
    yaml.dump(ansible_inventory, yaml_file, default_flow_style=False, default_style='"')

print("Ansible inventory has been created successfully.")