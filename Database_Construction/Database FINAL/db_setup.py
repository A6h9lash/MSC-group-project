from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#Creating the engine so the SQLAlchemy can communicate with our Database file.
engine = create_engine('sqlite:///Database.db', convert_unicode=True)

#Creating the session to act as the intermediary where queries are passed on to the engine.
db_session = scoped_session(sessionmaker(autocommit=False,
										autoflush=False,
										bind=engine))

#We then instantiate a base to set up the basis for all of our database tables to be imported.
Base = declarative_base()
Base.query = db_session.query_property()

#We then set up a function to import our models file to set up the tables for our database.
def init_db():
	import models
	Base.metadata.create_all(bind=engine)
