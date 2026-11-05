from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone

client = MongoClient("mongodb+srv://UNIFSA:unifsa@cluster0.k77h2jw.mongodb.net/")
bd = client["sociedade"]

contas = bd["usuarios"]
posts = bd["posts"]

try:
    client.admin.command("ping")
    print("Conectado com Sucesso!")

except Exception as e:
    raise Exception(f"Ocorreu um erro: {e}")

def get_usuario(usuario):
    return contas.find_one({"usuario": usuario})

def criar_usuario(usuario: str, senha: str) -> bool:

    if contas.find_one({"usuario": usuario}):
        return False
    
    contas.insert_one({
        "usuario": usuario,
        "senha": senha,  # em produção: hash (bcrypt)
        "amigos": [],
        "criado_em": datetime.now()
    })

    return True

def login_usuario(usuario: str, senha: str):
    return contas.find_one({"usuario": usuario, "senha": senha})



def criar_post(usuario: str, texto: str):
    posts.insert_one({
        "autor": usuario,
        "texto": texto,
        "criado_em": datetime.now(timezone.utc),
        "likes": []
    })

def get_feed() -> list:
    return list(posts.find().sort("criado_em", -1).limit(50))

def get_post_usuario(usuario):
    return list(posts.find({"autor":usuario}).sort("criado_em", -1))

def curtir_post(post_id, usuario: str):
    posts.update_one(
        {"_id": post_id},
        {"$addToSet": {"likes": usuario}}
    )


def verificar_amizade(usuario_logado, usuario_perfil):
    conta = contas.find_one({"usuario": usuario_logado})
    amigos = conta.get("amigos", []) if conta else []
    return usuario_perfil in amigos

def adicionar_amigo(usuario_logado, usuario_perfil):
    if usuario_logado == usuario_perfil:
        raise Exception("Você não pode adicionar a si mesmo como amigo.")

    existe = contas.find_one({"usuario": usuario_perfil})
    if not existe:
        raise Exception("Usuário não encontrado.")

    contas.update_one(
        {"usuario": usuario_logado},
        {"$addToSet": {"amigos": usuario_perfil}}
    )