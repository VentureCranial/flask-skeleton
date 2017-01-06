import json

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from util.log import AppLogger
from models import Example
import settings

engine = sa.create_engine(settings.DB_URL)
Session = sessionmaker(bind=engine)


Example.metadata.create_all(engine)
log = AppLogger.get_logger('load_fixtures')

def load_example_fixtures():
    log.info('BEGIN: loading example fixtures from fixtures/example.json')

    session = Session()
    with open('fixtures/example.json') as f:
        examples = json.load(f)

        add_me = [Example(
            name = e.get('name', ''),
            number = e.get('number', ''),
            ) for e in examples]

        session.add_all(add_me)
        session.commit()

    log.info('END: loading example fixtures from fixtures/example.json')

if __name__ == '__main__':
    load_example_fixtures()

