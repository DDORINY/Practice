# Flaskbook 5-Server Local Layout

Docker 없이 프로젝트를 5개의 실행 디렉터리로 나눕니다. 각 서버는 자기 디렉터리의 `app.py`로 실행합니다.

| 서버 | 역할 | 실행 파일 | 기본 포트 |
| --- | --- | --- | --- |
| frontend | 프론트 진입 서버, Flask 앱 프록시, AI 화면 연결 | `servers/frontend/app.py` | `8080` |
| flask | 기존 Flask 웹 앱, 인증, CRUD, 이미지 업로드/탐지 | `servers/flask/app.py` | `5000` |
| ai | Socket.IO 기반 AI 실시간 스트림 서버 | `servers/ai/app.py` | `5001` |
| db | SQLite DB 상태 확인/초기화 서버 | `servers/db/app.py` | `5002` |
| ipcam | RTSP 카메라 설정/연결 확인 서버 | `servers/ipcam/app.py` | `5003` |

## 기능 파일 위치

기존 Flask 기능 파일은 `servers/flask/apps` 아래로 이동했습니다.

```text
servers/flask/apps/app.py
servers/flask/apps/config.py
servers/flask/apps/auth/
servers/flask/apps/crud/
servers/flask/apps/detector/
servers/flask/apps/static/
servers/flask/apps/images/
```

AI 스트림 기능은 `servers/ai` 아래로 이동했습니다.

```text
servers/ai/aistream_app.py
servers/ai/service/AiStreamService.py
servers/ai/templates/
servers/ai/yolov8n.pt
```

IP 카메라 설정/연결 확인 기능은 `servers/ipcam` 아래에 있습니다.

```text
servers/ipcam/app.py
servers/ipcam/check_rtsp.py
```

기존 `apps/`, `Aistream/` 폴더는 기능 이동 후 삭제했습니다. 새 코드는 `servers` 아래 경로를 사용합니다.

## 실행

실행 설정은 프로젝트 루트의 `.env` 한 곳에서 관리합니다.

터미널을 5개 열고 각각 실행합니다.

```bash
venv/bin/python servers/db/app.py
```

```bash
venv/bin/python servers/flask/app.py
```

```bash
venv/bin/python servers/ai/app.py
```

```bash
venv/bin/python servers/frontend/app.py
```

IP 카메라 설정 확인 서버를 실행합니다.

```bash
venv/bin/python servers/ipcam/app.py
```

브라우저에서는 `http://localhost:8080`으로 접속합니다.

프론트 서버 첫 화면은 서버 상태 대시보드입니다. 여기에서 Flask 앱, AI 스트림, DB 상태, IPCAM RTSP 주소를 확인할 수 있습니다.

| 프론트 경로 | 기능 |
| --- | --- |
| `/` | 서버 상태 대시보드 |
| `/api/status` | 프론트에서 확인한 각 서버 상태 JSON |
| `/flask/` | Flask 앱 프록시 |
| `/ai_detect/aistream` | AI 스트림 화면 |

외부 PC에서는 `localhost` 대신 서버 PC의 IP를 사용합니다. 예를 들어 서버 IP가 `192.168.0.10`이면 `http://192.168.0.10:8080`으로 접속합니다.

AI 스트림 화면은 `http://localhost:8080/ai_detect/aistream`입니다. 프론트 서버가 이 경로를 AI 서버(`5001`)로 연결합니다.

DB를 새로 만들거나 테이블을 초기화해야 할 때는 아래 명령을 사용합니다.

```bash
FLASK_APP=servers/db/app.py venv/bin/flask init
```

## 실제 IP 카메라 사용

`.env`에서 아래 값을 실제 카메라 주소로 바꿉니다.

```bash
AISTREAM_RTSP_URL=rtsp://아이디:비밀번호@카메라IP:554/stream1
```

IP 카메라 주소를 아직 모르면 로컬에서 다음처럼 후보 경로를 확인할 수 있습니다.

```bash
venv/bin/python servers/ipcam/check_rtsp.py --host 카메라IP --user 아이디 --password 비밀번호
```
