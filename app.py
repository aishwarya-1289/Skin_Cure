# flask application
import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from skimage import io
from tensorflow.keras.preprocessing import image


# Flask utils
from flask import Flask, redirect, url_for, request, render_template, session
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
import mysql.connector

con=mysql.connector.connect(host='127.0.0.1',user='root',password='1289',database='SkinCure')
cursor=con.cursor()



# connection = mysql.connector.connect(host='127.0.0.1',
#                                      database='SkinCure',
#                                      user='root',
#                                      password='1289')

# cursor = connection.cursor()
# Define a flask app
app = Flask(__name__)
@app.route('/login_validation',methods=['POST'])
def login_validation():
    username=request.form.get('username')
    password=request.form.get('password')
    cursor.execute("select *from users WHERE username = %s AND password = %s " ,(username,password))


    users = cursor.fetchall()
    if len(users)>0:
        session['id']=users[0][0]
        return redirect('/index')
    else:

        return redirect('/') 
    
@app.route("/add_user",methods=['POST'])
def add_user():
    username=request.form.get('rusername')
    password=request.form.get('rpassword')
    email=request.form.get('remail')
    cursor.execute("INSERT INTO users (username,password,email) VALUES(%s,%s,%s)",(username,password,email))
    con.commit()
    

    cursor.execute("select *from users WHERE email = %s ",[email])
    myuser=cursor.fetchall()
    session['id']=myuser[0][0]
    return redirect('/index')
# app.secret_key = "super secret key"
# Model saved with Keras model.save()

# Can also use pretrained model from Keras                                                     
# Check https://keras.io/applications/

model =tf.keras.models.load_model('VGG16_Model1.h5',compile=False)
# model =tf.keras.models.load_model('CNN2.h5',compile=False)


print('Model loaded. Check http://127.0.0.1:4050/')


def model_predict(img_path, model):
    img = image.load_img(img_path, grayscale=False, target_size=(224, 224))
    show_img = image.load_img(img_path, grayscale=False, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = np.array(x, 'float32')
    x /= 255
    preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def register():
    # Main page
    # return render_template('index.html',username = session['username'])
    return render_template('register.html')

@app.route('/index')
def index():
    # Main page
    # return render_template('index.html',username = session['username'])
    return render_template('index.html')


# @app.route("/login",methods = ['GET','POST'])
# def login():
#     msg = ''
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         cursor.execute('SETECT * FROM user WHERE username=%s AND password=%s',(username,password))
#         record = cursor.fetchone()

#         if record:
#             session['loggedin'] = True
#             session['username'] = record[1]
#             return redirect(url_for('index'))
#         else:
#             msg = 'Incorrect Username or Password!!'

#     return render_template('login.html',msg=msg)


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        print('preds',preds[0])

        # x = x.reshape([64, 64]);
        disease_class = ['Basal Cell Carinoma', 'Benign Keratosis like Lesions', 'Eczema',
                         'Melanoma']
        a = preds[0]
        ind=np.argmax(a)
        print('Prediction:', disease_class[ind])
        prob = str(preds[0][ind] * 100)[:4]+"%"
        print('Probablity:',prob)
        result=[disease_class[ind],prob] #added array and prob
        return result  

    return None


@app.route('/offline.html')
def offline():
    return app.send_static_file('offline.html')


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080, debug=True)

    # Serve the app with gevent
    # http_server = WSGIServer(('', 4050), app)
    http_server.serve_forever()
    app.run()
