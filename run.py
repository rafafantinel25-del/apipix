import os
from dotenv import load_dotenv
from flask import Flask
import redis
from waitress import serve
from src.routes import pix_bp, user_bp, health_bp
from src.extensions import db, limiter

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configurações do banco de dados com fallback seguro para SQLite
    db_path = os.path.join(os.getcwd(), 'database')
    os.makedirs(db_path, exist_ok=True)
    use_mysql = os.getenv('USE_MYSQL') in ('1', 'true', 'yes', 'on')
    if use_mysql and os.getenv('DATABASE_URL'):
        db_uri = os.getenv('DATABASE_URL')
    else:
        db_uri = f'sqlite:///{os.path.join(db_path, "app.db")}'
    print(f"Usando banco de dados: {db_uri}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,
        'max_overflow': 40,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Inicializar extensões
    db.init_app(app)
    limiter.init_app(app)
    
    # Configurar Redis para cache
    try:
        redis_password = os.getenv('REDIS_PASSWORD', None)
        if redis_password == '':
            redis_password = None
            
        app.redis_client = redis.StrictRedis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=redis_password,
            decode_responses=True
        )
        # Testar conexão com Redis
        app.redis_client.ping()
        print("Redis conectado com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar com Redis: {e}")
        # Se Redis não estiver disponível, usar um cliente dummy
        class DummyRedis:
            def get(self, key):
                return None
            def setex(self, key, time, value):
                pass
            def ping(self):
                return True
        app.redis_client = DummyRedis()
    
    # Registrar blueprints
    app.register_blueprint(pix_bp, url_prefix='/pix')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(health_bp)  # Adicionar o blueprint de health
    
    # Criar tabelas do banco de dados
    with app.app_context():
        try:
            db.create_all()
            print("Tabelas criadas com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
    
    return app

app = create_app()

if __name__ == '__main__':
    print("Iniciando servidor...")
    # Configurações do servidor Waitress
    serve(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        threads=60,
        connection_limit=120,
        channel_timeout=30,
        expose_tracebacks=False
    )