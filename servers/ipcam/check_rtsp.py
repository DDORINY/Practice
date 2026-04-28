import argparse
import socket
import subprocess
from urllib.parse import quote, unquote


PATHS = [
    # 카메라 제조사마다 RTSP 주소 뒤 경로가 다릅니다.
    # 아래 목록은 자주 쓰이는 경로들을 모아둔 것입니다.
    "/stream1",
    "/stream2",
    "/Streaming/Channels/101",
    "/Streaming/Channels/102",
    "/cam/realmonitor?channel=1&subtype=0",
    "/cam/realmonitor?channel=1&subtype=1",
    "/live/ch00_0",
    "/live/ch00_1",
    "/h264Preview_01_main",
    "/h264Preview_01_sub",
    "/11",
    "/12",
    "/profile1",
    "/profile2",
]


def tcp_check(host, port, timeout=3):
    # 먼저 IP와 포트가 열려 있는지 확인합니다.
    # 포트가 닫혀 있으면 RTSP 주소를 아무리 바꿔도 영상이 나오지 않습니다.
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError as exc:
        print(f"[TCP] {host}:{port} failed: {exc}")
        return False


def build_url(host, port, username, password, path):
    # 비밀번호에 ! 같은 특수문자가 있어도 안전하게 URL로 바꿉니다.
    safe_username = quote(unquote(username), safe="")
    safe_password = quote(unquote(password), safe="")
    return f"rtsp://{safe_username}:{safe_password}@{host}:{port}{path}"


def test_url(url, timeout, transport):
    # ffprobe는 영상을 저장하지 않고 "이 주소가 열리는지"만 확인하는 도구입니다.
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-rtsp_transport",
        transport,
        "-stimeout",
        str(timeout * 1_000_000),
        "-i",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
    return result.returncode == 0, result.stderr.strip()


def main():
    # 터미널에서 받은 IP, 아이디, 비밀번호, 포트 값을 읽습니다.
    parser = argparse.ArgumentParser(description="Probe common RTSP paths.")
    parser.add_argument("--host", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--port", type=int, default=554)
    parser.add_argument("--timeout", type=int, default=5)
    parser.add_argument("--transport", default="tcp", choices=["tcp", "udp"])
    args = parser.parse_args()

    if not tcp_check(args.host, args.port, args.timeout):
        return 2

    print(f"[TCP] {args.host}:{args.port} open")

    found = False
    for path in PATHS:
        # 준비한 경로들을 하나씩 붙여보며 실제로 열리는 주소를 찾습니다.
        url = build_url(args.host, args.port, args.user, args.password, path)
        safe_url = url.replace(f":{quote(unquote(args.password), safe='')}@", ":***@")
        print(f"[RTSP] testing {safe_url}")

        ok, stderr = test_url(url, args.timeout, args.transport)
        if ok:
            print(f"[OK] {safe_url}")
            found = True
            continue

        first_error = stderr.splitlines()[-1] if stderr else "unknown error"
        print(f"[FAIL] {first_error}")

    if not found:
        # 여기까지 왔다면 포트는 열렸지만, 후보 경로 중 성공한 주소가 없는 것입니다.
        print("[RESULT] No working RTSP path found.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
