from flask import Flask, render_template, request, redirect, flash
import pymysql
from dynaconf import Dynaconf


app = Flask(__name__)

conf = Dynaconf(
     settings_file = [ 'settings.toml' ]
)


app.secret_key = [ "settings.toml" ]

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
    query = request.args.get('query')

    conn = connect_db()

    cursor = conn.cursor()

    if query is None: 
        cursor.execute("SELECT * FROM `Product` ;")
    else: 
        cursor.execute(f"SELECT * FROM `Product` WHERE `name` LIKE '%{query}%' OR `description LIKE '%{query}%' ;")

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('browse.html.jinja',  products = results)

    
@app.route("/product/<product_id>")

def product_page(product_id):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Product` WHERE `id` = {product_id}; ")

    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('product.html.jinja',  product = results)


@app.route("/signup", methods=["POST", "GET"])

def  signup():

    if request.method == 'POST':

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        emailadd = request.form["email"]
        password = request.form["password"]
        conpasswrd = request.form["conpassword"]
        conn = connect_db()

        cursor = conn.cursor()
        if conpasswrd != password:
            flash("The passwords don't match.")
        else:

        

            try:
                cursor.execute(f"""

            
                INSERT INTO `Customer` 
                    (`First_name`, `Last_name`, `Email`, `password`)
                VALUES
                    ('{first_name}', '{last_name}', '{emailadd}', '{password}');
            """)
            except pymysql.err.IntegrityError:
                flash("Sorry, account using this information has already been made. Please try a differenet email.")   
                
            else:
                return redirect("/signin")
            finally:       
                cursor.close()
                conn.close()
        
            




    return render_template('signup.html.jinja')

@app.route("/signin")

def  signin():
    return render_template('signin.html.jinja')