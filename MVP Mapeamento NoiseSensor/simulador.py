from datetime import datetime
import json
import os
import random
import time
from config import ARQUIVO_JSON, CAMINHO_GEOJSON, COTAS_DISTRITAIS, INTERVALO_COLETA


def ponto_dentro_poligono(x, y, poligono):
  """Ray-Casting para validar se a coordenada sorteada está dentro do bairro."""
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
  """Gera coordenadas fixas respeitando as cotas distritais."""
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


def loop_simulacao(sensores):
  """Loop executado em thread paralela para emitir leituras a cada segundo."""
  while True:
    agora = datetime.now()
    hora = agora.hour
    payload = []

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

      payload.append({
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

    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
      json.dump(payload, f, ensure_ascii=False)

    time.sleep(INTERVALO_COLETA)