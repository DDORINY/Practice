import os

# OpenCV가 RTSP 영상을 열 때 사용할 옵션입니다.
# 현재 RTSP 영상은 아래 AiStreamService에서 FFmpeg 명령으로 직접 열고 있습니다.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
os.environ["OPENCV_FFMPEG_DEBUG"] = "1"
os.environ["OPENCV_VIDEOIO_DEBUG"] = "1"

from flask import Flask, request
from flask_socketio import SocketIO
from threading import Lock
from servers.ai.service.AiStreamService import AiStreamService

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    # python-dotenv가 설치되어 있지 않아도 앱이 바로 죽지 않게 하는 예비 함수입니다.
    def load_dotenv():
        return False

# .env 파일에 적어둔 RTSP 주소, 웹캠 설정 등을 환경변수로 읽어옵니다.
load_dotenv()

# Flask는 웹 페이지를 보여주는 역할을 합니다.
app = Flask(__name__)

# SocketIO는 서버가 브라우저로 영상을 계속 보내기 위해 사용합니다.
# 일반 HTTP 요청은 한 번 받고 끝나지만, SocketIO는 계속 연결해둘 수 있습니다.
socketio = SocketIO(
    app,
    cors_allowed_origins=os.getenv("SOCKETIO_CORS_ORIGINS", "*"),
    async_mode=os.getenv("SOCKETIO_ASYNC_MODE", "threading"),
)

# 첫 접속 때만 백그라운드 작업을 시작하기 위한 변수
stream_started = False
stream_lock = Lock()


@app.route('/ai_detect/aistream')
def ai_stream():
    return {"status": "disabled", "message": "Use the frontend dashboard."}, 410


@app.get("/health")
def health():
    return {"status": "ok"}


def run_rtsp_logic():
    global stream_started
    try:
        # IP 카메라 주소는 코드에 직접 쓰지 않고 .env에서 읽습니다.
        # 예: AISTREAM_RTSP_URL=rtsp://아이디:비밀번호@IP:554/stream1
        rtsp_url = os.getenv("AISTREAM_RTSP_URL")
        if not rtsp_url:
            print("[SYSTEM] RTSP stream skipped: AISTREAM_RTSP_URL is not set")
            return

        # RTSP 영상 전송 방식입니다. 보통 tcp 또는 udp를 사용합니다.
        rtsp_transport = os.getenv("AISTREAM_RTSP_TRANSPORT", "tcp")

        # FFmpeg가 문제를 얼마나 자세히 출력할지 정합니다.
        ffmpeg_loglevel = os.getenv("AISTREAM_FFMPEG_LOGLEVEL", "error")
        print("[SYSTEM] RTSP task start")
        AiStreamService.run_rtsp_stream(
            socketio,
            rtsp_url,
            rtsp_transport=rtsp_transport,
            ffmpeg_loglevel=ffmpeg_loglevel,
        )
    finally:
        with stream_lock:
            stream_started = False
        print("[SYSTEM] RTSP task stopped; next client can restart it")


def run_webcam_logic():
    # 컴퓨터에 연결된 웹캠 번호입니다. 보통 첫 번째 웹캠은 0번입니다.
    cam_index = int(os.getenv("AISTREAM_WEBCAM_INDEX", "0"))
    print("[SYSTEM] Webcam task start")
    AiStreamService.run_webcam_stream(socketio, cam_index=cam_index)


def run_ai_logic():
    # IP 카메라 작업을 뒤에서 따로 실행합니다.
    # 이렇게 해야 웹 페이지가 멈추지 않고 계속 반응할 수 있습니다.
    socketio.start_background_task(run_rtsp_logic)

    # .env에서 AISTREAM_ENABLE_WEBCAM=0으로 설정하면 웹캠은 실행하지 않습니다.
    if os.getenv("AISTREAM_ENABLE_WEBCAM", "1") == "1":
        socketio.start_background_task(run_webcam_logic)
    else:
        print("[SYSTEM] Webcam stream skipped: AISTREAM_ENABLE_WEBCAM is not 1")


@socketio.on('connect')
def handle_connect():
    global stream_started
    print("[SYSTEM] client connected")

    # 여러 사용자가 접속해도 카메라 읽기 작업은 한 번만 시작되게 막습니다.
    with stream_lock:
        if not stream_started:
            stream_started = True
            socketio.start_background_task(run_ai_logic)


@socketio.on('browser_webcam_frame')
def handle_browser_webcam_frame(data):
    # 서버에 직접 연결된 웹캠이 없으면 브라우저 웹캠 프레임을 받아 AI 처리합니다.
    AiStreamService.process_browser_webcam_frame(socketio, data, sid=request.sid)
    return {"ok": True}


if __name__ == '__main__':
    # 이 파일을 직접 실행하면 AI 서버가 지정된 포트에서 시작됩니다.
    port = int(os.getenv("AISTREAM_PORT", "5001"))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)
