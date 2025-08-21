import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Adicionar a pasta raiz ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar do local correto
from src.extensions import db
from src.models.user import User
from src.models.payment import Payment
from src.routes.user import user_bp
from src.routes.pix import pix_bp

# Carregar variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()


# Função para buscar segredos do Google Secret Manager
def get_secret(project_id, secret_id, version_id="latest"):
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(
            f"AVISO: Não foi possível buscar o segredo '{secret_id}' do Secret Manager. Usando fallback. Erro: {e}"
        )
        return None


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
# --- Lógica de Configuração ---
# Verifica se a aplicação está rodando no Google App Engine
is_production = os.environ.get("GAE_ENV") == "standard"
if is_production:
    # --- Ambiente de Produção (Google App Engine) ---
    project_id = os.environ.get(
        "GCP_PROJECT"
    )  # GAE fornece essa variável automaticamente
    # Busca as configurações do Secret Manager
    db_url = get_secret(project_id, "DATABASE_URL")
    secret_key = get_secret(project_id, "SECRET_KEY")
    master_key = get_secret(project_id, "MASTER_PAGAMENTOS_SECRET_KEY")
    pix_api_key = get_secret(project_id, "PIX_API_KEY")
    # Garante que as configurações essenciais foram carregadas
    if not all([db_url, secret_key]):
        raise RuntimeError(
            "Falha ao carregar segredos essenciais (DATABASE_URL, SECRET_KEY) do Secret Manager."
        )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SECRET_KEY"] = secret_key
    # Define as outras chaves como variáveis de ambiente para o restante do app usar
    os.environ["MASTER_PAGAMENTOS_SECRET_KEY"] = master_key
    os.environ["PIX_API_KEY"] = pix_api_key
else:
    # --- Ambiente Local ---
    # Cria o caminho para o banco de dados local na pasta 'database'
    db_dir = os.path.join(os.path.dirname(__file__), "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db_path = os.path.join(db_dir, "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "uma_chave_local_de_teste_super_segura"
    )
    # IMPORTANTE: Garante que as variáveis do .env estejam disponíveis para o app
    # Se as variáveis não existirem no ambiente, use valores padrão para desenvolvimento
    if not os.getenv("MASTER_PAGAMENTOS_SECRET_KEY"):
        print(
            "AVISO: MASTER_PAGAMENTOS_SECRET_KEY não encontrada no .env, usando valor padrão para desenvolvimento"
        )
        os.environ["MASTER_PAGAMENTOS_SECRET_KEY"] = "chave_master_desenvolvimento"
    if not os.getenv("PIX_API_KEY"):
        print(
            "AVISO: PIX_API_KEY não encontrada no .env, usando valor padrão para desenvolvimento"
        )
        os.environ["PIX_API_KEY"] = "chave_pix_desenvolvimento"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Configurar CORS
CORS(app)
# Registrar blueprints
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(pix_bp, url_prefix="/api/pix")
# Inicializar o banco de dados
db.init_app(app)
# Criar as tabelas do banco de dados
with app.app_context():
    db.create_all()
    print("Tabelas do banco de dados criadas/atualizadas")


@app.route("/")
def index():
    return "PIX API is running"


@app.route("/health")
def health_check():
    return {"status": "healthy", "service": "PIX API"}, 200


if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host="0.0.0.0", port=5000, debug=True)
