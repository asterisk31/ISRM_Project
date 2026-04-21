DROP DATABASE IF EXISTS student_db;
CREATE DATABASE student_db;
USE student_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    role VARCHAR(20)
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    marks INT,
    email VARCHAR(100)
);

INSERT INTO users (username, password, role) VALUES
('alice', 'password123', 'user'),
('bob', 'welcome1', 'user'),
('admin', 'admin123', 'admin'),
('astha', '1234', 'user'),
('registrar', 'records2026', 'admin');

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
