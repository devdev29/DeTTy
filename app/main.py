import socket  # noqa: F401


SERVER_ADDR = ("127.0.0.1", 8000)

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    
    # Uncomment this to pass the first stage
    server_socket = socket.create_server(address=SERVER_ADDR, reuse_port=True)
    server_socket.accept() # wait for client
    server_socket.send("HTTP/1.1 200 OK\r\n\r\n")


def create_server(address: tuple, reuse_port: bool = False, backlog: int|None = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDR)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
    if backlog:
        server_socket.listen(backlog)
    else:
        server_socket.listen()
    return server_socket

if __name__ == "__main__":
    main()
