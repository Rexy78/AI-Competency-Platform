CREATE DATABASE IF NOT EXISTS resume_ai_db;
USE resume_ai_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    raw_text LONGTEXT,
    parsed_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    priority_level VARCHAR(50) DEFAULT 'High',
    INDEX idx_skill_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_id INT,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    proficiency VARCHAR(50) DEFAULT 'Intermediate',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS job_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100) DEFAULT 'Software Engineering',
    min_experience_years INT DEFAULT 0,
    INDEX idx_role_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS job_role_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_role_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'High',
    category VARCHAR(100) DEFAULT 'Backend',
    FOREIGN KEY (job_role_id) REFERENCES job_roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS resume_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    user_id INT NOT NULL,
    target_role VARCHAR(150),
    ats_score FLOAT DEFAULT 0.0,
    keyword_score FLOAT DEFAULT 0.0,
    skills_score FLOAT DEFAULT 0.0,
    formatting_score FLOAT DEFAULT 0.0,
    experience_score FLOAT DEFAULT 0.0,
    section_completeness_score FLOAT DEFAULT 0.0,
    suggestions_json JSON,
    radar_data_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS skill_gaps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    user_id INT NOT NULL,
    job_role VARCHAR(150) NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50) DEFAULT 'Medium',
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    user_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'High',
    why_text TEXT,
    prerequisites_json JSON,
    next_steps_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rating INT DEFAULT 5,
    comments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learning_roadmaps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_role VARCHAR(150) NOT NULL,
    steps_json JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
