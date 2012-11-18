# -*- coding: utf-8 -*-

from view import app
from flask import g, request, session
from config import db_config
import db
import util

app.debug = True

@app.before_request
def before_request():
    ua = request.headers['User-Agent']
    g.config = {}
    g.config['device'] = util.device(ua)
    if request.args.get('ad') == 'shine':
        g.config['adfree'] = True
    g.db_session = db.Session(bind=db.engine)


@app.teardown_request
def teardown_request(exception):
    g.db_session.close()
    if 'user' in session:
        pass
        #session.save_session(app, session, response)

if __name__ == '__main__':
    app.run()
