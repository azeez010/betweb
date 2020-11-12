from flask import Flask, request, jsonify, send_from_directory, render_template, flash, redirect, url_for
from passlib.hash import md5_crypt
from forms import MyForm, LoginForm, TestimonyForm 
from models import User, Make_request, Testimonial, app, db, LoginManager, login_required, login_user, logout_user, current_user, Bet_49ja 
from bet_49ja import bet_49ja_script
from is_safe_url import is_safe_url
import os
import shutil
from schema import user_schema
from flask_humanize import Humanize
from datetime import datetime
import time


# flash msg = Message('Hello', sender = 'dataslid@gmail.com', recipients = [email])
# msg.body = f"Hello Flask message sent from Flask-Mail, the token is {random_generated} "
# self.mail.send(msg)

humanize = Humanize(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "plesa login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route("/admin", methods=["GET"])
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
        make_admin = bool(request.form.get("admin"))
        make_pay = bool(request.form.get("pay"))
        user.is_admin = make_admin
        if make_pay:
            user.bet_49ja.is_paid_bot = make_pay
            user.bet_49ja.bot_type = "paid"
        else:
            user.bet_49ja.is_paid_bot = make_pay
            user.bet_49ja.bot_type = "demo"
        db.session.add(user)
        db.session.commit()
        
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
        print("HAAAAA")
    return render_template("sign_up.html", form=form)



@app.route("/logout")
def logout():
    logout_user()
    flash("You've logged out successfully, do visit soon")
    return redirect(url_for("login"))

@app.route("/bought-bot?id=", methods=["GET"])
def bought_bot():
    return render_template("home.html")


@app.route("/paid", methods=["POST", "GET"])
def create():
    name = request.args.get("q")
    bet9ja = paid_49ja_script(name)

    with open(f"{name}.py", "w") as f:
        f.write(bet9ja)

    os.system(f"workon flask & pyinstaller --onefile --clean --name={name}_49ja {name}.py") 
    if "paid_folder" in os.listdir():
        app_name = f"{name}_49ja.exe"
        # Delete the application if it already exists
        if  app_name in os.listdir(os.path.join(os.getcwd(), "paid_folder")):
            os.remove(os.path.join(os.getcwd(), "paid_folder", app_name))

        shutil.move(os.path.join(os.getcwd(), "dist", f"{name}_49ja.exe"), os.path.join(os.getcwd(), "paid_folder"))
        os.remove(os.path.join(os.getcwd(), f"{name}_49ja.spec"))
        os.remove(os.path.join(os.getcwd(), f"{name}.py"))
        # Remove the remaining folder of dist
        for directory, folder, files in os.walk(os.path.join(os.getcwd(), "dist")):            
            for each_file in files:
                os.remove(os.path.join(directory, each_file))
        
        # Remove all the remaining files of build
        for directory, folder, files in os.walk(os.path.join(os.getcwd(), "build")):
            for each_file in files:
                os.remove(os.path.join(directory, each_file))
   
        # Remove the remaining folder of build 
        for i in os.listdir(os.path.join(os.getcwd(), "build")):
            os.rmdir(os.path.join(os.getcwd(), "build", i))

        os.rmdir(os.path.join(os.getcwd(), "build"))
        os.rmdir(os.path.join(os.getcwd(), "dist"))
        paid_path = os.path.join(os.getcwd(), "paid_folder", app_name)
        paid_info = Paid_49ja(user_id=current_user.id, is_updated=False, paid_bot=paid_path)
        db.session.add(paid_info)
        db.session.commit()

    else:
        os.system("mkdir paid_folder")
        app_name = f"{name}_49ja.exe"
        # Delete the application if it already exists
        if  app_name in os.listdir(os.path.join(os.getcwd(), "paid_folder")):
            os.remove(os.path.join(os.getcwd(), "paid_folder", app_name))
        shutil.move(os.path.join(os.getcwd(), "dist", f"{name}_49ja.exe"), os.path.join(os.getcwd(), "paid_folder"))
        os.remove(os.path.join(os.getcwd(), f"{name}_49ja.spec"))
        os.remove(os.path.join(os.getcwd(), f"{name}.py"))
        
        # Remove the remaining folder of dist
        for directory, folder, files in os.walk(os.path.join(os.getcwd(), "dist")):            
            for each_file in files:
                os.remove(os.path.join(directory, each_file))
        # Remove the remaining folder of build 
        for i in os.listdir(os.path.join(os.getcwd(), "build")):
            os.rmdir(os.path.join(os.getcwd(), "build", i))
        
        # Remove all the remaining files of build
        for directory, folder, files in os.walk(os.path.join(os.getcwd(), "build")):
            for each_file in files:
                os.remove(os.path.join(directory, each_file))

        os.rmdir(os.path.join(os.getcwd(), "build"))
        os.rmdir(os.path.join(os.getcwd(), "dist"))
        
        paid_path = os.path.join(os.getcwd(), "paid_folder", app_name)
        paid_info = Paid_49ja(user_id=current_user.id, is_updated=False, paid_bot=paid_path)
        db.session.add(paid_info)
        db.session.commit()
        
    return f"{name}_paid.py created"

@app.route("/get-bot", methods=["POST", "GET"])
@login_required
def create_demo():
    name = request.args.get("q")
    version = request.args.get("v")
    userId = request.args.get("user_id")
    remote_url = request.args.get("url")

    bet_49ja = bet_49ja_script(name, version, remote_url, userId)

    with open(f"{name}.py", "w") as f:
        f.write(bet_49ja)
    if version == "demo":
        os.system(f"workon flask & pyinstaller --onefile --clean --name={name}_49ja_demo {name}.py") 
        if "49ja_folder" in os.listdir():
            create_app(name)
        else:
            os.system("mkdir 49ja_folder")
            create_app(name)
        #     app_name = f"{name}_49ja_demo.exe"
        #     # Delete the application if it already exists
        #     if  app_name in os.listdir(os.path.join(os.getcwd(), "49ja_folder")):
        #         os.remove(os.path.join(os.getcwd(), "49ja_folder", app_name))
        #     shutil.move(os.path.join(os.getcwd(), "dist", f"{name}_49ja_demo.exe"), os.path.join(os.getcwd(), "49ja_folder"))
        #     os.remove(os.path.join(os.getcwd(), f"{name}_49ja_demo.spec"))
        #     os.remove(os.path.join(os.getcwd(), f"{name}.py"))
            
        #     # Remove the remaining folder of dist
        #     for directory, folder, files in os.walk(os.path.join(os.getcwd(), "dist")):            
        #         for each_file in files:
        #             os.remove(os.path.join(directory, each_file))
        #     # Remove the remaining folder of build 
        #     for i in os.listdir(os.path.join(os.getcwd(), "build")):
        #         os.rmdir(os.path.join(os.getcwd(), "build", i))
            
        #     # Remove all the remaining files of build
        #     for directory, folder, files in os.walk(os.path.join(os.getcwd(), "build")):
        #         for each_file in files:
        #             os.remove(os.path.join(directory, each_file))

        #     os.rmdir(os.path.join(os.getcwd(), "build"))
        #     os.rmdir(os.path.join(os.getcwd(), "dist"))
            
        #     demo_path = os.path.join(os.getcwd(), "49ja_folder", app_name)
        #     demo_info = Demo_49ja(user_id=current_user.id, has_demo=True, demo=demo_path)
        #     db.session.add(demo_info)
        #     db.session.commit()
        
    return f"{name}_demo.py created"

def create_app(name):
    app_name = f"{name}_49ja_demo.exe"
    # Delete the application if it already exists
    if  app_name in os.listdir(os.path.join(os.getcwd(), "49ja_folder")):
        os.remove(os.path.join(os.getcwd(), "49ja_folder", app_name))

    shutil.move(os.path.join(os.getcwd(), "dist", f"{name}_49ja_demo.exe"), os.path.join(os.getcwd(), "49ja_folder"))
    os.remove(os.path.join(os.getcwd(), f"{name}_49ja_demo.spec"))
    os.remove(os.path.join(os.getcwd(), f"{name}.py"))
    # Remove the remaining folder of dist
    for directory, folder, files in os.walk(os.path.join(os.getcwd(), "dist")):            
        for each_file in files:
            os.remove(os.path.join(directory, each_file))
    
    # Remove all the remaining files of build
    for directory, folder, files in os.walk(os.path.join(os.getcwd(), "build")):
        for each_file in files:
            os.remove(os.path.join(directory, each_file))

    # Remove the remaining folder of build 
    for i in os.listdir(os.path.join(os.getcwd(), "build")):
        os.rmdir(os.path.join(os.getcwd(), "build", i))

    os.rmdir(os.path.join(os.getcwd(), "build"))
    os.rmdir(os.path.join(os.getcwd(), "dist"))
    bot_path = os.path.join(os.getcwd(), "49ja_folder", app_name)
    # Update the User bet9ja 49js status
    bot_info = Bet_49ja.query.filter_by(user_id=current_user.id).first()
    print(bot_info)
    bot_info.has_compiled = True 
    bot_info.bot_path = bot_path
    db.session.commit()


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

@app.route("/subscribe", methods=["GET"])
def subscribe():
    pass

import request_func
import mailing_server
import basic_auth 

@app.route("/download", methods=["POST", "GET"])
@login_required
def download():
    if current_user.has_paid:
        pass
    else:
        print(current_user.demo_49ja)
        demo_path = current_user.demo_49ja.demo
        print(demo_path)
        flash("downloading...")
        return send_from_directory(r"C:\Users\Olabode\Desktop\49ja server\49ja_folder", "xxxxxx_49ja.exe")


@app.context_processor
def context_processor():
    request_alert = Make_request.query.filter_by(not_seen=True).all()
    alert = False
    if request_alert:
        alert = True
    return dict(alert=alert)

if __name__  == '__main__':
    app.run(debug=True, host="0.0.0.0")