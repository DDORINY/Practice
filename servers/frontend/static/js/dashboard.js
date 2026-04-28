const strip = document.querySelector("#statusGrid");
const cctvTime = document.querySelector("#cctvTime");
const clock = document.querySelector("#clock");
const ipcamCard = document.querySelector(".ipcam-stream");
const webcamCard = document.querySelector(".webcam-stream");
const ipcamView = document.querySelector("#ipcamView");
const webcamView = document.querySelector("#webcamView");
const aiSocketStatus = document.querySelector("#aiSocketStatus");
const browserWebcam = document.querySelector("#browserWebcam");
const webcamCanvas = document.querySelector("#webcamCanvas");
const cctvRegion = document.querySelector("#cctvRegion");
const cctvRoadType = document.querySelector("#cctvRoadType");
const cctvType = document.querySelector("#cctvType");
const cctvLoadButton = document.querySelector("#cctvLoadButton");
const cctvRefreshButton = document.querySelector("#cctvRefreshButton");
const cctvList = document.querySelector("#cctvList");
const cctvListTitle = document.querySelector("#cctvListTitle");
const itsStatus = document.querySelector("#itsStatus");
const itsVideo = document.querySelector("#itsVideo");
const itsImage = document.querySelector("#itsImage");
const itsEmpty = document.querySelector("#itsEmpty");
const selectedCctvName = document.querySelector("#selectedCctvName");
const selectedCctvFormat = document.querySelector("#selectedCctvFormat");
const selectedCctvResolution = document.querySelector("#selectedCctvResolution");
const selectedCctvCoord = document.querySelector("#selectedCctvCoord");

let browserWebcamStarted = false;
let browserWebcamCount = 0;
let browserWebcamInFlight = false;
let webcamFrameReceived = false;
let hlsPlayer = null;
let currentCctvItems = [];

function formatDate(date) {
    const pad = (value) => String(value).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function renderService(service) {
    const pill = document.createElement("span");
    pill.className = `service-pill ${service.ok ? "online" : "offline"}`;
    pill.textContent = `${service.name} ${service.ok ? "정상" : "오프라인"}`;
    return pill;
}

async function loadStatus() {
    if (!strip) return;
    strip.innerHTML = "";

    try {
        const response = await fetch("/api/status", { cache: "no-store" });
        const payload = await response.json();
        payload.services.forEach((service) => strip.append(renderService(service)));
    } catch (error) {
        strip.append(renderService({ name: "Frontend", ok: false }));
    }
}

function tick() {
    const now = new Date();
    const time = now.toLocaleTimeString("ko-KR", { hour12: false });
    if (clock) clock.textContent = time;
    if (cctvTime) cctvTime.textContent = formatDate(now);
}

function showFrame(source, image) {
    const src = `data:image/jpeg;base64,${image}`;

    if ((source === "ipcam" || source === "rtsp") && ipcamView) {
        ipcamView.src = src;
        ipcamCard?.classList.add("has-frame");
    }

    if (source === "webcam" && webcamView) {
        webcamFrameReceived = true;
        webcamView.src = src;
        webcamCard?.classList.add("has-frame");
    }
}

function setAiSocketStatus(message) {
    if (aiSocketStatus) aiSocketStatus.textContent = message;
}

function setStreamError(source, message) {
    const card = source === "webcam" ? webcamCard : ipcamCard;
    if (!card) return;

    card.classList.remove("has-frame");
    card.setAttribute("title", message || "스트림 연결 실패");
}

async function startBrowserWebcam(socket, reason) {
    if (browserWebcamStarted || !browserWebcam || !webcamCanvas) return;
    browserWebcamStarted = true;

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn("Browser webcam is not supported:", reason);
        setAiSocketStatus("브라우저 웹캠을 사용할 수 없습니다.");
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false
        });

        browserWebcam.srcObject = stream;
        await browserWebcam.play();

        webcamCanvas.width = 640;
        webcamCanvas.height = 480;
        const context = webcamCanvas.getContext("2d", { willReadFrequently: true });

        setInterval(() => {
            if (!socket.connected || browserWebcam.readyState < 2 || browserWebcamInFlight) return;

            context.drawImage(browserWebcam, 0, 0, webcamCanvas.width, webcamCanvas.height);
            browserWebcamCount += 1;
            browserWebcamInFlight = true;

            socket.emit("browser_webcam_frame", {
                image: webcamCanvas.toDataURL("image/jpeg", 0.75),
                count: browserWebcamCount
            }, () => {
                browserWebcamInFlight = false;
            });
        }, 300);
    } catch (error) {
        console.warn("Browser webcam could not start:", error);
        setAiSocketStatus("웹캠 권한을 확인해 주세요.");
    }
}

function connectStreams() {
    if (typeof io !== "function") {
        console.warn("Socket.IO client is not loaded.");
        setAiSocketStatus("Socket.IO 클라이언트를 불러오지 못했습니다.");
        return;
    }

    const aiBaseUrl = window.AI_BASE_URL || "http://127.0.0.1:5001";
    const socket = io(aiBaseUrl, {
        path: "/socket.io",
        transports: ["websocket", "polling"]
    });

    socket.on("connect", () => {
        console.log("[AI SOCKET] connected:", socket.id);
        setAiSocketStatus("AI 서버 연결됨");
    });

    socket.on("disconnect", () => {
        setAiSocketStatus("AI 서버 연결 끊김");
    });

    socket.on("connect_error", (err) => {
        console.error("[AI SOCKET] connect_error:", err.message);
        setAiSocketStatus("AI 서버 연결 실패");
    });

    socket.on("ipcam_frame", (data) => {
        if (!data?.image) return;
        showFrame("ipcam", data.image);
    });

    socket.on("webcam_frame", (data) => {
        if (!data?.image) return;
        showFrame("webcam", data.image);
    });

    socket.on("ai_frame", (data) => {
        if (!data?.source || !data?.image) return;
        showFrame(data.source, data.image);
    });

    socket.on("stream_status", (data) => {
        if (data?.status === "failed") {
            setStreamError(data.source, data.message);
        }

        if (data?.source === "ipcam" && data.status === "failed") {
            setAiSocketStatus(`IP 카메라 연결 실패: ${data.message || "상태를 확인해 주세요."}`);
        }

        if (data?.source === "webcam" && data.status === "failed") {
            startBrowserWebcam(socket, data.message);
        }
    });

    setTimeout(() => {
        if (!webcamFrameReceived) {
            startBrowserWebcam(socket, "No server webcam frame received.");
        }
    }, 5000);
}

function setItsStatus(message) {
    if (itsStatus) itsStatus.textContent = message;
}

function resetItsPlayer(message) {
    if (hlsPlayer) {
        hlsPlayer.destroy();
        hlsPlayer = null;
    }

    if (itsVideo) {
        itsVideo.pause();
        itsVideo.removeAttribute("src");
        itsVideo.load();
        itsVideo.style.display = "none";
    }

    if (itsImage) {
        itsImage.removeAttribute("src");
        itsImage.style.display = "none";
    }

    if (itsEmpty) {
        itsEmpty.textContent = message || "CCTV를 선택해 주세요.";
        itsEmpty.style.display = "grid";
    }
}

function setSelectedCctv(item) {
    if (selectedCctvName) selectedCctvName.textContent = item?.name || "-";
    if (selectedCctvFormat) selectedCctvFormat.textContent = item?.format || item?.type || "-";
    if (selectedCctvResolution) selectedCctvResolution.textContent = item?.resolution || "-";
    if (selectedCctvCoord) selectedCctvCoord.textContent = item?.coordX && item?.coordY ? `${item.coordY}, ${item.coordX}` : "-";
}

function playCctv(item) {
    if (!item?.url) return;
    resetItsPlayer("");
    setSelectedCctv(item);
    setItsStatus(item.name);

    const url = item.url;
    const format = String(item.format || "").toLowerCase();
    const type = String(item.type || "");
    const isImage = type === "3" || /\.(jpg|jpeg|png)(\?|$)/i.test(url);
    const isHls = /\.m3u8(\?|$)/i.test(url) || type === "1" || type === "4" || format.includes("hls");

    if (isImage && itsImage) {
        itsImage.src = url;
        itsImage.style.display = "block";
        if (itsEmpty) itsEmpty.style.display = "none";
        return;
    }

    if (!itsVideo) return;
    itsVideo.style.display = "block";
    if (itsEmpty) itsEmpty.style.display = "none";

    if (isHls && window.Hls?.isSupported()) {
        hlsPlayer = new Hls({ lowLatencyMode: true });
        hlsPlayer.loadSource(url);
        hlsPlayer.attachMedia(itsVideo);
        hlsPlayer.on(Hls.Events.MANIFEST_PARSED, () => itsVideo.play().catch(() => {}));
        hlsPlayer.on(Hls.Events.ERROR, (_event, data) => {
            if (data?.fatal) resetItsPlayer("CCTV 영상을 재생할 수 없습니다.");
        });
        return;
    }

    itsVideo.src = url;
    itsVideo.play().catch(() => {});
}

function renderCctvList(items) {
    if (!cctvList) return;
    cctvList.innerHTML = "";

    if (!items.length) {
        cctvList.innerHTML = `
            <div class="empty-state">
                <span aria-hidden="true">+</span>
                <p>선택한 조건의 CCTV가 없습니다.</p>
            </div>
        `;
        resetItsPlayer("선택한 조건의 CCTV가 없습니다.");
        return;
    }

    items.forEach((item, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "cctv-item";
        button.innerHTML = `
            <strong>${item.name}</strong>
            <span>${item.format || "영상"} · ${item.resolution || "해상도 정보 없음"}</span>
        `;
        button.addEventListener("click", () => {
            document.querySelectorAll(".cctv-item.active").forEach((el) => el.classList.remove("active"));
            button.classList.add("active");
            playCctv(item);
        });
        cctvList.append(button);

        if (index === 0) {
            button.classList.add("active");
            playCctv(item);
        }
    });
}

async function loadCctvRegions() {
    if (!cctvRegion) return;

    const response = await fetch("/api/its/cctv/regions", { cache: "no-store" });
    const payload = await response.json();
    cctvRegion.innerHTML = "";

    payload.regions.forEach((region) => {
        const option = document.createElement("option");
        option.value = region.id;
        option.textContent = region.label;
        cctvRegion.append(option);
    });

    cctvRegion.value = "seoul";
}

async function loadCctvList() {
    if (!cctvRegion || !cctvRoadType || !cctvType) return;

    const params = new URLSearchParams({
        region: cctvRegion.value,
        roadType: cctvRoadType.value,
        cctvType: cctvType.value
    });

    setItsStatus("조회 중");
    resetItsPlayer("CCTV 목록을 불러오는 중입니다.");

    try {
        const response = await fetch(`/api/its/cctv?${params}`, { cache: "no-store" });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || "CCTV 조회 실패");

        currentCctvItems = payload.items || [];
        if (cctvListTitle) cctvListTitle.textContent = `${payload.region.label} CCTV (${payload.count})`;
        setItsStatus(`${payload.count}개 조회`);
        renderCctvList(currentCctvItems);
    } catch (error) {
        currentCctvItems = [];
        if (cctvListTitle) cctvListTitle.textContent = "지역 CCTV (0)";
        setItsStatus("조회 실패");
        if (cctvList) {
            cctvList.innerHTML = `
                <div class="empty-state">
                    <span aria-hidden="true">!</span>
                    <p>${error.message}</p>
                </div>
            `;
        }
        resetItsPlayer("CCTV 조회에 실패했습니다.");
    }
}

async function initCctvBrowser() {
    if (!cctvRegion) return;

    try {
        await loadCctvRegions();
        await loadCctvList();
    } catch (error) {
        setItsStatus("초기화 실패");
        resetItsPlayer(error.message);
    }

    cctvLoadButton?.addEventListener("click", loadCctvList);
    cctvRefreshButton?.addEventListener("click", loadCctvList);
    cctvRegion?.addEventListener("change", loadCctvList);
    cctvRoadType?.addEventListener("change", loadCctvList);
    cctvType?.addEventListener("change", loadCctvList);
}

tick();
loadStatus();
connectStreams();
initCctvBrowser();
setInterval(tick, 1000);
setInterval(loadStatus, 5000);
