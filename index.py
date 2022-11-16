from flask import Flask, request, render_template, redirect
import sqlite3 as sq3
import requests
import mariadb

user = None

API_KEY = "Im5Owvbo4HbMZgEjLP9zMlCv-d_kwEGOkQgNoDH5C38M"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]
error = 0 
exists = 0
reg = 0
miss = 0

app = Flask(__name__)

@app.route("/")
def redirct():
    return redirect("/login")
@app.route("/login")
def login():
    message = ""
    global error
    global reg
    date = False
    if error:
        date = True
        message = "Wrong Password"
        error = 0
    else:
        date = False

    if reg:
        date = True
        message = "Email Not Registered"
        reg = 0
    
    return render_template('login.html',date = date,message=message)


@app.route("/registration")
def registration():
    message = ""
    date = False
    global exists
    global miss
    if exists:
        date = True
        message = "Account Already Registered"
        exists = 0
    else:
        date = False
    if miss:
        miss = 0
        date = True
        message = "Password Not Match"
    return render_template('registration.html',date=date,message = message)





@app.route("/testing",methods = ["POST"])
def redir():
    data = request.form.to_dict()
    try:
        if data["password"] != data["re-enter"]:
            print("confirmation wrong")
            global miss
            miss = 1
            return redirect("/registration")
        conn = mariadb.connect(
            user="sql12575355",
            password="QUz4kAunlf",
            host="sql12.freesqldatabase.com",
            database="sql12575355"

        )
        cursor = conn.cursor()
        checkquery = "SELECT * FROM USERS WHERE EMAIL = '{}'".format(data["email"])
        cursor.execute(checkquery)
        flag = cursor.fetchall()
        if flag:
            global exists
            exists = 1
            return redirect("/registration")
        else:
            print("empty")
            query = "INSERT INTO USERS VALUES('{}','{}','{}')".format(data["name"],data["email"],data["password"])
            cursor.execute(query)
        
    except Exception as e:
        return redirect("/registration",code = 500)
    else:
        conn.commit()
        conn.close()
    return redirect("/login")





@app.route("/testing2",methods = ["POST"])
def redire():
    data = request.form.to_dict()
    try:
        conn = mariadb.connect(
            user="sql12575355",
            password="QUz4kAunlf",
            host="sql12.freesqldatabase.com",
            database="sql12575355"

        )
        cursor = conn.cursor()
        checkquery = "SELECT * FROM USERS WHERE EMAIL = '{}'".format(data["email"])
        cursor.execute(checkquery)
        out = cursor.fetchone()
        if not out:
            global reg
            reg = 1
            return redirect("/login")
        if out[2] != data["password"]:
            print(out[1],data["password"])
            global error
            error = 1
            return redirect("/login")
    except mariadb.Error as e:
        return str(e)
    else:
        conn.commit()
        conn.close()
        global user
        user = 1
    return redirect("/entryform")





@app.route("/entryform")
def entryform():
    if user:
        return render_template("entryform.html")
    else:
        return redirect("/login")





@app.route("/results",methods = ["POST"])
def results():
    data = request.form.to_dict()
    bp = float(data["bp"])
    bu = float(data["bu"])
    if data["dm"] == "Yes":
        dm = 1
    else:
        dm = 0
    hemo = float(data["hemo"])
    if data["htn"] == "Yes":
        htn = 1
    else:
        htn = 0
    if data["pc"] == "Abnormal":
        pc = 1
    else:
        pc = 0
    pcv = float(data["pcv"])
    if data["pe"] == "Yes":
        pe = 1
    else:
        pe = 0
    rc = float(data["rc"])
    sg = float(data["sg"])
    datas = [bp , bu , dm , hemo , htn , pc , pcv , pe , rc , sg]
    print(datas)
    payload_scoring = {"input_data": [{"fields": ["bp" , "bu" , "dm"  , "hemo" , "htn" , "pc" ,  "pcv" , "pe" , "rc" , "sg"], "values": [datas]}]}

    response_scoring = requests.post('https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/kidney_pred/predictions?version=2022-11-05', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + mltoken})
    result = response_scoring.json()["predictions"][0]["values"][0][0]
    if result:
        result = "Positive"
    else:
        result = "Negative"
    return render_template("results.html",result = result)





if __name__ == "__main__":
    app.run(debug=True)