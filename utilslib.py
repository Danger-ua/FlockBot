import os
import time
import yaml


def get_file_creation(filepath):
    return os.stat(filepath).st_ctime


def how_old_file(filepath):
    return int(time.time()) - get_file_creation(filepath)


def save_param(file_name, params_dict):
    file_path = os.path.dirname(__file__) + '/config/' + file_name
    f = open(file_path, 'w')
    yaml.dump(params_dict, f, allow_unicode=True)
    f.close()


def load_param(file_name):
    file_path = os.path.dirname(__file__) + '/config/' + file_name
    try:
        f = open(file_path, 'r')
        r = yaml.safe_load(f)
        f.close()
    except:
        print('File ' + file_path + ' doesn\'t exist')
        return dict()
    else:
        return r


def save_tokens(tokens_dict):
    save_param('.token.yaml', tokens_dict)


def load_tokens():
    return load_param('.token.yaml')


def save_config(conf_dict):
    save_param('config.yml', conf_dict)


def load_config():
    return load_param('config.yml')


def save_room_users_list(users_dict):
    save_param('users.yml', users_dict)


def load_room_users_list():
    return load_param('users.yml')
