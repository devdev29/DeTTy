from app.detty import DeTTy

app = DeTTy()

@app.register('/', 'GET')
def empty_func():
    ...

@app.register('/echo/{in_str}', 'GET')
def echo(in_str: str):
    return in_str

if __name__ == "__main__":
    app.run() 
