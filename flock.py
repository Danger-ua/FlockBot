import requests
import json
import utilslib
import argparse
from plugins import cloudflare, jira
from datetime import datetime
import db_tools


config = utilslib.load_config()
bot_id = config['flock']['bot-id']

tokens = utilslib.load_tokens()
tokens[bot_id] = {'userToken': config['flock']['bot-token']}


def app_init(info):
    # user = get_user_public_profile(bot_id, info['userId'])
    tokens[info['userId']] = {
        'userToken': info['userToken'],
        'token': info['token']
        #        'name': user['firstName'] + ' ' + user['lastName']
    }
    utilslib.save_tokens(tokens)
    return


def cf_ban(args):
    ip = args.ip
    action = None
# TO-DO: Add function for retrieve credentials
    if args.add:

        issue = jira.create_issue(creds, 'Block IP on Cloudflare',
                                  '<p>Block IP on Cloudflare due to malicious activity</p><p>IP: %s</p>' % args.ip)
        cloudflare.set_firewall(ip, issue)
        action = 'added to'
    if args.delete:
        cloudflare.del_firewall(ip)
        action = 'removed from'
    print(cloudflare.get_firewall())
    send_message_from_bot(args.userId, "IP (%s) have %s CF" % (args.ip, action))
    return None


parser = argparse.ArgumentParser()
sub_parser = parser.add_subparsers()

cf_ban_parse = sub_parser.add_parser('ban')
cf_ban_parse.add_argument('ip', default='show')
cf_ban_parse.add_argument('-a', '--add', action='store_true')
cf_ban_parse.add_argument('-d', '--delete', action='store_true')
cf_ban_parse.set_defaults(function=cf_ban)


def create_cir(args):
    curr_date = datetime.now().strftime('%Y-%m-%d')
    room_name = 'Test_CIR_%s_%s' % (curr_date, args.issue)
    users_list_id = list(utilslib.load_room_users_list()['cir'].keys())
    create_room(args.userId, room_name, users_list_id, False)
    send_message(args.userId, args.chatId,
                 'I have created room %s \nPlease continue discussion there' % room_name)
    #
    # sendmail.send('cir-got-issue@namecheap.pagerduty.com',room_name, room_name)
    #
    print(users_list_id)
    return


cir_parse = sub_parser.add_parser('cir')
cir_parse.add_argument('issue')
cir_parse.set_defaults(function=create_cir)


def gen_registration_url(args):
    user_id = args.userId
    url = db_tools.create_registration_url(user_id)
    if not url:
        send_message_from_bot(user_id, 'URL for you exist, please use it or wait until old will expire')
        return False
    url = config['main_url'] + 'regi/' + str(url)
    send_message_from_bot(user_id, 'Registration URL created success\n%s\n'
                                   'You have 5 minutes for register your credential' % url)
    return True


reg_parse = sub_parser.add_parser('reg')
reg_parse.set_defaults(function=gen_registration_url)


def mod_users_list(args):
    if str(args.chatId).startswith('g:'):
        send_message_from_bot(args.userId, 'Can\'t add group chat to users list')
        return
    users_list = utilslib.load_room_users_list()

    if args.list:
        if args.room not in users_list:
            send_message(bot_id, args.userId, 'Room named \'%s\' not found' % args.room)
            return
        msg_text = 'Users list will be added to the room \'%s\':\n' % args.room
        for user_txt in users_list[args.room].values():
            msg_text += '- ' + user_txt + '\n'
        send_message_from_bot(args.userId, msg_text)
        return

    if not users_list.get(args.room, False):
        users_list[args.room] = dict()

    if args.add:
        users_list[args.room][args.chatId] = args.chatName

    elif args.delete:
        del users_list[args.room][args.chatId]

    utilslib.save_room_users_list(users_list)
    return


users_parse = sub_parser.add_parser('user')
users_parse.add_argument('room')
users_parse.add_argument('-a', '--add', action='store_true')
users_parse.add_argument('-d', '--delete', action='store_true')
users_parse.add_argument('-l', '--list', action='store_true')
users_parse.set_defaults(function=mod_users_list)


def send_help(userID):
    msg = "Help message\n" \
          "usage: /sre <command> <params>\n" \
          "COMMANDS:\n" \
          " user <room_name> - modify users list from automatic add to rooms\n" \
          "\t--add(-a) - add user\n" \
          "\t--delete(-d) - delete user\n" \
          "\t--list(-l) - show users list\n\n" \
          " cir <issue> - create CIR and going across flow\n\n" \
          " reg - create credential for authenticate on Jira and Collad"
    send_message_from_bot(recipient_id=userID, text=msg)
    return


def run_cmd(info):
    msg = dict(info).get('text', False)
    if not msg:
        send_help(info['userId'])
        return
    args_string = msg.split(' ')
    args = parser.parse_args(args_string)

    # args.userid = object()
    args.userId = info['userId']
    args.chatId = info['chat']
    args.chatName = info['chatName']
    args.function(args)
    return None


# def add_user(user):
#     tokens[user['chat']] = {
#         'name': user['chatName']
#     }
#     utilslib.save_tokens(tokens)
#     send_message(bot_id, user['chat'], 'Welcome to SRE-L1 Helper Bot')
#
#
# def chat(info):
#     return 0


def send_message(sender_id, recipient_id, text, send_as=None):
    param = {
        'token': tokens[sender_id]['userToken'],
        'to': recipient_id,
        'text': text
    }
    if send_as is not None:
        param['sendAs'] = send_as
    _call_api('/chat.sendMessage', param)
    return


def send_message_from_bot(recipient_id, text):
    send_message(bot_id, recipient_id, text, None)


def _call_api(resource_path, params, get_json=True):
    base_url = 'https://api.flock.co/v1'
    url = base_url + resource_path
    response_data = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(params))
    if response_data.status_code != 200:
        print("Response status: " + response_data.text)
        return None
    if get_json:
        return response_data.json()
    else:
        return json.loads(response_data.text.encode('utf8'))


def get_contacts_list(sender):
    global token
    file_name = "users_list.json"
    if utilslib.how_old_file(file_name) > 600:
        res = _call_api('/roster.listContacts', {'token': tokens[sender]['token']})
        with open(file_name, 'w') as wfile:
            wfile.write(res.encode('utf8'))
            wfile.close()
    with open(file_name, 'r') as wfile:
        users_list = json.load(wfile)
    return users_list


def create_room(user_id, room_name, members=None, public=True):
    user_token = tokens[user_id]['userToken']
    # if members is None:
    #     members = list()
    #     members.append('u:xzwo2wnoaz2wz9a9')
    #     members.append('u:ssoxh4osoucxzncn')
    room_type = 'public'
    if not public: room_type = 'private'
    param = {
        'token': user_token,
        'name': room_name,
        'type': room_type,
        'members': members
    }
    _call_api('/channels.create', param)
    #    print()
    return


def get_user_public_profile(sender, user_id):
    param = {
        'token': tokens[sender]['token'],
        'userId': user_id
    }
    return _call_api('/users.getPublicProfile', param, get_json=False)
