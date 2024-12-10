from flask import Flask, render_template
import pymysql
from dynaconf import Dynaconf


app = Flask(__name__)

conf = Dynaconf(
     settings_file = [ 'settings.toml' ]
)

def connect_db():
    conn = pymysql.connect(
        host = "10.100.34.80",
        database = "cpaynter_Mechs&Robots",
        user = 'cpaynter',
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )
    return conn



@app.route('/')
def index():
    return render_template('homepage.html.jinja')


@app.route('/browse')
def product_browse():
      conn = connect_db()
      cursor = conn.cursor()
      cursor.execute('SELECT * FROM `Product` ;')
      results = cursor.fetchall()

      return render_template('browse.html.jinja',  products = results)
