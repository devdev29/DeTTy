from typing import Annotated
from app.detty import DeTTy
from app.models import HeaderParameter

app = DeTTy()

@app.register('/', 'GET')
def empty_func():
    ...

@app.register('/echo/{in_str}', 'GET')
def echo(in_str: str):
    return in_str

@app.register('/user-agent', 'GET')
def get_user_agent(user_agent: Annotated[str, HeaderParameter(header_name='User-Agent')]):
    return user_agent

if __name__ == "__main__":
    app.run() 
