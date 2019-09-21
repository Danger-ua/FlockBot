from flask import Flask, Response
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import flock
import web.register

app = Flask(__name__, template_folder='web')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///config/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/flock', methods=['POST'])
def msg_received():
    req = request.get_data()
    app.logger.debug(req)
    req = json.loads(req)
    if req['name'] == 'app.install':
        flock.app_init(req)
    elif req['name'] == 'client.slashCommand':
        flock.run_cmd(req)
    # elif req['name'] == 'chat.receiveMessage':
    #     flock.chat(req)

    return Response(status=200)


@app.route('/regi/<url_id>', methods=['GET', 'POST'])
def registration(url_id=None):
    if not url_id:
        return Response(status=404)
    elif len(url_id) != 10:
        return Response(status=404)
    check_result = web.register.check_url(url_id)
    app.logger.debug('URL check result: %s' % check_result)
    if not check_result:
        return Response(status=404)
    if request.method == 'GET':
        return web.register.register_page(url_id)
    elif request.method == 'POST':
        res = web.register.register_creds(request.form, url_id)
        if res:
            return Response(status=200)
        else:
            return Response(status=404)


if __name__ == '__main__':
    db.create_all()

    # url = db_models.RegistrationUrl(user_id='11112')
    # db.session.add(url)
    # db.session.commit()
    # print(db_models.RegistrationUrl().query.all())
    app.run(host='0.0.0.0', port=5000, debug=True)
    exit(0)
