-- Tạo database
CREATE DATABASE IF NOT EXISTS university_comparison CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE university_comparison;

-- Bảng Universities - Lưu thông tin các trường đại học
CREATE TABLE IF NOT EXISTS universities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    university_name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    ranking INT,
    website VARCHAR(255),
    established_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Bảng Admission_Requirements - Lưu yêu cầu đầu vào
CREATE TABLE IF NOT EXISTS admission_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT NOT NULL,
    program_name VARCHAR(255) NOT NULL,
    degree_level ENUM('Bachelor', 'Master', 'PhD', 'Diploma') NOT NULL,
    min_gpa DECIMAL(3,2),
    min_ielts DECIMAL(3,1),
    min_toefl INT,
    min_sat INT,
    min_gre INT,
    tuition_fee_usd DECIMAL(10,2),
    application_deadline DATE,
    additional_requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE
);

-- Insert dữ liệu mẫu
INSERT INTO universities (university_name, country, city, ranking, website, established_year) VALUES
('Harvard University', 'United States', 'Cambridge', 1, 'https://www.harvard.edu', 1636),
('Stanford University', 'United States', 'Stanford', 3, 'https://www.stanford.edu', 1885),
('University of Oxford', 'United Kingdom', 'Oxford', 2, 'https://www.ox.ac.uk', 1096),
('University of Cambridge', 'United Kingdom', 'Cambridge', 4, 'https://www.cam.ac.uk', 1209),
('MIT', 'United States', 'Cambridge', 5, 'https://www.mit.edu', 1861),
('National University of Singapore', 'Singapore', 'Singapore', 11, 'https://www.nus.edu.sg', 1905),
('University of Toronto', 'Canada', 'Toronto', 21, 'https://www.utoronto.ca', 1827),
('University of Melbourne', 'Australia', 'Melbourne', 14, 'https://www.unimelb.edu.au', 1853);

INSERT INTO admission_requirements (university_id, program_name, degree_level, min_gpa, min_ielts, min_toefl, min_sat, tuition_fee_usd, application_deadline, additional_requirements) VALUES
(1, 'Computer Science', 'Bachelor', 3.80, 7.5, 100, 1500, 54002.00, '2024-01-01', 'SAT Subject Tests, 2 recommendation letters'),
(1, 'Business Administration', 'Master', 3.50, 7.0, 100, NULL, 73440.00, '2024-01-15', 'GMAT 700+, Work experience required'),
(2, 'Engineering', 'Bachelor', 3.70, 7.0, 100, 1470, 56169.00, '2024-01-05', 'Strong math background'),
(2, 'Computer Science', 'Master', 3.60, 7.0, 100, NULL, 54315.00, '2024-12-15', 'GRE required, Programming experience'),
(3, 'Medicine', 'Bachelor', 3.90, 7.5, 110, NULL, 45000.00, '2023-10-15', 'BMAT or UKCAT required'),
(3, 'Law', 'Bachelor', 3.85, 7.5, 110, NULL, 42000.00, '2023-10-15', 'LNAT required'),
(4, 'Natural Sciences', 'Bachelor', 3.80, 7.5, 110, NULL, 44000.00, '2023-10-15', 'Strong science background'),
(5, 'Electrical Engineering', 'Bachelor', 3.90, 7.5, 100, 1540, 53790.00, '2024-01-01', 'Physics and Math excellence'),
(6, 'Data Science', 'Master', 3.40, 6.5, 85, NULL, 25000.00, '2024-02-28', 'Programming skills required'),
(7, 'Medicine', 'Bachelor', 3.70, 6.5, 100, NULL, 35000.00, '2024-01-15', 'MCAT required'),
(8, 'Engineering', 'Bachelor', 3.50, 6.5, 79, NULL, 30000.00, '2023-12-31', 'Math and Physics required');
