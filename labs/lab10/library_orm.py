from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# Add code to create a database engine that stores data in the local directory's library.db
engine = create_engine('sqlite:///library.db')
Base=declarative_base()

# Here we define columns for the table BOOK
# Notice that each column is also a normal Python instance attribute.
# Add columns: id (INT primary key) as INT
#              title, author, year, genre as TEXT
# Note, columns title and author cannot be NULL
class Book(Base):   
    __tablename__ = 'BOOK'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    author = Column(String(250), nullable=False)
    year = Column(String(250))
    genre = Column(String(250))
    
    def __str__(self):
        return "%s %s %s %s %s" % (self.id, self.title, self.author, self.year, self.genre)


class Library(object):

    # Student Task: Complete the code to create all tables in the database.
    def create_table(self):
        try:
            Base.metadata.create_all(engine)
        except:
            print("Table already there.")

    def insert_book(self, i,titl, autho, yea, genr):
        # Bind the engine to the metadata of the Base class so that the
        # declaratives can be accessed through a DBSession instance
        # Create a DBsession() instance to establish all conversations with the database
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        try:
            book = Book(id = i, title = titl, author = autho, year = yea, genre = genr)
            session.add(book)
            session.commit()        
        
        except:
            pass        

        session.close()
        # Student Task: Provide code to insert books into the table BOOK

    def search_book(self,title):
        print("\nSearch for book: " + title + "...")
        
        # Student Task:
        # Add the code to bind the engine to the metadata of the Base Class and
        # create a new DBSession().  Refer to the example in insert_book() method

        # Student Task: Build a query to search a book by Title
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        print(session.query(Book).filter(Book.title==title).one())

        session.close()

    def search_author(self,author):
        print("\nSearch for author: " + author + "...")
        DBSession = sessionmaker(bind=engine)        
        session = DBSession()
        # Student Task:
        # Add the code to bind the engine to the metadata of the Base Class and
        # create a new DBSession().  Refer to the example in insert_book() method

        # Student Task: Build a query to search a book by Author
        for rec in session.query(Book).filter(Book.author==author).all():
            print(rec)
        session.close()
        
                
#Create a new instance of library
library = Library()
#Create the tables in the databse
library.create_table()

#Insert records into the table
library.insert_book('001', 'Agile Design', 'Tom', '1997', 'textbook')
library.insert_book('002', 'Cooking', 'Jack', '1998', 'cookbook')
library.insert_book('003', 'Solid Principle', 'Tom', '2002', 'cookbook')

#Search the tables in the database
library.search_book('Agile Design')
library.search_author('Tom')


