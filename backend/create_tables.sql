-- KARİYERKOÇU TABLO YAPILARI
-- PostgreSQL için


CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	full_name VARCHAR(100), 
	phone VARCHAR(20), 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	target_sector VARCHAR(50), 
	target_position VARCHAR(50), 
	experience_level VARCHAR(50), 
	PRIMARY KEY (id)
)

;


CREATE TABLE cvs (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	original_filename VARCHAR(255) NOT NULL, 
	raw_text TEXT, 
	full_name VARCHAR(200), 
	title VARCHAR(200), 
	email VARCHAR(255), 
	phone VARCHAR(50), 
	linkedin VARCHAR(255), 
	github VARCHAR(255), 
	location VARCHAR(200), 
	summary TEXT, 
	skills JSON, 
	experience JSON, 
	education JSON, 
	projects JSON, 
	languages JSON, 
	certifications JSON, 
	experience_years VARCHAR(20), 
	is_parsed BOOLEAN, 
	parse_error TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;


CREATE TABLE cv_analyses (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	cv_id VARCHAR NOT NULL, 
	sector VARCHAR NOT NULL, 
	fields JSON NOT NULL, 
	experience_level VARCHAR NOT NULL, 
	field_analyses JSON NOT NULL, 
	strongest_field VARCHAR, 
	action_items JSON, 
	overall_score INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(cv_id) REFERENCES cvs (id)
)

;


CREATE TABLE interview_sessions (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	cv_id VARCHAR, 
	company_sector VARCHAR NOT NULL, 
	position VARCHAR NOT NULL, 
	experience_level VARCHAR NOT NULL, 
	interview_type VARCHAR NOT NULL, 
	status VARCHAR, 
	current_question_number INTEGER, 
	total_questions INTEGER, 
	total_score FLOAT, 
	average_score FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	completed_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(cv_id) REFERENCES cvs (id)
)

;


CREATE TABLE interview_questions (
	id VARCHAR NOT NULL, 
	session_id VARCHAR NOT NULL, 
	question_number INTEGER NOT NULL, 
	question_text TEXT NOT NULL, 
	question_tts TEXT,
	question_type VARCHAR, 
	transition_text TEXT, 
	transition_tts TEXT,
	is_answered BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES interview_sessions (id)
)

;


CREATE TABLE interview_answers (
	id VARCHAR NOT NULL, 
	question_id VARCHAR NOT NULL, 
	user_answer TEXT NOT NULL, 
	score INTEGER, 
	evaluation_reason TEXT, 
	ideal_answer TEXT, 
	strengths JSON, 
	weaknesses JSON, 
	answered_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(question_id) REFERENCES interview_questions (id)
)

;
