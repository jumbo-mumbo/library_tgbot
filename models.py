from sqlalchemy import Integer, String,\
                    Column, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    name = Column(String,nullable=False)

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=True)
    course_id = Column(Integer,ForeignKey('course.id',ondelete='CASCADE'))

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    item_id = Column(Integer, ForeignKey('item.id', ondelete='CASCADE'))


