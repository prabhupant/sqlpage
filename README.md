# SQLPage

Python library to easily add pagination on top of DB queries. Supports SQLAlchemy and SQLModel ORMs. This returns a 
base64 encoded string that can be used to paginate through the results.

## Usage

Install the latest version from PyPi

```bash
pip install sqlpage
```

Now configure your ORM and then simply call the `paginate` function to get the paginated results.

```python
result: PageData = paginate(session, query, page_size=page_size)
```

## Configuring with ORMs

Before using the `paginate` function, you need to configure the ORM. As SQLAlchemy and SQLModel uses different
ORMs, you need to configure them separately. This is a one-time setup and you would have already taken this while 
configuring the ORM when creating the DB models.

### SQLAlchemy

Create your table model

```python
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
```

Then create a DB session and call

```python
engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
Base.metadata.create_all(engine)

SessionSqlAlchemy = sessionmaker(bind=engine)
session = SessionSqlAlchemy()

query = session.query(TestTable)

result: PageData = paginate(session, query, page_size=page_size)
```

### SQLModel

Create your table model

```python
class TestTableSqlModel(SQLModel, table=True):
    __tablename__ = 'test_table'

    id: int = Field(primary_key=True)
    username: str = Field(default=None)
    email: str = Field(default=None)

```

Then create a DB session and call

```python
engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
Base.metadata.create_all(engine)

with Session(engine) as session:

    query = session.query(TestTable)

    result: PageData = paginate(session, query, page_size=page_size)
```

## Contributing 

Feel free to open an issues under the `Issues` tab. Contributions are welcome and appreciated.

