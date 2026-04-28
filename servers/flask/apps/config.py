import os
from pathlib import Path

serverdir = Path(__file__).parent.parent
projectdir = Path(__file__).resolve().parents[3]

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_csrf_secret_key")
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", "your_csrf_secret_key")

    # 이미지 업로드 경로에 apps/images를 지정한다
    UPLOAD_FOLDER = str(Path(serverdir, "apps", "images"))
    # 물체 감지에 이용하는 라벨
    # 물체 감지에 이용하는 라벨 p222 추가
    LABELS = [
        "unlabeled",
        "person",
        "bicycle",
        "car",
        "motorcycle",
        "airplane",
        "bus",
        "train",
        "truck",
        "boat",
        "traffic light",
        "fire hydrant",
        "street sign",
        "stop sign",
        "parking meter",
        "bench",
        "bird",
        "cat",
        "dog",
        "horse",
        "sheep",
        "cow",
        "elephant",
        "bear",
        "zebra",
        "giraffe",
        "hat",
        "backpack",
        "umbrella",
        "shoe",
        "eye glasses",
        "handbag",
        "tie",
        "suitcase",
        "frisbee",
        "skis",
        "snowboard",
        "sports ball",
        "kite",
        "baseball bat",
        "baseball glove",
        "skateboard",
        "surfboard",
        "tennis racket",
        "bottle",
        "plate",
        "wine glass",
        "cup",
        "fork",
        "knife",
        "spoon",
        "bowl",
        "banana",
        "apple",
        "sandwich",
        "orange",
        "broccoli",
        "carrot",
        "hot dog",
        "pizza",
        "donut",
        "cake",
        "chair",
        "couch",
        "potted plant",
        "bed",
        "mirror",
        "dining table",
        "window",
        "desk",
        "toilet",
        "door",
        "tv",
        "laptop",
        "mouse",
        "remote",
        "keyboard",
        "cell phone",
        "microwave",
        "oven",
        "toaster",
        "sink",
        "refrigerator",
        "blender",
        "book",
        "clock",
        "vase",
        "scissors",
        "teddy bear",
        "hair drier",
        "toothbrush",
    ]


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{projectdir / 'local.sqlite'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{projectdir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    # 이미지 업로드처에 tests/detector/images를 저장한다
    UPLOAD_FOLDER = str(Path(projectdir, "tests", "detector", "images"))

config = {
    "local": LocalConfig,
    "testing": TestingConfig
}
