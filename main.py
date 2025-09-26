from flask import Flask,render_template, redirect ,request,url_for, flash, session
import sqlite3
import os



app = Flask(__name__)


app.config['uploads'] = 'static/uploads'

os.makedirs(app.config['uploads'], exist_ok=True)



def get_db_connection(): #connection DataBase
    conn = sqlite3.connect("ELEC_DB.db") #connect "DB1.db"
    conn.row_factory = sqlite3.Row #convert to dictionary
    return conn

@app.route('/review')
def review():
    return render_template("review.html")
                           

@app.route('/basket')
def basket():
    return render_template("basket.html")

@app.route('/contract')
def contract():
    return render_template("contract.html")

@app.route('/about')
def about():
    return render_template("about.html")



@app.route('/homeElectronic')
def homeElectronic():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() #ดึงข้อมูลจากตาราง MENU
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    
    
    conn.close()
    return render_template("home Electronic.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)






@app.route('/homeled')
def homeled():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() #ดึงข้อมูลจากตาราง MENU
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    
    
    conn.close()
    return render_template("home led.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)




@app.route('/homeEquipment')
def homeEquipment():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() #ดึงข้อมูลจากตาราง MENU
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    
    
    conn.close()
    return render_template("home Equipment.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)




@app.route('/home')
def home():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() #ดึงข้อมูลจากตาราง MENU
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    
    
    conn.close()
    return render_template("home.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)


@app.route('/')
def Home1():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() #ดึงข้อมูลจากตาราง MENU
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE TYPE_FK = 3").fetchall()
    
    
    conn.close()
    return render_template("home.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)



@app.route("/register")
def register():
    return render_template("register.html")                             




@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['ACTOR_Email']
        password = request.form['ACTOR_Password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM ACTOR WHERE ACTOR_Email = ? AND ACTOR_Password = ?", 
                            (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['ACTOR_ID']
            session['email'] = user['ACTOR_Email']
            flash("Login Success!", "success")
            return redirect(url_for("/home"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")






@app.route('/insert_data')
def insert_data():
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM CATALOG")
    catalog = conn.execute("SELECT * FROM CATALOG").fetchall() #ดึงข้อมูลจากตาราง MENU
    Equipment = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 1").fetchall()
    led = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 2").fetchall()
    Electronic = conn.execute("SELECT * FROM CATALOG WHERE CATALOG_ID = 3").fetchall()
    
    conn.close()
    return render_template("insert_data.html", catalog = catalog, Equipment=Equipment, led=led, Electronic=Electronic)

@app.route("/submit", methods=["POST"])
def submit():
    CATALOG_Name = request.form['CATALOG_Name']
    CATALOG_Brand = request.form["CATALOG_Brand"]
    CATALOG_Detail = request.form["CATALOG_Detail"]
    CATALOG_Price = request.form['CATALOG_Price']
    TYPE_FK = request.form['TYPE_FK']
    
    
    # รับไฟล์
    file = request.files['CATALOG_Image']
    filename = None
    if file:
        filename = os.path.join(app.config['uploads'], file.filename)
        file.save(filename)

    # บันทึกลง DB
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("INSERT INTO CATALOG (TYPE_FK, CATALOG_Name, CATALOG_Price, CATALOG_Image, CATALOG_Detail, CATALOG_Brand) VALUES (?, ?, ?, ?, ?, ?)",
              (TYPE_FK, CATALOG_Name, CATALOG_Price, filename, CATALOG_Detail, CATALOG_Brand))
    conn.commit()
    conn.close()

    return redirect(url_for("insert_data"))



@app.route("/submit_register", methods=["POST"])
def submit_register():
    ACTOR_Username = request.form['ACTOR_Username']
    ACTOR_Email = request.form["ACTOR_Email"]
    ACTOR_Password = request.form["ACTOR_Password"]
    ACTOR_TELL = request.form["ACTOR_TELL"]
    ACTOR_Role = request.form['ACTOR_Role']
    
    


    # บันทึกลง DB
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("INSERT INTO ACTOR (ACTOR_Username, ACTOR_Email, ACTOR_Password, ACTOR_Role, ACTOR_TELL) VALUES (?, ?,?, ?, ?)",
              (ACTOR_Username, ACTOR_Email, ACTOR_Password, ACTOR_Role, ACTOR_TELL))
    conn.commit()
    conn.close()

    return redirect(url_for("register"))








@app.route("/delete/<int:CATALOG_ID>")
def delete(CATALOG_ID):
    conn = sqlite3.connect("ELEC_DB.db")
    c = conn.cursor()
    c.execute("SELECT CATALOG_Image FROM CATALOG WHERE CATALOG_ID=?", (CATALOG_ID,))
    row = c.fetchone()
    if row and row[0]:
        try:
            os.remove(row[0])  # ลบไฟล์ภาพออกจากโฟลเดอร์
        except FileNotFoundError:
            pass
    c.execute("DELETE FROM CATALOG WHERE CATALOG_ID=?", (CATALOG_ID,))
    conn.commit()
    conn.close()
    return redirect(url_for("insert_data"))



if __name__ == "__main__":
    app.run()