from flask import Flask,render_template,request
import sqlite3
import os

currentdir = os.path.dirname(os.path.abspath(__file__))
app =Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/',methods=["POST","GET"])
def log():
    name= request.form['fullname']
    email= request.form['email']
    cell= (int)(request.form['phonenumber'])
    connection = sqlite3.connect(currentdir + "\phoneapp.db")
    cur = connection.cursor()
    cur.execute("insert into booking(NAME,EMAIL,CELL) values(?,?,?)",(name,email,cell))
    connection.commit()
    return render_template('result.html')


if __name__ == "__main__":
    app.run(debug=True)