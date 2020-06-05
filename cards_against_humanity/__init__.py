from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# remote db
# conn_str = 'mysql+pymysql://alexjhill:s9nTETkSvzcv3e@alexjhill.mysql.pythonanywhere-services.com/alexjhill$cards_against_humanity'
# local db
conn_str = 'mysql+pymysql://root:password1@localhost/cards-against-humanity'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
db = SQLAlchemy(app)


from cards_against_humanity import views, models, api
