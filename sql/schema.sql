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

-- A capa atual de cada livro. O evento do S3 preenche esta tabela.
CREATE TABLE IF NOT EXISTS capa (
    livro_id BIGINT UNSIGNED NOT NULL,
    s3_chave VARCHAR(255) NOT NULL,
    tamanho_bytes INT UNSIGNED NOT NULL,
    tipo_conteudo VARCHAR(30) NOT NULL,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (livro_id),
    UNIQUE KEY uq_capa_chave (s3_chave),
    CONSTRAINT fk_capa_livro FOREIGN KEY (livro_id)
        REFERENCES livro(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
