from ultralytics import YOLO
import os
import cv2
import torch
import base64
import time
import subprocess
import numpy as np
from pathlib import Path
from threading import Lock
from urllib.parse import quote, unquote, urlsplit, urlunsplit


class AiStreamService:
    # YOLO 모델은 무겁기 때문에 한 번만 불러와서 계속 재사용합니다.
    _model = None

    # 찾고 싶은 물체 이름입니다. 비어 있으면 모든 물체를 화면에 표시만 합니다.
    _target_label = ""

    # GPU가 있으면 cuda를 쓰고, 없으면 CPU를 씁니다.
    _device = "cuda" if torch.cuda.is_available() else "cpu"

    # 여러 작업이 동시에 모델을 불러오거나 예측하지 않게 잠금 장치를 둡니다.
    _model_lock = Lock()
    _predict_lock = Lock()

    # 서버에서 처리할 영상 크기입니다. 너무 크면 느려질 수 있습니다.
    WIDTH = 640
    HEIGHT = 480

    # YOLO 모델 파일 위치입니다. 환경변수로 바꿀 수 있고, 기본값은 프로젝트 루트 모델입니다.
    MODEL_PATH = Path(
        os.getenv(
            "AISTREAM_MODEL_PATH",
            Path(__file__).resolve().parents[1] / "yolov8n.pt",
        )
    )

    @classmethod
    def load_model(cls):
        # 처음 한 번만 YOLO 모델을 메모리에 올립니다.
        with cls._model_lock:
            if cls._model is None:
                cls._model = YOLO(str(cls.MODEL_PATH))
                cls._model.to(cls._device)
                print(f"AI Model Loaded on: {cls._device}")
        return cls._model

    @classmethod
    def set_target(cls, label):
        # 예: "person"을 넣으면 사람이 감지될 때 알림을 보낼 수 있습니다.
        cls._target_label = (label or "").strip().lower()
        print(f"[SYSTEM] Detection target set to: {cls._target_label}")

    @staticmethod
    def mask_url(url):
        # 로그에 비밀번호가 그대로 찍히지 않도록 ***로 가립니다.
        parsed = urlsplit(url)
        if not parsed.password:
            return url

        username = parsed.username or ""
        hostname = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        netloc = f"{username}:***@{hostname}{port}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))

    @staticmethod
    def normalize_rtsp_url(url):
        # RTSP 비밀번호에 ! 같은 특수문자가 있어도 FFmpeg가 읽을 수 있게 바꿉니다.
        # 예: !! -> %21%21
        parsed = urlsplit(url)
        if not parsed.username and not parsed.password:
            return url

        username = quote(unquote(parsed.username or ""), safe="")
        password = quote(unquote(parsed.password or ""), safe="")
        hostname = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        netloc = f"{username}:{password}@{hostname}{port}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))

    @classmethod
    def predict(cls, model, frame, predict_device):
        # RTSP와 웹캠이 같은 YOLO 모델을 함께 쓰므로, 한 번에 하나씩 예측하게 합니다.
        with cls._predict_lock:
            return model.predict(
                frame,
                device=predict_device,
                conf=0.7,
                verbose=False,
                imgsz=640
            )

    @classmethod
    def emit_annotated_frame(cls, socketio, model, frame, predict_device, source, frame_count, to=None):
        # 웹캠 입력 방식이 달라도 AI 처리와 전송은 같은 규칙을 사용합니다.
        results = cls.predict(model, frame, predict_device)

        boxes = results[0].boxes
        annotated_frame = results[0].plot()

        success, buffer = cv2.imencode(
            ".jpg",
            annotated_frame,
            [cv2.IMWRITE_JPEG_QUALITY, 80]
        )
        if not success:
            print("[ERROR] JPEG 인코딩 실패")
            return False

        encoded_image = base64.b64encode(buffer.tobytes()).decode("utf-8")
        payload = {
            "source": source,
            "image": encoded_image,
            "count": frame_count
        }

        if to:
            socketio.emit("ai_frame", payload, to=to)
            socketio.emit(f"{source}_frame", payload, to=to)
        else:
            socketio.emit("ai_frame", payload)
            socketio.emit(f"{source}_frame", payload)

        if cls._target_label and boxes is not None and boxes.cls is not None:
            detected_names = [
                model.names[int(cls_idx)].lower()
                for cls_idx in boxes.cls.tolist()
            ]

            if cls._target_label in detected_names:
                alert_payload = {
                    "source": source,
                    "label": cls._target_label,
                    "time": time.strftime("%H:%M:%S")
                }
                if to:
                    socketio.emit("detection_alert", alert_payload, to=to)
                else:
                    socketio.emit("detection_alert", alert_payload)

        return True

    @classmethod
    def process_browser_webcam_frame(cls, socketio, data, sid=None):
        # 서버에 웹캠 장치가 없을 때 브라우저가 보내준 화면을 AI 처리합니다.
        image_data = (data or {}).get("image", "")
        frame_count = int((data or {}).get("count", 0))

        if not image_data:
            return

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as exc:
            print(f"[ERROR] 브라우저 웹캠 이미지 디코딩 실패: {exc}")
            return

        np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
        if frame is None:
            print("[ERROR] 브라우저 웹캠 프레임 변환 실패")
            return

        frame = cv2.resize(frame, (cls.WIDTH, cls.HEIGHT))
        model = cls.load_model()
        predict_device = 0 if cls._device == "cuda" else "cpu"
        cls.emit_annotated_frame(
            socketio,
            model,
            frame,
            predict_device,
            source="webcam",
            frame_count=frame_count,
            to=sid
        )

    @classmethod
    def run_rtsp_stream(cls, socketio, rtsp_url, rtsp_transport="tcp", ffmpeg_loglevel="error"):
        # IP 카메라의 RTSP 영상을 읽고, AI 결과가 그려진 이미지를 브라우저로 보냅니다.
        model = cls.load_model()
        predict_device = 0 if cls._device == "cuda" else "cpu"
        rtsp_url = cls.normalize_rtsp_url(rtsp_url)
        masked_rtsp_url = cls.mask_url(rtsp_url)
        rtsp_transport = (rtsp_transport or "tcp").strip().lower()
        ffmpeg_loglevel = (ffmpeg_loglevel or "error").strip().lower()

        # FFmpeg에게 "RTSP 영상을 읽어서, 압축하지 않은 BGR 이미지로 계속 보내줘"라고 요청합니다.
        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", ffmpeg_loglevel,
            "-rtsp_transport", rtsp_transport,
            "-i", rtsp_url,
            "-an",
            "-vf", f"scale={cls.WIDTH}:{cls.HEIGHT}",
            "-pix_fmt", "bgr24",
            "-vcodec", "rawvideo",
            "-f", "rawvideo",
            "-"
        ]

        print("[SYSTEM] FFmpeg stream start")
        print(f"[SYSTEM] RTSP transport: {rtsp_transport}")
        print("[SYSTEM] FFmpeg cmd:", " ".join(ffmpeg_cmd).replace(rtsp_url, masked_rtsp_url))

        try:
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
        except FileNotFoundError:
            message = "FFmpeg 실행 파일이 없어 OpenCV RTSP 연결로 전환합니다."
            print(f"[ERROR] {message}")
            socketio.emit("stream_status", {
                "source": "ipcam",
                "status": "fallback",
                "message": message
            })
            cls.run_rtsp_stream_opencv(socketio, rtsp_url)
            return

        # 한 프레임은 가로 * 세로 * 3색(B, G, R) 바이트입니다.
        frame_size = cls.WIDTH * cls.HEIGHT * 3
        frame_count = 0

        try:
            while True:
                # FFmpeg가 stdout으로 내보낸 원본 이미지 한 장을 읽습니다.
                raw_frame = process.stdout.read(frame_size)

                if len(raw_frame) != frame_size:
                    # 0바이트면 카메라 연결이 거부되었거나 FFmpeg가 바로 종료된 경우가 많습니다.
                    if len(raw_frame) == 0 and process.poll() is not None:
                        print("[ERROR] FFmpeg exited before producing a frame")
                    else:
                        print(f"[ERROR] raw_frame size mismatch: {len(raw_frame)} / {frame_size}")
                    process.terminate()
                    try:
                        _, stderr = process.communicate(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        _, stderr = process.communicate()

                    err = stderr.decode("utf-8", errors="ignore").replace(rtsp_url, masked_rtsp_url)
                    if err:
                        print("[FFMPEG STDERR]")
                        print(err)
                    break

                # 바이트 덩어리를 OpenCV가 이해하는 이미지 배열로 바꿉니다.
                frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape(
                    (cls.HEIGHT, cls.WIDTH, 3)
                )

                frame_count += 1

                # 모든 프레임을 AI에 넣으면 느려질 수 있어서 3장 중 1장만 처리합니다.
                if frame_count % 3 != 0:
                    socketio.sleep(0.001)
                    continue

                # YOLO가 사람, 자동차 같은 물체를 찾습니다.
                results = cls.predict(model, frame, predict_device)

                boxes = results[0].boxes

                # 감지된 물체 박스를 영상 위에 그립니다.
                annotated_frame = results[0].plot()

                # 브라우저로 보내기 좋게 이미지를 JPG로 압축합니다.
                success, buffer = cv2.imencode(
                    ".jpg",
                    annotated_frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 80]
                )
                if not success:
                    print("[ERROR] JPEG 인코딩 실패")
                    socketio.sleep(0.01)
                    continue

                # JPG 이미지를 문자열로 바꿔 SocketIO로 전송합니다.
                encoded_image = base64.b64encode(buffer.tobytes()).decode("utf-8")

                payload = {
                    "source": "ipcam",
                    "image": encoded_image,
                    "count": frame_count
                }
                socketio.emit("ai_frame", payload)
                socketio.emit("ipcam_frame", payload)

                if frame_count % 30 == 0:
                    print(f"[FRAME][RTSP] sent: {frame_count}")

                # 찾고 싶은 물체 이름이 설정되어 있으면 감지 알림을 보냅니다.
                if cls._target_label and boxes is not None and boxes.cls is not None:
                    detected_names = [
                        model.names[int(cls_idx)].lower()
                        for cls_idx in boxes.cls.tolist()
                    ]

                    if cls._target_label in detected_names:
                        socketio.emit("detection_alert", {
                            "source": "rtsp",
                            "label": cls._target_label,
                            "time": time.strftime("%H:%M:%S")
                        })

                socketio.sleep(0.01)

        finally:
            # 작업이 끝나면 FFmpeg를 정리해서 남아 있는 프로세스가 없게 합니다.
            if process.poll() is None:
                process.kill()
            print("[SYSTEM] FFmpeg stream ended")

    @classmethod
    def run_rtsp_stream_opencv(cls, socketio, rtsp_url):
        model = cls.load_model()
        predict_device = 0 if cls._device == "cuda" else "cpu"
        rtsp_url = cls.normalize_rtsp_url(rtsp_url)
        masked_rtsp_url = cls.mask_url(rtsp_url)

        print("[SYSTEM] OpenCV RTSP stream start")
        print(f"[SYSTEM] OpenCV RTSP url: {masked_rtsp_url}")

        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            cap.release()
            message = "OpenCV로 IP 카메라 RTSP 스트림을 열 수 없습니다."
            print(f"[ERROR] {message}")
            socketio.emit("stream_status", {
                "source": "ipcam",
                "status": "failed",
                "message": message
            })
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cls.WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cls.HEIGHT)

        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    message = "IP 카메라 프레임을 읽지 못했습니다."
                    print(f"[ERROR] {message}")
                    socketio.emit("stream_status", {
                        "source": "ipcam",
                        "status": "failed",
                        "message": message
                    })
                    break

                frame_count += 1
                if frame_count % 3 != 0:
                    socketio.sleep(0.001)
                    continue

                frame = cv2.resize(frame, (cls.WIDTH, cls.HEIGHT))
                if not cls.emit_annotated_frame(
                    socketio,
                    model,
                    frame,
                    predict_device,
                    source="ipcam",
                    frame_count=frame_count
                ):
                    socketio.sleep(0.01)
                    continue

                if frame_count % 30 == 0:
                    print(f"[FRAME][RTSP-OPENCV] sent: {frame_count}")

                socketio.sleep(0.01)
        finally:
            cap.release()
            print("[SYSTEM] OpenCV RTSP stream ended")

    @classmethod
    def run_webcam_stream(cls, socketio, cam_index=0):
        # 컴퓨터에 연결된 웹캠 영상을 읽고, AI 결과가 그려진 이미지를 브라우저로 보냅니다.
        # 1차: 기본 방식으로 열기
        cap = cv2.VideoCapture(cam_index)

        # 2차: 안 열리면 V4L2로 다시 시도
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)

        if not cap.isOpened():
            print(f"[ERROR] 웹캠을 열 수 없습니다. cam_index={cam_index}")
            socketio.emit("stream_status", {
                "source": "webcam",
                "status": "failed",
                "message": f"서버 웹캠을 열 수 없습니다. cam_index={cam_index}"
            })
            return

        model = cls.load_model()
        predict_device = 0 if cls._device == "cuda" else "cpu"

        # 카메라 포맷에 맞춰 MJPG 지정
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cls.WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cls.HEIGHT)

        frame_count = 0
        print(f"[SYSTEM] Webcam stream start (cam_index={cam_index})")

        try:
            while True:
                # 웹캠에서 이미지 한 장을 읽습니다.
                ret, frame = cap.read()

                if not ret or frame is None:
                    print("[ERROR] 웹캠 프레임 읽기 실패")
                    socketio.emit("stream_status", {
                        "source": "webcam",
                        "status": "failed",
                        "message": "서버 웹캠 프레임을 읽을 수 없습니다."
                    })
                    break

                frame_count += 1

                # 웹캠도 3장 중 1장만 AI에 넣어 속도를 아낍니다.
                if frame_count % 3 != 0:
                    socketio.sleep(0.001)
                    continue

                # YOLO가 웹캠 화면 속 물체를 찾고 브라우저로 보냅니다.
                if not cls.emit_annotated_frame(
                    socketio,
                    model,
                    frame,
                    predict_device,
                    source="webcam",
                    frame_count=frame_count
                ):
                    socketio.sleep(0.01)
                    continue

                socketio.sleep(0.01)

        finally:
            # 웹캠 장치를 반드시 닫아야 다음 실행 때 다시 사용할 수 있습니다.
            cap.release()
            print("[SYSTEM] Webcam stream ended")
