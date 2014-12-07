DROP TABLE IF EXISTS paste;
CREATE TABLE paste (  
  id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
  uuid BINARY(16) NOT NULL,
  digest BINARY(20) NOT NULL,
  content MEDIUMBLOB NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (digest),
  UNIQUE KEY (uuid)
)
ENGINE = InnoDB;

DELIMITER @@

DROP PROCEDURE IF EXISTS insert_paste@@
CREATE PROCEDURE insert_paste (
  p_uuid BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_id MEDIUMINT UNSIGNED
)
BEGIN
  START TRANSACTION;
  INSERT paste (uuid, digest, content)
  VALUES (p_uuid, UNHEX(SHA1(p_content)), p_content);
  SELECT last_insert_id() INTO p_id;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS put_paste@@
CREATE PROCEDURE put_paste (
  p_uuid BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_id MEDIUMINT UNSIGNED
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

DROP PROCEDURE IF EXISTS delete_paste@@
CREATE PROCEDURE delete_paste (
  p_uuid BINARY(16),
  OUT p_id MEDIUMINT UNSIGNED
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

DROP PROCEDURE IF EXISTS get_stats@@
CREATE PROCEDURE get_stats (
  OUT p_count INT,
  OUT p_length INT
)
BEGIN
  SELECT COUNT(*), SUM(LENGTH(content)) INTO p_count, p_length
  FROM paste;
END;
@@

DROP PROCEDURE IF EXISTS get_digest@@
CREATE PROCEDURE get_digest (
  p_digest BINARY(20),
  OUT p_id MEDIUMINT UNSIGNED
)
BEGIN
  SELECT id INTO p_id
  FROM paste
  WHERE digest = p_digest;
END;
@@

DROP PROCEDURE IF EXISTS get_content@@
CREATE PROCEDURE get_content (
  p_id MEDIUMINT UNSIGNED,
  OUT p_content MEDIUMBLOB
)
BEGIN
  SELECT content INTO p_content
  FROM paste
  WHERE id = p_id;
END;
@@
