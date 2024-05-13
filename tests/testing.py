import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from src.sqlpage import paginate, PageData

DATABASE_NAME = 'test_pypagination.db'
TABLE_NAME = "test_table"

Base = declarative_base()

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


def check_pagination_sqlmodel():
    print("Testing for SQLModel ORM")

    engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        call_pagination_and_test(session, orm="sqlmodel")

def check_pagination_sqlalchemy():
    print("Testing for SQLAlchemy ORM")

    engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
    Base.metadata.create_all(engine)

    SessionSqlAlchemy = sessionmaker(bind=engine)
    session = SessionSqlAlchemy()

    call_pagination_and_test(session, orm="sqlalchemy")


def call_pagination_and_test(session, orm: str):
    page_size = 10

    if orm == "sqlalchemy":
        from tests.table_model import TestTableSqlAlchemy as TestTable
    elif orm == "sqlmodel":
        from tests.table_model import TestTableSqlModel as TestTable
    else:
        raise ValueError('Invalid ORM type. Please select either sqlalchemy or sqlmodel')

    query = session.query(TestTable)

    result: PageData = paginate(session, query, page_size=page_size)

    print(f"Result length - {len(result.items)}")
    print(f"Called with page size - {page_size}")
    print(f"Next page token - {result.next_page_token}")

    page_size = page_size + 20

    print(f"Now querying for next page with page size {page_size}")

    result: PageData = paginate(session, query, page_size=page_size, token=result.next_page_token)

    print(f"Result length - {len(result.items)}")
    print(f"Called with page size - {page_size}")
    print(f"Next page token - {result.next_page_token}")


if __name__ == "__main__":
    create_and_populate_database()
    check_pagination_sqlalchemy()
    check_pagination_sqlmodel()





