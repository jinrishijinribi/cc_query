from flask import Flask, Blueprint
from flask_cors import CORS


route_bp = Blueprint("route", __name__, url_prefix='/api')


def create_app():
    app = Flask(__name__)
    import cc_query.routes
    CORS(app, supports_credentials=True)
    app.config.from_pyfile('config.py')
    app.register_blueprint(route_bp)
    return app
