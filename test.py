from flask import *
from flask_mail import *
app = Flask(__name__)
mail = Mail(app)
mail.connect()
@app.route("/")
def index():
    msg = Message("Hello",sender="shayanbahrainy@gmail.com",recipients=["shayanbahrainy@gmail.com"])
    mail.send(msg)
    return str(mail.record_messages())
app.run()