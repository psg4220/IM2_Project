import requests

# Replace with your Flask server address
BASE_URL = 'http://127.0.0.1:5000'

# Test creating a new account
def test_create_account(initial_balance):
    endpoint = f'{BASE_URL}/create_account'
    data = {'initial_balance': initial_balance}
    response = requests.post(endpoint, json=data)
    print(response.json())

# Test getting account balance
def test_get_balance(account_id):
    endpoint = f'{BASE_URL}/balance/{account_id}'
    response = requests.get(endpoint)
    print(response.json())

# Test sending money
def test_send_money(sender_id, receiver_id, amount):
    endpoint = f'{BASE_URL}/send'
    data = {'sender_id': sender_id, 'receiver_id': receiver_id, 'amount': amount}
    response = requests.post(endpoint, json=data)
    print(response.json())

# Test deleting an account
def test_delete_account(account_id):
    endpoint = f'{BASE_URL}/delete_account/{account_id}'
    response = requests.delete(endpoint)
    print(response.json())

if __name__ == '__main__':
    # Test cases
    # test_create_account(1000.0)
    # test_get_balance(1)  # Replace 1 with the account ID you want to check
    test_send_money(1, 2, 20.0)  # Replace 1 and 2 with sender and receiver account IDs
    # test_delete_account(1)  # Replace 1 with the account ID you want to delete
