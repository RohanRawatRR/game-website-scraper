import mysql.connector
from settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME

#establishing the connection
conn = mysql.connector.connect(
   user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, database=DATABASE_NAME
)

#Creating a cursor object using the cursor() method
cursor_obj = conn.cursor()

#Creating table as per requirement
cursor_obj.execute('''
    CREATE TABLE IF NOT EXISTS gi_videogame (
        id SERIAL PRIMARY KEY,
        created_at DATETIME,
        name CHAR(100),
        game_id CHAR(100) UNIQUE,
        all_platforms TEXT(300),
        developer CHAR(100),
        publisher CHAR(100),
        genre CHAR(100),
        industry_rating CHAR(100)
    )''')

cursor_obj.execute("""
    CREATE TABLE IF NOT EXISTS gi_videogame_release (
        id SERIAL PRIMARY KEY,
        videogame_id INTEGER REFERENCES gi_videogame(id),
        release_date DATE,
        released_on_platforms CHAR(250),
        CONSTRAINT unique_game_release UNIQUE(videogame_id, released_on_platforms, release_date)
    );
""")
#Closing the connection
print("Tables have been created")
conn.close()
