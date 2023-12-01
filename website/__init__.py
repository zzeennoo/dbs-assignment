from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# init the database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    #app configuration
    app.config['SECRET_KEY'] = 'abc'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/assignment2'

    #init the database with app 
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .actor import actor

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(actor, url_prefix = '/')

    return app