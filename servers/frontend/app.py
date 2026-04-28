import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from flask import Flask, Response, jsonify, redirect, render_template, request

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

FLASK_BASE_URL = os.getenv("FRONTEND_FLASK_BASE_URL", "http://127.0.0.1:5050")
AI_BASE_URL = os.getenv("FRONTEND_AI_BASE_URL", "http://127.0.0.1:5001")
DB_BASE_URL = os.getenv("FRONTEND_DB_BASE_URL", "http://127.0.0.1:5002")
IPCAM_BASE_URL = os.getenv("FRONTEND_IPCAM_BASE_URL", "http://127.0.0.1:5003")
ITS_CCTV_API_BASE_URL = os.getenv("ITS_CCTV_API_BASE_URL", "https://openapi.its.go.kr:9443/cctvInfo")
ITS_API_KEY = (os.getenv("ITS_API_KEY") or os.getenv("ITSKEY") or "").strip()
IPCAM_RTSP_URL = os.getenv(
    "AISTREAM_RTSP_URL",
    (
        f"rtsp://{os.getenv('FRONTEND_IPCAM_HOST', '127.0.0.1')}:"
        f"{os.getenv('IPCAM_RTSP_PORT', '8554')}{os.getenv('IPCAM_RTSP_PATH', '/stream1')}"
    ),
)
SKIP_HEADERS = {
    "content-encoding",
    "content-length",
    "connection",
    "transfer-encoding",
}

CCTV_REGIONS = {
    "all": {"label": "전국", "minX": 124.0, "maxX": 132.0, "minY": 33.0, "maxY": 39.6},
    "seoul": {"label": "서울", "minX": 126.76, "maxX": 127.18, "minY": 37.41, "maxY": 37.72},
    "gyeonggi": {"label": "경기", "minX": 126.35, "maxX": 127.85, "minY": 36.85, "maxY": 38.30},
    "incheon": {"label": "인천", "minX": 126.05, "maxX": 126.85, "minY": 37.20, "maxY": 37.90},
    "busan": {"label": "부산", "minX": 128.75, "maxX": 129.35, "minY": 34.95, "maxY": 35.40},
    "daegu": {"label": "대구", "minX": 128.35, "maxX": 128.80, "minY": 35.75, "maxY": 36.05},
    "daejeon": {"label": "대전", "minX": 127.25, "maxX": 127.55, "minY": 36.20, "maxY": 36.50},
    "gwangju": {"label": "광주", "minX": 126.70, "maxX": 127.05, "minY": 35.05, "maxY": 35.30},
    "ulsan": {"label": "울산", "minX": 129.00, "maxX": 129.55, "minY": 35.35, "maxY": 35.75},
    "sejong": {"label": "세종", "minX": 127.10, "maxX": 127.45, "minY": 36.40, "maxY": 36.75},
    "gangwon": {"label": "강원", "minX": 127.05, "maxX": 129.40, "minY": 37.00, "maxY": 38.65},
    "chungbuk": {"label": "충북", "minX": 127.25, "maxX": 128.75, "minY": 36.00, "maxY": 37.25},
    "chungnam": {"label": "충남", "minX": 126.05, "maxX": 127.65, "minY": 35.95, "maxY": 37.10},
    "jeonbuk": {"label": "전북", "minX": 126.35, "maxX": 127.85, "minY": 35.25, "maxY": 36.20},
    "jeonnam": {"label": "전남", "minX": 125.95, "maxX": 127.85, "minY": 33.85, "maxY": 35.55},
    "gyeongbuk": {"label": "경북", "minX": 128.00, "maxX": 130.10, "minY": 35.55, "maxY": 37.60},
    "gyeongnam": {"label": "경남", "minX": 127.55, "maxX": 129.60, "minY": 34.55, "maxY": 35.95},
    "jeju": {"label": "제주", "minX": 126.05, "maxX": 127.05, "minY": 33.10, "maxY": 33.65},
}


def check_http(name, url):
    try:
        response = requests.get(url, timeout=2)
        ok = response.status_code < 500
        return {
            "name": name,
            "ok": ok,
            "status": response.status_code,
            "url": url,
        }
    except requests.RequestException as exc:
        return {
            "name": name,
            "ok": False,
            "status": "offline",
            "url": url,
            "error": str(exc),
        }


def service_statuses():
    return [
        check_http("Frontend", request.host_url.rstrip("/") + "/health"),
        check_http("Flask", FLASK_BASE_URL + "/"),
        check_http("AI", AI_BASE_URL + "/health"),
        check_http("DB", DB_BASE_URL + "/health"),
        check_http("IPCAM", IPCAM_BASE_URL + "/health"),
    ]


def mask_url(url):
    parsed = urlsplit(url)
    if not parsed.password:
        return url

    username = parsed.username or ""
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return urlunsplit((parsed.scheme, f"{username}:***@{hostname}{port}", parsed.path, parsed.query, parsed.fragment))


def its_request(region_key, road_type, cctv_type):
    region = CCTV_REGIONS.get(region_key, CCTV_REGIONS["seoul"])
    params = {
        "apiKey": ITS_API_KEY,
        "type": road_type,
        "cctvType": cctv_type,
        "minX": region["minX"],
        "maxX": region["maxX"],
        "minY": region["minY"],
        "maxY": region["maxY"],
        "getType": "json",
    }
    response = requests.get(ITS_CCTV_API_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_cctv_items(payload):
    data = payload.get("response", {}).get("data", [])
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        data = []

    items = []
    for idx, item in enumerate(data):
        url = item.get("cctvurl") or item.get("CCTVURL") or item.get("CCTVUrl") or ""
        if not url:
            continue
        cctv_type = item.get("cctvtype") or ""
        items.append({
            "id": item.get("roadsectionid") or f"cctv-{idx}",
            "name": item.get("cctvname") or "이름 없음",
            "url": url,
            "format": item.get("cctvformat") or "",
            "resolution": item.get("cctvresolution") or "",
            "type": str(cctv_type),
            "coordX": item.get("coordx") or "",
            "coordY": item.get("coordy") or "",
            "createdAt": item.get("filecreatetime") or "",
        })
    return items


@app.get("/health")
def health():
    return {
        "status": "ok",
        "flask": FLASK_BASE_URL,
        "ai": AI_BASE_URL,
        "db": DB_BASE_URL,
        "ipcam_server": IPCAM_BASE_URL,
        "ipcam": IPCAM_RTSP_URL,
        "its_cctv": ITS_CCTV_API_BASE_URL,
        "its_key": bool(ITS_API_KEY),
    }


@app.get("/")
def dashboard():
    return render_template(
        "dashboard.html",
        flask_url="/flask/",
        ai_base_url=AI_BASE_URL,
        db_url=DB_BASE_URL + "/health",
        ipcam_health_url=IPCAM_BASE_URL + "/health",
        ipcam_url=IPCAM_RTSP_URL,
        ipcam_display_url=mask_url(IPCAM_RTSP_URL),
    )


@app.get("/api/status")
def api_status():
    return jsonify({"services": service_statuses()})


@app.get("/api/its/cctv/regions")
def api_cctv_regions():
    return jsonify({
        "regions": [
            {"id": key, "label": value["label"]}
            for key, value in CCTV_REGIONS.items()
        ]
    })


@app.get("/api/its/cctv")
def api_cctv():
    if not ITS_API_KEY:
        return jsonify({"error": "ITS_API_KEY 또는 ITSKEY가 .env에 없습니다."}), 400

    region_key = request.args.get("region", "seoul")
    road_type = request.args.get("roadType", "its")
    cctv_type = request.args.get("cctvType", "4")

    if region_key not in CCTV_REGIONS:
        return jsonify({"error": "지원하지 않는 지역입니다."}), 400
    if road_type not in {"its", "ex"}:
        return jsonify({"error": "roadType은 its 또는 ex만 가능합니다."}), 400
    if cctv_type not in {"1", "2", "3", "4", "5"}:
        return jsonify({"error": "cctvType은 1~5만 가능합니다."}), 400

    try:
        payload = its_request(region_key, road_type, cctv_type)
    except requests.RequestException as exc:
        return jsonify({"error": "ITS CCTV API 호출 실패", "detail": str(exc)}), 502
    except ValueError as exc:
        return jsonify({"error": "ITS CCTV API 응답 파싱 실패", "detail": str(exc)}), 502

    items = extract_cctv_items(payload)
    return jsonify({
        "region": {"id": region_key, "label": CCTV_REGIONS[region_key]["label"]},
        "roadType": road_type,
        "cctvType": cctv_type,
        "count": len(items),
        "items": items,
    })


@app.route("/ai_detect/aistream")
def ai_stream():
    return redirect("/")


@app.route("/flask/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/flask/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def proxy_to_flask(path):
    target = urljoin(f"{FLASK_BASE_URL}/", path)
    upstream = requests.request(
        method=request.method,
        url=target,
        params=request.args,
        data=request.get_data(),
        headers={key: value for key, value in request.headers if key.lower() != "host"},
        cookies=request.cookies,
        allow_redirects=False,
        timeout=60,
    )

    headers = [
        (key, value)
        for key, value in upstream.headers.items()
        if key.lower() not in SKIP_HEADERS
    ]

    location = upstream.headers.get("Location")
    if location and location.startswith(FLASK_BASE_URL):
        headers = [(key, value) for key, value in headers if key.lower() != "location"]
        headers.append(("Location", "/flask" + location.replace(FLASK_BASE_URL, "")))
    elif location and location.startswith("/"):
        headers = [(key, value) for key, value in headers if key.lower() != "location"]
        headers.append(("Location", "/flask" + location))

    return Response(upstream.content, upstream.status_code, headers)


if __name__ == "__main__":
    host = os.getenv("FRONTEND_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("FRONTEND_SERVER_PORT", "8080"))
    debug = os.getenv("FRONTEND_SERVER_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
