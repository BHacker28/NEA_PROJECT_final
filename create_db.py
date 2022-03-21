import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="NEAKokoro0232#"
)

my_cursor = mydb.cursor()

# commented to stop accidental run.
#my_cursor.execute("CREATE DATABASE nma")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)