from flask import render_template
import db_tools


def check_url(url_id):
    db_tools.remove_expired_urls()
    print("------- Check URL --------- url-id: %s" % url_id)
    user_id = db_tools.find_user_flock_id(url_id)
    if not user_id:
        return False
    return True


def register_page(url_id):
    print("------- Register page ---------")
    plugin_list = [
        {
            'name': 'collab',
            'desc': 'Collad'
        },
        {
            'name': 'jira',
            'desc': 'Jira'
        }
    ]
    return render_template("save_creds.html", reg_link=url_id, plgs=plugin_list)


def register_creds(form, url_id):
    print("------- Register creds ---------")
    user_id = db_tools.find_user_flock_id(url_id)
    if not user_id:
        return False
    plgs = list()
    for item in form:
        if form[item] == 'on':
            plgs.append(item)

    db_tools.save_credential(user_id, form['uname'], form['psw'], plugin=plgs)
    db_tools.remove_used_url(url_id)
    return True

