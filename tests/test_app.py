import json

email_address = '*** PLEASE ENTER YOUR EMAIL HERE **'
password = '*** PLEASE ENTER YOU PASSWORD HERE ***'


# Tests redirect to login page if not logged in.
def test_redirect_index_to_login(client):
    res = client.get('/')
    assert res.status_code == 302
    res_text = res.get_data(as_text=True)
    assert '<h1>Redirecting...</h1>' in res_text


# Tests that the login page loads correctly.
def test_login_page_loaded(client):
    res = client.get('/login')
    assert res.status_code == 200
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Login</h3>' in res_text


# Tests that the login function redirects to the home page when the correct information is entered.
def test_login_function_redirects_success(client):
    correct_password = {
        'email_address': email_address,
        'password': password
    }
    res = client.post(
        '/login', content_type='multipart/form-data', data=correct_password)
    assert res.status_code == 302
    res_text = res.get_data(as_text=True)
    assert '<h1>Redirecting...</h1>' in res_text


# Tests that the login function returns an error message when incorrect information is entered.
def test_login_function_redirects_fail(client):
    wrong_password = {
        'email_address': email_address,
        'password': 'ASDASD'
    }
    res = client.post(
        '/login', content_type='multipart/form-data', data=wrong_password)
    assert res.status_code == 500
    res_text = res.get_data(as_text=True)
    assert '<h1>Internal Server Error</h1>' in res_text


# Tests that the login function returns an error message when incorrect information is entered.
def test_menu_buttons_after_login(client):
    correct_password = {
        'email_address': email_address,
        'password': password
    }
    client.post('/login', content_type='multipart/form-data',
                data=correct_password)

    res = client.get('/')
    assert res.status_code == 200
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Main Menu</h3>' in res_text

    res = client.get('/transaction-report')
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Transaction Report</h3>' in res_text

    res = client.get('/transaction-query')
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Transaction ​Query</h3>' in res_text

    res = client.get('/get-transaction')
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Get Transaction Details</h3>' in res_text

    res = client.get('/get-client')
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Get Client Details</h3>' in res_text

    res = client.get('/logout')
    res_text = res.get_data(as_text=True)
    assert '<h1>Redirecting...</h1>' in res_text


# Tests that the transaction report page is working as expected.
def test_transaction_report(client):
    correct_password = {
        'email_address': email_address,
        'password': password
    }
    client.post('/login', content_type='multipart/form-data',
                data=correct_password)

    res = client.get('/')
    assert res.status_code == 200

    parameters = {
        'start-date': '05-10-2000',
        'end-date': '05-10-2020'
    }
    res = client.post('/transaction-report',
                      content_type='multipart/form-data', data=parameters)
    res_text = res.get_data(as_text=True)
    assert 'An error occurred while retrieving the transaction report.' in res_text


# Tests that the get transaction details page is working as expected.
def test_get_transaction(client):
    correct_password = {
        'email_address': email_address,
        'password': password
    }
    client.post('/login', content_type='multipart/form-data',
                data=correct_password)

    parameters = {
        'transaction-id': '1011025-1539356974-1293',
    }
    res = client.post('/get-transaction',
                      content_type='multipart/form-data', data=parameters)
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Result Table</h3>' in res_text


# Tests that the get client details page is working as expected.
def test_get_client(client):
    correct_password = {
        'email_address': email_address,
        'password': password
    }
    client.post('/login', content_type='multipart/form-data',
                data=correct_password)

    parameters = {
        'transaction-id': '1011025-1539356974-1293',
    }
    res = client.post('/get-client',
                      content_type='multipart/form-data', data=parameters)
    res_text = res.get_data(as_text=True)
    assert '<h3 class="title">Result Table</h3>' in res_text

# Command to execute tests: python3 -m pytest
