USE lms_text;

-- 1) MEMBERS (회원)
-- ---------------------------------------
CREATE TABLE members (
  id INT AUTO_INCREMENT PRIMARY KEY,

  -- 로그인
  uid VARCHAR(50) NOT NULL UNIQUE,
  pw_hash VARCHAR(255) NOT NULL,

  -- 기본정보
  name VARCHAR(50) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(120) NOT NULL,
  address VARCHAR(255) NOT NULL,

  -- 주민번호 원문 저장 금지: 생일만 보관
  birthdate DATE NOT NULL,

  -- 프로필 이미지 파일명(서버 저장 + DB에는 파일명)
  profile_img VARCHAR(255) NULL,

  -- 개인정보 보관기간 안내 동의(필수)
  retention_agreed TINYINT NOT NULL DEFAULT 0,
  retention_agreed_at DATETIME NULL,

  -- 권한/상태
  role ENUM('USER','ADMIN') NOT NULL DEFAULT 'USER',
  active TINYINT NOT NULL DEFAULT 1,

  -- 탈퇴/자동삭제
  deleted_at DATETIME NULL,
  purge_at DATETIME NULL,

  -- 로그인 기록
  last_login_at DATETIME NULL,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uk_members_email (email),
  KEY idx_members_active (active),
  KEY idx_members_role (role),
  KEY idx_members_purge_at (purge_at),
  KEY idx_members_created_at (created_at)
);
-- 2) PASSWORD RESET TOKENS (비밀번호 찾기)
-- ---------------------------------------
CREATE TABLE password_reset_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,
  token VARCHAR(64) NOT NULL UNIQUE,
  expires_at DATETIME NOT NULL,
  used TINYINT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_prt_member
    FOREIGN KEY (member_id) REFERENCES members(id)
    ON DELETE CASCADE,

  KEY idx_prt_member_id (member_id),
  KEY idx_prt_expires_at (expires_at)
);
-- 3) INQUIRIES (문의: 폼 + 마이페이지에서 내 문의 목록)
-- ---------------------------------------
CREATE TABLE inquiries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,

  title VARCHAR(150) NOT NULL,
  content TEXT NOT NULL,

  -- 처리 상태
  status ENUM('RECEIVED','IN_PROGRESS','DONE') NOT NULL DEFAULT 'RECEIVED',

  -- (옵션) 관리자 답변
  answer TEXT NULL,
  answered_at DATETIME NULL,
  answered_by INT NULL,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_inq_member
    FOREIGN KEY (member_id) REFERENCES members(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_inq_admin
    FOREIGN KEY (answered_by) REFERENCES members(id)
    ON DELETE SET NULL,

  KEY idx_inq_member_id (member_id),
  KEY idx_inq_status (status),
  KEY idx_inq_created_at (created_at)
);
-- 4) LECTURES (강의)
-- ---------------------------------------
CREATE TABLE lectures (
  id INT AUTO_INCREMENT PRIMARY KEY,

  title VARCHAR(150) NOT NULL,
  teacher VARCHAR(80) NULL,
  description TEXT NULL,

  start_date DATE NULL,
  end_date DATE NULL,

  capacity INT NOT NULL DEFAULT 0,
  is_open TINYINT NOT NULL DEFAULT 1,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  KEY idx_lectures_open (is_open),
  KEY idx_lectures_dates (start_date, end_date)
);
-- 5) ENROLLMENTS (강의 신청/취소 -> 내 강의실)
--   - 취소는 soft cancel: status
-- ---------------------------------------
CREATE TABLE enrollments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,
  lecture_id INT NOT NULL,

  status ENUM('ENROLLED','CANCELED') NOT NULL DEFAULT 'ENROLLED',
  applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  canceled_at DATETIME NULL,

  CONSTRAINT fk_enr_member
    FOREIGN KEY (member_id) REFERENCES members(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_enr_lecture
    FOREIGN KEY (lecture_id) REFERENCES lectures(id)
    ON DELETE CASCADE,

  -- 같은 강의를 중복 신청 방지(취소 후 재신청 허용하려면 정책 변경 필요)
  UNIQUE KEY uk_enr_member_lecture (member_id, lecture_id),
  KEY idx_enr_member (member_id),
  KEY idx_enr_lecture (lecture_id),
  KEY idx_enr_status (status)
);
-- 6) NEWS POSTS (MBC소식: 카드형 게시판)
-- ---------------------------------------
CREATE TABLE news_posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  admin_id INT NOT NULL,

  title VARCHAR(150) NOT NULL,
  content TEXT NOT NULL,

  view_count INT NOT NULL DEFAULT 0,
  is_pinned TINYINT NOT NULL DEFAULT 0,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_news_admin
    FOREIGN KEY (admin_id) REFERENCES members(id)
    ON DELETE RESTRICT,

  KEY idx_news_created_at (created_at),
  KEY idx_news_pinned (is_pinned)
);
-- 7) COMMUNITY POSTS (커뮤니티: 자유/자료게시판)
--   - board_type 으로 구분: FREE/DATA
-- ---------------------------------------
CREATE TABLE community_posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,

  board_type ENUM('FREE','DATA') NOT NULL DEFAULT 'FREE',
  title VARCHAR(150) NOT NULL,
  content TEXT NOT NULL,

  view_count INT NOT NULL DEFAULT 0,
  like_count INT NOT NULL DEFAULT 0,

  active TINYINT NOT NULL DEFAULT 1, -- 게시글 soft delete
  deleted_at DATETIME NULL,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_comm_member
    FOREIGN KEY (member_id) REFERENCES members(id)
    ON DELETE CASCADE,

  KEY idx_comm_type (board_type),
  KEY idx_comm_active (active),
  KEY idx_comm_created_at (created_at)
);
-- 8) 더미데이터 생성
-- ---------------------------------------
 INSERT INTO members
(uid, pw_hash, name, phone, email, address, birthdate,
 retention_agreed, retention_agreed_at, role, active, last_login_at)
VALUES
('user01','$2b$12$dummyhash','김민수','010-1111-0001','user01@test.com','서울 관악구','1995-03-12',1,NOW(),'USER',1,NOW()),
('user02','$2b$12$dummyhash','이서연','010-1111-0002','user02@test.com','서울 금천구','1997-07-22',1,NOW(),'USER',1,NOW()),
('user03','$2b$12$dummyhash','박지훈','010-1111-0003','user03@test.com','서울 구로구','1998-02-18',1,NOW(),'USER',1,NOW()),
('user04','$2b$12$dummyhash','최유진','010-1111-0004','user04@test.com','서울 영등포','1994-11-02',1,NOW(),'USER',1,NOW()),
('user05','$2b$12$dummyhash','정하늘','010-1111-0005','user05@test.com','서울 동작구','1996-01-09',1,NOW(),'USER',1,NOW()),
('user06','$2b$12$dummyhash','김도현','010-1111-0006','user06@test.com','서울 강남구','1993-05-30',1,NOW(),'USER',1,NOW()),
('user07','$2b$12$dummyhash','한지민','010-1111-0007','user07@test.com','서울 강서구','1992-12-12',1,NOW(),'USER',1,NOW()),
('user08','$2b$12$dummyhash','윤지호','010-1111-0008','user08@test.com','서울 마포구','1999-09-19',1,NOW(),'USER',1,NOW()),
('user09','$2b$12$dummyhash','강태현','010-1111-0009','user09@test.com','서울 서초구','1995-08-04',1,NOW(),'USER',1,NOW()),
('user10','$2b$12$dummyhash','송다은','010-1111-0010','user10@test.com','서울 송파구','1997-04-17',1,NOW(),'USER',1,NOW()),
('user11','$2b$12$dummyhash','임준서','010-1111-0011','user11@test.com','서울 성동구','1996-06-25',1,NOW(),'USER',1,NOW()),
('user12','$2b$12$dummyhash','조은별','010-1111-0012','user12@test.com','서울 광진구','1994-10-10',1,NOW(),'USER',1,NOW()),
('user13','$2b$12$dummyhash','오지훈','010-1111-0013','user13@test.com','서울 노원구','1998-03-21',1,NOW(),'USER',1,NOW()),
('user14','$2b$12$dummyhash','백서윤','010-1111-0014','user14@test.com','서울 은평구','1993-02-07',1,NOW(),'USER',1,NOW()),
('user15','$2b$12$dummyhash','남지성','010-1111-0015','user15@test.com','서울 중구','1992-07-29',1,NOW(),'USER',0,NOW());
