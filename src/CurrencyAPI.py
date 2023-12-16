from flask import Flask, request, render_template, jsonify
from Database import DatabaseManager

app = Flask(__name__)

database = DatabaseManager().database


@app.route("/", methods=['GET'])
def form():
    return render_template('form.html')


@app.route("/create_account", methods=['POST'])
def create_account():
    if request.method == "POST":
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            cursor = database.cursor()
            cursor.callproc('create_account', (username, password))
            database.commit()
            cursor.close()
            return jsonify({'username': username, 'password': password})
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405  # Method Not Allowed status code


@app.route("/create_currency", methods=['POST'])
def create_currency():
    if request.method == "POST":
        try:
            currency_name = request.form.get("currency_name")
            master_user_id = request.form.get("account_id")
            master_user_pass = request.form.get("master_password")
            max_supply = request.form.get("max_supply")
            cursor = database.cursor()
            cursor.callproc('create_currency', (currency_name, master_user_id, master_user_pass, max_supply))
            database.commit()
            cursor.close()
            return jsonify(
                {
                    "currency_name": currency_name,
                    "master_user_id": master_user_id,
                    "master_user_pass": master_user_pass,
                    "max_supply": max_supply
                }
            )
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405  # Method Not Allowed status code


@app.route("/transfer_funds", methods=['POST'])
def transfer_funds():
    if request.method == 'POST':
        try:
            sender_account_id = request.form.get("sender_account_id")
            sender_password = request.form.get("auth_transfer_password")
            receiver_account_id = request.form.get("receiver_account_id")
            currency_id = request.form.get("currency_id")
            amount = request.form.get("amount")

            cursor = database.cursor()
            cursor.callproc('transfer_funds',
                            (sender_account_id, sender_password, receiver_account_id, currency_id, amount))
            database.commit()
            return jsonify({
                "sender_account_id": sender_account_id,
                "receiver_account_id": receiver_account_id,
                "currency_id": currency_id,
                "amount": amount,
            })

        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500

    return jsonify({'error': 'Method Not Allowed'}), 405
