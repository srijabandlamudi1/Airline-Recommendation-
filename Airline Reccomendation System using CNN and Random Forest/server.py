from flask import Flask, render_template, request, redirect, session, flash
from mysqlconn import connectToMySQL
from flask_bcrypt import Bcrypt 
import re
import scrape_reviews as sr
import CNN as cn
import CNNReview as cnr
import RF as raf
import RFReview as rfr
import Recommend as rec


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'
bcrypt = Bcrypt(app)
@app.route("/")
def index():
    db= connectToMySQL('registration')
    user = db.query_db('SELECT * FROM user;')
    return render_template("index.html", all_people = user)
    

@app.route("/createdatabase")
def createdabase():
	sr.getReview()
	flash("Dataset Created")
	return redirect("/welcome")



@app.route("/create", methods=["POST"])
def create():
    is_valid = True		
    if len(request.form['first_name']) < 1:
        is_valid = False 
        flash("Please enter a first name")
    elif 'first_name'.isalpha() == True:
        is_valid = False
        flash("All characters are not alphabets")
    
    else:
        print("All characters are alphabets.")

    if len(request.form['last_name']) < 1: 
        is_valid = False 
        flash("Please enter a last name")
    elif 'last_name'.isalpha() == True:  
        is_valid = False
        flash("All characters are not alphabets.") 
    else:
        print("All characters are alphabets.")
    
    if len(request.form['email']) < 2:
        is_valid = False
        flash("Please enter a valid email")
    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!")

        # User.objects.all()
        # User.objects.get(ID=5)
        # if not User.objects.filter(email="asdf"):
    else:
        db = connectToMySQL("registration")
        query = "SELECT email from user WHERE email = %(email)s;"
        data = {
            "email": request.form['email']

        }
        result = db.query_db(query,data)
        print(result)
        if len(result) > 0:
            is_valid = False
            flash("Email already exists!")

    if len(request.form['password']) < 8:
        flash("Please enter a valid password")

    if request.form['c_password'] != request.form['password']:
        is_valid = False
        flash("Password does not match")
    
    if is_valid==True:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])  
        print(pw_hash) 
        query = "INSERT INTO user (first_name, last_name, email, password, created_on, updated_on) VALUES (%(fn)s, %(ln)s, %(email)s, %(pass_hash)s, NOW(), NOW());"
        data = {
            "fn": request.form["first_name"],
            "ln": request.form["last_name"],
            "email": request.form["email"],
            "pass_hash" : pw_hash.decode('utf-8')
        }
        db = connectToMySQL('registration')
        flash("Successfully added")
        userid = db.query_db(query,data)
        print("userid",userid)
        session['userid'] = userid
        return redirect("/welcome")
    else:
        return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    # match = True
    db = connectToMySQL("registration")
    query = "SELECT * from user WHERE email = %(email)s;"
    data = {
        "email": request.form["email"]

    }
    result = db.query_db(query,data)

    print(result)

    if len(result) == 0:
        flash("Email not found, please register!")
        return redirect("/")

    else:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']) == True:
            session['userid'] = result[0]['id']
            return redirect("/welcome")
        else:
            flash("Password does not match!")
            return redirect("/")
            
@app.route("/welcome")
def welcome():
    if 'userid' not in session:
        flash("you must log in first")
        return redirect("/")

    query = "SELECT * FROM user WHERE id=%(id)s;"
    data = {
        "id": session['userid']
    }
    db = connectToMySQL('registration')
    userData = db.query_db(query, data)
    return render_template("welcome.html", userData=userData[0])


@app.route("/RFPage")
def RFPage():
    if 'userid' not in session:
        flash("you must log in first")
        return redirect("/")

    query = "SELECT * FROM user WHERE id=%(id)s;"
    data = {
        "id": session['userid']
    }
    db = connectToMySQL('registration')
    userData = db.query_db(query, data)
    return render_template("RFPage.html", userData=userData[0])
        
@app.route("/RFALG", methods=["POST"])
def RFALG():
	f=request.form['method']
	print("method",f)
	result=-1
	if f=="rate":
		raf.process()
		flash("Rating Based RandomForest")
		result=0
	if f=="review":
		print("method",f)
		rfr.process()
		flash("Review Based RandomForest")
		result=1
	if 'userid' not in session:
		flash("you must log in first")
		return redirect("/")
	query = "SELECT * FROM user WHERE id=%(id)s;"
	data = {
		"id": session['userid']
	}
	db = connectToMySQL('registration')
	userData = db.query_db(query, data)
	return render_template("RFPage.html", userData=userData[0],result=result)


@app.route("/CNNPage")
def CNNPage():
    if 'userid' not in session:
        flash("you must log in first")
        return redirect("/")

    query = "SELECT * FROM user WHERE id=%(id)s;"
    data = {
        "id": session['userid']
    }
    db = connectToMySQL('registration')
    userData = db.query_db(query, data)
    return render_template("CNNPage.html", userData=userData[0])


@app.route("/CNNALG", methods=["POST"])
def CNNALG():
	f=request.form['method']
	print("method",f)
	result=-1
	if f=="rate":
		cn.process()
		flash("Rating Based CNN")
		result=0
	if f=="review":
		print("method",f)
		cnr.process()
		flash("Review Based CNN")
		result=1
	if 'userid' not in session:
		flash("you must log in first")
		return redirect("/")
	query = "SELECT * FROM user WHERE id=%(id)s;"
	data = {
		"id": session['userid']
	}
	db = connectToMySQL('registration')
	userData = db.query_db(query, data)
	return render_template("CNNPage.html", userData=userData[0],result=result)


@app.route("/RecommendPage")
def RecommendPage():
    if 'userid' not in session:
        flash("you must log in first")
        return redirect("/")

    query = "SELECT * FROM user WHERE id=%(id)s;"
    data = {
        "id": session['userid']
    }
    db = connectToMySQL('registration')
    userData = db.query_db(query, data)
    return render_template("RecommendPage.html", userData=userData[0])

@app.route("/Recommend1", methods=["POST"])
def Recommend1():
	src=request.form['src']
	dest=request.form['dest']
	seat=request.form['seat']
	cabin=request.form['cabin']
	food=request.form['food']
	ent=request.form['ent']
	ground=request.form['ground']
	money=request.form['money']
	recom,nonrecom=rec.process(src,dest,seat,cabin,food,ent,ground,money)
	print(recom)
	print(nonrecom)
	#result="Recommended airlines is " + recom
	#flash(result)
	if 'userid' not in session:
		flash("you must log in first")
		return redirect("/")
	query = "SELECT * FROM user WHERE id=%(id)s;"
	data = {
		"id": session['userid']
	}
	db = connectToMySQL('registration')
	userData = db.query_db(query, data)
	return render_template("RecommendPage.html", userData=userData[0],result=recom,result1=nonrecom)


@app.route("/logout", methods=["POST"])
def logout():
    query = "SELECT * FROM user WHERE id=%(id)s;"

    data = {
        "id": session['userid']
    }
    db = connectToMySQL('registration')
    userData = db.query_db(query, data)
    
    session.clear()
    return redirect("/")








if __name__ == "__main__":
    app.run(debug=True)



#pull up all the emails in database
#scond query is to find out if the users email is in the database.
#compare password with password in the system