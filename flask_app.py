from flask import Flask, request, jsonify, send_from_directory, render_template, flash, redirect, url_for
from passlib.hash import md5_crypt
from forms import MyForm, LoginForm, TestimonyForm 
from models import User, Make_request, Testimonial, app, db, LoginManager, login_required, login_user, logout_user, current_user, Bet_49ja, Financial_data, Transaction_Table, current_user
from bet_49ja import bet_49ja_script
from is_safe_url import is_safe_url
from schema import user_schema
from flask_humanize import Humanize
from datetime import datetime
from pypaystack import Transaction, Customer, Plan
from mailing_server import mail_folks
import boto3, botocore, time, hashlib, hmac, json, os, shutil, request_func, mailing_server, basic_auth, string, random
# plesa login
humanize = Humanize(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "please login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/callback", methods=["POST", "GET"])
def paycallback():
    if request.method == "POST":
        data = request.json
        event = data.get("event")
        if event == "charge.success" and request.headers.get("X-Forwarded-For") in ['52.31.139.75', '52.49.173.169', '52.214.14.220']:
            reference = data["data"].get("reference")
            amount = data["data"].get('amount')
            email = data["data"].get('customer').get('email')
            cus_code = data["data"].get('customer').get('customer_code')
            paid_at = data["data"].get('paidAt')
            auth_code = data["data"].get('authorization').get('authorization_code')
            paid_time = datetime.now()
            get_transaction = Transaction_Table.query.filter_by(ref_no=reference).first()
            get_transaction.amount = amount
            get_transaction.auth_code = auth_code
            get_transaction.cus_code =  cus_code
            get_transaction.email = email
            get_transaction.paid_at = paid_time
            # Update User Table to reflect the payment made
            update_user = User.query.filter_by(email=email).first()
            # email=user_email, 
            update_user.bet_49ja.is_paid_bot = True
            update_user.bet_49ja.bot_type = "paid"
            update_user.bet_49ja.has_compiled = False
            update_user.bet_49ja.is_demo = False
            # Commit the changes
            db.session.commit()
            
        return f"{request.json}"
    else:
        return redirect("/dashboard")


@app.route("/notify-and-compile")
def compile_paid_bot():
    user_bet9ja_name = request.args.get("q")
    username = current_user.username
    id = current_user.id
    update_user = User.query.filter_by(id=id, email=email).first()
    update_user.bet_49ja.is_building = True
    update_user.bet_49ja.has_compiled = False
    update_user.bet_49ja.bet9ja_username = user_bet9ja_name 
    db.session.commit()
    # Mail Admin
    email = ods.environ.get("email") 
    subject = "I have paid and there by requesting for my bot"
    body = f"I have paid through paystack and I am hereby requesting for my 49ja bot, My bet9ja Username is {user_bet9ja_name}, My username is {user_name}"
    mail_folks(email, subject, body)
    # Mail Client
    email = current_user.email
    subject = "You request is processing"
    body = f"Hi {user_name}, We have started building your bot and you will get notified when done, If the bot building takes too long, Make a Request on our site that would notify us"
    mail_folks(email, subject, body)
    
    return "peace"

@app.route("/paystack")
def main():

    """
    All Response objects are a tuple containing status_code, status, message and data
    """
    # print(dir(request))
    email = current_user.email
    
    paystack_secret = os.environ.get("paystack_test")
    bot_price = 25000 * 100
    #Instantiate the transaction object to handle transactions.  
    #Pass in your authorization key - if not set as environment variable PAYSTACK_AUTHORIZATION_KEY
    # email = "dataslid@gmail.com" "sk_test_faadf90960bad25e6a2b5c9be940792f928b73ac"
    transaction = Transaction(authorization_key=paystack_secret)
    transaction_table = Transaction_Table.query.filter_by(email=email).first()
    if transaction_table:
        response = transaction.charge(email, f"{transaction_table.auth_code}", int(transaction_table.amount)) #+rge a customer N100.
        print(response)
        reference = response[3].get('reference')
        transaction = Transaction_Table(ref_no=reference)
        db.session.add(transaction)
        db.session.commit()
        return redirect('/dashboard')
    else:
        init_transaction = transaction.initialize(email, bot_price)
        reference = init_transaction[3].get('reference')
        transaction = Transaction_Table(ref_no=reference)
        db.session.add(transaction)
        db.session.commit()
        return redirect(init_transaction[3].get('authorization_url'))
    





# Redirect / to home
@app.route("/", methods=["GET"])
def no_route():
    return redirect(url_for("home"))
    
@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/search-admin", methods=["GET"])
@login_required
def search():
    name = request.args.get("q")
    users = User.query.filter(User.username.like(f"%{name}%")).all()
    users_list = user_schema.dump(users)
    return {"users": users_list}

@app.route("/my-admin", methods=["GET"])
@login_required
def admin():
    users = User.query.all()
    return render_template("admin.html", users=users)
    

@app.route("/manage-user", methods=["GET", "POST"])
@login_required
def manage_user():
    id =  request.args.get("id")
    user = User.query.get(id)
    if request.method == "POST":
        # print(request.form)
        update_pay = request.form.get("pay")
        update_admin = request.form.get("admin")
        update_building = request.form.get("building")
        user.is_admin = bool(update_admin)
        user.bet_49ja.is_building = bool(update_building)
        user.bet_49ja.is_paid_bot = bool(update_pay)
        if bool(update_pay):
            user.bet_49ja.bot_type = "paid"
        else:
            user.bet_49ja.bot_type = "demo"
            
        db.session.commit()
        # Get files from Admin
        botapp = request.files.get('botapp')
        # print(botapp)
        if botapp:
            filename = botapp.filename
            file_ext = filename.split('.')[1]
            if file_ext == "exe":
                storage_key = os.environ.get("aws_key")
                storage_secret = os.environ.get("aws_secret")
                storage_bucket = "betbots"
                conn = boto3.client(
                    's3',
                    aws_access_key_id=storage_key,
                    aws_secret_access_key=storage_secret
                    )

                key = f'user_bots/{filename}'
                conn.upload_fileobj(botapp, storage_bucket, key)
                user.bet_49ja.is_building = False
                user.bet_49ja.has_compiled = True
                user.bet_49ja.bot_path = key
                db.session.commit()

                flash(f"You have successfully update {user.username}'s ability and has uploaded files to S3")
            else:
                flash(f"The file uploaded must be an exe")

        flash(f"You have successfully update {user.username}'s ability")
        return redirect(f"/manage-user?id={user.id}")

    return render_template("manage_user.html", user=user)

@app.route("/testimony", methods=["GET", "POST"])
def testimony():
    form = TestimonyForm()
    testimonies = Testimonial.query.order_by(Testimonial.datetime.desc()).all()[:5]

    if request.method == "POST" and form.validate_on_submit():
        text = form.testimony.data
        testimony = Testimonial(testimony=text, user_id=current_user.id, datetime=datetime.now())
        db.session.add(testimony)
        db.session.commit()
        flash(f"Thanks {current_user.username}, for dropping your testimony") 
        return redirect(url_for("testimony"))
    
    return render_template("testimony.html", form=form, testimonies=testimonies)


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and md5_crypt.verify(password, user.password):
            login_user(user)
            next_page = request.args.get("next")
            is_safe_url(next_page, request.url)
            if is_safe_url(next_page, request.url):
                return redirect(next_page)
            return redirect("/dashboard") 
        else:
            flash("e-mail or password is incorrect")
            return redirect("/login")
    else:
        return render_template("login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = MyForm()
    if request.method == "POST" and form.validate_on_submit():
        password = form.password.data
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        password = md5_crypt.hash(password)
        check_for_first_user = len(User.query.all())
        if not check_for_first_user:
            user = User(username=name, is_admin=True, email=email, phone=phone, password=password)
        else:
            user = User(username=name, is_admin=False, email=email, phone=phone, password=password)
        in_49ja = Bet_49ja(user_id=user.id)
        db.session.add(in_49ja)
        db.session.add(user)
        db.session.commit()
        # Instantiating the 49ja Table
        in_49ja = Bet_49ja(user_id=user.id)
        db.session.add(in_49ja)
        db.session.commit()
        flash("You have signed up successfully")    
        return redirect('/login')
    else:
        return render_template("sign_up.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash("You've logged out successfully, do visit soon")
    return redirect(url_for("login"))

# @app.route("/bought-bot?id=", methods=["GET"])
# def download():
#     return render_template("home.html")

@app.route("/subscribe", methods=["GET"])
def subscribe():
    user_id = request.args.get("q")
    price = request.args.get("price")
    expire_time = time.time() + (86400 * 31 )
    user_sub = Bet_49ja.query.filter_by(user_id=user_id).first()
    user_sub.is_subscribe = True
    user_sub.bot_type = "subscribe"
    user_sub.sub_exp_date = expire_time
    fin_data = Financial_data(price=price, user_id=user_id, bot_type="subscribe", datetime=datetime.now())
    db.session.add(fin_data)
    db.session.commit()
    email = fin_data.user.email
    subject = "Thanks for subscribing to Dataslid 49ja bot for this month"
    message = "We are glad that you subcribed to our 49ja's monthly plans, follow a bankroll, be consistent by runing the bot daily and at the end you will be glad you that you subcribed"
    try:
        mail_folks(email, subject, message)
        mail_folks("dataslid@gmail.com", "someone just subscribed to the 49ja bot", f"We just made {price} because {fin_data.user.username} subscribed to the 49ja bots")
    except Exception as exc:
        return jsonify({"ok": "true", "err": f"something went wrong {str(exc)}"})    
    return jsonify({"ok": "true"})

@app.route("/has_subscribed", methods=["GET"])
def check_subscription():
    user_id = request.args.get("q")
    now = time.time()
    check = Bet_49ja.query.filter_by(user_id=user_id, is_subscribe=True).first()
    if check:
        if now < float(check.sub_exp_date):
            return jsonify({"result": "true"})
        else:
            return jsonify({"result": ""})
    else:
        return jsonify({"result": ""})

@app.context_processor
def context_processor():
    request_alert = Make_request.query.filter_by(not_seen=True).all()
    alert = False
    if request_alert:
        alert = True
    return dict(alert=alert)

if __name__  == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")