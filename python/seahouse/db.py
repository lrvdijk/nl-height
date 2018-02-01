import typing

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from seahouse.config import get_config

#  Engine and session needs to be initialized first
Session = sessionmaker()

engine = None
session = None  # type: typing.Optional[Session]


def init():
    """
    Initialise database connection
    """
    global engine, session

    config = get_config()
    database_string = config.get('postgres', 'sqlalchemy.url')

    engine = create_engine(database_string)
    Session.configure(bind=engine)

    session = Session()


def test_connection():
    try:
        engine.engine.connect()
    except SQLAlchemyError:
        return False

    return True
