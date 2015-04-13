from base64 import b64decode
from uuid import uuid4
import datetime
import os
import re

from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
import config

Base = declarative_base()
engine = create_engine('sqlite:///' + config.DB_PATH)
Session = sessionmaker(bind=engine)

class Debt(Base):
    __tablename__ = 'debts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owed_to = Column(String)
    amount = Column(Integer)
    date = Column(Date)
    notes = Column(String)
    image_name = Column(String)

    def __init__(self, name, owed_to, amount, date, notes, encoded_data):
        if not isinstance(date, datetime.date):
            raise AssertionError('Date is supposed to be an instance of date.')

        self.name = name
        self.owed_to = owed_to
        self.amount = amount
        self.date = date
        self.notes = notes
        self.image_name = self._save_image(encoded_data)

    def to_public_dict(self):
        the_date = datetime.datetime(self.date.year, self.date.month, self.date.day)
        total_seconds = (the_date - datetime.datetime(1970, 1, 1)).total_seconds()
        total_millis = int(total_seconds * 1000)

        return {
            'id': self.id,
            'name': self.name,
            'owed_to': self.owed_to,
            'amount': self.amount,
            'date': total_millis,
            'notes': self.notes,
            'image_path': os.path.join(config.UPLOADS_DIR_NAME, self.image_name) if self.image_name else None
        }

    def _save_image(self, encoded_data):
        if not encoded_data: return None

        ext, data = re.match('data:image/(\w+);base64,(.*)$', encoded_data).groups()
        name = '{}.{}'.format(uuid4(), ext)
        path = os.path.join(config.UPLOADS_DIR, name)

        with open(path, 'wb') as fout:
            fout.write(b64decode(data))

        return name


def add_sample_data():
    session = Session()
    if session.query(Debt).count() == 0:
        d1 = Debt('Marty', 'Val', 300, datetime.date.today(), 'This is the first test.', None)
        session.add(d1)
        session.commit()
        session.close()

Base.metadata.create_all(engine)
add_sample_data()