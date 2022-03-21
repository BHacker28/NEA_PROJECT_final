from flask import Flask, render_template, flash, request, redirect, url_for, session
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

# !!!! Remove instructor table
# !!!! Add location to lesson table

# !!! Need Belt id not name in account object
# !!! class to add new account must account for relations

# !! Passwords dont match

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

table_check(mycursor)
mydb.commit()

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
        self._user_id = id
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
        return self._email

    @property
    def password_hash(self):
        return self._password_hash

    @property
    def user_id(self):
        return self._user_id

    @property
    def authority(self):
        return self._authority

    @property
    def last_logged_in(self):
        return self._last_logged_in

    @property
    def date_added(self):
        return self._date_added

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def age(self):
        return self._age

    @property
    def belt_id(self):
        return self._belt_id

    @property
    def last_graded(self):
        return self._last_graded

    @property
    def instructor_id(self):
        return self._instructor_id

    @property
    def location(self):
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
        self._user_id = user_id

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

def conv_id_obj(id):
    where_parameter = (str(id), )
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
    current.last_graded = user_data[0][4]

    return current

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
                                   "last_logged_in, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s) "
        accountValues = (accounts_id, foreign_user_id, accounts_email, accounts_password_hash, accounts_authority,
                         accounts_last_logged_in, accounts_date_added)

        sql_insert_into_users = "INSERT INTO users (user_id, first_name, last_name, age, belt_id,last_graded) VALUES " \
                                "(%s, %s, %s, %s, %s, %s) "
        userValues = (foreign_user_id, users_first_name, users_last_name, users_age, foreign_belt_id, users_last_graded)

        mycursor.execute(sql_insert_into_users, userValues)
        mycursor.execute(sql_insert_into_accounts, accountValues)

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
        try:
            find_account = "SELECT id FROM accounts WHERE email = %s"
            where_condition = (form.email.data, )
            mycursor.execute(find_account,where_condition)
            login_id = mycursor.fetchone()
            account_data_all = conv_id_obj(login_id[0])

            # Check Hashed Password with inputted one
            if check_password_hash(account_data_all.password_hash, form.password.data):
                flash("Login Successful!", "success")
                return render_template('test.html', current_user = account_data_all)
            else:
                flash("Wrong Password or Username. Try Again...", category="danger")
        except:
            print("account doesn't exist")
            flash("Wrong Password or Username. Try Again...", category="danger")

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
            new_account.email = form.email.data
            new_account.first_name = form.first_name.data
            new_account.last_name = form.last_name.data
            new_account.belt_id = form.belt_id.data
            new_account.authority = form.authority.data
            new_account.age = form.age.data
            new_account.date_added = datetime.utcnow()
            new_account.password_hash = hashed_pw
            new_account.last_logged_in = datetime.utcnow()
            new_account.last_graded = datetime.utcnow()
            insert_account_into_db(new_account)

            flash("User Added Successfully!", 'success')
            return redirect(url_for('account_details', id=new_account.id))

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
