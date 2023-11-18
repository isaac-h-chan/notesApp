# app.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    # Check username and password
    username = request.form.get('username')
    password = request.form.get('password')

    # Hardcoded username and password for demonstration
    if username == 'username' and password == 'password':
        # Redirect to home.html upon successful login
        return redirect(url_for('home'))
    else:
        # You can handle authentication failure here
        return render_template('login.html', error='Incorrect username or password')

@app.route('/create_account.html', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Get user input from the registration form
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Check if the email is already associated with an existing account
        if any(user['email'] == email for user in users):
            return render_template('create_account.html', error='An account with this email already exists.')

        # Create a new user and add them to the database
        new_user = {'username': username, 'password': password, 'email': email}
        users.append(new_user)

        # Redirect to the login page after successful registration
        return redirect(url_for('login'))

    return render_template('create_account.html')

@app.route('/forgot_password.html', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Check if the provided email exists in the database
        email = request.form.get('email')
        user = next((user for user in users if user['email'] == email), None)

        if user:
            # Implement logic to send a password reset link (not implemented in this example)
            # You can send an email with a reset link or generate a token and provide a link with the token
            # For simplicity, this example just redirects to a confirmation page
            return redirect(url_for('password_reset_confirmation'))
        else:
            # Handle the case where the email is not found in the database
            return render_template('forgot_password.html', error='Email not found.')

    return render_template('forgot_password.html')

@app.route('/password_reset_confirmation')
def password_reset_confirmation():
    return render_template('password_reset_confirmation.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/options')
def options():
    return render_template('options.html')

@app.route('/logout')
def logout():
    # You can perform any necessary logout logic here
    # For now, we'll just redirect to the login page
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
