import os

def load_dotenv():
    # Encontra o arquivo .env no diretório raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(base_dir, ".env")
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

API_BASE_URL = os.getenv("ALIA_API_BASE_URL", "")
API_KEY = os.getenv("ALIA_API_KEY", "")
MODEL_ID = os.getenv("ALIA_MODEL_ID", "")

# Validação básica
if not API_BASE_URL or not API_KEY or not MODEL_ID:
    print("[AVISO] Configurações de API ausentes ou incompletas no arquivo .env!")
