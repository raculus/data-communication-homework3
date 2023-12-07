import os
from tqdm import tqdm
import pickle

CHUNK_SIZE = 256 * 1024  # 256kb


def file_list(path):
    file_list = os.listdir(path)
    print(file_list)


def send_chunk(chunk, client_socket):
    """
    TODO: chunk 전송하는 함수
    """
    client_socket.sendall(chunk)
    pass


def send_file(file_path, file_name, client_socket, log):
    """
    파일 전송 함수
    """
    file_path += "/" + file_name
    with open(file_path, "rb") as file:
        file_size = os.path.getsize(file_path)
        print(f"Sending File: {file_path}")
        progress_bar = tqdm(total=file_size, unit="B", unit_scale=True)
        client_socket.sendall(pickle.dumps({"file_size": file_size, "file_name": file_name}))
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            client_socket.sendall(chunk)
            log.info(f"Sent {file_name} {len(chunk)} bytes")
            progress_bar.update(len(chunk))
        progress_bar.close()