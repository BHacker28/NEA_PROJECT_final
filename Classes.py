# Account Object
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
        self._approved = None

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
    def approved(self):
        return self._approved

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

    @approved.setter
    def approved(self, approved):
        self._approved = approved


# Lesson Object

class Lesson:

    def __init__(self, id):
        self._lesson_id = id
        self._day = None
        self._day_index = None
        self._start_time = None
        self._end_time = id
        self._location = None
        self._maximum = None
        self._info = None
        self._level = None

    # Getters
    @property
    def lesson_id(self):
        return self._lesson_id

    @property
    def day(self):
        return self._day

    @property
    def day_index(self):
        return self._day_index

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def location(self):
        return self._location

    @property
    def maximum(self):
        return self._maximum

    @property
    def info(self):
        return self._info

    @property
    def level(self):
        return self._level

    # ------------- Setters -------------

    @lesson_id.setter
    def lesson_id(self, lesson_id):
        self._lesson_id = lesson_id

    @day.setter
    def day(self, day):
        self._day = day

    @day_index.setter
    def day_index(self, day_index):
        self._day_index = day_index

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

    @end_time.setter
    def end_time(self, end_time):
        self._end_time = end_time

    @location.setter
    def location(self, location):
        self._location = location

    @maximum.setter
    def maximum(self, maximum):
        self._maximum = maximum


    @info.setter
    def info(self, info):
        self._info = info

    @level.setter
    def level(self, level):
        self._level = level

