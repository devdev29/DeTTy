import socket  # noqa: F401
import os


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    
    # Uncomment this to pass the first stage
    server_socket = create_server(address=("127.0.0.1", 4221), reuse_port=True)
    server_socket.accept() # wait for client
    server_socket.send("HTTP/1.1 200 OK\r\n\r\n")


def create_server(address: tuple, reuse_port: bool = False, backlog: int|None = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(address)
    if os.name not in ('nt', 'cygwin'):
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if reuse_port:
        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            raise ValueError("SO_REUSEPORT not supported on this platform")
    if backlog:
        server_socket.listen(backlog)
    else:
        server_socket.listen()
    return server_socket

if __name__ == "__main__":
    main()
