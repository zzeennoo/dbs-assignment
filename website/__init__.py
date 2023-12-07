from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# init the database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    #app configuration
    app.config['SECRET_KEY'] = 'abc'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Longvu123@localhost/assignment2'
    ##############################

    
    #init the login manager
    from .model import Patient

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    
    def load_user(patient_id):
        return Patient.query.get(patient_id)
    ##############################


    #init the database with app 
    db.init_app(app)
    ##############################


    from .views import views
    from .auth import auth
    from .actor import actor

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(actor, url_prefix = '/')

    return app

