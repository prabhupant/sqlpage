import base64
import json
from typing import Sequence, Optional, Any

import sqlalchemy
import sqlmodel
from sqlalchemy import Row
from .models import PageData, PageToken


def paginate(session, query: sqlalchemy.orm.query.Query, token: str = None, page_size: int = 10) -> PageData[Any]:
    """
    Method to get the result from query in a paginated way.

    :param session: The DB session
    :param query: SQL query that is to be executed
    :param token: next page token. Should be None when passed for the first time. Defaults to None
    :param page_size: The size of the page. Defaults to 10

    :return: PageData[Any]
    """
    if not token:
        page_token = decode_token(make_first_token(query=query, page_size=page_size))
        page_token.total_count = query.count()
    else:
        page_token = decode_token(token)

        # Since this is the second time call, so check if the page_size if not the default value, and then update it here
        if page_size != 10:
            page_token.page_size = page_size

    statement = query.limit(page_token.page_size).offset(page_token.offset)

    result: Sequence[Row] = get_result(session, statement)

    size = len(result)

    total_elements_fetched = page_token.elements_fetched + size

    next_page_token: Optional[str] = None

    if total_elements_fetched < page_token.total_count:
        next_page_token = make_token(
            PageToken(
                total_count=page_token.total_count,
                page_size=page_size,
                remaining=page_token.total_count - total_elements_fetched,
                page_num=page_token.page_num + 1,
                offset=page_token.offset + size,
                elements_fetched=total_elements_fetched,
            )
        )

    return PageData(items=result, next_page_token=next_page_token)


def get_result(session, statement) -> Sequence[Row]:
    result: Sequence[Row]

    if isinstance(session, sqlmodel.orm.session.Session):
        return session.exec(statement).all()
    elif isinstance(session, sqlalchemy.orm.session.Session):
        return session.execute(statement).all()
    else:
        raise Exception(f"Unsupported session type {type(session)} passed. "
                        f"Please use session for SQLAlchemy or SQLModel")

def run_on_sqlalchemy(session):
    isinstance(session, sqlalchemy.orm.session.Session)
    pass

def make_first_token(query: sqlalchemy.orm.query.Query, page_size: int = 10):
    total_count = query.count()
    page_token: PageToken = PageToken(
        total_count=total_count,
        page_size=page_size,
        remaining=total_count,
        page_num=0,
        offset=0,
        elements_fetched=0,
    )
    return make_token(page_token)


def make_token(page_token: PageToken):
    dto_str = json.dumps(page_token.dict())
    encoded_str = base64.b64encode(dto_str.encode("utf-8")).decode("utf-8")
    return "b:" + encoded_str

def decode_token(token):
    encoded_str = token[2:]
    decoded_str = base64.b64decode(encoded_str).decode("utf-8")
    kwargs = json.loads(decoded_str)
    return PageToken(**kwargs)

