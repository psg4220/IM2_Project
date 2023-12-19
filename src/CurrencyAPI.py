from flask import Flask, request, render_template, jsonify
from Database import DatabaseManager

app = Flask(__name__)

database = DatabaseManager().database


@app.route('/')
def main_page():
    return "<h1>Hello</h1>"


@app.route("/create_account", methods=['POST'])
def create_account():
    if request.method == "POST":
        try:
            username = request.form.get('create_account_username')
            password = request.form.get('create_account_password')
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
            currency_name = request.form.get("create_currency_name")
            master_user_id = request.form.get("master_account_id")
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
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/view_currency', methods=['GET'])
def view_currency():
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM currency')
            res = cursor.fetchall()
            data = []
            for currency in res:
                data.append(
                    {
                        'currency_id': currency[0],
                        'currency_name': currency[1],
                        'master_account': currency[2]
                    }
                )
            cursor.close()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/view_currency/<id>', methods=['GET'])
def view_currency_with_id(user_id):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM currency WHERE id = %s', (user_id,))
            res = cursor.fetchall()[0]
            cursor.close()
            return jsonify(
                {
                    'currency_id': res[0],
                    'currency_name': res[1],
                    'master_account': res[2]
                }
            ), 200
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


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


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if request.method == 'POST':
        try:
            username = request.form.get('delete_account_username')
            password = request.form.get('delete_account_password')
            cursor = database.cursor()
            cursor.callproc('delete_account',
                            (username, password))
            database.commit()
            return jsonify({
                'username': username
            })

        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500

    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/retrieve_balance/<username>', methods=['GET'])
def retrieve_balance_username(username):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT currency_name,balance FROM currency_balance_view WHERE account_name = %s',
                           (username,))
            res = cursor.fetchall()
            cursor.close()
            return jsonify(res)
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/retrieve_transaction_record', methods=['GET'])
def retrieve_transaction_record():
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM transaction_record_view')
            res = cursor.fetchall()
            cursor.close()
            return jsonify(res)
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/retrieve_transaction_record/<username>', methods=['GET'])
def retrieve_transaction_record_username(username):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM transaction_record_view WHERE sender_account = %s OR receiver_account = %s',
                           (username, username))
            res = cursor.fetchall()
            cursor.close()
            return jsonify(res)
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/get_account_id/<username>', methods=['GET'])
def get_account_id(username):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT id FROM username WHERE username = %s', (username,))
            res = cursor.fetchone()
            cursor.close()
            return jsonify(
                {
                    'user_id': res[0]
                }
            )
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/get_account_username/<user_id>', methods=['GET'])
def get_account_username(user_id):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT username FROM username WHERE id = %s', (user_id,))
            res = cursor.fetchone()
            cursor.close()
            return jsonify(
                {
                    'username': res[0]
                }
            )
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/get_currency_id/<currency_name>', methods=['GET'])
def get_currency_id(currency_name):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT id FROM currency WHERE name = %s', (currency_name,))
            res = cursor.fetchone()
            cursor.close()
            return jsonify(
                {
                    'currency_id': res[0]
                }
            )
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.route('/get_currency_name/<currency_id>', methods=['GET'])
def get_currency_name(currency_id):
    if request.method == 'GET':
        try:
            cursor = database.cursor()
            cursor.execute('SELECT name FROM currency WHERE id = %s', (currency_id,))
            res = cursor.fetchone()
            cursor.close()
            return jsonify(
                {
                    'currency_name': res[0]
                }
            )
        except Exception as e:
            return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
    return jsonify({'error': 'Method Not Allowed'}), 405


















