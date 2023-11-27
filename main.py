from datetime import datetime
from typing import Optional, List
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Request, status
from pydantic import BaseModel, Field
from fastapi.exceptions import ResponseValidationError
from enum import Enum
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Trading App"
)


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors()}),
    )

fake_users = [
    {'id': 1, 'role': 'admin', 'name': 'Bob'},
    {'id': 2, 'role': 'investor', 'name': 'John'},
    {'id': 3, 'role': 'traded', 'name': 'Matt'},
    {'id': 4, 'role': 'investor', 'name': 'Homer', 'degree':[
        {'id': 1, 'created_at': '2020-01-01T00:00:00', 'type_degree': 'expert'}
    ]},
]


class DegreeType(Enum):
    newbie = 'newbie'
    expert = 'expert'


class Degree(BaseModel):
    id: int
    created_at: datetime
    type_degree: DegreeType


class User(BaseModel):
    id: int
    role: str
    name: str
    degree: Optional[List[Degree]] = []


@app.get("/users/{user_id}", response_model=list[User])
def get_user(user_id: int):
    return [user for user in fake_users if user.get('id') == user_id]


fake_trades = [
    {'id':1, 'user_id':1, 'currency': 'BTC', 'side':'buy', 'price': 123, 'amount': 2.12},
    {'id':2, 'user_id':1, 'currency': 'BTC', 'side':'sell', 'price': 125, 'amount': 2.12},
]


@app.get('/trades')
def get_trades(limit: int=1, offset: int=0):
    return fake_trades[offset:][:limit]


fake_users2 = [
    {'id':1, 'role':'admin', 'name': 'Bob'},
    {'id':2, 'role':'investor', 'name': 'John'},
    {'id':3, 'role':'traded', 'name': 'Matt'},
]


@app.post("/users/{user_id}")
def change_user_name(user_id: int, new_name: str):
    current_user = list(filter(lambda user: user.get('id') == user_id, fake_users2))[0]
    current_user['name'] = new_name
    return {"status": 200, "data" : current_user}


class Trade(BaseModel):
    id: int
    user_id: int
    currency: str = Field(max_length=5)
    side: str
    price: float = Field(ge=0)
    amount: float


@app.post("/trades")
def add_trades(trades: list[Trade]):
    fake_trades.extend(trades)
    return {'status': 200, 'data': fake_trades}



# uvicorn main:app  - запуск приложения