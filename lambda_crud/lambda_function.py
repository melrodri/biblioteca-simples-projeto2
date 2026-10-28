"""CRUD pequeno de autores e livros para API Gateway HTTP API (payload 2.0)."""

import json
import os
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import unquote_plus

import boto3
import pymysql
from botocore.config import Config
from pymysql.cursors import DictCursor


def resposta(status, dados):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(dados, ensure_ascii=False),
    }


def conectar():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        port=int(os.environ.get("DB_PORT", "3306")),
        connect_timeout=5,
        cursorclass=DictCursor,
        autocommit=False,
        charset="utf8mb4",
    )


def inteiro_positivo(valor):
    if isinstance(valor, bool):
        return None
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None
    return numero if numero > 0 and str(valor).strip() == str(numero) else None


def validar_autor(dados):
    nome = dados.get("nome")
    if not isinstance(nome, str) or not nome.strip() or len(nome.strip()) > 150:
        return None, "Nome deve ter entre 1 e 150 caracteres."
    return {"nome": nome.strip()}, None


def validar_livro(dados):
    titulo = dados.get("titulo")
    ano = inteiro_positivo(dados.get("ano_publicacao"))
    autor_id = inteiro_positivo(dados.get("autor_id"))
    ano_atual = datetime.now(timezone.utc).year
    if not isinstance(titulo, str) or not titulo.strip() or len(titulo.strip()) > 200:
        return None, "Título deve ter entre 1 e 200 caracteres."
    if ano is None or ano > ano_atual:
        return None, f"Ano deve ser um inteiro entre 1 e {ano_atual}."
    if autor_id is None:
        return None, "Selecione um autor válido."
    return {"titulo": titulo.strip(), "ano_publicacao": ano, "autor_id": autor_id}, None


def ler_corpo(evento):
    try:
        dados = json.loads(evento.get("body") or "{}")
    except (TypeError, ValueError):
        return None
    return dados if isinstance(dados, dict) else None


def buscar(cursor, entidade, identificador):
    if entidade == "autores":
        cursor.execute("SELECT id, nome FROM autor WHERE id = %s", (identificador,))
    else:
        cursor.execute(
            "SELECT l.id, l.titulo, l.ano_publicacao, l.autor_id, a.nome AS autor_nome "
            "FROM livro l JOIN autor a ON a.id = l.autor_id WHERE l.id = %s",
            (identificador,),
        )
    return cursor.fetchone()


def iniciar_banco(cursor):
    # Invocação direta no console da Lambda: {"action":"init_db"}.
    # Uma requisição HTTP nunca entra neste ramo.
    caminho = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(caminho, encoding="utf-8") as arquivo:
        comandos = [parte.strip() for parte in arquivo.read().split(";") if "CREATE TABLE" in parte]
    for comando in comandos:
        cursor.execute(comando[comando.index("CREATE TABLE"):])
    return {"mensagem": "Tabelas autor, livro e capa prontas."}


def s3():
    return boto3.client("s3", region_name="us-east-1", config=Config(signature_version="s3v4"))


def processar_capa(evento):
    """Um upload em capas/ grava tamanho e tipo da imagem no RDS."""
    bucket_esperado = os.environ["CAPAS_BUCKET"]
    for registro in evento["Records"]:
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


def rota_aula4(evento, partes, metodo):
    """Retorna uma resposta para as três rotas novas ou None para o CRUD."""
    if partes == ["relatorios", "livros-por-autor"] and metodo == "GET":
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT a.id AS autor_id, a.nome, COUNT(l.id) AS quantidade_livros "
                    "FROM autor a LEFT JOIN livro l ON l.autor_id = a.id "
                    "GROUP BY a.id, a.nome ORDER BY a.nome"
                )
                return resposta(200, cursor.fetchall())

    if len(partes) == 4 and partes[0] == "livros" and partes[2] == "capa":
        livro_id = inteiro_positivo(partes[1])
        if livro_id is None:
            return resposta(400, {"erro": "ID inválido."})
        if partes[3] == "url-upload" and metodo == "POST":
            dados = ler_corpo(evento)
            tipo = dados.get("tipo_conteudo") if dados else None
            if tipo not in ("image/png", "image/jpeg"):
                return resposta(400, {"erro": "Use uma imagem PNG ou JPEG."})
            with conectar() as conexao:
                with conexao.cursor() as cursor:
                    cursor.execute("SELECT id FROM livro WHERE id = %s", (livro_id,))
                    if not cursor.fetchone():
                        return resposta(404, {"erro": "Livro não encontrado."})
            extensao = "png" if tipo == "image/png" else "jpg"
            chave = f"capas/{livro_id}/{uuid.uuid4()}.{extensao}"
            url = s3().generate_presigned_url(
                "put_object",
                Params={"Bucket": os.environ["CAPAS_BUCKET"], "Key": chave, "ContentType": tipo},
                ExpiresIn=300,
            )
            return resposta(200, {"url": url, "chave": chave})
    if len(partes) == 3 and partes[0] == "livros" and partes[2] == "capa" and metodo == "GET":
        livro_id = inteiro_positivo(partes[1])
        if livro_id is None:
            return resposta(400, {"erro": "ID inválido."})
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT s3_chave, tamanho_bytes, tipo_conteudo FROM capa WHERE livro_id = %s",
                    (livro_id,),
                )
                capa = cursor.fetchone()
        if not capa:
            return resposta(404, {"erro": "Capa não encontrada."})
        capa["url"] = s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": os.environ["CAPAS_BUCKET"], "Key": capa["s3_chave"]},
            ExpiresIn=300,
        )
        return resposta(200, capa)
    return None


def lambda_handler(event, context):
    if "Records" in event:
        try:
            return processar_capa(event)
        except (pymysql.MySQLError, OSError, KeyError, ValueError):
            print("Falha ao processar capa; verificar evento e configuração.")
            raise
    direto = "requestContext" not in event
    if direto and event.get("action") != "init_db":
        return resposta(400, {"erro": "Evento de teste inválido."})
    if not direto:
        metodo = event.get("requestContext", {}).get("http", {}).get("method", "")
        partes = [parte for parte in (event.get("rawPath") or "").strip("/").split("/") if parte]
        try:
            resposta_extra = rota_aula4(event, partes, metodo)
            if resposta_extra is not None:
                return resposta_extra
        except (pymysql.MySQLError, OSError, KeyError, ValueError):
            print("Falha na rota da Aula 4; conferir CloudWatch.")
            return resposta(500, {"erro": "Erro interno."})
        if len(partes) not in (1, 2) or partes[0] not in ("autores", "livros"):
            return resposta(404, {"erro": "Rota não encontrada."})
        entidade = partes[0]
        identificador = inteiro_positivo(partes[1]) if len(partes) == 2 else None
        if len(partes) == 2 and identificador is None:
            return resposta(400, {"erro": "ID inválido."})
        if metodo not in ("GET", "POST", "PUT", "DELETE"):
            return resposta(405, {"erro": "Método não permitido."})
        if (metodo == "POST" and identificador is not None) or (
            metodo in ("PUT", "DELETE") and identificador is None
        ):
            return resposta(405, {"erro": "Método não permitido nesta rota."})
        dados = ler_corpo(event) if metodo in ("POST", "PUT") else None
        if metodo in ("POST", "PUT") and dados is None:
            return resposta(400, {"erro": "Envie um objeto JSON válido."})
        if metodo in ("POST", "PUT"):
            dados, erro = (validar_autor(dados) if entidade == "autores" else validar_livro(dados))
            if erro:
                return resposta(400, {"erro": erro})

    try:
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                if direto:
                    resultado = iniciar_banco(cursor)
                    conexao.commit()
                    return resposta(200, resultado)

                if metodo == "GET" and identificador is not None:
                    item = buscar(cursor, entidade, identificador)
                    return resposta(200, item) if item else resposta(404, {"erro": "Registro não encontrado."})

                if metodo == "GET":
                    if entidade == "autores":
                        cursor.execute("SELECT id, nome FROM autor ORDER BY nome, id")
                    else:
                        cursor.execute(
                            "SELECT l.id, l.titulo, l.ano_publicacao, l.autor_id, a.nome AS autor_nome "
                            "FROM livro l JOIN autor a ON a.id = l.autor_id ORDER BY l.titulo, l.id"
                        )
                    return resposta(200, cursor.fetchall())

                if metodo == "POST":
                    if entidade == "autores":
                        cursor.execute("INSERT INTO autor (nome) VALUES (%s)", (dados["nome"],))
                    else:
                        cursor.execute("SELECT id FROM autor WHERE id = %s", (dados["autor_id"],))
                        if not cursor.fetchone():
                            return resposta(400, {"erro": "Autor não encontrado."})
                        cursor.execute(
                            "INSERT INTO livro (titulo, ano_publicacao, autor_id) VALUES (%s, %s, %s)",
                            (dados["titulo"], dados["ano_publicacao"], dados["autor_id"]),
                        )
                    item = buscar(cursor, entidade, cursor.lastrowid)
                    conexao.commit()
                    return resposta(201, item)

                if not buscar(cursor, entidade, identificador):
                    return resposta(404, {"erro": "Registro não encontrado."})

                if metodo == "PUT":
                    if entidade == "autores":
                        cursor.execute("UPDATE autor SET nome = %s WHERE id = %s", (dados["nome"], identificador))
                    else:
                        cursor.execute("SELECT id FROM autor WHERE id = %s", (dados["autor_id"],))
                        if not cursor.fetchone():
                            return resposta(400, {"erro": "Autor não encontrado."})
                        cursor.execute(
                            "UPDATE livro SET titulo = %s, ano_publicacao = %s, autor_id = %s WHERE id = %s",
                            (dados["titulo"], dados["ano_publicacao"], dados["autor_id"], identificador),
                        )
                    item = buscar(cursor, entidade, identificador)
                    conexao.commit()
                    return resposta(200, item)

                if entidade == "autores":
                    cursor.execute("SELECT COUNT(*) AS total FROM livro WHERE autor_id = %s", (identificador,))
                    if cursor.fetchone()["total"]:
                        return resposta(409, {"erro": "Exclua os livros deste autor antes."})
                    cursor.execute("DELETE FROM autor WHERE id = %s", (identificador,))
                else:
                    cursor.execute("DELETE FROM livro WHERE id = %s", (identificador,))
                conexao.commit()
                return resposta(200, {"mensagem": "Registro excluído."})
    except (pymysql.MySQLError, OSError, KeyError, ValueError):
        # Detalhes de conexão e credenciais não são devolvidos ao navegador.
        print("Falha no acesso ao banco; confira configuração e CloudWatch.")
        return resposta(500, {"erro": "Erro interno. Confira a configuração do banco."})
