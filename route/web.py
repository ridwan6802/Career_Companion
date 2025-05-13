# app_web.py

from flask import Blueprint, current_app, render_template, redirect, url_for, session
from datetime import datetime

# Create Blueprint instance
app_web = Blueprint('app', __name__)  # 'app' is the blueprint name for use in url_for()

@app_web.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

import os
from flask import send_from_directory

@app_web.route('/uploads/notes/<filename>')
def serve_note_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads', 'notes'), filename)

@app_web.route('/uploads/events/<filename>')
def serve_event_image(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads', 'events'), filename)



@app_web.route('/')
def index():
    return redirect(url_for('app.dashboard')) if 'loggedin' in session else redirect(url_for('app.login_page'))


@app_web.route('/calendar')
def calendar():
    return render_template('calendar.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/login')
def login_page():
    return redirect(url_for('app.dashboard')) if 'loggedin' in session else render_template('login.html')

@app_web.route('/signup')
def signup_page():
    return redirect(url_for('app.dashboard')) if 'loggedin' in session else render_template('signup.html')

@app_web.route('/dashboard')
def dashboard():
    return render_template('Dashboard.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/class_routine_viewer')
def class_routine_viewer():
    return render_template('class_routine_viewer.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/Lost_And_Found_Board')
def Lost_And_Found_Board():
    return render_template('Lost_And_Found_Board.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/Peer_Chatroom')
def Peer_Chatroom():
    return render_template('Peer_Chatroom.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/Mental_Health_Check')
def Mental_Health_Check():
    return render_template('Mental_Health_Check.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/Teacher_Directory')
def Teacher_Directory():
    return render_template('Teacher_Directory.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/Vacancy_Board')
def Vacancy_Board():
    return render_template('Vacancy_Board.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/Alumni_Connect')
def Alumni_Connect():
    return render_template('Alumni_Connect.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/edit_profile')
def show_edit_profile():
    return render_template('edit_profile.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/notifier')
def notifier():
    return render_template('routine_notification_system.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/cafeteria_menu')
def cafeteria_menu():
    return render_template('cafeteria_menu.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/club_events_feed')
def club_events_feed():
    return render_template('club_events_feed.html', user_type=session.get("user_type")) if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/study_note_sharing')
def study_note_sharing():
    return render_template('study_note_sharing.html') if 'loggedin' in session else redirect(url_for('app.login_page'))

@app_web.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('app.login_page'))
