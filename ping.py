import ping3


def send_ping(destination):
    """
    ping을 보내는 함수
    """
    try:
        response_time = ping3.ping(destination)
        if response_time is not None:
            print(f"Ping response time: {response_time} ms")
        else:
            print("Ping request timed out")
    except ping3.exceptions.PingError as e:
        print(f"Ping error: {str(e)}")
