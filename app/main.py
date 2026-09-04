import http.server
import os
import socketserver
import threading
import time
import webbrowser
from config import PASTA_RAIZ, PORTA
from mapa import gerar_mapa
from simulador import inicializar_sensores_fixos, loop_simulacao


def main():
  print("1/3 - Distribuindo sensores fixos pelas regiões de Santo André...")
  sensores = inicializar_sensores_fixos()

  print("2/3 - Gerando mapa interativo...")
  gerar_mapa()

  print("3/3 - Iniciando thread paralela de simulação...")
  t = threading.Thread(target=loop_simulacao, args=(sensores,), daemon=True)
  t.start()

  # Breve pausa para garantir o primeiro arquivo JSON gravado
  time.sleep(0.5)

  os.chdir(PASTA_RAIZ)
  handler = http.server.SimpleHTTPRequestHandler
  handler.log_message = lambda self, format, *args: None

  with socketserver.TCPServer(("", PORTA), handler) as httpd:
    url = f"http://localhost:{PORTA}/mapa_santo_andre.html"
    print(f"\n✅ Painel operacional rodando em: {url}")
    print("Pressione Ctrl+C para encerrar.\n")
    webbrowser.open(url)
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      print("\nServidor encerrado com sucesso.")


if __name__ == "__main__":
  main()