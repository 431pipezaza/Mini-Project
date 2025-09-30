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
          
            return redirect(url_for("register"))
        
        else: c.execute("INSERT INTO ADMIN (ADMIN_Username, ADMIN_Email, ADMIN_Password, ADMIN_TELL, ADMIN_Role) VALUES (?, ?, ?, ?, ?)",
                  (username, email, password, tell, role))
    if role == "Customer":
        c.execute("SELECT * FROM CUSTOMER WHERE CUSTOMER_Email=?", (email,))
        if c.fetchone():
            conn.close()
      
            return redirect(url_for("register"))
        else: c.execute("INSERT INTO CUSTOMER (CUSTOMER_Username, CUSTOMER_Email, CUSTOMER_Password, CUSTOMER_TELL, CUSTOMER_Role) VALUES (?, ?, ?, ?, ?)",
                  (username, email, password, tell, role))

    conn.commit()
    conn.close()
   
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
        else:
            flash("อีเมลหรือรหัสผ่านสำหรับแอดมินไม่ถูกต้อง", "danger")

    elif role == "Customer":
        c.execute("SELECT * FROM CUSTOMER WHERE CUSTOMER_Email=? AND CUSTOMER_Password=?", (email, password))
        user = c.fetchone()
        if user:
            session['customer_id'] = user['CUSTOMER_ID']
            conn.close()
            return redirect(url_for("customer_home"))
        else:
            flash("อีเมลหรือรหัสผ่านสำหรับลูกค้าไม่ถูกต้อง", "danger")

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
    CATALOG_Number = request.form['CATALOG_Number']
    TYPE_FK = request.form['TYPE_FK']
 
    file = request.files['CATALOG_Image']
    filename = None
    if file:
        filename = os.path.join(app.config['uploads'], file.filename)
        file.save(filename)

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("INSERT INTO CATALOG (TYPE_FK, CATALOG_Name, CATALOG_Price, CATALOG_Image, CATALOG_Detail, CATALOG_Brand, CATALOG_Number) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (TYPE_FK, CATALOG_Name, CATALOG_Price, filename, CATALOG_Detail, CATALOG_Brand,CATALOG_Number))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_insert_data"))


@app.route('/submit_cart', methods=['POST'])
def submit_cart():
    if 'customer_id' not in session:
        flash("กรุณาเข้าสู่ระบบก่อนเพิ่มสินค้าในตะกร้า", "warning")
        return redirect(url_for("login"))

    customer_id = session['customer_id']
    CATALOG_ID = request.form['CATALOG_ID']
    CART_Name = request.form['CART_Name']
    CART_Price = request.form['CART_Price']
    CART_Detail = request.form['CART_Detail']
    CART_Brand = request.form['CART_Brand']
    CART_Quantity = int(request.form.get('CART_Quantity', 1))

    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute(
    "INSERT INTO CART (CART_Name, CART_Price, CART_Detail, CART_Brand, CUSTOMER_ID, CART_Quantity, CATALOG_ID) VALUES (?, ?, ?,?, ?, ?, ?)",
    (CART_Name, CART_Price, CART_Detail, CART_Brand, customer_id, CART_Quantity,CATALOG_ID)
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
    return redirect(url_for("admin_insert_data"))



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


@app.route('/customer_home_equipment')
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

    total_price = sum(float(item["CART_Price"]) * item["CART_Quantity"] for item in cart_items)

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


@app.route("/checkout_cart")
def checkout_cart():
    if "customer_id" not in session:
        flash("กรุณาเข้าสู่ระบบก่อน", "danger")
        return redirect(url_for("login"))

    customer_id = session["customer_id"]

    with sqlite3.connect("ELEC_DB.db") as conn:
        c = conn.cursor()

      
        c.execute("SELECT CATALOG_ID, CART_Quantity FROM CART WHERE CUSTOMER_ID=?", (customer_id,))
        cart_items = c.fetchall()

        for catalog_id, qty in cart_items:
            # ตรวจสอบจำนวน stock ปัจจุบัน
            c.execute("SELECT CATALOG_Number FROM CATALOG WHERE CATALOG_ID=?", (catalog_id,))
            stock_row = c.fetchone()

            if stock_row is None:
                flash("ไม่พบข้อมูลสินค้าบางรายการ", "danger")
                return redirect(url_for("customer_cart"))

            stock = stock_row[0]

            if stock >= qty:
                # ลดจำนวนสินค้าในสต็อก
                c.execute("""
                    UPDATE CATALOG
                    SET CATALOG_Number = CATALOG_Number - ?
                    WHERE CATALOG_ID=?
                """, (qty, catalog_id))
            else:
                flash("สินค้าบางรายการมีจำนวนไม่เพียงพอ", "danger")
                return redirect(url_for("customer_cart"))

        # ลบตะกร้าหลังสั่งซื้อสำเร็จ
        c.execute("DELETE FROM CART WHERE CUSTOMER_ID=?", (customer_id,))
        conn.commit()

    return render_template("checkout_success.html")



@app.route('/update_cart_quantity/<int:cart_id>/<action>')
def update_cart_quantity(cart_id, action):
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    customer_id = session['customer_id']

    with sqlite3.connect("ELEC_DB.db") as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # ดึงจำนวนปัจจุบัน
        c.execute("SELECT CART_Quantity FROM CART WHERE CART_ID=? AND CUSTOMER_ID=?", (cart_id, customer_id))
        row = c.fetchone()

        if row is None:
            flash("ไม่พบสินค้าในตะกร้า", "danger")
            return redirect(url_for('customer_cart'))

        quantity = row['CART_Quantity']

        # อัปเดตตาม action
        if action == 'increase':
            quantity += 1
        elif action == 'decrease' and quantity > 1:
            quantity -= 1

        c.execute("UPDATE CART SET CART_Quantity=? WHERE CART_ID=? AND CUSTOMER_ID=?", (quantity, cart_id, customer_id))
        conn.commit()

    return redirect(url_for('customer_cart'))




if __name__ == "__main__":
    app.run()