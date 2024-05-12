import base64
import json
from typing import Sequence, Optional, Any

import sqlalchemy
from sqlalchemy import Row

from constants import Constants
from models import PageToken, PageData


class PyPagination:

    def __init__(self, session, query: sqlalchemy.orm.query.Query, page_size:int=Constants.DEFAULT_PAGE_SIZE):
        self.session = session
        self.query = query
        self.page_size = page_size

    def make_first_token(self):
        total_count = self.query.count()
        page_token: PageToken = PageToken(
            total_count=total_count,
            page_size=self.page_size,
            remaining=total_count,
            page_num=0,
            offset=0,
            elements_fetched=0,
        )
        return self.make_token(page_token)


    def paginate(self, token: str = None) -> PageData[Any]:
        if token is None:
            page_token = self.decode_token(self.make_first_token())
            page_token.total_count = self.query.count()
            statement = self.query.limit(page_token.page_size).offset(page_token.offset)
        else:
            page_token = self.decode_token(token)
            statement = self.query.limit(page_token.page_size).offset(page_token.offset)

        result: Sequence[Row] = self.session.exec(statement).all()

        size = len(result)

        total_elements_fetched = page_token.elements_fetched + size

        next_page_token: Optional[str] = None

        if total_elements_fetched < page_token.total_count:
            next_page_token = self.make_token(
                PageToken(
                    total_count=page_token.total_count,
                    page_size=self.page_size,
                    remaining=page_token.total_count - total_elements_fetched,
                    page_num=page_token.page_num + 1,
                    offset=page_token.offset + size,
                    elements_fetched=total_elements_fetched,
                )
            )

        return PageData(items=result, next_page_token=next_page_token)

    @staticmethod
    def make_token(page_token: PageToken):
        dto_str = json.dumps(page_token.dict())
        encoded_str = base64.b64encode(dto_str.encode("utf-8")).decode("utf-8")
        return "b:" + encoded_str

    @staticmethod
    def decode_token(token):
        encoded_str = token[2:]
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        kwargs = json.loads(decoded_str)
        return PageToken(**kwargs)

