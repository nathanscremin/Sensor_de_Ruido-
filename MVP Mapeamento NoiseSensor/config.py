import os

PASTA_RAIZ = os.path.dirname(os.path.abspath(__file__))

# Arquivos
CAMINHO_GEOJSON = os.path.join(PASTA_RAIZ, "santo_andre_dashboard.geojson")
ARQUIVO_JSON = os.path.join(PASTA_RAIZ, "dados_sensores.json")
ARQUIVO_HTML = os.path.join(PASTA_RAIZ, "mapa_santo_andre.html")

# Servidor Local
PORTA = 8000

# Cotas de distribuição dos sensores
COTAS_DISTRITAIS = {"Santo André": 35, "Capuava": 10, "Paranapiacaba": 15}

# Intervalo de amostragem (segundos)
INTERVALO_COLETA = 1