-- TP 1) Create the tables in the database
-- Exécuté automatiquement au démarrage (spring.sql.init.mode=always).
DROP TABLE IF EXISTS artists;

CREATE TABLE artists (
    id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    name   VARCHAR(100) NOT NULL,
    domain VARCHAR(50)  NOT NULL   -- PAINTER, MUSICIAN, PHOTOGRAPHER, ...
);
