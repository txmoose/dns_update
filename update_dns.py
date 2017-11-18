#!/usr/bin/env python3
"""
Script to check external IP address and update CloudFlare zones accordingly
"""

import CloudFlare
import requests
from config import *


cf = CloudFlare.CloudFlare(email=CF_EMAIL, token=CF_TOKEN)


def extract_domain(record):
    """
    Helper function to get domain from a whole dns record
    :param record: whole dns record as a string
    :return: apex domain as a string
    """
    return '.'.join(record.split('.')[-2:])

def get_zone_id(domain):
    """
    Helper function to get zone ID from Cloudflare
    :param record: Cloudflare Zone as a string
    :return: zone ID as a string
    """
    zones = cf.zones.get()

    for zone in zones:
        if zone['name'] == domain:
            return zone['id']

def get_current_ip():
    """
    Function to get external IP address
    :return: External IP address as a string
    """
    r = requests.get(GET_IP_URL)
    return r.text.strip('\n')


def get_current_dns(record):
    """
    Function to get current content of specific DNS record
    :param record: record to get content of as a String
    :return: content of record as a String
    """
    domain = extract_domain(record)
    zone_id = get_zone_id(domain)

    dns_records = cf.zones.dns_records.get(zone_id)

    for dns_record in dns_records:
        if dns_record['name'] == record:
            return dns_record['content']


def update_dns(record, new_ip):
    """
    Function to update CloudFlare Zones if
    external IP is not the same
    :return:
    """
    domain = extract_domain(record)
    zone_id = get_zone_id(domain)

    dns_records = cf.zones.dns_records.get(zone_id)

    for dns_record in dns_records:
        if dns_record['name'] == record:
            updated_record = dns_record
            record_id = dns_record['id']

    updated_record['content'] = new_ip

    d = cf.zones.dns_records.delete(zone_id, record_id)
    r = cf.zones.dns_records.post(zone_id, data=updated_record)



def main():
    # TODO: Add logging
    # TODO: Add email notifications when updates are made
    records_to_check = ['home.brieden.org', 'cloud.txmoose.com', 'home.txmoose.com']
    current_ip = get_current_ip()

    for record_to_check in records_to_check:
        if get_current_dns(record_to_check) != current_ip:
            update_dns(record_to_check, current_ip)
            print("Updated {}".format(record_to_check))
        else:
            print("Records match")


if __name__ == '__main__':
    main()
