import socket
from _thread import *
import os
import pickle
import logging

FILENAME = "Server.txt"
if os.path.exists(FILENAME):
    os.remove(FILENAME)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(FILENAME, "w", "utf-8"), logging.StreamHandler()],
)

log = logging.getLogger()

client_sockets = []


HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999


for i in range(1, 5):
    if not os.path.exists(f"Client{i}"):
        os.mkdir(f"Client{i}")


def get_client_index(client_socket):
    return client_sockets.index(client_socket) + 1


def threaded(client_socket, addr):
    index = get_client_index(client_socket)
    name = f"Client{index}"
    dic = {"index": index}
    client_socket.sendall(pickle.dumps(dic))

    while True:
        if len(client_sockets) < 4:
            continue
        try:
            data = client_socket.recv(1024)
            if not data:
                log.info(f"Disconnected by {addr[0]} ({name})")
                break

            data = pickle.loads(data)

        except ConnectionResetError as e:
            log.info(f"Disconnected by {addr[0]} ({name})")
            client_socket.close()
            break
        except ConnectionAbortedError as e:
            break


def server():
    log.info(f"Server start at {HOST}:{PORT}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    log.info("Wait join client")
    print()
    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_sockets.append(client_socket)
            start_new_thread(threaded, (client_socket, addr))
            log.info(f"Join {addr[0]} (Client{client_sockets.index(client_socket)+1})")
            if len(client_sockets) == 4:
                log.info("All clients joined")
                for client in client_sockets:
                    # client_sockets에서 client를 제외한 나머지 client 리스트
                    clientList = [
                        c.getpeername() for c in client_sockets if c != client
                    ]
                    client.sendall(pickle.dumps({"clients": clientList}))
                    log.info(
                        f"Send client list to Client{client_sockets.index(client)+1}:{client.getpeername()[1]}"
                    )
                    log.debug(clientList)

    except Exception as e:
        log.error(e)


def close():
    for client in client_sockets:
        client.close()
    log.info("Server stopping...")
    os._exit(0)


server()
close()
