import sqlite3

class CoffeeDB():
    """
    Database helper function for coffee chatbot
    CoffeeDB.conn is the Connection object that represents the database
    CoffeeDB.c is the Cursor object to perform SQL commands
    
    More info about DB-API interface for SQLite databases:
    https://docs.python.org/3/library/sqlite3.html#cursor-objects
    """

    def __init__ (self, dbname = 'coffeebot.db'):
        self.conn = sqlite3.connect(dbname,check_same_thread=False)
        self.c = self.conn.cursor()
    
    def setup(self):
        '''declares database schema'''

        self.c.execute(''' 
                CREATE TABLE IF NOT EXISTS
                users
                (user_id INT PRIMARY KEY,
                chat_id INT UNIQUE,
                datetime DATETIME,
                username VARCHAR(50) NOT NULL,
                firstname VARCHAR(50) NOT NULL,
                gender VARCHAR(20) DEFAULT 'They/Them',
                agegroup VARCHAR(10),
                bio VARCHAR(300),
                matched INT DEFAULT 0
                )
            ''')
        self.conn.commit()

if __name__ == "__main__":
    db = CoffeeDB()
    db.setup()
    db.c.execute(''' SELECT * FROM users ''')
    print(db.c.fetchall())