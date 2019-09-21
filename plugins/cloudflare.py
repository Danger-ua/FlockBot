import requests
import json
import utilslib

config = utilslib.load_config()['cf']

cf_zone_link = 'https://api.cloudflare.com/client/v4/zones/%s/firewall/access_rules/rules' % config['zone-id']
cf_company_link = 'https://api.cloudflare.com/client/v4/organizations/%s/firewall/access_rules/rules' % config['company-id']

cf_header = {
    "X-Auth-Email": config['auth-email'],
    "X-Auth-Key": config['api-key'],
    "Content-Type": "application/json"
}


def get_firewall(ip_filter = None):
    cf_filter = {
        "configuration.value": ip_filter,
        "per_page": "200"
    }
    r = requests.get(cf_zone_link, headers=cf_header, params=cf_filter).json()
    ip_list = list()
    for item in r['result']:
        ip = dict()
        ip['id'] = item['id']
        ip['ip'] = item['configuration']['value']
        ip['notes'] = item['notes']
        ip_list.append(ip)
    return ip_list


def set_firewall(ip, notes=''):
    rule = {
        "mode": "challenge",
        "configuration": {
            "target": "ip",
            "value": ip
        },
        "notes": notes
    }
    r = requests.post(cf_zone_link, headers=cf_header, data=json.dumps(rule))
    print(r.content)
    return


def del_firewall(ip):
    item = get_firewall(ip)
    if len(item) == 0:
        return None

    rule_id = item[0]['id']
    r = requests.delete(cf_zone_link + '/' + rule_id, headers=cf_header, data={"cascade":"none"})
    print(r.content)
    return True
