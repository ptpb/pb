/*
BEGIN PASTE SCHEMA
*/
DELIMITER ;

DROP TABLE IF EXISTS paste;
CREATE TABLE paste (
  id MEDIUMINT NOT NULL AUTO_INCREMENT,
  secret BINARY(16) NOT NULL,
  digest BINARY(20) NOT NULL,
  content MEDIUMBLOB NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (secret),
  UNIQUE KEY (digest)
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS private;
CREATE TABLE private (
  digest BINARY(20) NOT NULL,
  secret BINARY(16) NOT NULL,
  content BLOB NOT NULL,
  PRIMARY KEY (digest),
  UNIQUE KEY (secret)
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS vanity;
CREATE TABLE vanity (
  label TINYBLOB NOT NULL,
  digest BINARY(20) NOT NULL,
  secret BINARY(16) NOT NULL,
  content BLOB NOT NULL,
  PRIMARY KEY (label(39)),
  UNIQUE KEY (digest),
  UNIQUE KEY (secret)
)
ENGINE = InnoDB;

DELIMITER @@

DROP PROCEDURE IF EXISTS paste_insert@@
CREATE PROCEDURE paste_insert (
  p_secret BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_id MEDIUMINT
)
BEGIN
  START TRANSACTION;
  INSERT paste (secret, digest, content)
  VALUES (p_secret, UNHEX(SHA1(p_content)), p_content);
  SELECT last_insert_id() INTO p_id;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS paste_insert_private@@
CREATE PROCEDURE paste_insert_private (
  p_secret BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_digest BINARY(20)
)
BEGIN
  START TRANSACTION;
  INSERT private (secret, digest, content)
  VALUES (p_secret, @d:=UNHEX(SHA1(p_content)), p_content);
  SELECT @d INTO p_digest;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS paste_insert_vanity@@
CREATE PROCEDURE paste_insert_vanity (
  p_label TINYBLOB,
  p_secret BINARY(16),
  p_content MEDIUMBLOB
)
BEGIN
  INSERT vanity (label, digest, secret, content)
  VALUES (p_label, UNHEX(SHA1(p_content)), p_secret, p_content);
END;
@@

DROP PROCEDURE IF EXISTS paste_put@@
CREATE PROCEDURE paste_put (
  p_secret BINARY(16),
  p_content MEDIUMBLOB,
  OUT p_id MEDIUMINT,
  OUT p_digest BINARY(20),
  OUT p_label TINYBLOB
)
BEGIN
  START TRANSACTION;
  UPDATE paste
  SET digest = UNHEX(SHA1(p_content)), content = p_content
  WHERE secret = p_secret;
  UPDATE private
  SET digest = UNHEX(SHA1(p_content)), content = p_content
  WHERE secret = p_secret;
  UPDATE private
  SET digest = UNHEX(SHA1(p_content)), content = p_content
  WHERE secret = p_secret;
  /* .. */
  SELECT id INTO p_id
  FROM paste
  WHERE secret = p_secret;
  SELECT digest INTO p_digest
  FROM private
  WHERE secret = p_secret;
  SELECT label INTO p_label
  FROM vanity
  WHERE secret = p_secret;
  COMMIT;
END;
@@

DROP PROCEDURE IF EXISTS paste_delete@@
CREATE PROCEDURE paste_delete (
  p_secret BINARY(16),
  OUT p_id MEDIUMINT,
  OUT p_digest BINARY(20),
  OUT p_label TINYBLOB
)
BEGIN
  START TRANSACTION;
  SELECT id INTO p_id
  FROM paste
  WHERE secret = p_secret;
  SELECT digest INTO p_digest
  FROM private
  WHERE secret = p_secret;
  SELECT label INTO p_label
  FROM vanity
  WHERE secret = p_secret;
  /* .. */
  DELETE
  FROM paste
  WHERE secret = p_secret;
  DELETE
  FROM private
  WHERE secret = p_secret;
  DELETE
  FROM vanity
  WHERE secret = p_secret;
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
  FROM (
    SELECT content FROM paste
    UNION
    SELECT content FROM private
    UNION
    SELECT content FROM vanity
  ) AS p;
END;
@@

DROP PROCEDURE IF EXISTS paste_get_digest@@
CREATE PROCEDURE paste_get_digest (
  p_digest BINARY(20),
  OUT p_id MEDIUMINT,
  OUT p_label TINYBLOB,
  OUT p_exists BIT(1)
)
BEGIN
  SELECT id INTO p_id
  FROM paste
  WHERE digest = p_digest;
  SELECT label INTO p_label
  FROM vanity
  WHERE digest = p_digest;
  SELECT 1 INTO p_exists
  FROM private
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
  SELECT p.content INTO p_content
  FROM (
    SELECT content
    FROM paste
    WHERE digest = p_digest
    UNION
    SELECT content
    FROM private
    WHERE digest = p_digest
    UNION
    SELECT content
    FROM vanity
    WHERE digest = p_digest
  ) AS p;
END;
@@

DROP PROCEDURE IF EXISTS paste_get_content_vanity@@
CREATE PROCEDURE paste_get_content_vanity (
  p_label TINYBLOB,
  OUT p_content MEDIUMBLOB
)
BEGIN
  SELECT content INTO p_content
  FROM vanity
  WHERE label = p_label;
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
