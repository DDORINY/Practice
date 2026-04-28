from datetime import datetime

from flask_login import UserMixin  # p151 추가

# from werkzeug.security import generate_password_hash p151변경
from werkzeug.security import check_password_hash, generate_password_hash  # p151 추가

from servers.flask.apps.app import db, login_manager  # p151 추가


# db.Model을 상속한 User 클래스를 작성한다.
# 파라미터에 UserMixin 추가
# class User(db.Model):
class User(db.Model, UserMixin):
    # 테이블 명의 지정한다.
    __tablename__ = "users"
    # 칼럼의 정의한다.
    id = db.Column(db.Integer, primary_key=True)  # id로 정수타입의 기본키
    username = db.Column(db.String, index=True)  # 사용자명 문자열타입으로 인덱싱처리
    email = db.Column(db.String, unique=True, index=True)  # 이메일 문자열 타입으로 유니크하게 인덱싱
    password_hash = db.Column(db.String)  # 암호 문자열타입
    created_at = db.Column(db.DateTime, default=datetime.now)  # 생성일은 날짜타입
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 수정일은 날짜타입 업데이트는 현재시간

    user_images = db.relationship(
        "UserImage", backref="user", order_by="desc(UserImage.id)"
    )
    
    # user_images = db.relationship("UserImage", backref="user")

    # 비밀번호를 설정하기 위한 프로퍼티(캡슐화 : 직접 수정불가능 하게 속성처리함.)
    @property
    def password(self):
        raise AttributeError("읽어 들일 수 없음")

    # 비밀번호를 설정하기 위해 setter 함수로 해시화한 비밀번호를 설정한다.
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 비밀번호 체크를 한다. P153 추가
    # 입력된 비밀번호가 db의 해시화된 비밀번호와 일치하는지 체크
    # 일치하면 True, 불일치 False
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 이메일 중복 체크를 한다. DB에 같은 이메일이
    # 있으면 True, 없으면 False
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None


# 로그인하고 있는 사용자 정보를 취득하는 암수를 작성한다.
# 사용자의 유니크 ID를 인수로 넘겨서 데이터베이스로부터 특정 사용자를 취득해서 반환해야 한다.
@login_manager.user_loader  # 데코레이터
def load_user(user_id):
    return User.query.get(user_id)  
