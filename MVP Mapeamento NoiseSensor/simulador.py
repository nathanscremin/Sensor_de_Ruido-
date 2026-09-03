from datetime import datetime
import json
import math
import os
import random
import time
from config import (
    ARQUIVO_HISTORICO,
    ARQUIVO_JSON,
    CAMINHO_GEOJSON,
    COTAS_DISTRITAIS,
    INTERVALO_COLETA,
    INTERVALO_HISTORICO_MINUTOS,
)


def ponto_dentro_poligono(x, y, poligono):
  n = len(poligono)
  dentro = False
  p1x, p1y = poligono[0]
  for i in range(n + 1):
    p2x, p2y = poligono[i % n]
    if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
      if p1y != p2y:
        x_inter = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
      if p1x == p2x or x <= x_inter:
        dentro = not dentro
    p1x, p1y = p2x, p2y
  return dentro


def inicializar_sensores_fixos():
  with open(CAMINHO_GEOJSON, "r", encoding="utf-8") as f:
    geo_data = json.load(f)

  bairros = geo_data["features"]
  distritos = {"Santo André": [], "Capuava": [], "Paranapiacaba": []}

  for b in bairros:
    dist = b["properties"].get("NM_DIST", "Santo André")
    if dist in distritos:
      distritos[dist].append(b)
    else:
      distritos["Santo André"].append(b)

  sensores = []
  sensor_id = 1

  for nome_dist, qtd_alvo in COTAS_DISTRITAIS.items():
    lista_bairros = distritos[nome_dist]
    if not lista_bairros:
      continue
    random.shuffle(lista_bairros)

    criados_dist = 0
    idx = 0
    while criados_dist < qtd_alvo:
      bairro_atual = lista_bairros[idx % len(lista_bairros)]
      idx += 1

      coords = bairro_atual["geometry"]["coordinates"][0]
      nome_bairro = bairro_atual["properties"].get("NM_BAIRRO", "Região")

      lons = [pt[0] for pt in coords]
      lats = [pt[1] for pt in coords]

      for _ in range(100):
        rand_lon = random.uniform(min(lons), max(lons))
        rand_lat = random.uniform(min(lats), max(lats))
        if ponto_dentro_poligono(rand_lon, rand_lat, coords):
          sensores.append({
              "id": f"NS-{sensor_id:03d}",
              "bairro": nome_bairro,
              "distrito": nome_dist,
              "latitude": round(rand_lat, 6),
              "longitude": round(rand_lon, 6),
              "potencia_nominal_w": random.uniform(3.5, 5.0),
              "consumo_acumulado_kwh": round(random.uniform(10.0, 50.0), 4),
          })
          sensor_id += 1
          criados_dist += 1
          break

  return sensores


def calcular_leq(valores_decibeis):
  """Calcula a média energética oficial (Leq) de uma lista de decibéis."""
  if not valores_decibeis:
    return 0.0
  soma_energia = sum(10 ** (v / 10.0) for v in valores_decibeis)
  return round(10.0 * math.log10(soma_energia / len(valores_decibeis)), 1)


def calcular_proximo_fechamento(delta_segundos):
  agora_ts = time.time()
  return (math.floor(agora_ts / delta_segundos) + 1) * delta_segundos


def loop_simulacao(sensores):
  delta_hist_s = INTERVALO_HISTORICO_MINUTOS * 60
  proximo_fechamento_ts = calcular_proximo_fechamento(delta_hist_s)

  # Buffer em memória para acumular as coletas de cada segundo
  buffer_amostras = {s["id"]: [] for s in sensores}

  # Carrega histórico existente para não sobrescrever em restarts
  historico_geral = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        historico_geral = json.load(f)
    except Exception:
      historico_geral = []

  while True:
    ts_atual = time.time()
    agora = datetime.fromtimestamp(ts_atual)
    hora = agora.hour
    payload_vivo = []

    for s in sensores:
      if s["distrito"] == "Paranapiacaba":
        ruido_base = (
            random.uniform(34, 45)
            if (hora < 6 or hora > 21)
            else random.uniform(42, 52)
        )
      else:
        ruido_base = (
            random.uniform(55, 68)
            if (7 <= hora <= 19)
            else random.uniform(42, 50)
        )

      houve_anomalia = random.random() < 0.04
      if houve_anomalia:
        decibeis = round(ruido_base + random.uniform(22, 35), 1)
        status = "ALERTA_RUIDO"
      else:
        decibeis = round(ruido_base + random.gauss(0, 2.0), 1)
        status = "NORMAL"

      tensao = round(random.uniform(124.8, 128.2), 1)
      potencia = round(s["potencia_nominal_w"] + random.uniform(-0.15, 0.25), 2)
      s["consumo_acumulado_kwh"] = round(
          s["consumo_acumulado_kwh"]
          + (potencia / 1000) * (INTERVALO_COLETA / 3600),
          5,
      )

      # Guarda na memória para o agregador
      buffer_amostras[s["id"]].append(decibeis)

      payload_vivo.append({
          "sensor_id": s["id"],
          "timestamp": agora.strftime("%H:%M:%S"),
          "bairro": s["bairro"],
          "distrito": s["distrito"],
          "latitude": s["latitude"],
          "longitude": s["longitude"],
          "decibeis_dba": decibeis,
          "status_ruido": status,
          "eletrica": {
              "tensao_v": tensao,
              "potencia_w": potencia,
              "consumo_acumulado_kwh": s["consumo_acumulado_kwh"],
          },
      })

    # 1. Salva a telemetria instantânea de 1s (Dashboard)
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
      json.dump(payload_vivo, f, ensure_ascii=False)

    # 2. Verifica se a janela de histórico atingiu o minuto cravado
    if ts_atual >= proximo_fechamento_ts:
      fechamento_dt = datetime.fromtimestamp(proximo_fechamento_ts)
      timestamp_str = fechamento_dt.strftime("%Y-%m-%d %H:%M:00")

      for s in sensores:
        amostras = buffer_amostras[s["id"]]
        if amostras:
          historico_geral.append({
              "sensor_id": s["id"],
              "bairro": s["bairro"],
              "distrito": s["distrito"],
              "fechamento": timestamp_str,
              "amostras_coletadas": len(amostras),
              "leq_dba": calcular_leq(amostras),
              "max_dba": max(amostras),
              "min_dba": min(amostras),
              "consumo_acumulado_kwh": s["consumo_acumulado_kwh"],
          })
          buffer_amostras[s["id"]] = []

      # Mantém os últimos 2.000 registros para o arquivo não crescer indefinidamente
      historico_geral = historico_geral[-2000:]

      with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico_geral, f, ensure_ascii=False, indent=2)

      print(
          f"📦 [Histórico Consolidado] Janela fechada com sucesso em:"
          f" {timestamp_str}"
      )
      proximo_fechamento_ts = calcular_proximo_fechamento(delta_hist_s)

    time.sleep(INTERVALO_COLETA)