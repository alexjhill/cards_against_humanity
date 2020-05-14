from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db 1
# conn_str = 'mysql+pymysql://unfbbwlp7m40iqvv:Th8cO1VKB9sUy94XFYQg@b1seqbavm975g4dqrctm-mysql.services.clever-cloud.com/b1seqbavm975g4dqrctm'
# db 2 (backup)
# conn_str = 'mysql+pymysql://upbx80jfe46euwjn:u1PKoKQrwlh4WE47aHM7@bzubvxk0tyjehwx4q0og-mysql.services.clever-cloud.com/bzubvxk0tyjehwx4q0og'
# local db
conn_str = 'mysql+pymysql://root:password1@localhost/cards-against-humanity'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
db = SQLAlchemy(app)

from cards_against_humanity import views, models, api
