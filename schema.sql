CREATE DATABASE photoshare;
USE photoshare;
DROP TABLE Pictures CASCADE;
DROP TABLE Users CASCADE;
DROP TABLE Tags CASCADE;
DROP TABLE Comments CASCADE;
DROP TABLE Albums CASCADE;
DROP TABLE Associated_With_Tags CASCADE;
DROP TABLE Befriend_With CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    gender ENUM('Female', 'Male', 'Other'),
    date_of_birth DATE,
    hometown VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Albums(
  album_id int4 AUTO_INCREMENT,
  user_id int4,
  date_of_creation DATE,
  album_name VARCHAR(255),
  CONSTRAINT album_pk PRIMARY KEY (album_id),
  CONSTRAINT ua_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  album_id int4,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  likes int4, 
  INDEX apid_idx (album_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  CONSTRAINT ap_fk FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
  CONSTRAINT up_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Tags(
  word VARCHAR(255),
  picture_id int4,
  CONSTRAINT picture_fk FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE,
  CONSTRAINT tags_pk PRIMARY KEY (word, picture_id)
);


CREATE TABLE Comments(
  comment_id int4 AUTO_INCREMENT,
  user_id int4,
  comment_date DATE,
  comment_text TEXT,
  picture_id int4,
  CONSTRAINT cp_fk FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE,
  CONSTRAINT comments_pk PRIMARY KEY (comment_id)
);




CREATE TABLE Befriend_With(
  userA INT4,
  userB INT4,
  CONSTRAINT userA_fk FOREIGN KEY (userA) REFERENCES Users(user_id) ON DELETE CASCADE,
  CONSTRAINT userB_fk FOREIGN KEY (userB) REFERENCES Users(user_id) ON DELETE CASCADE,
  CONSTRAINT befriend_with_pk PRIMARY KEY (userA, userB)
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Users(email,password,gender) VALUES ('test3@bu.edu', 'test', 1);
INSERT INTO Comments(user_id, comment_date, comment_text) VALUES (0, CURRENT_DATE, "HAVE A TRY");

SELECT * FROM Users;
SELECT * FROM Comments;
show tables;


