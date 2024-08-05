import sqlite3 

con = sqlite3.connect('database.db') 
con.execute('ALTER TABLE users ADD COLUMN nome VARCHAR(256)') 
con.close() 