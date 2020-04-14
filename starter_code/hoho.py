import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("postgres://postgres:areeg@localhost:5432/fyyurproject")) 
db = scoped_session(sessionmaker(bind=engine))    

flights = db.execute("SELECT city, state, FROM Venue").fetchall() 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:areeg@localhost:5432/fyyurproject'

print(flights)