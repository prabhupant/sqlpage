import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Session, SQLModel, Field

from models import PageData
from pypagination import PyPagination

DATABASE_NAME = 'test_pypagination.db'
TABLE_NAME = "test_table"

Base = declarative_base()


class TestTable(SQLModel, table=True):
    __tablename__ = 'test_table'

    id: int = Field(primary_key=True)
    username: str = Field(default=None)
    email: str = Field(default=None)


def create_and_populate_database():
    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL
                    )''')

    cursor.execute(f'SELECT COUNT(*) FROM {TABLE_NAME}')
    count = cursor.fetchone()[0]

    if count != 100:
        for i in range(100):
            cursor.execute(f"INSERT INTO {TABLE_NAME} (username, email) VALUES ('user{i}', 'user{i}@user.com')")
    else:
        print('Database already populated')

    conn.commit()
    conn.close()


def check_pagination():
    # Create an engine to connect to your SQLite database
    engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=True)
    Base.metadata.create_all(engine)

    # Create a session
    with Session(engine) as session:

        query = session.query(TestTable)

        result: PageData = PyPagination(session, query, page_size=10).paginate()

        assert result is not None
        assert result.next_page_token is not None
        assert len(result.items) == 10


if __name__ == "__main__":
    create_and_populate_database()
    check_pagination()





