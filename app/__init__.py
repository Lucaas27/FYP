from flask import Flask, redirect, session, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user,AnonymousUserMixin
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail




app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
moment = Moment(app)
mail = Mail(app)
login_manager=LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category="info"



from app import routes, models, errors
from app.models import *


# Give a username to anonymous users
class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'
    
# Add the anonymous class to anonymous_user
login_manager.anonymous_user = Anonymous


class MyAdminIndexView(AdminIndexView):
    
    def is_accessible(self):
        return current_user.username == 'admin'
    
class ShopModelView(ModelView):

    def is_accessible(self):
        return current_user.username== 'admin'
  

admin = Admin(app, index_view=MyAdminIndexView(), name='Admin', template_mode='bootstrap3')
# administrative views here

    
admin.add_view(ShopModelView(User, db.session))
admin.add_view(ShopModelView(ItemForSale, db.session))
admin.add_view(ShopModelView(Category, db.session))
admin.add_view(ShopModelView(OAuth, db.session))
admin.add_view(ShopModelView(Address, db.session))
admin.add_view(ShopModelView(Order, db.session))
