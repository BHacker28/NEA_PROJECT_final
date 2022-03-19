from flask import Flask, render_template, flash, request, redirect, url_for, sessions
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, SelectField, IntegerField, \
    validators
from wtforms.validators import DataRequired, EqualTo, Length, NoneOf
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
import yaml
import mysql.connector
from mysql.connector import errorcode

# !!!!! Clean up, remove all tutorial junk into separate file, doesnt matter it runs or not


# !!!! Remove instructor table
# !!!! Add location to lesson table

# !!! Need Belt id not name in account object
# !!! class to add new account must account for relations

# !! CREATE TABLE CREATION STATEMENTS
# !! REMOVE CAPACITY TABLE

# ! Change age to DoB
#    --- Add a age calculator to account object to work out age automatically

# IMPORTANT
# MUST CHANGE BELT OPTION TO READ OFF BELTS TABLES

# Add position in class to bookings, remove capacity table and authority
# therefore need to add adding to instructor table if the field is set to instructor

# remove login in manager
# replace with flask session

# add a method for commit a account object to database using cursor

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
def DeleteAllTables(cursor):
    try:
        cursor.execute("DROP TABLE BOOKINGS")
    except:
        print("Table doesn't exist")

    try:
        cursor.execute("DROP TABLE LESSONS")
    except:
        print("Table doesn't exist")
    try:
        cursor.execute("DROP TABLE ACCOUNTS")
    except:
        print("Table doesn't exist")

    try:
        cursor.execute("DROP TABLE USERS")
    except:
        print("Table doesn't exist")

    try:
        cursor.execute("DROP TABLE BELTS")
    except:
        print("Table doesn't exist")


# SQL Statments for table check and creation
TABLES = {'BELTS': '''CREATE TABLE BELTS(
                   belt_id int PRIMARY KEY,
                   belt_name char(50) NOT NULL,
                   wait_time DATE);''', 'USERS': '''CREATE TABLE USERS(
                   user_id int PRIMARY KEY,
                   belt_id int NOT NULL,
                   first_name char(50) NOT NULL,
                   last_name char(50) NOT NULL,
                   age int NOT NULL,
                   last_graded DATETIME,      
                   FOREIGN KEY(belt_id) REFERENCES belts(belt_id));''', 'ACCOUNTS': '''CREATE TABLE ACCOUNTS(
                      id int PRIMARY KEY,
                      user_id int NOT NULL,
                      email char(100) NOT NULL UNIQUE,
                      password_hash char(90) NOT NULL,
                      authority char(10) NOT NULL,
                      date_added DATETIME,
                      last_logged_in DATETIME,
                      FOREIGN KEY (user_id) REFERENCES Users(user_id));''', 'LESSONS': '''CREATE TABLE LESSONS(
                     lesson_id int AUTO_INCREMENT,
                     id int NOT NULL,
                     day char(10) NOT NULL,
                     time int NOT NULL,
                     location char(50),
                     PRIMARY KEY (lesson_id));''', 'BOOKINGS': '''CREATE TABLE BOOKINGS(
                      booking_id int PRIMARY KEY,
                      user_id int NOT NULL,
                      lesson_id int NOT NULL,
                      date DATE NOT NULL,
                      position int NOT NULL,
                      FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id),
                      FOREIGN KEY (user_id) REFERENCES Users(user_id));'''}


try:  # try statement to provide user-friendly error messages if any database-related errors are raised
    mydb = mysql.connector.connect(  # configure connection to mysql database
        host=db['mysql_host'],
        user=db['mysql_user'],
        password=db['mysql_password'],
        port=db['mysql_port'],
        database=db['mysql_db'])
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Unable to authorise access to database")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

mycursor = mydb.cursor()


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
            if table_name == "BELTS":
                mycursor.execute("INSERT INTO BELTS(belt_id, belt_name, wait_time) VALUES (1, 'White', '0000-03-00'), "
                                 "(2, 'Orange - One White Stripe', '0000-03-00'),"
                                 "(3, 'Orange', '0000-03-00'),"
                                 "(4, 'Yellow', '0000-03-00'),"
                                 "(5, 'Green','0000-03-00'),"
                                 "(6, 'Purple', '0000-03-00'),"
                                 "(7, 'Blue', '0000-03-00'),"
                                 "(8, 'Brown - One White Stripe', '0000-03-00'),"
                                 "(9, 'Brown - Two White Stripe', '0000-03-00'),"
                                 "(10, 'Brown', '0000-03-00'),"
                                 "(11, '1st Dan', '0000-03-00'),"
                                 "(12, '2nd Dan', '0000-03-00'),"
                                 "(13, '3rd Dan', '0000-03-00'),"
                                 "(14, '4th Dan', '0000-03-00'),"
                                 "(15, '5th Dan', '0000-03-00'),"
                                 "(16, '6th Dan', '0000-03-00'),"
                                 "(17, '7th Dan', '0000-03-00'),"
                                 "(18, '8th Dan', '0000-03-00'),"
                                 "(19, '9th Dan', '0000-03-00'),"
                                 "(20, '10th Dan', '0000-03-00')")
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
DeleteAllTables(mycursor)
table_check(mycursor)

# CREATE DATABASE TABLES IF MISSING

# Secret key
app.config['SECRET_KEY'] = db['app_secret_key']


# ======================================================================================================================
# Forms (WTF!)
# ======================================================================================================================


# Create Login Form
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


# Create account object
class Account:

    def __init__(self, id):
        self._id = id
        self._email = None
        self._password_hash = None
        self._user_id = None
        self._authority = None
        self._last_logged_in = None
        self._date_added = None
        self._first_name = None
        self._last_name = None
        self._age = None
        self._belt_id = None
        self._last_graded = None
        self._instructor_id = None
        self._location = None

    # Getters
    @property
    def id(self):
        return self._id

    @property
    def email(self):
        if self._email is None:
            mycursor.execute('SELECT email FROM accounts WHERE id = %s', [self._id])
            email = mycursor.fetchall()
            email = email[0][0]
            self._email = email
            return email
        else:
            return self._email

    @property
    def password_hash(self):
        if self._password_hash is None:
            mycursor.execute('SELECT password_hash FROM accounts WHERE id = %s', [self._id])
            password = mycursor.fetchall()
            password = password[0][0]
            self._password_hash = password
            return password
        else:
            return self._password_hash

    @property
    def user_id(self):
        if self._user_id is None:
            mycursor.execute('SELECT user_id FROM accounts WHERE id = %s', [self._id])
            user_id = mycursor.fetchall()
            user_id = user_id[0][0]
            self._user_id = user_id
            return user_id
        else:
            return self._user_id

    @property
    def authority(self):
        if self._authority is None:
            mycursor.execute('SELECT authority FROM accounts WHERE id = %s', [self._id])
            authority = mycursor.fetchall()
            authority = authority[0][0]
            self._authority = authority
            return authority
        else:
            return self._authority

    @property
    def last_logged_in(self):
        if self._last_logged_in is None:
            mycursor.execute('SELECT last_logged_in FROM accounts WHERE id = %s', [self._id])
            last_logged_in = mycursor.fetchall()
            last_logged_in = last_logged_in[0][0]
            self._last_logged_in = last_logged_in
            return last_logged_in
        else:
            return self._last_logged_in

    @property
    def date_added(self):
        if self._date_added is None:
            mycursor.execute('SELECT date_added FROM accounts WHERE id = %s', [self._id])
            date_added = mycursor.fetchall()
            date_added = date_added[0][0]
            self._date_added = date_added
            return date_added
        else:
            return self._date_added

    @property
    def first_name(self):
        if self._first_name is None:
            mycursor.execute('SELECT first_name FROM users INNER JOIN accounts ON users.user_id = accounts.user_id '
                             'WHERE '
                             'accounts.id = %s', [self._id])
            first_name = mycursor.fetchall()
            first_name = first_name[0][0]
            self._first_name = first_name
            return first_name
        else:
            return self._first_name

    @property
    def last_name(self):
        if self._last_name is None:
            mycursor.execute('SELECT last_name FROM users INNER JOIN accounts ON users.user_id = accounts.user_id '
                             'WHERE '
                             'accounts.id = %s', [self._id])
            last_name = mycursor.fetchall()
            last_name = last_name[0][0]
            self._last_name = last_name
            return last_name
        else:
            return self._last_name

    @property
    def age(self):
        if self._age is None:
            mycursor.execute('SELECT age FROM users INNER JOIN accounts ON users.user_id = accounts.user_id WHERE '
                             'accounts.id = %s', [self._id])
            age = mycursor.fetchall()
            age = age[0][0]
            self._age = age
            return age
        else:
            return self._age

    @property
    def belt_id(self):
        if self._belt_id is None:
            mycursor.execute('SELECT belt_id FROM users INNER JOIN accounts ON users.user_id = accounts.user_id '
                             'WHERE '
                             'accounts.id = %s', [self._id])
            belt_id = mycursor.fetchall()
            belt_id = belt_id[0][0]
            self._belt_id = belt_id
            return belt_id
        else:
            return self._belt_id

    @property
    def last_graded(self):
        if self._last_graded is None:
            mycursor.execute('SELECT last_graded FROM users INNER JOIN accounts ON users.user_id = accounts.user_id '
                             'WHERE '
                             'accounts.id = %s', [self._id])
            last_graded = mycursor.fetchall()
            last_graded = last_graded[0][0]
            self._last_graded = last_graded
            return last_graded
        else:
            return self._last_graded

    @property
    def instructor_id(self):
        if self._instructor_id is None:
            mycursor.execute('SELECT instructor_id FROM instructors INNER JOIN users ON instructors.user_id = '
                             'users.user_id INNER JOIN '
                             'accounts ON users.user_id = accounts.user_id WHERE '
                             'accounts.id = %s', [self._id])
            instructor_id = mycursor.fetchall()
            instructor_id = instructor_id
            self._instructor_id = instructor_id
            return instructor_id
        else:
            return self._instructor_id

    @property
    def location(self):
        if self._location is None:
            mycursor.execute('SELECT location FROM instructors WHERE instructor_id = %s', [self.instructor_id])
            location = mycursor.fetchall()
            location = location[0][0]
            self._location = location
            return location
        else:
            return self._location

    # ------------- Setters -------------

    @id.setter
    def id(self, id):
        self._id = id

    @email.setter
    def email(self, email):
        self._email = email

    @password_hash.setter
    def password_hash(self, password_hash):
        self._password_hash = password_hash

    @user_id.setter
    def user_id(self, user_id):
        self.user_id = user_id

    @authority.setter
    def authority(self, authority):
        self._authority = authority

    @last_logged_in.setter
    def last_logged_in(self, last_logged_in):
        self._last_logged_in = last_logged_in

    @date_added.setter
    def date_added(self, date_added):
        self._date_added = date_added

    @first_name.setter
    def first_name(self, first_name):
        self._first_name = first_name

    @last_name.setter
    def last_name(self, last_name):
        self._last_name = last_name

    @age.setter
    def age(self, age):
        self._age = age

    @belt_id.setter
    def belt_id(self, belt_id):
        self._belt_id = belt_id

    @last_graded.setter
    def last_graded(self, last_graded):
        self._last_graded = last_graded

    @instructor_id.setter
    def instructor_id(self, instructor_id):
        self._instructor_id = instructor_id

    @location.setter
    def location(self, location):
        self._location = location


# Function to update an account object to the database
def update_to_db(account):
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

        sql_insert_into_accounts = "INSERT INTO accounts (id, user_id ,email, password_hash, authority, " \
                                   "last_logged_in, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s)", (accounts_id,
                                                                                                       foreign_user_id,
                                                                                                       accounts_email,
                                                                                                       accounts_password_hash,
                                                                                                       accounts_authority,
                                                                                                       accounts_last_logged_in,
                                                                                                       accounts_date_added)

        sql_insert_into_users = "INSERT INTO users (user_id, first_name, last_name, age, belt_id,last_graded) VALUES " \
                                "(%s, %s, %s, %s, %s, %s)", (
                                    foreign_user_id, users_first_name, users_last_name, users_age, foreign_belt_id,
                                    users_last_graded)

        mycursor.execute(sql_insert_into_accounts)
        mycursor.execute(sql_insert_into_users)
        mydb.commit()

    except mysql.connector.Error as error:
        print(error.msg)


# ======================================================================================================================
# Decorators
# ======================================================================================================================


# Create a route decorator
@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        account = Accounts.query.filter_by(email=form.email.data).first()
        print(account)
        if account:
            # Check Hashed Password
            if check_password_hash(account.password_hash, form.password.data):
                login_user(account)
                flash("Login Successful!", "success")

                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!", "warning")
        else:
            flash("Wrong Password or Username. Try Again...", category="warning")
    return render_template('login.html', form=form)


# Create Logout Function
@app.route('/logout', methods=['GET', 'POST'])
# LOG IN REQUIRED
def logout():
    flash("You Have been logged out!", "info")
    return redirect(url_for('login'))


# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
# LOG IN REQUIRED
def dashboard():
    return render_template('dashboard.html')


# need to change the html as accessing the old method with the account object being incorrect.
# File "E:\College\Computer Science\NEA\Pycharm\templates\create_student.html", line 42, in block 'content'
#    <strong>First Name:</strong> {{ account.user.first_name }}<br/>
# jinja2.exceptions.UndefinedError: 'tuple object' has no attribute 'user'

@app.route('/create/student', methods=['GET', 'POST'])
def create_student():
    print("hello")
    form = NewStudentForm()
    account = None
    print("test6")
    if form.validate_on_submit():
        print("test5")
        search_account_statement = "SELECT * FROM accounts WHERE email = %(email)s"
        parameter = {'email': form.email.data}
        mycursor.execute(search_account_statement, parameter)
        account = mycursor.fetchone()
        print("test4")
        if account is None:
            mycursor.execute("SELECT id FROM accounts ORDER BY id DESC")
            print("test3")
            next_id = mycursor.fetchone()
            try:
                new_id = int(next_id[0]) + 1

            except:
                new_id = 1
            new_account = Account(new_id)

            print("test2")
            # Hash password
            hashed_pw = generate_password_hash(form.password.data, "sha256")
            # find belt in database
            new_account.email = form.email.data
            new_account.first_name = form.first_name.data
            new_account.last_name = form.last_name.data
            new_account.belt_id = form.belt_id.data
            new_account.authority = form.authority.data
            new_account.age = form.age.data
            new_account.date_added = datetime.utcnow()

            print("test1")
            insert_account_into_db(new_account)
            print("test19087097")
            flash("User Added Successfully!", 'success')
            return redirect(url_for('account_details', id=account.id))

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


@app.route('/delete/account/<int:id>')
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


@app.route('/edit/account/<int:id>', methods=['GET', 'POST'])
def edit_account(id):
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


@app.route('/account/<int:id>', methods=['GET', 'POST'])
def account_details(id):
    account = Account(id)
    return render_template("account.html",
                           account=account)


# ======================================================================================================================
# Error Handlers
# ======================================================================================================================


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


# Run the App
if __name__ == '__main__':
    app.run()

