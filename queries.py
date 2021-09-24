from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Course,Item,Book

engine = create_engine("postgresql+psycopg2://root:explay@localhost/tglib")
session = Session(bind=engine)

k1 = Course(name = '1 kurs')

#a1 = session.add(k1)
#session.commit()

similiar_items = session.query(Item.name, Course.name).join(Course).filter(Item.name == 'bio').all()
print(similiar_items)



