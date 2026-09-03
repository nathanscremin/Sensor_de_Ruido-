import os

PASTA_RAIZ = os.path.dirname(os.path.abspath(__file__))

# Arquivos
CAMINHO_GEOJSON = os.path.join(PASTA_RAIZ, "santo_andre_dashboard.geojson")
ARQUIVO_JSON = os.path.join(PASTA_RAIZ, "dados_sensores.json")
ARQUIVO_HISTORICO = os.path.join(PASTA_RAIZ, "historico_sensores.json")
ARQUIVO_HTML = os.path.join(PASTA_RAIZ, "mapa_santo_andre.html")

# Servidor Local
PORTA = 8000

# Cotas de distribuição dos sensores
COTAS_DISTRITAIS = {"Santo André": 35, "Capuava": 10, "Paranapiacaba": 15}

# Frequência de telemetria ao vivo (segundos)
INTERVALO_COLETA = 1

# Janela de agregação do histórico em minutos (Use 1 para testar agora, 5 para produção)
INTERVALO_HISTORICO_MINUTOS = 1