import requests
import json
import CurrencyAPI

BASE_URL = "http://127.0.0.1:5000"


def test_create_account(username, password):
    data = {
        'create_account_username': username,
        'create_account_password': password
    }
    res = requests.post(f'{BASE_URL}/create_account', data=data)
    assert res.ok
    return json.dumps(res.json(), indent=4)


def test_create_currency(currency_name, master_account_id, master_account_password, max_supply):
    data = {
        'create_currency_name': currency_name,
        'master_account_id': master_account_id,
        'master_password': master_account_password,
        'max_supply': max_supply
    }
    res = requests.post(f'{BASE_URL}/create_currency', data=data)
    assert res.ok
    return json.dumps(res.json(), indent=4)


def test_delete_account(username, password):
    data = {
        'delete_account_username': username,
        'delete_account_password': password
    }
    res = requests.post(f'{BASE_URL}/delete_account', data=data)
    assert res.ok
    return json.dumps(res.json(), indent=4)


def test_retrieve_balance(user_id):
    res = requests.get(f'{BASE_URL}/retrieve_balance/{user_id}')
    assert res.ok
    return json.dumps(res.json(), indent=4)


def test_view_currency():
    res = requests.get(f'{BASE_URL}/view_currency')
    assert res.ok
    return json.dumps(res.json(), indent=4)


def test_view_currency(user_id):
    res = requests.get(f'{BASE_URL}/view_currency/{user_id}')
    assert res.ok
    return json.dumps(res.json(), indent=4)


def test_get_account_id(username):
    res = requests.get(f'{BASE_URL}/get_account_id/{username}')
    assert res.ok
    return res.json().get('user_id')


def test_get_account_username(user_id):
    res = requests.get(f'{BASE_URL}/get_account_username/{user_id}')
    assert res.ok
    return res.json().get('username')


def test_get_currency_id(currency_name):
    res = requests.get(f'{BASE_URL}/get_currency_id/{currency_name}')
    assert res.ok
    return res.json().get('currency_id')


def test_get_currency_name(currency_id):
    res = requests.get(f'{BASE_URL}/get_currency_name/{currency_id}')
    assert res.ok
    return res.json().get('currency_name')


def test_transfer_funds(sender_account_id, auth_transfer_password, receiver_account_id, currency_id, amount):
    data = {
        'sender_account_id': sender_account_id,
        'auth_transfer_password': auth_transfer_password,
        'receiver_account_id': receiver_account_id,
        'currency_id': currency_id,
        'amount': amount
    }
    res = requests.post(f'{BASE_URL}/transfer_funds', data=data)
    assert res.ok
    return json.dumps(res.json(), indent=4)


def main():
    ...


if "__main__" == __name__:
    main()
