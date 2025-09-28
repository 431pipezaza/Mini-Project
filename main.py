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
    username = request.form['ACTOR_Username']
    email = request.form['ACTOR_Email']
    password = request.form['ACTOR_Password']
    tell = request.form['ACTOR_TELL']
    role = request.form['ACTOR_Role'] 

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()


    if role == "Admin":
        c.execute("SELECT * FROM ADMIN WHERE ADMIN_Email=?", (email,))
        if c.fetchone():
            conn.close()
            flash("Email นี้มีผู้ใช้แล้ว", "danger")
            return redirect(url_for("register"))
        
        else: c.execute("INSERT INTO ADMIN (ADMIN_Username, ADMIN_Email, ADMIN_Password, ADMIN_TELL, ADMIN_Role) VALUES (?, ?, ?, ?, ?)",
                  (username, email, password, tell, role))
    if role == "Customer":
        c.execute("SELECT * FROM CUSTOMER WHERE CUSTOMER_Email=?", (email,))
        if c.fetchone():
            conn.close()
            flash("Email นี้มีผู้ใช้แล้ว", "danger")
            return redirect(url_for("register"))
        else: c.execute("INSERT INTO CUSTOMER (CUSTOMER_Username, CUSTOMER_Email, CUSTOMER_Password, CUSTOMER_TELL, CUSTOMER_Role) VALUES (?, ?, ?, ?, ?)",
                  (username, email, password, tell, role))

    conn.commit()
    conn.close()
    flash("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "success")
    return redirect(url_for("login"))




@app.route('/submit_login', methods=["POST"])
def submit_login():
    email = request.form["ACTOR_Email"]
    password = request.form["ACTOR_Password"]
    role = request.form["ACTOR_Role"] 

    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    user = None

    if role == "Admin":
        c.execute("SELECT * FROM ADMIN WHERE ADMIN_Email=? AND ADMIN_Password=?", (email, password))
        user = c.fetchone()
        if user:
            session['admin_id'] = user['ADMIN_ID']
            conn.close()
            return redirect(url_for("admin_home"))

    elif role == "Customer":
        c.execute("SELECT * FROM CUSTOMER WHERE CUSTOMER_Email=? AND CUSTOMER_Password=?", (email, password))
        user = c.fetchone()
        if user:
            session['customer_id'] = user['CUSTOMER_ID']
            conn.close()
            return redirect(url_for("customer_home"))

    conn.close()
    return redirect(url_for("login"))


@app.route("/customer_search")
def customer_search():
    query = request.args.get("search")
    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""SELECT * FROM CATALOG WHERE CATALOG_Name LIKE ? OR CATALOG_Detail LIKE ?""", ('%' + query + '%', '%' + query + '%'))

    results = c.fetchall()
    conn.close()
    if not results:
        flash(f"ไม่พบสินค้าที่ตรงกับ '{query}'", "warning")


    return render_template("customer_home.html", catalog=results, search_query=query)



@app.route("/admin_search")
def admin_search():
    query = request.args.get("search")
    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""SELECT * FROM CATALOG WHERE CATALOG_Name LIKE ? OR CATALOG_Detail LIKE ?""", ('%' + query + '%', '%' + query + '%'))

    results = c.fetchall()
    conn.close()
    if not results:
        flash(f"ไม่พบสินค้าที่ตรงกับ '{query}'", "warning")


    return render_template("admin_home.html", catalog=results, search_query=query)




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

    return redirect(url_for("admin_insert_data"))


@app.route('/submit_cart', methods=['POST'])
def submit_cart():
    if 'customer_id' not in session:
        flash("กรุณาเข้าสู่ระบบก่อนเพิ่มสินค้าในตะกร้า", "warning")
        return redirect(url_for("login"))

    customer_id = session['customer_id']

    CART_Name = request.form['CART_Name']
    CART_Price = request.form['CART_Price']
    CART_Detail = request.form['CART_Detail']
    CART_Brand = request.form['CART_Brand']

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO CART (CART_Name, CART_Price, CART_Detail, CART_Brand, CUSTOMER_ID) VALUES (?, ?, ?, ?, ?)",
        (CART_Name, CART_Price, CART_Detail, CART_Brand, customer_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('customer_cart'))






################################################### ADMIN ###############################################################

@app.route('/admin_insert_data')
def admin_insert_data():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 3").fetchall()
    conn.close()
    return render_template("admin_insert_data.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)


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
    c.execute("SELECT * FROM ADMIN")

    catalog = conn.execute("SELECT * FROM CATALOG").fetchall()
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()

    conn.close()
    return render_template("admin_home_electronic.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

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
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    admin_id = session['admin_id']

    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM ADMIN WHERE ADMIN_ID = ?", (admin_id,))
    admin = c.fetchone()
    conn.close()

    return render_template("admin_profile.html", admin=admin)





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


@app.route('/customer_profile')
def customer_profile():
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    customer_id = session['customer_id']
    with sqlite3.connect("ELEC_DB.db") as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM CUSTOMER WHERE CUSTOMER_ID = ?", (customer_id,))
        customer = c.fetchone()

    return render_template("customer_profile.html", customer=customer)





@app.route("/update_profile", methods=["POST"])
def update_profile():
    user_id = request.form["user_id"]
    username = request.form["username"]
    email = request.form["email"]
    tell = request.form["tell"]
    password = request.form.get("password") 

    role = "Admin" if "admin_id" in session else "Customer"
    table = "ADMIN" if role == "Admin" else "CUSTOMER"
    id_field = "ADMIN_ID" if role == "Admin" else "CUSTOMER_ID"

    with sqlite3.connect("ELEC_DB.db") as conn:
        c = conn.cursor()

        # ✅ ตรวจสอบ email ซ้ำ (ยกเว้นของตัวเอง)
        c.execute(f"SELECT 1 FROM {table} WHERE {table}_Email=? AND {id_field}!=?", (email, user_id))
        if c.fetchone():
            flash("อีเมลนี้ถูกใช้แล้ว", "danger")
            return redirect(url_for("admin_profile") if role=="Admin" else url_for("customer_profile"))

        # ✅ update
        if password:
            c.execute(f"""
                UPDATE {table} 
                SET {table}_Username=?, {table}_Email=?, {table}_TELL=?, {table}_Password=? 
                WHERE {id_field}=?
            """, (username, email, tell, password, user_id))
        else:
            c.execute(f"""
                UPDATE {table} 
                SET {table}_Username=?, {table}_Email=?, {table}_TELL=? 
                WHERE {id_field}=?
            """, (username, email, tell, user_id))

        conn.commit()

    flash("แก้ไขข้อมูลสำเร็จ", "success")
    return redirect(url_for("admin_profile") if role=="Admin" else url_for("customer_profile"))



@app.route("/edit_profile", methods=["GET"])
def edit_profile():
    if "admin_id" in session:
        table, id_field, user_id = "ADMIN", "ADMIN_ID", session["admin_id"]
    elif "customer_id" in session:
        table, id_field, user_id = "CUSTOMER", "CUSTOMER_ID", session["customer_id"]
    else:
        flash("กรุณาเข้าสู่ระบบก่อน", "danger")
        return redirect(url_for("login"))

    with sqlite3.connect("ELEC_DB.db") as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(f"SELECT {id_field} as ID, {table}_Username as Username, {table}_Email as Email, {table}_TELL as TELL, {table}_Role as Role FROM {table} WHERE {id_field}=?", (user_id,))
        user = c.fetchone()

    return render_template("edit_profile.html", user=user)





@app.route('/customer_cart')
def customer_cart():
    if 'customer_id' not in session:
        return redirect(url_for("login"))

    customer_id = session['customer_id']

    conn = sqlite3.connect("ELEC_DB.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM CART WHERE CUSTOMER_ID=?", (customer_id,))
    cart_items = c.fetchall()
    conn.close()

    total_price = sum(float(item["CART_Price"]) for item in cart_items)
    return render_template("customer_cart.html", CART=cart_items, total_price=total_price)





@app.route("/delete_cart/<int:cart_id>")
def delete_cart(cart_id):
    if 'customer_id' not in session:
        return redirect(url_for("login"))

    customer_id = session['customer_id']

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("DELETE FROM CART WHERE CART_ID=? AND CUSTOMER_ID=?", (cart_id, customer_id))
    conn.commit()
    conn.close()

    return redirect(url_for("customer_cart"))




if __name__ == "__main__":
    app.run()