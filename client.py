import socket
from _thread import *
import sys
import pickle
import logging
import os
import ping3

HOST = "192.168.219.117"
PORT = 9999

if len(sys.argv) == 2:
    HOST = sys.argv[1]

arg = sys.argv
if len(arg) == 2:
    HOST = arg[1]
elif len(arg) == 3:
    HOST = arg[1]
    PORT = int(arg[2])


index: int
name: str
log = logging.getLogger()

# 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 연결 수립
client_socket.connect((HOST, PORT))

# p2p 소켓 생성
p2p_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_server_socket.bind(client_socket.getsockname())
p2p_server_socket.listen()

p2p_clients = []

# 클라이언트 이름 지정, 로그 생성
while True:
    data = client_socket.recv(1024)
    if not data:
        print("not data")
        continue
    data = pickle.loads(data)
    if "index" in data:
        index = data["index"]
        name = f"Client{index}"
        filename = f"{name}.txt"
        if os.path.exists(filename):
            os.remove(filename)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(filename, "w", "utf-8"),
                logging.StreamHandler(),
            ],
        )
        break


def p2p_thread(p2p):
    while True:
        continue
        data = p2p.recv(1024)
        if not data:
            log.debug("p2p thread: not data")
            os._exit(1)
        data = pickle.loads(data)
        print(data)


def p2p_server():
    while True:
        p2p, addr = p2p_server_socket.accept()
        p2p_clients.append(p2p)
        log.info(f"Connected by {p2p.getpeername()}")
        start_new_thread(p2p_thread, (p2p,))


def send_file_list(dest_client):
    file_list = os.listdir(f"Client{index}")
    dic = {"file_list": file_list}
    dest_client.sendall(pickle.dumps(dic))


def recv_client_list(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            log.debug("recv_clinet_list: not data")
            continue

        data = pickle.loads(data)
        if "clients" not in data:
            continue
        client_list = data["clients"]
        for client in client_list:
            log.info(f"Trying to connect {client}")
            # 서버에 연결
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 연결 수립
            client_socket.connect(client)
        continue

        # client_list = [(127.0.0.1, 1234), (192.168.0.1, 4567), (...)]
        ping_list = [ping3.ping(client[0]) for client in client_list]
        # pingList = [0.5, 0.1, 0.0, ...]

        zipped_lists = zip(ping_list, client_list)

        # zip된 리스트를 ping 기준으로 정렬
        sorted_pairs = sorted(zipped_lists)

        # 정렬된 리스트에서 client_list만 추출
        client_list = [item[1] for item in sorted_pairs]
        return client_list


def find_files(client_socket, client_list):
    for client in client_list:
        data = client_socket.recv(1024)
        if not data:
            log.debug("find_files: not data")
            continue
        data = pickle.loads(data)


start_new_thread(p2p_server, ())
client_list = recv_client_list(client_socket)
