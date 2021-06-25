import time
from typing import TYPE_CHECKING

import requests
from decouple import config

from tasks.command import command

if TYPE_CHECKING:
    from invoke.context import Context

CLOUDFLARE_API_TOKEN = config('CLOUDFLARE_API_TOKEN', default=None)
CLOUDFLARE_API_KEY = config('CLOUDFLARE_API_KEY', default=None)
CLOUDFLARE_EMAIL = config('CLOUDFLARE_EMAIL', default=None)
CLOUDFLARE_ZONE_ID = config('CLOUDFLARE_ZONE_ID', default=None)
SUBDOMAINS = []

PROXIED = True
IPV4_ENABLED = True
IPV6_ENABLED = True


def delete_entries(type):
    """Delete A or AAAA records for which there is no IPv4 or IPv6 connection."""
    answer = cf_api(
        f'zones/{CLOUDFLARE_ZONE_ID}/dns_records?per_page=100&type={type}',
        method='GET',
    )
    if answer is None or answer['result'] is None:
        time.sleep(5)
        return
    for record in answer['result']:
        identifier = str(record['id'])
        cf_api(f'zones/{CLOUDFLARE_ZONE_ID}/dns_records/{identifier}', method='DELETE')
        print(f'🗑️ Deleted stale record {identifier}')


def get_ips():
    if IPV4_ENABLED:
        try:
            a = requests.get('https://1.1.1.1/cdn-cgi/trace').text.split('\n')
            a.pop()
            a = dict(s.split('=') for s in a)['ip']
        except Exception:
            delete_entries('A')
    if IPV6_ENABLED:
        try:
            aaaa = requests.get('https://[2606:4700:4700::1111]/cdn-cgi/trace').text.split(
                '\n'
            )
            aaaa.pop()
            aaaa = dict(s.split('=') for s in aaaa)['ip']
        except Exception:
            delete_entries('AAAA')
    ips = {}
    if a is not None:
        ips['ipv4'] = {'type': 'A', 'ip': a}
    if aaaa is not None:
        ips['ipv6'] = {'type': 'AAAA', 'ip': aaaa}
    return ips


def commit_record(ip):
    subdomains = SUBDOMAINS
    response = cf_api(f'zones/{CLOUDFLARE_ZONE_ID}', method='GET')
    if response is None or response['result']['name'] is None:
        time.sleep(5)
        return
    base_domain_name = response['result']['name']
    ttl = 300  # default Cloudflare TTL
    for subdomain in subdomains:
        subdomain = subdomain.lower().strip()
        record = {
            'type': ip['type'],
            'name': subdomain,
            'content': ip['ip'],
            'proxied': PROXIED,
            'ttl': ttl,
        }
        dns_records = cf_api(
            f'zones/{CLOUDFLARE_ZONE_ID}/dns_records?per_page=100&type={ip["type"]}',
            method='GET',
        )
        fqdn = base_domain_name
        if subdomain:
            fqdn = f'{subdomain}.{base_domain_name}'
        identifier = None
        modified = False
        duplicate_ids = []
        if dns_records is not None:
            for r in dns_records['result']:
                if r['name'] == fqdn:
                    if identifier:
                        if r['content'] == ip['ip']:
                            duplicate_ids.append(identifier)
                            identifier = r['id']
                        else:
                            duplicate_ids.append(r['id'])
                    else:
                        identifier = r['id']
                        if (
                            r['content'] != record['content']
                            or r['proxied'] != record['proxied']
                        ):
                            modified = True
        if identifier:
            if modified:
                print(f'📡 Updating record {record}')
                response = cf_api(
                    f'zones/{CLOUDFLARE_ZONE_ID}/dns_records/{identifier}',
                    method='PUT',
                    headers={},
                    data=record,
                )
        else:
            print(f'➕ Adding new record ' + str(record))
            response = cf_api(
                f'zones/{CLOUDFLARE_ZONE_ID}/dns_records',
                method='POST',
                headers={},
                data=record,
            )
        for identifier in duplicate_ids:
            identifier = str(identifier)
            print(f'🗑️ Deleting stale record {identifier}')
            response = cf_api(
                f'zones/{CLOUDFLARE_ZONE_ID}/dns_records/{identifier}',
                method='DELETE',
            )
    return True


def cf_api(endpoint, method, headers={}, data=False):
    api_token = CLOUDFLARE_API_TOKEN
    if api_token:
        headers = {'Authorization': 'Bearer ' + api_token, **headers}
    else:
        headers = {
            'X-Auth-Email': CLOUDFLARE_EMAIL,
            'X-Auth-Key': CLOUDFLARE_API_KEY,
        }
    if data == False:
        response = requests.request(
            method, f'https://api.cloudflare.com/client/v4/{endpoint}', headers=headers
        )
    else:
        response = requests.request(
            method,
            f'https://api.cloudflare.com/client/v4/{endpoint}',
            headers=headers,
            json=data,
        )

    if response.ok:
        return response.json()
    else:
        print(f'📈 Error sending "{method}" request to "{response.url}":')
        print(response.text)
        return None


@command
def update_dns_records(context: 'Context'):
    """Update DNS records."""
    for ip in get_ips().values():
        commit_record(ip)
