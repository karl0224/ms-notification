from flask import Flask, request, jsonify
from mailersend import emails
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

mailer = emails.NewEmail(os.getenv('MAILERSEND_API_KEY'))

def load_users():
    with open('usuarios.json', 'r') as file:
        return json.load(file)

def save_users(users):
    with open('usuarios.json', 'w') as file:
        json.dump(users, file, indent=4)

def send_email(data):
    mail_body = ""

    mail_from = {
        "name": "Carlos Prueba",
        "email": "prueba@trial-351ndgw2xzrgzqx8.mlsender.net",
    }

    reply_to = {
        "name": "Name",
        "email": "reply@domain.com",
    }

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(data["recipients"], mail_body)
    mailer.set_subject(data["subject"], mail_body)
    mailer.set_html_content(data["content"], mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    return mailer.send(mail_body)

def two_factor_auth(data):
    mail_body = {

   }

    mail_from = {
        "name": "Carlos Prueba",
        "email": "prueba@trial-351ndgw2xzrgzqx8.mlsender.net",
    }

    reply_to = {
        "name": "Name",
        "email": "reply@domain.com",
    }

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(data["recipients"], mail_body)
    mailer.set_subject(data["subject"], mail_body)
    mailer.set_html_content(email_placeholder(data["code"]), mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    return mailer.send(mail_body)

def email_placeholder(code):
    # Make a string with multiple lines
    body = f"""
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px;">
        <div class="container" style="max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <div class="header" style="text-align: center; margin-bottom: 20px;">
                <h1 style="margin: 0; color: #007bff;">Two-Factor Authentication</h1>
            </div>
            <div class="content" style="text-align: center;">
                <p>Your authentication code is:</p>
                <div class="code" style="font-size: 24px; font-weight: bold; background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd; display: inline-block; margin-top: 20px;">{code}</div>
                <p>Please enter this code to complete your login.</p>
            </div>
            <div class="footer" style="text-align: center; margin-top: 20px; font-size: 12px; color: #777;">
                <p>If you did not request this code, please ignore this email.</p>
            </div>
        </div>
    </body>
    """

    return body

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello World!'})

@app.route('/users', methods=['GET'])
def getUsers():
    users = load_users()
    return jsonify(users)

@app.route('/users/<int:userId>', methods=['GET'])
def getUser(userId):
    users = load_users()
    user = None
    i = 0
    found = False
    # Búsqueda utilizando while y bandera
    while i < len(users) and not found:
        if users[i]['id'] == userId:
            user = users[i]
            found = True
        i += 1
    if found:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def createUser():
    users = load_users()
    data = request.get_json()

    if len(users) > 0:
        i = 1
        last_user = users[0]

        while i < len(users):
            if users[i]['id'] > last_user['id']:
                last_user = users[i]
            i += 1

        new_id = last_user['id'] + 1
    else:
        new_id = 1

    new_user = {
        "id": new_id,
        "name": data['name'],
        "password": data['password'],
        "email": data['email'],
        "nickname": data['nickname']
    }

    users.append(new_user)
    save_users(users)
    return jsonify({"message": "User created successfully"}), 204

@app.route('/users/<int:userId>', methods=['PUT'])
def updateUser(userId):
    users = load_users()
    user = None
    i = 0

    found = False
    # Búsqueda utilizando while y bandera
    while i < len(users) and not found:
        if users[i]['id'] == userId:
            user = users[i]
            found = True
        i += 1

    if found:
        data = request.get_json()
        user['name'] = data['name']
        user['password'] = data['password']
        user['email'] = data['email']
        user['nickname'] = data['nickname']

        save_users(users)
        return jsonify({"message": "User updated successfully"})

    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users/<int:userId>', methods=['DELETE'])
def deleteUser(userId):
    users = load_users()
    user = None
    i = 0

    found = False
    # Búsqueda utilizando while y bandera
    while i < len(users) and not found:
        if users[i]['id'] == userId:
            user = users[i]
            found = True
        i += 1

    if found:
        users.remove(user)
        save_users(users)
        return jsonify({"message": "User deleted successfully"})

    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/send-email', methods=['POST'])

def send_email():
    data = request.get_json()
    response = two_factor_auth(data)

    if int(response) == 202:
        return jsonify({"message": "Email sent successfully"})
    else:
        return jsonify({"error": "Error sending email"}), 500

if __name__ == '__main__':
    app.run(debug=True)