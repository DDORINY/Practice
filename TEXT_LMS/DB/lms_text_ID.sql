CREATE USER 'mbc_text'@'localhost' IDENTIFIED BY '1234';

CREATE DATABASE lms_text
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

GRANT ALL PRIVILEGES ON lms_text.* TO 'mbc_text'@'localhost';
FLUSH PRIVILEGES;