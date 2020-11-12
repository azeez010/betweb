from models import app, User
from flask import request, render_template, jsonify
from flask_mail import Mail, Message

app.config['MAIL_SERVER']='email-smtp.us-east-1.amazonaws.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'AKIA5NZ7IZHABZFICRFI'
app.config['MAIL_PASSWORD'] = 'BIs5gK2yuYVNxJsWl2u4VTzevA/TAt+axmJZegGB25xT'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route("/mail-users", methods=["POST"])
def mail_user():
    recipient = request.json.get("user")
    message = request.json.get("mail")
    subject = request.json.get("subject")
    try:
        if recipient == "all":
            all_users = User.query.all()
            for user in all_users:
                msg = Message(subject, sender = 'dataslid@gmail.com', recipients = [user.email])
                msg.body = message
                msg.html = render_template('mail_template.html', message=message)
                mail.send(msg)
        else:
            msg = Message(subject, sender = 'dataslid@gmail.com', recipients = [recipient])
            msg.body = message
            msg.html = render_template('mail_template.html', message=message)
            mail.send(msg)
        return jsonify({"ok": "true"})
    except Exception as exc:
        return jsonify({"ok": ""})