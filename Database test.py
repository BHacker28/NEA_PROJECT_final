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
from random import randint
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



# Configure App
# Configure DB

db = yaml.safe_load(open('db.yaml'))

# SQL Statements for table check and creation
TABLES = {}


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


TABLES['BELTS'] = '''CREATE TABLE BELTS(
                   belt_id int PRIMARY KEY,
                   belt_name char(50) NOT NULL,
                   wait_time DATE);'''


TABLES['users'] = '''CREATE TABLE USERS(
                   user_id int PRIMARY KEY,
                   belt_id int NOT NULL,
                   first_name char(50) NOT NULL,
                   last_name char(50) NOT NULL,
                   age int NOT NULL,
                   last_graded DATETIME,      
                   FOREIGN KEY(belt_id) REFERENCES belts(belt_id));'''

TABLES['accounts'] = '''CREATE TABLE ACCOUNTS(
                      id int PRIMARY KEY,
                      user_id int NOT NULL,
                      email char(100) NOT NULL UNIQUE,
                      password_hash char(90) NOT NULL,
                      authority char(10) NOT NULL,
                      date_added DATETIME,
                      last_logged_in DATETIME,
                      FOREIGN KEY (user_id) REFERENCES Users(user_id));'''

TABLES['lessons'] = '''CREATE TABLE LESSONS(
                     lesson_id int AUTO_INCREMENT,
                     id int NOT NULL,
                     day char(10) NOT NULL,
                     time int NOT NULL,
                     location char(50),
                     PRIMARY KEY (lesson_id));'''

TABLES['bookings'] = '''CREATE TABLE BOOKINGS(
                      booking_id int PRIMARY KEY,
                      user_id int NOT NULL,
                      lesson_id int NOT NULL,
                      date DATE NOT NULL,
                      position int NOT NULL,
                      FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id),
                      FOREIGN KEY (user_id) REFERENCES Users(user_id));'''

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
    for table_name in TABLES:
        table_sql_statement = TABLES[table_name]
        try:
            print("Attempting to create table: {}".format(table_name), end=' - ')
            cursor.execute(table_sql_statement)
            mydb.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("{} Already Exists.".format(table_name))
            else:
                print(err.msg)
        else:
            print("Table was missing and has been created")


# Main
# DeleteAllTables(mycursor)
# table_check(mycursor)

mycursor.execute("INSERT INTO belts(belt_id, belt_name, wait_time) VALUES (1, 'White', '0000-03-00'), "
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
