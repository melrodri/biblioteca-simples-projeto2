"""CRUD pequeno de autores e livros para API Gateway HTTP API (payload 2.0)."""

import json
import os
from datetime import datetime, timezone

import pymysql
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
    return {"mensagem": "Tabelas autor e livro prontas."}


def lambda_handler(event, context):
    direto = "requestContext" not in event
    if direto and event.get("action") != "init_db":
        return resposta(400, {"erro": "Evento de teste inválido."})
    if not direto:
        metodo = event.get("requestContext", {}).get("http", {}).get("method", "")
        partes = [parte for parte in (event.get("rawPath") or "").strip("/").split("/") if parte]
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
