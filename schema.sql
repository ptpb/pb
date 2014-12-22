/*
BEGIN PASTE SCHEMA
*/

DROP TABLE IF EXISTS paste;
CREATE TABLE paste (
  id MEDIUMINT NOT NULL AUTO_INCREMENT,
  uuid BINARY(16) NOT NULL,
  digest BINARY(20) NOT NULL,
  content MEDIUMBLOB NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (digest),
  UNIQUE KEY (uuid)
)
ENGINE = InnoDB;

DELIMITER @@

DROP PROCEDURE IF EXISTS paste_insert@@
CREATE PROCEDURE paste_insert (
  p_uuid BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_id MEDIUMINT
)
BEGIN
  START TRANSACTION;
  INSERT paste (uuid, digest, content)
  VALUES (p_uuid, UNHEX(SHA1(p_content)), p_content);
  SELECT last_insert_id() INTO p_id;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS paste_put@@
CREATE PROCEDURE paste_put (
  p_uuid BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_id MEDIUMINT
)
BEGIN
  START TRANSACTION;
  SELECT id INTO p_id
  FROM paste
  WHERE uuid = p_uuid;
  UPDATE paste
  SET digest = UNHEX(SHA1(p_content)), content = p_content
  WHERE uuid = p_uuid;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS paste_delete@@
CREATE PROCEDURE paste_delete (
  p_uuid BINARY(16),
  OUT p_id MEDIUMINT
)
BEGIN
  START TRANSACTION;
  SELECT id INTO p_id
  FROM paste
  WHERE uuid = p_uuid;
  DELETE
  FROM paste
  WHERE uuid = p_uuid;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS paste_get_stats@@
CREATE PROCEDURE paste_get_stats (
  OUT p_count INT,
  OUT p_length INT
)
BEGIN
  SELECT COUNT(*), SUM(LENGTH(content)) INTO p_count, p_length
  FROM paste;
END;
@@

DROP PROCEDURE IF EXISTS paste_get_digest@@
CREATE PROCEDURE paste_get_digest (
  p_digest BINARY(20),
  OUT p_id MEDIUMINT
)
BEGIN
  SELECT id INTO p_id
  FROM paste
  WHERE digest = p_digest;
END;
@@

DROP PROCEDURE IF EXISTS paste_get_content@@
CREATE PROCEDURE paste_get_content (
  p_id MEDIUMINT,
  OUT p_content MEDIUMBLOB
)
BEGIN
  SELECT content INTO p_content
  FROM paste
  WHERE id = p_id;
END;
@@

DROP PROCEDURE IF EXISTS paste_get_content_digest@@
CREATE PROCEDURE paste_get_content_digest (
  p_digest BINARY(20),
  OUT p_content MEDIUMBLOB
)
BEGIN
  SELECT content INTO p_content
  FROM paste
  WHERE digest = p_digest;
END;
@@

/*
END PASTE SCHEMA
*/

/*
BEGIN URL SCHEMA
*/

DELIMITER ;

DROP TABLE IF EXISTS url;
CREATE TABLE url (
  id MEDIUMINT NOT NULL AUTO_INCREMENT,
  digest BINARY(20) NOT NULL,
  content BLOB NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (digest)
)
ENGINE = InnoDB;

DELIMITER @@

DROP PROCEDURE IF EXISTS url_insert@@
CREATE PROCEDURE url_insert (
  p_content BLOB,
  OUT p_id MEDIUMINT
)
BEGIN
  START TRANSACTION;
  INSERT url (digest, content)
  VALUES (UNHEX(SHA1(p_content)), p_content);
  SELECT last_insert_id() INTO p_id;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS url_get_digest@@
CREATE PROCEDURE url_get_digest (
  p_digest BINARY(20),
  OUT p_id MEDIUMINT
)
BEGIN
  SELECT id INTO p_id
  FROM url
  WHERE digest = p_digest;
END;
@@

DROP PROCEDURE IF EXISTS url_get_content@@
CREATE PROCEDURE url_get_content (
  p_id MEDIUMINT,
  OUT p_content BLOB
)
BEGIN
  SELECT content INTO p_content
  FROM url
  WHERE id = p_id;
END;
@@

/*
END URL SCHEMA
*/
