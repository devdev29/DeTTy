import os

import click

from typing import Annotated

from app.detty import DeTTy
from app.models import HeaderParameter, BodyParameter
from app.http_response import HttpResponse
from app.http_constants import HttpStatus

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

@app.register('/files/{filename}', 'GET')
def get_file(filename: str, response: HttpResponse):
    dir_name = '/tmp/data/codecrafters.io/http-server-tester/'
    file_path = os.path.join(dir_name, filename)
    print(file_path)
    if not os.path.exists(file_path):
        response.status_code = HttpStatus.NOT_FOUND.code
        response.reason_phrase = HttpStatus.NOT_FOUND.phrase
        return response
    with open(file_path, 'rb') as file:
        response.response_body = file.read().decode('ASCII')
        response.media_type = 'application/octet-stream'
    return response

@app.register('/files/{filename}','POST')
def create_file(filename: str, file_body: Annotated[str, BodyParameter()]):
    dir_name = '/tmp/data/codecrafters.io/http-server-tester/'
    file_path = os.path.join(dir_name, filename)
    print(file_path)
    with open(file_path, 'wb') as file:
        file.write(file_body.encode('ASCII'))

@click.command()
@click.option('--directory', type=click.Path(exists=True), default='/tmp/')
def run_main(directory: str):
    print(directory)
    app.run(multithreaded=True)

if __name__ == "__main__":
    run_main()