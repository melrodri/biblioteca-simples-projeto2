-- Biblioteca Simples: esquema da Aula 3 (MySQL no Amazon RDS).
-- Execute no banco indicado por DB_NAME. A repetição é segura.

CREATE TABLE IF NOT EXISTS autor (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS livro (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    ano_publicacao INT NOT NULL,
    autor_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    KEY idx_livro_autor (autor_id),
    CONSTRAINT fk_livro_autor FOREIGN KEY (autor_id)
        REFERENCES autor(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
