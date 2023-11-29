# app.py
from flask import render_template, request, redirect, url_for, jsonify
from flask import session as login_session
from notesApp.models import User, Tag, Note, NoteTag
from notesApp import flask_obj, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask import Flask, render_template, request

@flask_obj.route('/')
def login():
    return render_template('login.html')

@flask_obj.route('/login', methods=['POST'])
def handle_login():
    # Check username and password
    email = request.form.get('email')
    password = request.form.get('password')

    # Hardcoded username and password for demonstration
    if not bool(db.session.execute(db.select(User).where(User.email == email)).scalar()):
            return render_template('login.html', error1='No account exists with this email.') 
   
    if check_password_hash(db.session.execute(db.select(User.password).where(User.email == email)).scalar(), password):
        # store current user's user id for later usage
        login_session['id'] = db.session.execute(db.select(User.id).where(User.email == email)).scalar()

        # Redirect to home.html upon successful login
        return redirect(url_for('home'))
    else:
        # You can handle authentication failure here
        return render_template('login.html', error2='Incorrect Password')

@flask_obj.route('/create_account', methods=['GET', 'POST'])
def create_account():
    data = request.form
    if request.method == 'POST':
        # Get user input from the registration form
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Check if the email is already associated with an existing account
        if bool(db.session.execute(db.select(User).where(User.email == email)).scalar()):
            return render_template('create_account.html', data=request.form, error='An account with this email already exists.')
        
        # Create a new user and add them to the database
        new_user = User(email=email, username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    return render_template('create_account.html', data=data)

@flask_obj.route('/forgot_password', methods=['GET', 'POST'])
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

@flask_obj.route('/password_reset_confirmation')
def password_reset_confirmation():
    return render_template('password_reset_confirmation.html')

@flask_obj.route('/home', methods=['GET', 'POST'])
def home():
    note_tuples = []
    # view only notes for specific user
    notes = Note.query.filter(Note.user_id == login_session['id']).all()
    for note in notes:
        note_tuples.append((note.id, note.title, note.body))
    return render_template('home.html', **locals())

@flask_obj.route('/save/<int:note_id>', methods=["POST"])
def save_note(note_id):

    if request.method == 'POST':
        if note_id == 0:
            title = "New Note" if not request.json['note_title'] else request.json['note_title']
            body = "Note body goes here!" if not request.json['note_body'] else request.json['note_body']

            new_note = Note(title=title, body=body, user_id = login_session['id'])
            db.session.add(new_note)
            db.session.commit()
            response = {
                "new": True,
                "note_title": title,
                "note_body": body,
                "note_id": new_note.id
            }
        else:
            db.session.execute(db.update(Note).where(Note.id==note_id).values({Note.title: request.json['note_title'], Note.body: request.json['note_body']}))
            db.session.commit()
            response = {
                "new": False
            }
        return jsonify(response)


@flask_obj.route("/get_note/<int:note_id>", methods=["GET"])
def get_note(note_id):
    print(note_id, type(note_id))
    note = db.session.execute(db.select(Note).where(Note.id==note_id)).scalar()
    tags = []
    for tag in db.session.execute(db.select(Tag).where((NoteTag.note_id==note_id) & (NoteTag.tag_id==Tag.id) & (Tag.user_id==login_session['id']))).scalars().all():
        tags.append((tag.id, tag.title))
    response = {
        "id": note_id,
        "selected_title": note.title,
        "selected_body": note.body,
        "tags": tags
    }
    print(response)

    return jsonify(response)

@flask_obj.route("/add_tag", methods=["POST"])
def add_tag():
    selected_note_id = request.json.get("selected_note_id")
    tag_name = request.json.get("tag_name")
    if not bool(db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id==login_session['id']))).all()):
        tag = Tag(title=tag_name, user_id=login_session['id'])
        db.session.add(tag)
        db.session.commit()
    else:
        print('already exists')
        tag = db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id == login_session['id']))).scalar()
    
    if not bool(db.session.execute(db.select(NoteTag).where((NoteTag.note_id==selected_note_id) & (NoteTag.tag_id==tag.id))).all()):
        noteTag = NoteTag(note_id=selected_note_id, tag_id=tag.id)
        db.session.add(noteTag)
        db.session.commit()
    
    response = {
        "tag_id": tag.id,
        "tag_name": tag.title
    }
    return jsonify(response)

@flask_obj.route('/delete', methods=["GET"])
def go_to_delete():
    note_tuples = []
    # view only notes for specific user
    print(login_session['id'])
    notes = Note.query.filter(Note.user_id == login_session['id']).all()
    print(notes)
    for note in notes:
        note_tuples.append((note.id, note.title, note.body))
    print(note_tuples)
    return render_template("delete.html", note_tuples=note_tuples)

@flask_obj.route('/delete_notes', methods=["DELETE"])
def delete_notes():
    data = request.json['notes']
    for id in data:
        db.session.execute(db.delete(Note).where(Note.id==id))
        db.session.execute(db.delete(NoteTag).where(NoteTag.note_id==id))
    db.session.commit()
    return jsonify("OK")

@flask_obj.route('/options')
def options():
    return render_template('options.html')

@flask_obj.route('/logout')
def logout():
    # You can perform any necessary logout logic here
    # For now, we'll just redirect to the login page
    del login_session['id']
    return render_template('login.html')


# Function to update the user profile // Somehow the name did not update
def update_user_profile(new_name,new_email, new_password):
    user = User.query.filter(User.id == login_session['id']).first()
    if user:
        user.username = new_name
        user.email = new_email
        user.password = generate_password_hash(new_password)
        db.session.commit()
#need to update the password on database into hash
@flask_obj.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')

        update_user_profile(new_name, new_email, new_password)
        return redirect(url_for('home'))

    return render_template('update_profile.html')

