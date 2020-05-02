from flask import Flask, redirect, session, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView





app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category="info"


from app import routes, models, errors
from app.models import User, Item, Category

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'


class MyAdminIndexView(AdminIndexView):
    
    def is_accessible(self):
        return session.get('username') == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))
    
class ShopModelView(ModelView):

    def is_accessible(self):
        return session.get('username') == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))
    

admin = Admin(app, index_view=MyAdminIndexView(), name='Admin', template_mode='bootstrap3')
# administrative views here

    
admin.add_view(ShopModelView(User, db.session))
admin.add_view(ShopModelView(Item, db.session))
admin.add_view(ShopModelView(Category, db.session))