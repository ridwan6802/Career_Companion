from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import MySQLdb.cursors
from datetime import datetime, timedelta, date, time
import datetime
from config import Config

import os
from werkzeug.utils import secure_filename


import requests
import random


app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
app.config.from_object(Config)
mysql = MySQL(app)
CORS(app)








@app.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}






UPLOAD_FOLDER = 'uploads/notes'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'ppt', 'pptx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file_notes(filename): # Changed function name for notes
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



UPLOAD_FOLDER_EVENTS = 'uploads/events'  # New upload folder
ALLOWED_EXTENSIONS_EVENTS = {'png', 'jpg', 'jpeg'}  # Allowed image extensions # Changed variable name
app.config['UPLOAD_FOLDER_EVENTS'] = UPLOAD_FOLDER_EVENTS
os.makedirs(UPLOAD_FOLDER_EVENTS, exist_ok=True)  # Create the directory if it doesn't exist

def allowed_file_events(filename): # Changed function name for events
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_EVENTS











# -------------------- Web Page Routes -------------------- #
from route.web import app_web
app.register_blueprint(app_web)
"""
@app.route('/')
def index():
    return redirect(url_for('dashboard')) if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return redirect(url_for('dashboard')) if 'loggedin' in session else render_template('login.html')

@app.route('/signup')
def signup_page():
    return redirect(url_for('dashboard')) if 'loggedin' in session else render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('Dashboard.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/class_routine_viewer')
def class_routine_viewer():
    return render_template('class_routine_viewer.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/Lost_And_Found_Board')
def Lost_And_Found_Board():
    return render_template('Lost_And_Found_Board.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/Peer_Chatroom')
def Peer_Chatroom():
    return render_template('Peer_Chatroom.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/Mental_Health_Check')
def Mental_Health_Check():
    return render_template('Mental_Health_Check.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/Teacher_Directory')
def Teacher_Directory():
    return render_template('Teacher_Directory.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/Vacancy_Board')
def Vacancy_Board():
    return render_template('Vacancy_Board.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/Alumni_Connect')
def Alumni_Connect():
    return render_template('Alumni_Connect.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/edit_profile')
def show_edit_profile():
    return render_template('edit_profile.html') if 'loggedin' in session else redirect(url_for('login_page'))

@app.route('/notifier')
def notifier():
    return render_template('routine_notification_system.html') if 'loggedin' in session else redirect(url_for('login_page'))


@app.route('/cafeteria_menu')
def cafeteria_menu():
    return render_template('cafeteria_menu.html') if 'loggedin' in session else redirect(url_for('login_page'))


@app.route('/club_events_feed')
def club_events_feed():
    return render_template('club_events_feed.html') if 'loggedin' in session else redirect(url_for('login_page'))


@app.route('/study_note_sharing')
def study_note_sharing():
    return render_template('study_note_sharing.html') if 'loggedin' in session else redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))
"""








# -------------------- API Routes -------------------- #
EXTERNAL_API_URL = "https://www.themealdb.com/api/json/v1/1/filter.php"  # Base URL

def fetch_meals_from_category(category):
    url = f"{EXTERNAL_API_URL}?c={category}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('meals', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from {url}: {e}")
        return []

@app.route('/api/cafeteria_menu')
def get_cafeteria_menu():
    categories = ["Beef", "Chicken", "Vegetarian", "Dessert"]  # Example categories
    menu_items = []
    for category in categories:
        meals = fetch_meals_from_category(category)
        if meals:
            # Randomly select one meal from each category
            selected_meal = random.choice(meals)
            meal_details_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={selected_meal['idMeal']}"
            meal_details_response = requests.get(meal_details_url)
            meal_details_response.raise_for_status()
            meal_details = meal_details_response.json().get('meals')[0]

            menu_items.append({
                'name': meal_details.get('strMeal', 'Unknown'),
                'description': meal_details.get('strInstructions', 'No description'),
                'price': random.randint(80, 200),  # Placeholder price
                'image_url': meal_details.get('strMealThumb', 'https://via.placeholder.com/400x300'),
                'availability': category,
                'rating': random.uniform(3.5, 5.0),  # Placeholder rating
                'rating_count': random.randint(20, 150) # Placeholder count
            })

    return jsonify(menu_items)




@app.route('/api/calendar_events')
def get_calendar_events():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT 
                ch.id, 
                ch.user_id, 
                ch.table_name, 
                ch.table_row_id, 
                ch.registered_at,
                e.title AS event_title,
                e.event_time AS event_datetime,
                e.location AS event_location,
                c.name AS club_name,       -- Corrected: Fetch club name
                et.name AS event_type_name -- Corrected: Fetch event type name
            FROM calendar_history ch
            LEFT JOIN events e ON ch.table_name = 'events' AND ch.table_row_id = e.id
            LEFT JOIN clubs c ON e.club_id = c.id
            LEFT JOIN event_types et ON e.event_type_id = et.id
        """)
        events = cursor.fetchall()
        cursor.close()

        # Format the data for FullCalendar
        formatted_events = []
        for event in events:
            formatted_events.append({
                'id': event['id'],
                'title': event['event_title'] or f"{event['table_name']} ID: {event['table_row_id']}",
                'start': event['event_datetime'].isoformat(),
                'location': event['event_location'],
                'club': event['club_name'],
                'eventType': event['event_type_name']
            })

        return jsonify(formatted_events)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    







@app.route('/api/events/delete/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the event exists
        cursor.execute("SELECT image_path FROM events WHERE id = %s LIMIT 1", (event_id,))
        event = cursor.fetchone()

        if event:
            image_path = event['image_path']
            current_user_id = session['user_id']

            if session['user_type'] == 1:  # Admin can delete any event
                # **First, delete related records in registered_events**
                cursor.execute("DELETE FROM registered_events WHERE event_id = %s", (event_id,))
                mysql.connection.commit()

                # Then, delete the image file (if it exists)
                try:
                    if image_path:
                        os.remove(os.path.join(app.root_path, image_path))
                        print(f"File deleted: {image_path}")
                except FileNotFoundError:
                    print(f"File not found: {image_path}")

                # Finally, delete the event from the events table
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                mysql.connection.commit()
                cursor.close()
                return jsonify({'status': 'success', 'message': 'Event and associated registrations deleted successfully'})
            else:
                cursor.close()
                return jsonify({'status': 'error', 'message': 'You are not authorized to delete this Event'}), 403
        else:
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Event not found'}), 404
    except Exception as e:
        if 'foreign key constraint fails' in str(e):
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Cannot delete event because there are active registrations. Please remove registrations first.'}), 400 # Or a more specific error code
        else:
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'status': 'error', 'message': str(e)}), 500







@app.route('/api/events/add', methods=['POST'])
def add_event():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    club_id = request.form.get('club')
    event_type_id = request.form.get('eventType')
    title = request.form.get('eventTitle')
    event_time = request.form.get('datetime')
    location = request.form.get('address')
    registration_link = request.form.get('reglink')
    description = request.form.get('description')

    if not club_id or not event_type_id or not title or not event_time or not location:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    image_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file_events(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER_EVENTS'], filename)
            file.save(image_path)
            image_path = f"uploads/events/{filename}"  # Store relative path in DB
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO events (club_id, event_type_id, title, event_time, location, registration_link, description, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (club_id, event_type_id, title, event_time, location, registration_link, description, image_path))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Event added successfully'})
    except Exception as e:
        if image_path:  # Remove uploaded file on error
            try:
                os.remove(image_path)
            except FileNotFoundError:
                print(f"File not found during cleanup: {image_path}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/events/show', methods=['GET'])
def get_events():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
            SELECT
                e.*,
                c.name AS club_name,
                et.name AS event_type_name
            FROM events e
            JOIN clubs c ON e.club_id = c.id
            JOIN event_types et ON e.event_type_id = et.id
            WHERE 1=1
        """
        params = []

        search_term = request.args.get('search')
        if search_term:
            query += " AND (e.title LIKE %s OR e.description LIKE %s OR e.location LIKE %s)"
            params.extend([f"%{search_term}%"] * 3)

        club_id = request.args.get('club_id')
        if club_id:
            query += " AND e.club_id = %s"
            params.append(club_id)

        event_type_id = request.args.get('event_type_id')
        if event_type_id:
            query += " AND e.event_type_id = %s"
            params.append(event_type_id)

        query += " ORDER BY e.event_time"

        cursor.execute(query, params)
        events = cursor.fetchall()
        if session['user_type'] == 1:
            for event in events:
                event['can_delete'] = 1==1

        return jsonify({'status': 'success', 'events': events})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/events/rsvp', methods=['POST'])
def rsvp_event():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    event_id = data.get('event_id')
    if not event_id:
        return jsonify({'status': 'error', 'message': 'Missing event ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO registered_events (user_id, event_id)
            VALUES (%s, %s)
        """, (session['user_id'], event_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Registration successful'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/events/calendar', methods=['POST'])
def add_to_calendar():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    event_id = data.get('event_id')
    if not event_id:
        return jsonify({'status': 'error', 'message': 'Missing event ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO calendar_history (user_id, table_name, table_row_id)
            VALUES (%s, %s, %s)
        """, (session['user_id'], 'events', event_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Added to calendar'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    







@app.route('/api/notes/upload', methods=['POST'])
def upload_note():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    course_code = request.form.get('courseCode')  # Corrected names
    course_title = request.form.get('courseTitle')
    description = request.form.get('description')
    semester = request.form.get('semester')
    category = request.form.get('category')

    if not course_code or not course_title or not semester or not category:
        return jsonify({'status': 'error', 'message': 'Course code, title, semester, and category are required'}), 400

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and allowed_file_notes(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_path_for_db = f"uploads/notes/{filename}"

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO study_notes (user_id, course_code, course_title, description, file_path, semester, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], course_code, course_title, description, file_path_for_db, semester, category))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'success', 'message': 'Note uploaded successfully'})
        except Exception as e:
            os.remove(file_path)
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400






@app.route('/api/notes/view', methods=['GET'])
def view_notes():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT 
                sn.*, 
                s.name AS semester_name, 
                c.name AS category_name
            FROM study_notes sn
            LEFT JOIN semesters s ON sn.semester = s.id  -- Assuming sn.semester is the semester ID
            LEFT JOIN categories c ON sn.category = c.id  -- Assuming sn.category is the category ID
            ORDER BY sn.uploaded_at DESC
        """)
        notes = cursor.fetchall()

        for note in notes:
            note['can_delete'] = note['user_id'] == session['user_id']

        return jsonify({'status': 'success', 'notes': notes})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/notes/filter', methods=['GET'])
def filter_notes():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    search_term = request.args.get('search')
    semester_filter = request.args.get('semester')
    category_filter = request.args.get('category')

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
            SELECT 
                sn.*, 
                s.name AS semester_name, 
                c.name AS category_name
            FROM study_notes sn
            LEFT JOIN semesters s ON sn.semester = s.id
            LEFT JOIN categories c ON sn.category = c.id
            WHERE 1=1  -- Start with a condition that is always true
        """
        params = []

        if search_term:
            query += " AND (sn.course_code LIKE %s OR sn.course_title LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        if semester_filter:
            query += " AND sn.semester = %s"
            params.append(semester_filter)

        if category_filter:
            query += " AND sn.category = %s"
            params.append(category_filter)

        query += " ORDER BY sn.uploaded_at DESC"

        cursor.execute(query, tuple(params))
        notes = cursor.fetchall()

        for note in notes:
            note['can_delete'] = note['user_id'] == session['user_id']

        return jsonify({'status': 'success', 'notes': notes})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    






@app.route('/api/notes/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch the file path and user_id of the note
        cursor.execute("SELECT file_path, user_id FROM study_notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()

        if note:
            file_path = note['file_path']
            uploaded_by = note['user_id']
            current_user_id = session['user_id']

            if session['user_type'] == 1:  # Admin can delete any note
                # Delete the file
                try:
                    os.remove(os.path.join(app.root_path, file_path))
                except FileNotFoundError:
                    # Log the error, but continue with database deletion
                    print(f"File not found: {file_path}")

                cursor.execute("DELETE FROM study_notes WHERE id = %s", (note_id,))
                mysql.connection.commit()
                cursor.close()
                return jsonify({'status': 'success', 'message': 'Note and file deleted successfully'})
            elif uploaded_by == current_user_id: # User can delete only own note
                # Delete the file
                try:
                    os.remove(os.path.join(app.root_path, file_path))
                except FileNotFoundError:
                    # Log the error, but continue with database deletion
                    print(f"File not found: {file_path}")

                cursor.execute("DELETE FROM study_notes WHERE id = %s", (note_id,))
                mysql.connection.commit()
                cursor.close()
                return jsonify({'status': 'success', 'message': 'Note and file deleted successfully'})
            else:
                cursor.close()
                return jsonify({'status': 'error', 'message': 'You are not authorized to delete this note'}), 403
        else:
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Note not found'}), 404
    except Exception as e:
        cursor.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/semesters/<int:year>', methods=['GET'])
def get_semesters_by_year(year):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, name FROM semesters WHERE year = %s", (year,)) #changed query
        semesters = cursor.fetchall()  # Fetch all rows
        cursor.close()
        return jsonify({'status': 'success', 'semesters': semesters}) #return all row
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    



@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    user_name = data.get('username')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    
    # Fix here: handle phone number
    phone = data.get('phone')
    try:
        phone = int(phone) if phone else 0
    except ValueError:
        phone = 0

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({'status': 'fail', 'message': 'Email already exists'})

    cursor.execute(
        "INSERT INTO users (user_type, email, password, user_name, phone_number, created_date) VALUES (2, %s, %s, %s, %s, %s)",
        (email, password, user_name, phone, datetime.datetime.now())
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({'status': 'success', 'message': 'User registered successfully'})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password_input = data.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user['password'], password_input):
        session['loggedin'] = True
        session['user_id'] = user['id']
        session['user_type'] = user['user_type']
        session['username'] = user['user_name']
        return jsonify({'status': 'success', 'message': 'Login successful'})
    return jsonify({'status': 'fail', 'message': 'Invalid credentials'})







@app.route('/api/class_routine_viewer/add', methods=['POST'])
def add_routine():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    required_fields = ['day', 'datetime', 'room', 'faculty', 'course']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO class_routine_viewer (user_id, day, datetime, room, faculty, course)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            data['day'],
            data['datetime'],
            data['room'],
            data['faculty'],
            data['course']
        ))
        mysql.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return jsonify({'status': 'success', 'id': new_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/class_routine_viewer/delete', methods=['POST'])
def delete_routine():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing routine ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "DELETE FROM class_routine_viewer WHERE id = %s AND user_id = %s",
            (data['id'], session['user_id'])
        )
        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if affected_rows == 0:
            return jsonify({'status': 'error', 'message': 'Routine not found or not owned by user'}), 404

        return jsonify({'status': 'success', 'message': 'Routine deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/class_routine_viewer/view', methods=['GET'])
def view_class_routines():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        if session['user_type'] == 2:
            cursor.execute("SELECT * FROM class_routine_viewer WHERE user_id = %s ORDER BY id DESC", (session['user_id'],))
        else:
            cursor.execute("SELECT * FROM class_routine_viewer ORDER BY id DESC")

        data = cursor.fetchall()
        return jsonify({'status': 'success', 'data': data})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})










@app.route('/api/mental_health_check/add', methods=['POST'])
def add_mental_health_check():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    feelings_str = ','.join(data.get('feelings', []))
    note = data.get('note')
    name = data.get('name')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO mental_health_check (user_id, name, feelings, note, submission_time)
            VALUES (%s, %s, %s, %s, NOW())
        """, (session['user_id'], name, feelings_str, note))
        mysql.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return jsonify({'status': 'success', 'id': new_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/mental_health_check/delete', methods=['POST'])
def delete_mental_health_check():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing check-in ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "DELETE FROM mental_health_check WHERE id = %s AND user_id = %s",
            (data['id'], session['user_id'])
        )
        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if affected_rows == 0:
            return jsonify({'status': 'error', 'message': 'Check-in not found or not owned by user'}), 404

        return jsonify({'status': 'success', 'message': 'Check-in deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/mental_health_check/view', methods=['GET'])
def view_mental_health_checks():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # For now, only allow users to see their own check-ins.
        # You can adjust this based on your application's requirements (e.g., admin users).
        cursor.execute("SELECT id, name, feelings, note FROM mental_health_check WHERE user_id = %s ORDER BY submission_time DESC", (session['user_id'],))
        data = cursor.fetchall()
        return jsonify({'status': 'success', 'data': data})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    

















@app.route('/api/teacher_directory/add', methods=['POST'])
def add_teacher():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    required_fields = ['faculty_name', 'email', 'consultation_hours', 'courses_done', 'note']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO teacher_directory (user_id, faculty_name, email, consultation_hours, courses_done, note)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            data['faculty_name'],
            data['email'],
            data['consultation_hours'],
            data['courses_done'],
            data['note']
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/teacher_directory/delete', methods=['POST'])
def delete_teacher():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing teacher ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        if session['user_type'] == 1:  # Admin can delete any teacher
            cursor.execute(
                "DELETE FROM teacher_directory WHERE id = %s",
                (data['id'],)
            )
        else:  # Regular users can only delete their own teachers
            cursor.execute(
                "DELETE FROM teacher_directory WHERE id = %s AND user_id = %s",
                (data['id'], session['user_id'])
            )
        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if affected_rows == 0:
            return jsonify({'status': 'error', 'message': 'Teacher not found or not owned by user'}), 404

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/teacher_directory/view', methods=['GET'])
def view_teacher_directory():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Retrieve all teachers, ordered by id (descending)
        cursor.execute("SELECT * FROM teacher_directory ORDER BY id DESC",)
        data = cursor.fetchall()

        # Add 'can_delete' flag to each teacher
        for row in data:
            row['can_delete'] = (session['user_type'] == 1) or (row['user_id'] == session['user_id'])

        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    


    






@app.route('/api/vacancy_board/add', methods=['POST'])
def add_vacancy():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    required_fields = ['title', 'details', 'post_user_type']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    if data['post_user_type'] not in ('teacher', 'student'):
        return jsonify({'status': 'error', 'message': 'Invalid post user type'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO vacancy_board (user_id, title, details, post_user_type, status)
            VALUES (%s, %s, %s, %s, 'open')
        """, (
            session['user_id'],
            data['title'],
            data['details'],
            data['post_user_type']
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vacancy_board/delete', methods=['POST'])
def delete_vacancy():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing vacancy ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        if session['user_type'] == 1:  # Admin can delete any post
            cursor.execute(
                "DELETE FROM vacancy_board WHERE id = %s",
                (data['id'],)
            )
        else:  # Regular users can only delete their own posts
            cursor.execute(
                "DELETE FROM vacancy_board WHERE id = %s AND user_id = %s",
                (data['id'], session['user_id'])
            )
        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if affected_rows == 0:
            return jsonify({'status': 'error', 'message': 'Vacancy not found or not owned by user'}), 404

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vacancy_board/view', methods=['GET'])
def view_vacancies():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Retrieve all vacancies, ordered by creation date (newest first)
        cursor.execute("SELECT * FROM vacancy_board ORDER BY created_at DESC")  # DESC for descending order
        data = cursor.fetchall()

        # Add 'can_edit' and 'can_delete' flags to each vacancy
        for row in data:
            row['can_edit'] = (session['user_type'] == 1) or (row['user_id'] == session['user_id'])
            row['can_delete'] = (session['user_type'] == 1) or (row['user_id'] == session['user_id'])

        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vacancy_board/update_status', methods=['POST'])
def update_vacancy_status():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data or 'status' not in data:
        return jsonify({'status': 'error', 'message': 'Missing vacancy ID or status'}), 400

    if data['status'] not in ('open', 'booked', 'ongoing', 'closed'):
        return jsonify({'status': 'error', 'message': 'Invalid status'}), 400

    try:
        cursor = mysql.connection.cursor()
        if session['user_type'] == 1:  # Admin can update any post
            cursor.execute(
                "UPDATE vacancy_board SET status = %s WHERE id = %s",
                (data['status'], data['id'])
            )
        else:  # Regular users can only update their own posts
            cursor.execute(
                "UPDATE vacancy_board SET status = %s WHERE id = %s AND user_id = %s",
                (data['status'], data['id'], session['user_id'])
            )
        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({'status': 'error', 'message': 'Vacancy not found or not owned by user'}), 404

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
















@app.route('/api/alumni_connect/add', methods=['POST'])
def add_alumni_post():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    required_fields = ['full_name', 'graduation_year', 'degree', 'current_job', 'email', 'message']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO alumni_connect (user_id, full_name, graduation_year, degree, current_job, email, linkedin_link, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            data['full_name'],
            data['graduation_year'],
            data['degree'],
            data['current_job'],
            data['email'],
            data.get('linkedin_link'),
            data['message']
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alumni_connect/delete', methods=['POST'])
def delete_alumni_post():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing post ID'}), 400

    try:
        cursor = mysql.connection.cursor()
        if session['user_type'] == 1:  # Admin can delete any post
            cursor.execute(
                "DELETE FROM alumni_connect WHERE id = %s",
                (data['id'],)
            )
        else:  # Regular user can only delete their own post
            cursor.execute(
                "DELETE FROM alumni_connect WHERE id = %s AND user_id = %s",
                (data['id'], session['user_id'])
            )

        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if affected_rows == 0:
            return jsonify({'status': 'error', 'message': 'Post not found or not owned by user'}), 404

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alumni_connect/view', methods=['GET'])
def view_alumni_posts():
    if 'user_id' not in session or 'user_type' not in session:
        # For now, let's allow viewing even if not logged in, but no delete options
        session['user_id'] = -1  # Set a default user ID for non-logged-in users
        session['user_type'] = 0  # Set a default user type

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM alumni_connect ORDER BY created_at DESC")
        data = cursor.fetchall()

        # Add 'can_delete' flag to each post
        for row in data:
            row['can_delete'] = (session['user_type'] == 1) or (row['user_id'] == session['user_id'])

        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
























# -------------------- API Routes for Lost and Found Board -------------------- #
@app.route('/api/lost_and_found/add', methods=['POST'])
def add_lost_and_found_item():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    required_fields = ['type', 'item_name', 'date', 'time', 'place', 'owner_finder_name', 'contact', 'address']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO lost_and_found_board (user_id, type, item_name, date, time, place, approximate_value, owner_finder_name, contact, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            data['type'],
            data['item_name'],
            data['date'],
            data['time'],
            data['place'],
            data.get('approximate_value'),
            data['owner_finder_name'],
            data['contact'],
            data['address']
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/lost_and_found/delete', methods=['POST'])
def delete_lost_found():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    if 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing item ID'}), 400

    try:
        cursor = mysql.connection.cursor()

        if session['user_type'] == 1:
            # Admin can delete any entry
            cursor.execute("DELETE FROM lost_and_found_board WHERE id = %s", (data['id'],))
        else:
            # Users can delete only their own entries
            cursor.execute(
                "DELETE FROM lost_and_found_board WHERE id = %s AND user_id = %s",
                (data['id'], session['user_id'])
            )

        affected_rows = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if affected_rows == 0:
            return jsonify({'status': 'error', 'message': 'Item not found or not owned by user'}), 403

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




    


@app.route('/api/lost_and_found/view', methods=['GET'])
def view_lost_and_found():
    if 'user_id' not in session or 'user_type' not in session:
        session['user_id'] = -1
        session['user_type'] = 0

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM lost_and_found_board ORDER BY id DESC")
        data = cursor.fetchall()

        for row in data:
            row['can_delete'] = (session['user_type'] == 1) or (row['user_id'] == session['user_id'])

            for key in row:
                value = row[key]
                if isinstance(value, (datetime.datetime, date)):
                    row[key] = value.strftime('%Y-%m-%d')  # only date
                elif isinstance(value, time):
                    row[key] = value.strftime('%H:%M')  # only time
                elif isinstance(value, timedelta):
                    row[key] = str(value)

        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500






















@app.route('/api/peer_chatroom/send', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'status': 'error', 'message': 'Empty message'}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO peer_chatroom (sender_id, message, created_at) VALUES (%s, %s, NOW())",
            (session['user_id'], message)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/peer_chatroom/messages', methods=['GET'])
def get_messages():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT pc.id, pc.sender_id, u.user_name AS sender_name, pc.message, pc.created_at
            FROM peer_chatroom pc
            JOIN users u ON pc.sender_id = u.id
            ORDER BY pc.id ASC
        """)
        messages = cursor.fetchall()
        cursor.close()

        return jsonify({'status': 'success', 'data': messages})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500














@app.route('/api/edit_profile', methods=['POST'])
def edit_profile():
    data = request.get_json()
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    repeat_password = data.get('repeat_password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    if new_password or repeat_password:
        if not old_password:
            return jsonify({'status': 'error', 'message': 'Old password is required to change password'})
        if not check_password_hash(user['password'], old_password):
            return jsonify({'status': 'error', 'message': 'Old password is incorrect'})
        if new_password != repeat_password:
            return jsonify({'status': 'error', 'message': 'New passwords do not match'})
        new_hashed = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET user_name=%s, email=%s, phone=%s, password=%s WHERE id=%s",
                       (name, email, phone, new_hashed, user_id))
    else:
        cursor.execute("UPDATE users SET user_name=%s, email=%s, phone=%s WHERE id=%s",
                       (name, email, phone, user_id))

    mysql.connection.commit()
    return jsonify({'status': 'success', 'message': 'Profile updated successfully'})





@app.route('/api/get_profile')
def get_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT user_name, email, phone_number FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        return jsonify({'status': 'success', 'data': user})
    else:
        return jsonify({'status': 'error', 'message': 'User not found'})
















@app.route('/api/routine-notifications')
def get_routine_notifications():
    now = datetime.datetime.now()
    later = now + timedelta(hours=2)

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, day, datetime, room, faculty, course
        FROM class_routine_viewer
        WHERE datetime BETWEEN %s AND %s
        ORDER BY datetime ASC
    """, (now, later))

    rows = cur.fetchall()
    routine_list = []
    for row in rows:
        routine_list.append({
            "id": row[0],
            "day": row[1],
            "datetime": row[2].strftime("%Y-%m-%d %H:%M:%S"),
            "room": row[3],
            "faculty": row[4],
            "course": row[5]
        })

    cur.close()
    return jsonify(routine_list)




# -------------------- Start Server -------------------- #
if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])