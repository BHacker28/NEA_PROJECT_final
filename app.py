from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, SelectField, IntegerField, \
    validators, TimeField
from wtforms.validators import DataRequired, EqualTo, Length, NoneOf, NumberRange
from wtforms.widgets import TextArea
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
import yaml
import mysql.connector
from mysql.connector import errorcode
from dateutil.relativedelta import relativedelta
import webbrowser
import calendar
from Classes import Account, Lesson


# dictionary of account in a session takes form:
# {'_id': 1, '_email': 's', '_password_hash':
# 'sha256$joODB5oL94CRGYYC$a39acb5d56a03905bd1c168ad8afc0c0d8d64577d15d9070eb365e38060e5737', '_user_id': 1,
# '_authority': 'student', '_last_logged_in': datetime.datetime(2022, 3, 22, 12, 56, 13), '_date_added':
# datetime.datetime(2022, 3, 22, 12, 56, 13), '_first_name': 'Ben', '_last_name': 'Hacker', '_age': 18, '_belt_id':
# 1, '_last_graded': datetime.datetime(2022, 3, 22, 12, 56, 13), '_approved': None}


# ! Change age to DoB
#    --- Add an age calculator to account object to work out age automatically

# IMPORTANT

# create lesson page

# commit to database

# class browser

# ----- display all classes from a certain place

# -- therefore need a location select page after clicking book button that will be added to main page

# clicking book, brings up screen in more detail with info and a conf button

# ---- adds user_id lesson id date to bookings

# ----- this should check to see all the classes where lesson id and date matches, count the number,
# and compare to maximum number of people

# page to seen own bookings

# page identical to bookings for instructor, but when clicked on brings up every student booked. copy pasta

# ---- account edit screen after new account and editing own personal account

# ---- lesson amend, delete

# New cluster of pages management umbrella  for instructors also contain a creation widget thingy for student/lesson
#       account search system?
#       ability to edit account and delete accounts as instuctor
#       approve page as well.

# time until grade

# geolocation reccomendation feature


# other things
# create custom error 500 page

# Create the app
app = Flask(__name__)

# Configure App
# Configure DB

db = yaml.safe_load(open('db.yaml'))


# !!!WARNING!!! DEV TOOL ONLY
# This deletes all tables from current database in order to refresh them. This method is extremely destructive and
# must be used with caution
def DeleteAllTables(cursor, key):
    if key == db['db_wipe_key']:
        try:
            cursor.execute("DROP TABLE BOOKINGS")
        except:
            print("Table doesn't exist")
        try:
            cursor.execute("DROP TABLE LESSONS")
        except:
            print("Table doesn't exist")
        try:
            int("hello")
            cursor.execute("DROP TABLE ACCOUNTS")

        except:
            print("Table doesn't exist")

        try:
            int("hello")
            cursor.execute("DROP TABLE USERS")

        except:
            print("Table doesn't exist")

        try:
            int("hello")
            cursor.execute("DROP TABLE BELTS")

        except:
            print("Table doesn't exist")

        print("\n\n" + "-" * 60 + "\n\nDatabase has been wiped.\n\n" + '-' * 60)
    else:
        print("\n\n" + "-" * 60 + "\n\nDatabase wipe attempted and failed due to invalid key.\n\n" + '-' * 60)


# SQL Statements for table check and creation

TABLES = {'BELTS': '''CREATE TABLE BELTS(
                   belt_id int PRIMARY KEY,
                   belt_name char(50) NOT NULL,
                   wait_time DATE);''', 'USERS': ''' CREATE TABLE USERS(
                   user_id int PRIMARY KEY,
                   belt_id int NOT NULL,
                   first_name char(50) NOT NULL,
                   last_name char(50) NOT NULL,
                   age int NOT NULL,
                   last_graded DATE,      
                   FOREIGN KEY(belt_id) REFERENCES belts(belt_id));''', 'ACCOUNTS': '''CREATE TABLE ACCOUNTS(
                      id int PRIMARY KEY,
                      user_id int NOT NULL,
                      email char(100) NOT NULL UNIQUE,
                      password_hash char(90) NOT NULL,
                      authority char(10) NOT NULL,
                      date_added DATE,
                      last_logged_in DATE,
                      approved bool NOT NULL,
                      FOREIGN KEY (user_id) REFERENCES Users(user_id));''', 'LESSONS': '''CREATE TABLE LESSONS(
                     lesson_id int AUTO_INCREMENT,
                     day char(10) NOT NULL,
                     day_index int NOT NULL,
                     start_time TIME NOT NULL,
                     end_time TIME NOT NULL,
                     location char(50),
                     maximum int NOT NULL,
                     info char(200),
                     level char(50) NOT NULL,
                     PRIMARY KEY (lesson_id));''', 'BOOKINGS': '''CREATE TABLE BOOKINGS(
                      booking_id int PRIMARY KEY,
                      user_id int NOT NULL,
                      lesson_id int NOT NULL,
                      date DATE NOT NULL,
                      FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id),
                      FOREIGN KEY (user_id) REFERENCES Users(user_id));'''}

Belt_lookup_table = '''INSERT INTO BELTS(belt_id, belt_name, wait_time) VALUES (0, 'Not Selected', '0000-00-00'),
                    (1, 'White', '0000-03-00'),
                    (2, 'Orange - One White Stripe', '0000-03-00'),
                    (3, 'Orange', '0000-03-00'),
                    (4, 'Yellow', '0000-03-00'),
                    (5, 'Green','0000-03-00'),
                    (6, 'Purple', '0000-03-00'),
                    (7, 'Blue', '0000-03-00'),
                    (8, 'Brown - One White Stripe', '0000-03-00'),
                    (9, 'Brown - Two White Stripe', '0000-03-00'),
                    (10, 'Brown', '0000-03-00'),
                    (11, '1st Dan', '0000-03-00'),
                    (12, '2nd Dan', '0000-03-00'),
                    (13, '3rd Dan', '0000-03-00'),
                    (14, '4th Dan', '0000-03-00'),
                    (15, '5th Dan', '0000-03-00'),
                    (16, '6th Dan', '0000-03-00'),
                    (17, '7th Dan', '0000-03-00'),
                    (18, '8th Dan', '0000-03-00'),
                    (19, '9th Dan', '0000-03-00'),
                    (20, '10th Dan', '0000-03-00');'''

try:  # try statement to provide user-friendly error messages if any database-related errors are raised
    mydb = mysql.connector.connect(  # configure connection to mysql database
        host=db['mysql_host'],
        user=db['mysql_user'],
        password=db['mysql_password'],
        port=db['mysql_port'],
        database=db['mysql_db'],
        auth_plugin='mysql_native_password')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Unable to authorise access to database")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

# Create cursor to run commands to database
mycursor = mydb.cursor(buffered=True)


# CREATE THE TABLES WHICH DO NOT EXIST

def table_check(cursor):
    table_count = 0

    for table_name in TABLES:
        table_sql_statement = TABLES[table_name]
        try:
            print("Attempting to create table: {}".format(table_name), end='  -  ')
            cursor.execute(table_sql_statement)
            mydb.commit()
            table_count += 1
            # checks each table to name for required table which needs filling
            if table_name == "BELTS":
                mycursor.execute(Belt_lookup_table)
                mydb.commit()
                print("Belts Table filled.", end=' - ')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Already Exists.")
                table_count += 1
            else:
                print(err.msg)
        else:
            print("Table was missing and has been created")

    if table_count == 5:
        print("\n All required tables are present within the database")


# Checks to see if any tables are missing
# DeleteAllTables(mycursor, 9121)
table_check(mycursor)
mydb.commit()

# CREATE DATABASE TABLES IF MISSING

# Secret key
app.config['SECRET_KEY'] = db['app_secret_key']


# ======================================================================================================================
# Forms (WTF!)
# ======================================================================================================================


# Create Login Form

class ConfirmForm(FlaskForm):
    submit = SubmitField("Confirm")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Password Form
class PasswordForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password_hash = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NewStudentForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    belt_id = SelectField("Belt", choices=[('0', 'Choose...'), ('1', 'White'), ('2', 'Orange - One White Stripe'),
                                           ('3', 'Orange'), ('4', 'Yellow'), ('5', 'Green'), ('6', 'Purple'),
                                           ('7', 'Blue'), ('8', 'Brown - One White Stripe'),
                                           ('9', 'Brown - Two White Stripes'), ('10', 'Brown'), ('11', '1st Dan'),
                                           ('12', '2nd Dan'), ('13', '3rd Dan'), ('14', '4th Dan'),
                                           ('15', '5th Dan'), ('16', '6th Dan'), ('17', '7th Dan'),
                                           ('18', '8th Dan'), ('19', '9th Dan'), ('20', '10th Dan')],
                          validators=[NoneOf('0', 'Choose...')])

    authority = SelectField("Account Type", choices=[('0', 'Choose...'), ('student', 'Student'),
                                                     ('instructor', 'Instructor')],
                            validators=[NoneOf('0', 'Choose...')])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('password_match',
                                                                             message='Passwords Must Match!')], )
    password_match = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Confirm")


class EditStudentForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    belt_id = SelectField("Belt", choices=[('0', 'Choose...'), ('1', 'White'), ('2', 'Orange - One White Stripe'),
                                           ('3', 'Orange'), ('4', 'Yellow'), ('5', 'Green'), ('6', 'Purple'),
                                           ('7', 'Blue'), ('8', 'Brown - One White Stripe'),
                                           ('9', 'Brown - Two White Stripes'), ('10', 'Brown'), ('11', '1st Dan'),
                                           ('12', '2nd Dan'), ('13', '3rd Dan'), ('14', '4th Dan'),
                                           ('15', '5th Dan'), ('16', '6th Dan'), ('17', '7th Dan'),
                                           ('18', '8th Dan'), ('19', '9th Dan'), ('20', '10th Dan')],
                          validators=[NoneOf('0', 'Choose...')])

    authority = SelectField("Account Type", choices=[('0', 'Choose...'), ('student', 'Student'),
                                                     ('instructor', 'Instructor')],
                            validators=[NoneOf('0', 'Choose...')])
    submit = SubmitField("Confirm")


class SignUpForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('password_match',
                                                                             message='Passwords Must Match!')], )
    password_match = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Confirm")


class NewLessonForm(FlaskForm):
    day = SelectField("Day", choices=[('0', 'Choose...'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'),
                                      ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'),
                                      ('Saturday', 'Saturday'),
                                      ('Sunday', 'Sunday')],
                      validators=[NoneOf('0', 'Choose...')])

    lesson_start = TimeField('Lesson start', validators=[DataRequired()])
    lesson_end = TimeField('Lesson end', validators=[DataRequired()])
    maximum = IntegerField('Maximum Students', validators=[DataRequired()])
    location = SelectField("Location", choices=[('0', 'Choose...'), ('wincanton', 'Wincanton'), ('merriot', 'Merriot'),
                                                ('queen camel', 'Queen Camel')],
                           validators=[NoneOf('0', 'Choose...')])
    level = SelectField("Aimed at:", choices=[('0', 'Choose...'),('all', 'All'), ('adults', 'Adults'), ('children', 'Children'),
                                            ('little samurai', 'Little Samurai'), ('senior grades', 'Senior Grades'), ('junior grades', 'Junior Grades')],
                           validators=[NoneOf('0', 'Choose...')])
    information = StringField("Class Information", validators=[DataRequired()], widget=TextArea())

    submit = SubmitField("Confirm")

    def validate_times(self, lesson_start, lesson_end):
        if lesson_start > lesson_end:
            return False
        else:
            return True


def calc_date_between(start, end):

    if end == "now":
        end = datetime.utcnow()

    try:
        start = start.date()
    except:
        print("Start date is already in date form")

    try:
        end = end.date()
    except:
        print("End date is already in date form")
    diff = relativedelta(end, start)
    years = diff.years
    months = diff.months
    days = diff.days

    Date_in_form = date(years, months, days)

    return  Date_in_form, years, months, days


def conv_accountid_obj(id):
    where_parameter = (str(id),)
    sql_fetch_all_accounts = "SELECT * FROM accounts WHERE id = %s"
    sql_fetch_all_users = "SELECT * FROM users WHERE user_id = %s"
    mycursor.execute(sql_fetch_all_accounts, where_parameter)
    account_data = mycursor.fetchall()
    mycursor.execute(sql_fetch_all_users, where_parameter)
    user_data = mycursor.fetchall()

    current = Account(id)

    current.user_id = id
    current.email = account_data[0][2]
    current.password_hash = account_data[0][3]
    current.authority = account_data[0][4]
    current.date_added = account_data[0][5]
    current.last_logged_in = account_data[0][6]
    current.belt_id = user_data[0][1]
    current.first_name = user_data[0][2]
    current.last_name = user_data[0][3]
    current.last_graded = user_data[0][5]
    current.age = user_data[0][4]
    return current


def conv_lessonid_obj(id):
    where_parameter = (str(id),)
    sql_fetch_all_lessons = "SELECT * FROM lessons WHERE lesson_id = %s"
    mycursor.execute(sql_fetch_all_lessons, where_parameter)
    lessons_data = mycursor.fetchall()
    current = Lesson(id)

    current.day = lessons_data[0][1]
    current.day_index = lessons_data[0][2]
    current.start_time = lessons_data[0][3]
    current.end_time = lessons_data[0][4]
    current.location = lessons_data[0][5]
    current.maximum = lessons_data[0][6]
    current.info = lessons_data[0][7]
    current.level = lessons_data[0][8]

    return current


def conv_beltid_name(id):
    get_name = "SELECT belt_name FROM belts WHERE belt_id = %s"
    id_str = (str(id),)
    mycursor.execute(get_name, id_str)
    belt_name = mycursor.fetchone()
    return belt_name[0]


def conv_date_day(date):
    date = calendar.day_name[date.weekday()]
    return date


def conv_date_string(date):
    date_string = date[0:16]
    return date_string


# Function to update an account object to the database
def update_account_to_db(account):
    try:
        accounts_id = account.id
        accounts_email = account.email
        accounts_password_hash = account.password_hash
        accounts_last_logged_in = account.last_logged_in
        accounts_date_added = account.date_added
        accounts_authority = account.authority
        foreign_user_id = account.user_id
        users_first_name = account.first_name
        users_last_name = account.last_name
        users_age = account.age
        foreign_belt_id = account.belt_id
        users_last_graded = account.last_graded

        mycursor.execute("UPDATE Accounts SET email=%s, password_hash=%s, last_logged_in=%s, date_added=%s, "
                         "authority=%s, user_id=%s WHERE id=%s", (accounts_email, accounts_password_hash,
                                                                  accounts_last_logged_in, accounts_date_added,
                                                                  accounts_authority,
                                                                  foreign_user_id, accounts_id))
        mycursor.execute("UPDATE Users SET first_name=%s, last_name=%s, age=%s, last_graded=%s, belt_id=%s WHERE "
                         "user_id=%s", (users_first_name, users_last_name, users_age, users_last_graded,
                                        foreign_belt_id, foreign_user_id))
        mydb.commit()
    except:
        print("Error Commiting changes to the database.")


def insert_account_into_db(account):
    try:
        accounts_id = account.id
        accounts_email = account.email
        accounts_password_hash = account.password_hash
        accounts_last_logged_in = account.last_logged_in
        accounts_date_added = account.date_added
        accounts_authority = account.authority
        foreign_user_id = account.user_id
        users_first_name = account.first_name
        users_last_name = account.last_name
        users_age = account.age
        foreign_belt_id = account.belt_id
        users_last_graded = account.last_graded
        account_approved = account.approved

        sql_insert_into_accounts = "INSERT INTO accounts (id, user_id ,email, password_hash, authority, " \
                                   "last_logged_in, date_added, approved) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
        accountValues = (accounts_id, foreign_user_id, accounts_email, accounts_password_hash, accounts_authority,
                         accounts_last_logged_in, accounts_date_added, account_approved)

        sql_insert_into_users = "INSERT INTO users (user_id, first_name, last_name, age, belt_id,last_graded) VALUES " \
                                "(%s, %s, %s, %s, %s, %s) "
        userValues = (foreign_user_id, users_first_name, users_last_name, users_age, foreign_belt_id, users_last_graded)

        mycursor.execute(sql_insert_into_users, userValues)
        mycursor.execute(sql_insert_into_accounts, accountValues)

        mydb.commit()

    except mysql.connector.Error as error:
        print(error.msg)

def insert_lesson_into_db(lesson):
    try:

        sql_insert_into_lessons = "INSERT INTO lessons (lesson_id, day ,day_index, start_time, end_time, location, " \
                                   "maximum, info, level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
        lessonvalues = (lesson.lesson_id, lesson.day,lesson.day_index, lesson.start_time, lesson.end_time, lesson.location,
                         lesson.maximum, lesson.info, lesson.level)

        mycursor.execute(sql_insert_into_lessons, lessonvalues)


        mydb.commit()

    except mysql.connector.Error as error:
        print(error.msg)



def book_into_lesson(lesson_id,user_id, date_to_book):
    try:
        print("test1")
        mycursor.execute("SELECT booking_id FROM bookings ORDER BY booking_id DESC")
        print("2")
        next_id = mycursor.fetchone()
        print("3")

        try:
            new_id = int(next_id[0]) + 1
        except:
            new_id = 1

        sql_insert_into_bookings = "INSERT INTO bookings (booking_id, user_id ,lesson_id, date) VALUES (%s, %s, %s, %s)"
        print("4")
        booking_values = (new_id, user_id, int(lesson_id), date_to_book)
        print("5")

        mycursor.execute(sql_insert_into_bookings, booking_values)
        print("6")

        mydb.commit()
        print("7")

    except mysql.connector.Error as error:
        print("failed")
        print(error.msg)


# ======================================================================================================================
# Decorators - Main Website
# ======================================================================================================================

# Create a route decorator
@app.route('/', methods=['GET','POST'])
def index():  # Opening Page
    session['user'] = None
    return render_template("index.html")


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            find_account = "SELECT id FROM accounts WHERE email = %s"
            where_condition = (form.email.data,)
            mycursor.execute(find_account, where_condition)
            login_id = mycursor.fetchone()
            account_data_all = conv_accountid_obj(login_id[0])

            # Check Hashed Password with inputted one
            if check_password_hash(account_data_all.password_hash, form.password.data):
                flash("Login Successful!", "success")
                session['user'] = account_data_all.__dict__
                session['manage_user'] = None
                session['user']['_date_added'] = session['user']['_date_added']
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password or Username. Try Again...", category="danger_below")
        except:
            print("account doesn't exist")
            flash("Wrong Password or Username. Try Again...", category="danger_below")
    return render_template('login.html', form=form)


# Create Logout Function
@app.route('/logout', methods=['GET', 'POST'])
# LOG IN REQUIRED
def logout():
    session['user'] = None

    flash("You Have been logged out!", "info")
    return render_template('index.html')


# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
# LOG IN REQUIRED
def dashboard():
    belt_id = session['user']['_belt_id']
    belt_name_q = "SELECT belt_name FROM belts WHERE belt_id = %s"
    belt_id = (belt_id,)
    mycursor.execute(belt_name_q, belt_id)
    belt_name = mycursor.fetchall()
    date_added = conv_date_string(session['user']['_date_added'])
    return render_template('dashboard.html', belt_name=belt_name[0][0], date_added=date_added)


# ======================================================================================================================
# Accounts
# ======================================================================================================================

@app.route('/account/create', methods=['GET', 'POST'])
def create_student():
    try:
        account = conv_accountid_obj(session['user']['_id'])
        auth = account.authority
        if auth != "instructor":
            flash("Sorry, you must be logged in as an instructor to use this feature.", category="danger_below")
            return redirect(url_for('login'))

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    if session['manage_user'] is None:

        form = NewStudentForm()
        account = None

        if form.validate_on_submit():
            search_account_statement = "SELECT * FROM accounts WHERE email = %(email)s"
            parameter = {'email': form.email.data}
            mycursor.execute(search_account_statement, parameter)
            account = mycursor.fetchone()

            if account is None:
                mycursor.execute("SELECT id FROM accounts ORDER BY id DESC")

                next_id = mycursor.fetchone()
                try:
                    new_id = int(next_id[0]) + 1

                except:
                    new_id = 1
                new_account = Account(new_id)

                # Hash password
                hashed_pw = generate_password_hash(form.password.data, "sha256")
                # find belt in database
                current_date = datetime.utcnow()
                current_date = current_date.date()
                new_account.email = form.email.data
                new_account.first_name = form.first_name.data
                new_account.last_name = form.last_name.data
                new_account.belt_id = form.belt_id.data
                new_account.authority = form.authority.data
                new_account.age = form.age.data
                new_account.date_added = current_date
                new_account.password_hash = hashed_pw
                new_account.last_logged_in = current_date
                new_account.last_graded = current_date
                new_account.approved = True
                insert_account_into_db(new_account)
                session['manage_user'] = new_account.__dict__
                belt_name = conv_beltid_name(session['manage_user']['_belt_id'])
                session['belt_name'] = belt_name
                flash("User Added Successfully!", 'success')
                return redirect(url_for('create_student'))

            form.first_name.data = ''
            form.last_name.data = ''
            form.email.data = ''
            form.belt_id.data = ''
            form.authority.data = ''
            form.password.data = ''
            form.password_match.data = ''
            form.age.data = ''

        return render_template("create_student.html",
                               form=form)
    else:
        return render_template("create_student.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    account = None

    if form.validate_on_submit():
        search_account_statement = "SELECT * FROM accounts WHERE email = %(email)s"
        parameter = {'email': form.email.data}
        mycursor.execute(search_account_statement, parameter)
        account = mycursor.fetchone()

        if account is None:
            mycursor.execute("SELECT id FROM accounts ORDER BY id DESC")

            next_id = mycursor.fetchone()
            try:
                new_id = int(next_id[0]) + 1

            except:
                new_id = 1
            new_account = Account(new_id)

            # Hash password
            hashed_pw = generate_password_hash(form.password.data, "sha256")
            # find belt in database
            new_account.email = form.email.data
            new_account.first_name = form.first_name.data
            new_account.last_name = form.last_name.data
            new_account.belt_id = 1
            new_account.authority = 'student'
            new_account.age = form.age.data
            new_account.date_added = datetime.utcnow()
            new_account.password_hash = hashed_pw
            new_account.last_logged_in = datetime.utcnow()
            new_account.last_graded = datetime.utcnow()
            new_account.approved = True
            insert_account_into_db(new_account)

            flash("Account request Successful! Please wait for the account to be approved by your instructor.",
                  'success')
            return redirect(url_for('index'))

        form.first_name.data = ''
        form.last_name.data = ''
        form.email.data = ''
        form.password.data = ''
        form.password_match.data = ''
        form.age.data = ''

    return render_template("signup.html",
                           form=form)


@app.route('/account/delete/')
def delete_account(id):
    account_to_delete = Accounts.query.get_or_404(id)
    try:
        db.session.delete(account_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        return render_template("dashboard.html")

    except:
        flash("Whoops! There was a problem deleting user. Try again...")
        return redirect(url_for('account_details', id=id))


@app.route('/account/edit/', methods=['GET', 'POST'])
def edit_account():
    account = Accounts.query.get_or_404(id)
    form = EditStudentForm()
    if form.validate_on_submit():
        print("HERE")
        account.user.first_name = form.first_name.data
        account.user.last_name = form.last_name.data
        account.email = form.email.data
        account.user.belt = Belts.query.filter_by(belt_id=form.belt_id.data).first()
        account.authority = form.authority.data
        account.user.age = int(form.age.data)
        # Update Database
        db.session.add(account)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('account_details', id=account.id))

    form.first_name.data = account.user.first_name
    form.last_name.data = account.user.last_name
    form.email.data = account.email
    form.belt_id.data = str(account.user.belt.belt_id)
    form.authority.data = account.authority
    form.age.data = str(account.user.age)
    return render_template('edit_account.html', form=form)


@app.route('/account/check', methods=['GET', 'POST'])
def account_details():
    return render_template("account.html")


# ======================================================================================================================
# Lessons
# ======================================================================================================================


@app.route('/create/lesson', methods=['GET', 'POST'])
def create_lesson():

    form = NewLessonForm()
    try:
        account = conv_accountid_obj(session['user']['_id'])
        auth = account.authority
        if auth != "instructor":
            flash("Sorry, you must be logged in as an instructor to use this feature.", category="danger_below")
            return redirect(url_for('login'))

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    if form.validate_on_submit():
        if form.validate_times(form.lesson_start.data, form.lesson_end.data):
            search_lessons_statement = "SELECT day, start_time, lesson_id, location FROM lessons WHERE start_time = %(start_time)s AND day = %(day)s and location = %(location)s"
            parameter = {'start_time': form.lesson_start.data, 'day': form.day.data, 'location': form.location.data}
            mycursor.execute(search_lessons_statement, parameter)
            lesson = mycursor.fetchone()

            if lesson is None:
                mycursor.execute("SELECT lesson_id FROM lessons ORDER BY lesson_id DESC")
                next_id = mycursor.fetchone()

                try:
                    new_id = int(next_id[0]) + 1
                except:
                    new_id = 1

                new_lesson = Lesson(new_id)

                new_lesson.day = form.day.data
                new_lesson.start_time = form.lesson_start.data
                new_lesson.end_time = form.lesson_end.data
                new_lesson.location = form.location.data
                new_lesson.maximum = form.maximum.data
                new_lesson.info = form.information.data
                new_lesson.level = form.level.data

                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                new_lesson.day_index = days.index(form.day.data)
                insert_lesson_into_db(new_lesson)

                flash("Lesson created Successfully!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("WARNING. There is already a lesson booked at this location for this slot.", "warning")

            form.day.data = ''
            form.lesson_start.data = ''
            form.lesson_end.data = ''
            form.location.data = ''
            form.maximum.data = ''
            form.information.data = ''
            form.level.data = ''

        else:
            flash("End time must be after the start time.", "danger")

    return render_template("create_lesson.html",
                           form=form)


@app.route('/book/location', methods=['GET', 'POST'])
def location_choice():

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))


    return render_template("location_choice.html")


# ======================================================================================================================
# Wincanton
# ======================================================================================================================


@app.route('/book/location/wincanton', methods=['GET', 'POST'])
def location_wincanton():

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    get_bookings = "SELECT * FROM lessons WHERE location = 'wincanton' ORDER BY day_index "
    mycursor.execute(get_bookings)
    lessons = mycursor.fetchall()
    lessons = list(lessons)

    # create variable and list used in loop
    count = 0
    lesson_list = []

    for lesson in lessons:

        lesson = list(lesson)
        time_delta = lesson[3]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds//60) - (hours*60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[3] = time

        time_delta = lesson[4]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[4] = time
        lesson_list.append(lesson)
        count += 1

    lessons = tuple(lesson_list)
    return render_template("location_wincanton.html", lessons=lessons)


@app.route('/book/location/wincanton/<id>', methods=['GET', 'POST'])
def book_lesson_wincanton(id):
    form = ConfirmForm()

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    get_bookings = "SELECT * FROM lessons WHERE location = 'wincanton' ORDER BY day_index "
    mycursor.execute(get_bookings)
    lessons = mycursor.fetchall()
    lessons = list(lessons)
    book_into = conv_lessonid_obj(id)
    booking_information = book_into.__dict__

    time_delta = booking_information['_start_time']
    seconds = time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    if minutes < 10:
        time = "{}:{}0".format(hours, minutes)
    else:
        time = "{}:{}".format(hours, minutes)

    booking_information['_start_time'] = time

    time_delta = booking_information['_end_time']
    seconds = time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    if minutes < 10:
        time = "{}:{}0".format(hours, minutes)
    else:
        time = "{}:{}".format(hours, minutes)

    booking_information['_end_time'] = time




    print(booking_information)
    # create variable and list used in loop
    count = 0
    lesson_list = []

    for lesson in lessons:

        lesson = list(lesson)
        time_delta = lesson[3]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[3] = time

        time_delta = lesson[4]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[4] = time
        lesson_list.append(lesson)
        count += 1
    lessons = tuple(lesson_list)

    if form.validate_on_submit():
        book_into = conv_lessonid_obj(id)
        today_date = date.today()

        today_index = datetime.today().isoweekday()
        today_index -= 1
        diff_today_booking = int(book_into.day_index) - int(today_index)
        date_to_book = today_date + timedelta(days=diff_today_booking)
        number_in_lesson = "SELECT * FROM bookings WHERE lesson_id = %(lesson_id)s AND date = %(date)s"

        parameter = {'lesson_id': book_into.lesson_id, 'date': today_date}
        mycursor.execute(number_in_lesson,parameter)
        database_output = mycursor.fetchall()
        current_total = len(database_output)
        new_total = current_total + 1


        if diff_today_booking < 0:
            flash("This class has already happened this week. Please try booking for a different class.", "danger")
            return redirect(url_for("location_wincanton"))
        if diff_today_booking == 0:
            today = datetime.now()
            time = book_into.start_time

            seconds = time.seconds
            hours = seconds // 3600
            minutes = (seconds // 60) - (hours * 60)
            seconds = seconds - ((minutes * 60) + (hours * 3600))
            year = today.year
            month = today.month
            day = today.day

            lesson_datetime = datetime(year, month, day, hours, minutes, seconds)
            time_diff = lesson_datetime - today

            if time_diff.days < 0:
                flash("This class has already happened. Please try booking for a different class.", "danger")
                return redirect(url_for("location_wincanton"))

        if new_total < book_into.maximum:
            already_booked = "SELECT * FROM bookings WHERE lesson_id = %(lesson_id)s AND date = %(date)s AND user_id " \
                             "= %(user_id)s "
            parameter_2 = {'lesson_id': book_into.lesson_id, 'date': date_to_book, 'user_id': session['user']['_id']}
            mycursor.execute(already_booked, parameter_2)
            check = mycursor.fetchone()

            if check is None:
                book_into_lesson(book_into.lesson_id, session['user']['_id'], date_to_book)

            else:
                flash("You are already booked into this class.", "warning")
                return redirect(url_for("location_wincanton"))
        else:
            flash("Sorry, the class is full.", "warning")
            return redirect(url_for("location_wincanton"))

    return render_template("book_overlay_wincanton.html", lessons=lessons, form=form, info=booking_information)

# ======================================================================================================================
# Merriot
# ======================================================================================================================


@app.route('/book/location/Merriot', methods=['GET', 'POST'])
def location_merriot():

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    get_bookings = "SELECT * FROM lessons WHERE location = 'merriot' ORDER BY day_index "
    mycursor.execute(get_bookings)
    lessons = mycursor.fetchall()
    lessons = list(lessons)

    # create variable and list used in loop
    count = 0
    lesson_list = []

    for lesson in lessons:

        lesson = list(lesson)
        time_delta = lesson[3]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds//60) - (hours*60)

        if minutes < 10:
            time = "{}:{}0".format(hours,minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[3] = time

        time_delta = lesson[4]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[4] = time
        lesson_list.append(lesson)
        count += 1

    lessons = tuple(lesson_list)
    return render_template("location_merriot.html", lessons=lessons)


@app.route('/book/location/merriot/<id>', methods=['GET', 'POST'])
def book_lesson_merriot(id):
    form = ConfirmForm()

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    get_bookings = "SELECT * FROM lessons WHERE location = 'merriot' ORDER BY day_index "
    mycursor.execute(get_bookings)
    lessons = mycursor.fetchall()
    lessons = list(lessons)
    book_into = conv_lessonid_obj(id)
    booking_information = book_into.__dict__

    time_delta = booking_information['_start_time']
    seconds = time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    if minutes < 10:
        time = "{}:{}0".format(hours, minutes)
    else:
        time = "{}:{}".format(hours, minutes)

    booking_information['_start_time'] = time

    time_delta = booking_information['_end_time']
    seconds = time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    if minutes < 10:
        time = "{}:{}0".format(hours, minutes)
    else:
        time = "{}:{}".format(hours, minutes)

    booking_information['_end_time'] = time




    print(booking_information)
    # create variable and list used in loop
    count = 0
    lesson_list = []

    for lesson in lessons:

        lesson = list(lesson)
        time_delta = lesson[3]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[3] = time

        time_delta = lesson[4]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[4] = time
        lesson_list.append(lesson)
        count += 1
    lessons = tuple(lesson_list)

    if form.validate_on_submit():
        book_into = conv_lessonid_obj(id)
        today_date = date.today()

        today_index = datetime.today().isoweekday()
        today_index -= 1
        diff_today_booking = int(book_into.day_index) - int(today_index)
        date_to_book = today_date + timedelta(days=diff_today_booking)
        number_in_lesson = "SELECT * FROM bookings WHERE lesson_id = %(lesson_id)s AND date = %(date)s"

        parameter = {'lesson_id': book_into.lesson_id, 'date': today_date}
        mycursor.execute(number_in_lesson,parameter)
        database_output = mycursor.fetchall()
        current_total = len(database_output)
        new_total = current_total + 1


        if diff_today_booking < 0:
            flash("This class has already happened this week. Please try booking for a different class.", "danger")
            return redirect(url_for("location_merriot"))
        if diff_today_booking == 0:
            today = datetime.now()
            time = book_into.start_time

            seconds = time.seconds
            hours = seconds // 3600
            minutes = (seconds // 60) - (hours * 60)
            seconds = seconds - ((minutes * 60) + (hours * 3600))
            year = today.year
            month = today.month
            day = today.day

            lesson_datetime = datetime(year, month, day, hours, minutes, seconds)
            time_diff = lesson_datetime - today

            if time_diff.days < 0:
                flash("This class has already happened. Please try booking for a different class.", "danger")
                return redirect(url_for("location_merriot"))

        if new_total < book_into.maximum:
            already_booked = "SELECT * FROM bookings WHERE lesson_id = %(lesson_id)s AND date = %(date)s AND user_id " \
                             "= %(user_id)s "
            parameter_2 = {'lesson_id': book_into.lesson_id, 'date': date_to_book, 'user_id': session['user']['_id']}
            mycursor.execute(already_booked, parameter_2)
            check = mycursor.fetchone()

            if check is None:
                book_into_lesson(book_into.lesson_id, session['user']['_id'], date_to_book)

            else:
                flash("You are already booked into this class.", "warning")
                return redirect(url_for("location_merriot"))
        else:
            flash("Sorry, the class is full.", "warning")
            return redirect(url_for("location_merriot"))

    return render_template("book_overlay_merriot.html", lessons=lessons, form=form, info=booking_information)


# ======================================================================================================================
# Queen Camel
# ======================================================================================================================


@app.route('/book/location/queencamel', methods=['GET', 'POST'])
def location_queen_camel():

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    get_bookings = "SELECT * FROM lessons WHERE location = 'queen camel' ORDER BY day_index "
    mycursor.execute(get_bookings)
    lessons = mycursor.fetchall()
    lessons = list(lessons)

    # create variable and list used in loop
    count = 0
    lesson_list = []

    for lesson in lessons:

        lesson = list(lesson)
        time_delta = lesson[3]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds//60) - (hours*60)

        if minutes < 10:
            time = "{}:{}0".format(hours,minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[3] = time

        time_delta = lesson[4]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[4] = time
        lesson_list.append(lesson)
        count += 1

    lessons = tuple(lesson_list)
    print(lessons)
    return render_template("location_queen_camel.html", lessons=lessons)


@app.route('/book/location/queen_camel/<id>', methods=['GET', 'POST'])
def book_lesson_queen_camel(id):
    form = ConfirmForm()

    try:
        account = conv_accountid_obj(session['user']['_id'])

    except:

        flash("Sorry, you must be logged in to use this feature.", category="danger_below")
        return redirect(url_for('login'))

    get_bookings = "SELECT * FROM lessons WHERE location = 'queen camel' ORDER BY day_index "
    mycursor.execute(get_bookings)
    lessons = mycursor.fetchall()
    lessons = list(lessons)
    book_into = conv_lessonid_obj(id)
    booking_information = book_into.__dict__

    time_delta = booking_information['_start_time']
    seconds = time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    if minutes < 10:
        time = "{}:{}0".format(hours, minutes)
    else:
        time = "{}:{}".format(hours, minutes)

    booking_information['_start_time'] = time

    time_delta = booking_information['_end_time']
    seconds = time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)

    if minutes < 10:
        time = "{}:{}0".format(hours, minutes)
    else:
        time = "{}:{}".format(hours, minutes)

    booking_information['_end_time'] = time




    print(booking_information)
    # create variable and list used in loop
    count = 0
    lesson_list = []

    for lesson in lessons:

        lesson = list(lesson)
        time_delta = lesson[3]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[3] = time

        time_delta = lesson[4]
        seconds = time_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) - (hours * 60)

        if minutes < 10:
            time = "{}:{}0".format(hours, minutes)
        else:
            time = "{}:{}".format(hours, minutes)
        lesson[4] = time
        lesson_list.append(lesson)
        count += 1
    lessons = tuple(lesson_list)

    if form.validate_on_submit():
        book_into = conv_lessonid_obj(id)
        today_date = date.today()

        today_index = datetime.today().isoweekday()
        today_index -= 1
        diff_today_booking = int(book_into.day_index) - int(today_index)
        date_to_book = today_date + timedelta(days=diff_today_booking)
        number_in_lesson = "SELECT * FROM bookings WHERE lesson_id = %(lesson_id)s AND date = %(date)s"

        parameter = {'lesson_id': book_into.lesson_id, 'date': today_date}
        mycursor.execute(number_in_lesson,parameter)
        database_output = mycursor.fetchall()
        current_total = len(database_output)
        new_total = current_total + 1


        if diff_today_booking < 0:
            flash("This class has already happened this week. Please try booking for a different class.", "danger")
            return redirect(url_for("location_queen_camel"))
        if diff_today_booking == 0:
            today = datetime.now()
            time = book_into.start_time

            seconds = time.seconds
            hours = seconds // 3600
            minutes = (seconds // 60) - (hours * 60)
            seconds = seconds - ((minutes * 60) + (hours * 3600))
            year = today.year
            month = today.month
            day = today.day

            lesson_datetime = datetime(year, month, day, hours, minutes, seconds)
            time_diff = lesson_datetime - today

            if time_diff.days < 0:
                flash("This class has already happened. Please try booking for a different class.", "danger")
                return redirect(url_for("location_queen_camel"))

        if new_total < book_into.maximum:
            already_booked = "SELECT * FROM bookings WHERE lesson_id = %(lesson_id)s AND date = %(date)s AND user_id " \
                             "= %(user_id)s "
            parameter_2 = {'lesson_id': book_into.lesson_id, 'date': date_to_book, 'user_id': session['user']['_id']}
            mycursor.execute(already_booked, parameter_2)
            check = mycursor.fetchone()

            if check is None:
                book_into_lesson(book_into.lesson_id, session['user']['_id'], date_to_book)

            else:
                flash("You are already booked into this class.", "warning")
                return redirect(url_for("location_queen_camel"))
        else:
            flash("Sorry, the class is full.", "warning")
            return redirect(url_for("location_queen_camel"))

    return render_template("book_overlay_queen_camel.html", lessons=lessons, form=form, info=booking_information)
# ======================================================================================================================
# Error Handlers
# ======================================================================================================================


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

# test = conv_accountid_obj(1).__dict__
# test2 = conv_accountid_obj(2).__dict__
# dict  = [test,test2]
# test3 = dict
# for x in dict:
#    print(x)
#    print(x['_email'])

# Run the App
if __name__ == '__main__':
    app.run(debug=True)

webbrowser.open('http://127.0.0.1:5000/')