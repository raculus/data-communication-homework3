import socket
import sys
import pickle
import logging
import os
import ping3
from threading import Thread
from file_chunk import *

HOST = "192.168.219.117"
PORT = 9999

# IP를 인자로 받음
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

# 서버로 부터 클라이언트 이름 지정 받고, 로그 생성
while True:
    data = client_socket.recv(1024)
    if not data:
        log.error("not data")
        break
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


def p2p_client_threaded(address):
    """
    다른 서버에 접속하기 위한 스레드 (클라이언트 스레드)
    """
    # 서버에 연결
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 연결 수립
    sock.connect(address)

    my_file_name = os.listdir(f"Client{index}")[0]
    while True:
        data = sock.recv(1024)
        if not data:
            log.info(f"Disconnected by{p2p_clients.index(sock)}")
            break
        data = pickle.loads(data)
        log.debug(f"p2p_cleint_thread data: {data}")
        log.info(f"Send file to Client")
        send_file(f"Client{index}", my_file_name, sock, log)


def p2p_server_threaded(sock):
    """
    다른 클라이언트를 받기 위한 스레드 (서버 스레드)
    """
    sock.sendall(pickle.dumps(p2p_server_socket.getsockname()))
    while True:
        data = sock.recv(1024)
        if not data:
            log.info(f"Disconnected by{p2p_clients.index(sock)}")
            break
        data = pickle.loads(data)
        if "file_size" in data:
            file_size = data["file_size"]
            file_name = data["file_name"]
            file_path = f"Client{index}/{file_name}"
            print(f"Receiving File: {file_size}")
            received_data = b""
            while True:
                chunk = sock.recv(CHUNK_SIZE)
                if not chunk:
                    break
                received_data += chunk
                log.info(f"Received {file_name} {len(received_data)}/{file_size} bytes")
                if(len(received_data) >= file_size):
                    break
            with open(file_path, "wb") as file:
              file.write(received_data)


def p2p_server():
    """
    서버를 구동하여 클라이언트 연결을 수락하는 스레드
    """
    while True:
        # 클라이언트 연결 수락
        p2p, addr = p2p_server_socket.accept()
        p2p_clients.append(p2p)
        log.info(f"Connected Client{p2p_clients.index(p2p)+1}")

        # 클라이언트마다 스레드 생성
        p2p_thread = Thread(target=p2p_server_threaded, args=(p2p,))
        p2p_thread.daemon = True
        p2p_thread.name = f"p2p_thread{p2p_clients.index(p2p)+1}"
        p2p_thread.start()


def send_file_list(dest_client):
    file_list = os.listdir(f"Client{index}")
    dic = {"file_list": file_list}
    dest_client.sendall(pickle.dumps(dic))
    log.info(f"Send file list to Client{client_list.index(dest_client)}")


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
            p2p_client_thread = Thread(target=p2p_client_threaded, args=(client,))
            p2p_client_thread.daemon = True
            p2p_client_thread.name = f"p2p_client_thread{client_list.index(client)+1}"
            p2p_client_thread.start()
        continue


def sort_client_list_by_ping(client_list):
    # client_list = [(127.0.0.1, 1234), (192.168.0.1, 4567), (...)]
    ping_list = [ping3.ping(client[0]) for client in client_list]
    # pingList = [0.5, 0.1, 0.0, ...]

    zipped_lists = zip(ping_list, client_list)

    # zip된 리스트를 ping 기준으로 정렬
    sorted_pairs = sorted(zipped_lists)

    # 정렬된 리스트에서 client_list만 추출
    client_list = [item[1] for item in sorted_pairs]
    return client_list


# 서버를 위한 스레드 생성
p2p_server_thread = Thread(target=p2p_server)
p2p_server_thread.daemon = True
p2p_server_thread.name = "p2p_server"
p2p_server_thread.start()

client_list = recv_client_list(client_socket)
log.info(f"Client{index} close")
