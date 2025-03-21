from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login
import math


app = Flask(__name__)

conf = Dynaconf(
     settings_file = [ 'settings.toml' ]
)


app.secret_key = conf.secret_key


login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/signin'

class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, user_id, email, first_name, last_name):
            self.id = user_id
            self.email = email
            self.first_name = first_name
            self.last_name = last_name
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Customer` WHERE `id` = {user_id}; ")

    results = cursor.fetchone()
    
    cursor.close()

    conn.close()

    if results is not None:
        return User(results["id"], results["Email"], results["First_name"], results["Last_name"])





def connect_db():
    conn = pymysql.connect(
        host = "db.steamcenter.tech",
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
    if results is None:
        abort(404)

    cursor.close()
    conn.close()

    return render_template('product.html.jinja',  product = results)

@app.route("/product/<product_id>/cart", methods=["POST"])
@flask_login.login_required
def add_to_cart(product_id):
    conn = connect_db()
    cursor = conn.cursor()

    qty = request.form["qty"]
    Customer_id = flask_login.current_user.id

    cursor.execute(f"""
    INSERT INTO `Cart`
        (`qty`, `Customer_id`, `Product_id`)
    VALUE
        ('{qty}', '{Customer_id}', '{product_id}')
    ON DUPLICATE KEY UPDATE
        `qty` = `qty` + {qty}
    """)

    cursor.close()
    conn.close()
    return redirect ("/cart")

@app.route("/signup", methods=["POST", "GET"])
def  signup():
    if flask_login.current_user.is_authenticated == True:
        return redirect("/")
    else:
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


@app.route("/signin", methods=["POST", "GET"])
def sign_in():
    if flask_login.current_user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            email = request.form['email'].strip()
            password = request.form['password']
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `Customer` WHERE `email` = '{email}'; ")
            cursor.execute(f"SELECT * FROM `Customer` WHERE `password` = {password}; ")
            
            results = cursor.fetchone()
            if results is None:
                flash("Beep Boop (Your information is incorrect.)")
            elif password != results["password"]:
                flash("Beep Boop (Your information is incorrect.)")
            else:
                user = User(results["id"], results["Email"], results["First_name"], results["Last_name"])
                flask_login.login_user(user)
                return redirect('/')

    return render_template('signin.html.jinja')

@app.route('/logout')
def logout():

    flask_login.logout_user()
    return redirect('/')


@app.route('/cart')
@flask_login.login_required
def cart():

    conn = connect_db()
    cursor = conn.cursor()

    customer_id = flask_login.current_user.id

    cursor.execute(f"""
        SELECT 
            `name`, `price`, `qty`, `image`, `Product_id`, `Cart`.`id` 
        FROM `Cart`
        JOIN `Product` ON `Product_id` = `Product`.`id` 
        WHERE `customer_id` = {customer_id};
        """)

    results = cursor.fetchall()

    total = 0

    for product in results:

        qty = product["qty"]
        price = product["price"]
        item_total = qty * price 
        total = item_total + total


    
    cursor.close()
    conn.close()


    return render_template("cartpage.html.jinja", product=results , total=total)


@app.route("/cart/<cart_id>/del", methods = ["POST"])
@flask_login.login_required
def delete(cart_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM `Cart` WHERE `id`={cart_id};")
    cursor.close()
    conn.close()
    return redirect("/cart")


@app.route("/cart/<cart_id>/upd", methods = ["POST"])
@flask_login.login_required
def upd(cart_id):
    conn = connect_db()
    cursor = conn.cursor()
    qty = request.form["qty"]
    cursor.execute(f"UPDATE `Cart` SET `quantity`={qty} WHERE `id`={cart_id};")
    cursor.close()
    conn.close()
    return redirect("/cart")


@app.route("/cart/sale/")
@flask_login.login_required
def purch():
    conn = connect_db()
    cursor = conn.cursor()
    

@app.route("/review/")
@flask_login.login_required
def review():

    conn = connect_db()
    cursor = conn.cursor()

@app.route("/checkout")
@flask_login.login_required
def checkout():
    customer_id = flask_login.current_user.id
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"""SELECT `name`,`price`,`quantity`,`image`,`product_id`,`Cart`.`id` 
    FROM `Cart` JOIN `Product` ON `product_id` = `Product`.`id`
    WHERE `customer_id` = {customer_id};""")
    result = cursor.fetchall()
    total = 0
    tax = 0.08875
    for product in result:
        quantity = product["quantity"]
        price = product["price"]
        item_total = price * quantity
        total = item_total + total

    tax_total = total * tax
    overall_total = total + tax_total


