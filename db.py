import sqlite3

conn = sqlite3.connect('coffeebot.db')
c = conn.cursor()

c.execute(''' CREATE TABLE users
                (user_id INT PRIMARY KEY,
                chat_id INT UNIQUE,
                username VARCHAR(50) NOT NULL,
                firstname VARCHAR(50) NOT NULL,
                gender VARCHAR(20) DEFAULT 'They/Them',
                agegroup VARCHAR(10),
                bio VARCHAR(300),
                matched INT DEFAULT 0
                )
            ''')

conn.commit()