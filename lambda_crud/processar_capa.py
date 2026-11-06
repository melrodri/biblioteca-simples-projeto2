"""Processa as notificações de criação de capas no S3."""

import os
import re
from urllib.parse import unquote_plus

from lambda_function import conectar, s3


def lambda_handler(evento, contexto):
    """Um upload em capas/ grava tamanho e tipo da imagem no RDS."""
    bucket_esperado = os.environ["CAPAS_BUCKET"]
    for registro in evento.get("Records", []):
        bucket = registro["s3"]["bucket"]["name"]
        chave = unquote_plus(registro["s3"]["object"]["key"])
        if bucket != bucket_esperado:
            continue
        caminho = re.fullmatch(r"capas/([1-9][0-9]*)/[0-9a-f-]+\.(png|jpg)", chave)
        if not caminho:
            print("Arquivo ignorado fora do padrão de capas.")
            continue
        info = s3().head_object(Bucket=bucket, Key=chave)
        tipo = info.get("ContentType")
        tamanho = info.get("ContentLength", 0)
        if tipo not in ("image/png", "image/jpeg") or not 0 < tamanho <= 5 * 1024 * 1024:
            print("Capa ignorada: tipo ou tamanho inválido.")
            continue
        livro_id = int(caminho.group(1))
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT id FROM livro WHERE id = %s", (livro_id,))
                if not cursor.fetchone():
                    print("Capa ignorada: livro não existe.")
                    continue
                cursor.execute(
                    "INSERT INTO capa (livro_id, s3_chave, tamanho_bytes, tipo_conteudo) "
                    "VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE "
                    "s3_chave = VALUES(s3_chave), tamanho_bytes = VALUES(tamanho_bytes), "
                    "tipo_conteudo = VALUES(tipo_conteudo), atualizado_em = CURRENT_TIMESTAMP",
                    (livro_id, chave, tamanho, tipo),
                )
                conexao.commit()
        print(f"Capa processada: livro {livro_id}, {tamanho} bytes.")
    return {"mensagem": "Evento S3 processado."}
