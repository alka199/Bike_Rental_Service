from flask import Flask, redirect, render_template,request,flash, request_started,url_for,session
from flask_mail import *
from user import user_operation
from provider import provider_operation
from captcha.image import ImageCaptcha
import random
import hashlib
from datetime import datetime
import speech_recognition as sr

app = Flask(__name__)

app.secret_key = "hkldsjfklds78784hdsy787i"
#-------------------mail configuration---------------------------
app.config["MAIL_SERVER"]='smtp.office365.com'
app.config["MAIL_PORT"] = '587'
app.config["MAIL_USERNAME"] = 'alkakumari2022@outlook.com'
app.config["MAIL_PASSWORD"]= 'Mk162@25'
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
mail = Mail(app)
#----------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


#------------------user sign up pages--------------------------------------------------
@app.route('/user_signup')
def user_signup():
    num=random.randrange(1000,9999)
    # Create an image instance of the given size
    img = ImageCaptcha(width = 280, height = 90)

    # Image captcha text
    global captcha_text
    captcha_text = str(num)
 
    # write the image on the given file and save it
    img.write(captcha_text, 'static/images/CAPTCHA.png')
    return render_template('user_signup.html')
#-------------------------------------------------------------------------------------------
@app.route('/user_signup_insert',methods=['GET','POST'])
def user_signup_insert():
    if request.method=='POST': 
        if captcha_text!=request.form["captcha"]:
                        flash("invalid captcha!!!")
                        return render_template('user_signup.html')

        name=request.form["name"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        password=request.form["password"]
        #--- password hashing----------------
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()
        #---------user insert-----------------
        op = user_operation()  # object create
        op.user_signup_insert(name,email,mobile,password)
        #------- email verification--------------------------------
        global otp
        otp = random.randint(100000,999999)
        msg = Message('Email verification',sender = 'alkakumari2022@outlook.com', recipients = [email])
        msg.body = "Hi "+ name + "\nYour email OTP is: " + str(otp)
        mail.send(msg)
        return render_template('email_verify.html',email=email)
#-----------------------------------------------------------------------------------------------------------
@app.route('/email_verify',methods=['GET','POST'])
def email_verify():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        flash("Your Email is Verified.. You can Login Now!!!")
        return redirect(url_for('user_login'))
    email=request.form['email']
    op = user_operation()  # object create
    op.user_delete(email)
    flash("Your Email verification is failed... Register with Valid Email!!!")
    return redirect(url_for('user_signup'))

#------------------user login pages--------------------------------------------------
@app.route('/user_login')
def user_login():
    return render_template('user_login.html')
#----------------- User Login Verify -------------------------------------------------
@app.route('/user_login_verify',methods=['GET','POST'])
def user_login_verify():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        op = user_operation()
        r=op.user_login_verify(email,password)
        if r==0:
            flash("Invalid Email or Password")
            return redirect(url_for('user_login'))
        else:
            return redirect(url_for('user_dashboard'))

#------------- User LogOut----------------------------------------------------
@app.route('/user_logout')
def user_logout():
    session.clear()
    return redirect(url_for('user_login'))
#------------------------------------------------------------------------------

#------------- User Dashboard -----------------------------------------------
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_email' in session:
        return render_template('user_dashboard.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#---------------- User Profile -----------------------------------------------
@app.route('/user_profile')
def user_profile():
    if 'user_email' in session:
        op = user_operation()
        r=op.user_profile()
        return render_template('user_profile.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#-------------- User Profile Update -------------------------------------------------
@app.route('/user_profile_update',methods=['GET','POST'])
def user_profile_update():
    if 'user_email' in session:
        if request.method=='POST':
            name=request.form['name']
            mobile=request.form['mobile']
            op = user_operation()
            op.user_profile_update(name,mobile)
            flash("your profile is updated successfully!!!")
            return redirect(url_for('user_profile'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#--------------- User Bike ------------------------------------------------------------
@app.route('/user_bike')
def user_bike():
    if 'user_email' in session:
        return render_template('user_bike.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))
#--------------------------------------------------------------------------------------
@app.route('/user_bike_search',methods=['GET','POST'])
def user_bike_search():
    if 'user_email' in session:
        if request.method=='POST':
            city=request.form['city']
            op = user_operation()
            r=op.user_bike_search(city)
            return render_template('user_bike.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))
#--------------------------------------------------------------------------------------
@app.route('/user_bike_voice_search',methods=['GET','POST'])
def user_bike_voice_search():
    if 'user_email' in session:
        r = sr.Recognizer()
        with sr.Microphone() as source:
        # read the audio from the default microphone
         audio_data = r.record(source, duration=5)
         #covert speech to text
         city = r.recognize_google(audio_data)
         # text = r.recognize-google (audio_data, language="es-ES")
        op = user_operation()
        r=op.user_bike_search(city)
        return render_template('user_bike.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#-----------------User Bike Date-------------------------------------------------------
@app.route('/user_bike_date',methods=['GET','POST'])
def user_bike_date():
    if 'user_email' in session:
        if request.method=='GET':
            bike_id=request.args.get('bike_id')
            provider_id=request.args.get('provider_id')
            charges=request.args.get('charges')
            return render_template('user_bike_date.html',bike_id=bike_id,provider_id=provider_id,charges=charges)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#---------------------User Bike Date Insert--------------------------------------------
@app.route('/user_bike_date_insert',methods=['GET','POST'])
def user_bike_date_insert():
    if 'user_email' in session:
        
        if request.method=='POST':
            bike_id=request.form['bike_id']
            provider_id=request.form['provider_id']
            start_date=request.form['start_date']
            end_date=request.form['end_date']
            charges=request.form['charges']
            op = user_operation()
            op.user_bike_date_insert(bike_id,provider_id,start_date,end_date,charges)

            flash("Bike booking is confirm!!!")
            return redirect(url_for('user_dashboard'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))
#---------------------------------------------------------------------------------------
@app.route('/user_rent_view')
def user_rent_view():
    if 'user_email' in session:
        op = user_operation()
        r=op.user_rent_view()
        return render_template('user_rent_view.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#-----------------------------------------------------------------------------------------------
@app.route('/user_review',methods=['GET','POST'])
def user_review():
    if 'user_email' in session:
        if request.method == 'GET':
            bike_id=request.args.get('bike_id')
            op = user_operation()
            r=op.user_review(bike_id)
            return render_template('user_review.html',rec=r,bike_id=bike_id)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#-------------------------------------------------------------------------------------------------
@app.route('/user_review_insert',methods=['GET','POST'])
def user_review_insert():
    if 'user_email' in session:
        if request.method=='POST':
            bike_id=request.args.get('bike_id')
            star=request.form['star']
            message=request.form['message']
            op = user_operation()
            op.user_review_insert(bike_id,star,message)
            flash("Your review is submitted successfully!")
            return redirect(url_for('user_review',bike_id=bike_id))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#--------------------------------------------------------------------------------------
#------------------------------- provider routing--------------------------------------
#--------------------------------------------------------------------------------------
@app.route('/provider_signup')
def provider_signup():
    num=random.randrange(1000,9999)
    # Create an image instance of the given size
    img = ImageCaptcha(width = 280, height = 90)

    # Image captcha text
    global captcha_text1
    captcha_text1 = str(num)
 
    # write the image on the given file and save it
    img.write(captcha_text1, 'static/images/CAPTCHA1.png')
    return render_template('provider_signup.html')
#---------------------------------------------------------------------------------------
@app.route('/provider_signup_insert',methods=['GET','POST'])
def provider_signup_insert():
    if request.method=='POST': 
        if captcha_text1!=request.form["captcha"]:
                        flash("invalid captcha!!!")
                        return render_template('provider_signup.html')

        name=request.form["name"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        address=request.form["address"]
        city=request.form["city"]
        password=request.form["password"]
        #--- password hashing----------------
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()
        #---------provider insert-----------------
        op = provider_operation()  # object create
        rec=op.provider_signup_insert(name,email,mobile,address,city,password)
        for r in rec:
            flash("Your Provider ID is: "+ str(r[0])+"  ..... login now..")
        return render_template('provider_login.html')
#----------------------------------------------------------------------------------------
#------------------provider login pages--------------------------------------------------
@app.route('/provider_login')
def provider_login():
    return render_template('provider_login.html')
#-----------------------------------------------------------------------------------------
@app.route('/provider_login_verify',methods=['GET','POST'])
def provider_login_verify():
    if request.method=='POST':
        provider_id=request.form['provider_id']
        password=request.form['password']
        op = provider_operation()
        r=op.provider_login_verify(provider_id,password)
        if r==0:
            flash("Invalid ID or Password")
            return redirect(url_for('provider_login'))
        else:
            return redirect(url_for('provider_dashboard'))

#------------------------------------------------------------------------------------------
@app.route('/provider_logout')
def provider_logout():
    session.clear()
    return redirect(url_for('provider_login'))
#------------------------------------------------------------------------------------------
@app.route('/provider_dashboard')
def provider_dashboard():
    if 'provider_id' in session:
        return render_template('provider_dashboard.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#--------------------------------------------------------------------------------------------
@app.route('/provider_profile')
def provider_profile():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_profile()
        return render_template('provider_profile.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#--------------------------------------------------------------------------------------------------
@app.route('/provider_profile_update',methods=['GET','POST'])
def provider_profile_update():
    if 'provider_id' in session:
        if request.method=='POST':
            email=request.form['email']
            mobile=request.form['mobile']
            address=request.form['address']
            op = provider_operation()
            op.provider_profile_update(email,mobile,address)
            flash("your profile is updated successfully!!!")
            return redirect(url_for('provider_profile'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#-----------------------------------------------------------------------------------------------------
@app.route('/provider_bike')
def provider_bike():
    if 'provider_id' in session:
        return render_template('provider_bike.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#-------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_insert',methods=['GET','POST'])
def provider_bike_insert():
    if 'provider_id' in session:
        if request.method=='POST':
            model_name=request.form['model_name']
            reg_no=request.form['reg_no']
            charge=request.form['charge']
            mfg_date=request.form['mfg_date']
            descp=request.form['descp']
            # for photo upload
            photo=request.files["photo"]
            photo_name = photo.filename
            photo.save("static/bike/" + photo_name)
            #----bike insert-------------------
            op = provider_operation()
            op.provider_bike_insert(model_name,reg_no,charge,mfg_date,descp,photo_name)
            flash("your bike is inserted successfully!!!")
            return redirect(url_for('provider_bike'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#-------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_view')
def provider_bike_view():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_bike_view()
        return render_template('provider_bike_view.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#----------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_delete',methods=['GET','POST'])
def provider_bike_delete():
    if 'provider_id' in session:
        if request.method=='GET':
            bike_id=request.args.get('bike_id')
            op = provider_operation()
            op.provider_bike_delete(bike_id)
            flash("bike is deleted successfully!!!")
            return redirect(url_for('provider_bike_view'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#----------------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_profile',methods=['GET','POST'])
def provider_bike_profile():
    if 'provider_id' in session:
        if request.method=='GET':
            bike_id=request.args.get('bike_id')
            op = provider_operation()
            r=op.provider_bike_profile(bike_id)
            return render_template ('provider_bike_profile.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#------------------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_profile_update',methods=['GET','POST'])
def provider_bike_profile_update():
    if 'provider_id' in session:
        if request.method=='POST':
            bike_id=request.args.get('bike_id')
            model_name=request.form['model_name']
            reg_no=request.form['reg_no']
            charge=request.form['charge']
            mfg_date=request.form['mfg_date']
            descp=request.form['descp']
            op = provider_operation()
            op.provider_bike_profile_update(bike_id,model_name,reg_no,charge,mfg_date,descp)
            flash("Your Bike Details are Updated successfully!!!")
            return redirect(url_for('provider_bike_profile',bike_id=bike_id))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#--------------------------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_rent')
def provider_bike_rent():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_bike_rent()
        return render_template('provider_bike_rent.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#-----------------------------------------------------------------------------------------------------------------------------
@app.route('/provider_delete')
def provider_delete():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_delete()
        flash("you account is deleted successfully..join with us!")
        return redirect(url_for('provider_signup'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

if __name__=="__main__":
	app.run(debug =  True)
