
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

import settings

Base = declarative_base()

class Example(Base):
    __tablename__ = 'example'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    number = sa.Column(sa.Integer)

    def __repr__(self):
       return "<Example(id=%s, name='%s', number='%s')>" % (
                            self.id, self.name, self.number)
