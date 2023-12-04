import os
from tqdm import tqdm

CHUNK_SIZE = 256 * 1024  # 256kb


def file_list(path):
    file_list = os.listdir(path)
    print(file_list)


def send_chunk(chunk):
    """
    TODO: chunk 전송하는 함수
    """
    pass


def send_file(file_path):
    """
    파일 전송 함수
    """
    with open(file_path, "rb") as file:
        file_size = os.path.getsize(file_path)
        print(f"Sending File: {file_path}")
        progress_bar = tqdm(total=file_size, unit="B", unit_scale=True)
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            send_chunk(chunk)
            progress_bar.update(len(chunk))
        progress_bar.close()


def receive_chunk():
    """
    TODO: chunk 수신하는 함수
    """
    pass


def recv_file(file_path):
    """
    파일 수신 함수
    """
    received_data = b""
    while True:
        chunk = receive_chunk()
        if not chunk:
            break
        received_data += chunk
        print(f"Received {len(received_data)} bytes")
    with open(file_path, "wb") as file:
        file.write(received_data)
