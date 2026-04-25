DROP DATABASE IF EXISTS student_db;
CREATE DATABASE student_db;
USE student_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    session_token VARCHAR(255) NULL
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    marks INT NOT NULL,
    email VARCHAR(100) NOT NULL
);

INSERT INTO users (username, password, role) VALUES
('alice', 'scrypt:32768:8:1$0YbdWjQjNLLSATkr$fd963459601de92664d89a782bf9df491ce02ac6202a2a9f54e9fd4a14cd1a91d68dcdfe065b952dc3bd75f9f0bbb190346ec82ce10398a5a871763200e85413', 'user'),
('bob', 'scrypt:32768:8:1$rZRfuqNvVTqOllsl$09ef69dc890fdf2dd9742e201201e8a7b9033701930585b5bf68dae23bee4dc17083c9e9661fd30ae4b43173d400e6c89958393a27fa2c377d927f8135e0e050', 'user'),
('admin', 'scrypt:32768:8:1$xZx9Rbttm4INmQcU$67ca7a9bda531a8020f8817ab9a9ae505b1400ec59e8959f3befcf8dbe8190992dfebda0b99be6a09bd9b129e5bf759008d775ba3e50b3f2d20b099c8cd4ca62', 'admin'),
('astha', 'scrypt:32768:8:1$iYKBLdNU63TrcFGo$9e723a8485dea710ee5bd6eeabc59eec9a56910b9ee1a2222c301f2ec7c5cc97410dc289b7bd574544d429e060a0e6387bb7fe99af72853ad1c04c1b42806a49', 'user'),
('registrar', 'scrypt:32768:8:1$uuMjYmHHYODGSM7t$f33f148a3ae318a25fcaa479fd4b3a33046ef5f8187f92b9e15806118229dadb531c4e62dd4d67cb78fb10eafc3a0a25b0f520efea05bedd7e2b938205861588', 'admin');

INSERT INTO students (name, marks, email) VALUES
('Aarav Mehta', 84, 'aarav.mehta@northbridge.example'),
('Isha Rao', 91, 'isha.rao@northbridge.example'),
('Kabir Singh', 76, 'kabir.singh@northbridge.example'),
('Maya Thomas', 88, 'maya.thomas@northbridge.example'),
('Neel Kapoor', 69, 'neel.kapoor@northbridge.example'),
('Fionnula Foottit', 58,'ffoottit12@icio.us'),
('Doyle Carles', 47, 'dcarles11@hugedomains.com'),
('Berenice Pettisall', 46, 'bpettisall0@ftc.gov'),
('Aubrie Allwright',98, 'aallwrighti@house.gov'),
('Sara Fernandes', 95, 'sara.fernandes@northbridge.example');
