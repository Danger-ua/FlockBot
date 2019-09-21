import db_models
from main import db, app
# from utilslib import load_config
from datetime import datetime
import crypto


def _check_user_url_exist(user_id):
    remove_expired_urls()
    app.logger.debug('User_id: ' + user_id)
    app.logger.debug("Users list from DB")
    app.logger.debug(db_models.RegistrationUrl.query.all())
    res = db_models.RegistrationUrl.query.filter_by(user_id=user_id).all()
    app.logger.debug("Found user from DB")
    app.logger.debug(res)
    if len(res) > 0:
        app.logger.debug("User with url found")
        return True


def create_registration_url(user_id):
    if _check_user_url_exist(user_id):
        print("Check user url exist: false")
        return None
    url = db_models.RegistrationUrl(user_id=user_id)
    # print(url)
    db.session.add(url)
    db.session.commit()
    return url.url


def remove_expired_urls():
    urls = db_models.RegistrationUrl.query.filter(db_models.RegistrationUrl.expiration < datetime.utcnow()).all()
    app.logger.debug(urls)
    for url in urls:
        db.session.delete(url)
    db.session.commit()
    return


def remove_used_url(url):
    url_db = db_models.RegistrationUrl.query.filter(db_models.RegistrationUrl.url == url).first()
    db.session.delete(url_db)
    db.session.commit()
    app.logger.debug("Delete user url from DB: " + url_db)
    return


def find_user_flock_id(url_id):
    url = db_models.RegistrationUrl.query.filter_by(url=url_id).first()
    if not url:
        return False
    return url.user_id


def save_credential(user_flock_id, user_name, user_password, plugins):
    c_username = crypto.encode(user_name)
    c_password = crypto.encode(user_password)
    for plugin in plugins:
        user_cred = db_models.Credential.query.\
            filter(db_models.Credential.plugin == plugin, db_models.Credential.id == user_flock_id).first()
        if not user_cred:
            user_cred = db_models.\
                Credential(id=user_flock_id, username=c_username, password=c_password, plugin=plugin)
            db_models.db.session.add(user_cred)
        else:
            user_cred.username = c_username
            user_cred.password = c_password
        db_models.db.session.commit()
    return True


def get_credential(user_flock_id, plugin):
    user_cred = db_models.Credential.query.\
        filter(db_models.Credential.plugin == plugin, db_models.Credential.id == user_flock_id).first()
    if not user_cred:
        return False
    e_username = crypto.decode(user_cred.username)
    e_password = crypto.decode(user_cred.password)
    return e_username, e_password

