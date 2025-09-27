from flask import Flask,render_template, redirect ,request,url_for, flash, session
import sqlite3
import os


app = Flask(__name__)

app.secret_key = "9f1c3c27a08f2e4ab1c25c9278d5c1b2"

app.config['uploads'] = 'static/uploads'

os.makedirs(app.config['uploads'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    return conn

#################################################### LOGIN #############################################################

@app.route('/')
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")   


                           


@app.route("/submit_register", methods=["POST"])
def submit_register():
    ACTOR_Username = request.form['ACTOR_Username']
    ACTOR_Email = request.form["ACTOR_Email"]
    ACTOR_Password = request.form["ACTOR_Password"]
    ACTOR_TELL = request.form["ACTOR_TELL"]
    ACTOR_Role = request.form['ACTOR_Role']

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("INSERT INTO ACTOR (ACTOR_Username, ACTOR_Email, ACTOR_Password, ACTOR_Role, ACTOR_TELL) VALUES (?, ?,?, ?, ?)",
              (ACTOR_Username, ACTOR_Email, ACTOR_Password, ACTOR_Role, ACTOR_TELL))
    conn.commit()
    conn.close()

    return redirect(url_for("register"))

@app.route('/submit_login', methods=["POST"])
def submit_login():
    email = request.form["ACTOR_Email"]
    password = request.form["ACTOR_Password"]
    role = request.form["ACTOR_Role"]

    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM ACTOR WHERE ACTOR_Email=? AND ACTOR_Password=? AND ACTOR_Role=?" , (email, password, role))
    user = c.fetchone()
    conn.close()
    if user:
        if role == "Admin":
            return redirect(url_for("admin_home"))
        elif role == "Customer":
            return redirect(url_for("customer_home"))
    else:
        return redirect(url_for("login"))

@app.route("/search")
def search():
    query = request.args.get("search")
    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""SELECT * FROM CATALOG WHERE CATALOG_Name LIKE ? OR CATALOG_Detail LIKE ?""", ('%' + query + '%', '%' + query + '%'))

    results = c.fetchall()
    conn.close()
    if not results:
        flash(f"ไม่พบสินค้าที่ตรงกับ '{query}'", "warning")


    return render_template("home.html", catalog=results, search_query=query)


@app.route("/submit", methods=["POST"])
def submit():
    CATALOG_Name = request.form['CATALOG_Name']
    CATALOG_Brand = request.form["CATALOG_Brand"]
    CATALOG_Detail = request.form["CATALOG_Detail"]
    CATALOG_Price = request.form['CATALOG_Price']
    TYPE_FK = request.form['TYPE_FK']
 
    file = request.files['CATALOG_Image']
    filename = None
    if file:
        filename = os.path.join(app.config['uploads'], file.filename)
        file.save(filename)

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("INSERT INTO CATALOG (TYPE_FK, CATALOG_Name, CATALOG_Price, CATALOG_Image, CATALOG_Detail, CATALOG_Brand) VALUES (?, ?, ?, ?, ?, ?)",
              (TYPE_FK, CATALOG_Name, CATALOG_Price, filename, CATALOG_Detail, CATALOG_Brand))
    conn.commit()
    conn.close()

    return redirect(url_for("insert_data"))



@app.route('/submit_cart', methods=['POST'])
def submit_cart():

    CART_Name = request.form['CART_Name']
    CART_Price = request.form['CART_Price']
    CART_Detail = request.form['CART_Detail']
    CART_Brand = request.form['CART_Brand']


    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("INSERT INTO CART (CART_Name, CART_Price, CART_Detail, CART_Brand) VALUES ( ?, ?, ?, ?)",
              ( CART_Name, CART_Price, CART_Detail, CART_Brand))
    conn.commit()
    conn.close()

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CART")
    CART = conn.execute("SELECT * FROM CART").fetchall()
    total_price = sum(float(CART[2]) for CARTS in CART)
    conn.close()
    return render_template("cart.html", CART = CART,total_price=total_price)



################################################### ADMIN ###############################################################

@app.route('/insert_data')
def insert_data():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 3").fetchall()
    conn.close()
    return render_template("insert_data.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)


@app.route("/delete/<int:CATALOG_ID>")
def delete(CATALOG_ID):
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT CATALOG_Image FROM CATALOG WHERE CATALOG_ID=?", (CATALOG_ID,))
    row = c.fetchone()
    if row and row[0]:
        try:
            os.remove(row[0])
        except FileNotFoundError:
            pass
    c.execute("DELETE FROM CATALOG WHERE CATALOG_ID=?", (CATALOG_ID,))
    conn.commit()
    conn.close()
    return redirect(url_for("insert_data"))



@app.route('/admin_about')
def admin_about():
    return render_template("admin_about.html")



@app.route('/admin_home_electronic')
def admin_home_electronic():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    
    c.execute("SELECT * FROM CATALOG")
    c.execute("SELECT * FROM ACTOR")

    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()

    ACTOR_ID = conn.execute("SELECT * FROM ACTOR WHERE ACTOR_ID").fetchall()
    conn.close()
    return render_template("admin_home_electronic.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic, ACTOR_ID=ACTOR_ID)

@app.route('/admin_home_led')
def admin_home_led():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("admin_home_led.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

@app.route('/admin_home_equipment')
def admin_home_equipment():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() 
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("admin_home_equipment.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

@app.route('/admin_home')
def admin_home():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("admin_home.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)


@app.route('/admin_review')
def admin_review():
    return render_template("admin_review.html")


@app.route('/admin_profile')
def admin_profile():
    return render_template("profile.html")




####################################################### CUSTOMER ################################################################

@app.route('/customer_about')
def customer_about():
    return render_template("customer_about.html")



@app.route('/customer_home_electronic')
def customer_home_electronic():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("customer_home_electronic.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

@app.route('/customer_home_led')
def customer_home_led():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("customer_home_led.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

@app.route('/homeEquipment')
def customer_home_equipment():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() 
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("customer_home_equipment.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

@app.route('/customer_home')
def customer_home():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    conn.close()
    return render_template("customer_home.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)


@app.route('/customer_review')
def customer_review():
    return render_template("customer_review.html")





if __name__ == "__main__":
    app.run()