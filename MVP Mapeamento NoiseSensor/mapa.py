import json
from config import ARQUIVO_HTML, CAMINHO_GEOJSON
import folium


def gerar_mapa():
  with open(CAMINHO_GEOJSON, "r", encoding="utf-8") as f:
    geo_data = json.load(f)

  m = folium.Map(
      location=[-23.72, -46.43],
      zoom_start=11,
      min_zoom=10,
      max_zoom=16,
      max_bounds=True,
      min_lat=-23.86,
      max_lat=-23.58,
      min_lon=-46.60,
      max_lon=-46.25,
      tiles="OpenStreetMap",
  )

  geo_layer = folium.GeoJson(
      geo_data,
      name="Bairros de Santo André",
      style_function=lambda feature: {
          "fillColor": "#3388ff",
          "color": "#002244",
          "weight": 1.2,
          "fillOpacity": 0.15,
      },
      highlight_function=lambda feature: {
          "fillColor": "#ff7800",
          "color": "#ff0000",
          "weight": 2,
          "fillOpacity": 0.35,
      },
      tooltip=folium.GeoJsonTooltip(
          fields=["NM_BAIRRO", "NM_DIST"],
          aliases=["Bairro:", "Distrito:"],
          localize=True,
      ),
  )
  geo_layer.add_to(m)

  custom_ui = f"""
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>

    <style>
        path.leaflet-interactive:focus, .leaflet-interactive:focus, svg:focus {{ outline: none !important; }}

        /* Painel fixado no canto superior direito */
        #painel-superior {{
            position: absolute;
            top: 15px;
            right: 15px;
            z-index: 1000;
            width: 320px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: calc(100vh - 30px);
        }}

        .card-ui {{
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(6px);
            padding: 12px 14px;
            border-radius: 8px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.18);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            border: 1px solid #e2e8f0;
        }}

        .search-inputs {{
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }}

        #bairro-input {{
            flex: 1;
            padding: 7px 10px;
            font-size: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            outline: none;
            background: #fff;
        }}

        #btn-reset {{
            padding: 7px 12px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 12px;
        }}

        /* DROPDOWN BRANCO DE BAIRROS (embaixo da barra de busca) */
        #bairros-dropdown {{
            position: absolute;
            top: calc(100% + 3px);
            left: 0;
            right: 0;
            max-height: 140px;
            overflow-y: auto;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            z-index: 2000;
            display: none;
        }}
        #bairros-dropdown::-webkit-scrollbar {{ width: 5px; }}
        #bairros-dropdown::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}

        .dropdown-item {{
            padding: 7px 10px;
            font-size: 12px;
            color: #334155;
            cursor: pointer;
            border-bottom: 1px solid #f1f5f9;
            transition: background 0.12s;
        }}
        .dropdown-item:last-child {{ border-bottom: none; }}
        .dropdown-item:hover {{
            background: #f8fafc;
            color: #0284c7;
            font-weight: 600;
        }}

        /* LISTA VERTICAL ROLÁVEL DE SENSORES */
        #lista-sensores-container {{
            max-height: 170px;
            overflow-y: auto;
            margin-top: 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding-right: 4px;
        }}
        #lista-sensores-container::-webkit-scrollbar {{ width: 5px; }}
        #lista-sensores-container::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}

        .item-sensor {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 8px;
            background: #f8fafc;
            border-radius: 5px;
            border-left: 3px solid #2ecc71;
            cursor: pointer;
            font-size: 12px;
            transition: transform 0.12s, background 0.12s;
            border-top: 1px solid #f1f5f9;
            border-right: 1px solid #f1f5f9;
            border-bottom: 1px solid #f1f5f9;
        }}
        .item-sensor:hover {{
            background: #e2e8f0;
            transform: translateX(-2px);
        }}
        .item-sensor .badge-dba {{
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            color: #fff;
            background: #2ecc71;
            font-size: 11px;
        }}

        /* CARD DE DETALHES DO SENSOR (Embaixo da lista de sensores, 100% branco) */
        #card-detalhes-sensor {{
            display: none;
            font-size: 12px;
            line-height: 1.5;
            color: #1e293b;
        }}
        #card-detalhes-sensor b {{ color: #0284c7; }}
        #card-detalhes-sensor hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 6px 0; }}

        .live-dot {{
            display: inline-block; width: 8px; height: 8px; background: #2ecc71;
            border-radius: 50%; margin-right: 5px; animation: blink 1s infinite;
        }}
        @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
    </style>

    <div id="painel-superior">
        <!-- Card 1: Status Geral -->
        <div class="card-ui">
            <div style="font-size: 12px; color: #555; display: flex; justify-content: space-between; align-items: center;">
                <span><span class="live-dot"></span><b>NoiseSensor Santo André</b></span>
                <span id="hora-atual">--:--:--</span>
            </div>
        </div>

        <!-- Card 2: Busca + Lista de Sensores -->
        <div class="card-ui">
            <label style="font-size: 11px; font-weight: 700; color: #2c3e50; text-transform: uppercase;">📍 Filtrar por Região</label>

            <div style="position: relative;">
                <div class="search-inputs">
                    <input id="bairro-input" placeholder="Selecione ou digite um bairro..." autocomplete="off" />
                    <button id="btn-reset">Limpar</button>
                </div>
                <div id="bairros-dropdown"></div>
            </div>

            <div style="margin-top: 10px; display: flex; justify-content: space-between; font-size: 11px; color: #64748b;">
                <b>SENSORES ATIVOS</b>
                <span id="contador-sensores">60 nós</span>
            </div>

            <!-- Lista Rolável Vertical -->
            <div id="lista-sensores-container"></div>
        </div>

        <!-- Card 3: Detalhes do Sensor (Aparece ao passar o mouse ou clicar) -->
        <div id="card-detalhes-sensor" class="card-ui"></div>
    </div>

    <script>
        window.addEventListener('load', function() {{
            const map = {m.get_name()};
            const geoLayer = {geo_layer.get_name()};

            const input = document.getElementById('bairro-input');
            const dropdown = document.getElementById('bairros-dropdown');
            const btnReset = document.getElementById('btn-reset');
            const horaEl = document.getElementById('hora-atual');
            const listaContainer = document.getElementById('lista-sensores-container');
            const contadorEl = document.getElementById('contador-sensores');
            const cardDetalhes = document.getElementById('card-detalhes-sensor');

            const layersMap = {{}};
            const nomesBairros = [];
            let highlightedPolygon = null;
            let bairroFiltrado = null;
            let sensorHoverAtual = null;

            let markersGroup = L.layerGroup().addTo(map);
            let heatLayer = L.heatLayer([], {{
                radius: 32, blur: 22, maxZoom: 14,
                gradient: {{0.2: '#2ecc71', 0.5: '#f1c40f', 0.8: '#e67e22', 1.0: '#e74c3c'}}
            }}).addTo(map);

            const sensorMarkers = {{}};
            let telemetriaCache = [];

            const defaultPolyStyle = {{ fillColor: "#3388ff", color: "#002244", weight: 1.2, fillOpacity: 0.15 }};
            const selectedPolyStyle = {{ fillColor: "#e74c3c", color: "#962d22", weight: 3, fillOpacity: 0.45 }};

            function aplicarDestaqueBairro(layer, nomeBairro) {{
                if (highlightedPolygon && highlightedPolygon !== layer) {{
                    highlightedPolygon.setStyle(defaultPolyStyle);
                }}
                highlightedPolygon = layer;
                layer.setStyle(selectedPolyStyle);
                bairroFiltrado = nomeBairro;
                renderizarListaSensores();
            }}

            function limparSelecao() {{
                if (highlightedPolygon) {{
                    highlightedPolygon.setStyle(defaultPolyStyle);
                    highlightedPolygon = null;
                }}
                input.value = "";
                bairroFiltrado = null;
                dropdown.style.display = "none";
                renderizarListaSensores();
                map.setView([-23.72, -46.43], 11);
            }}

            geoLayer.eachLayer(function(layer) {{
                if (layer.feature && layer.feature.properties) {{
                    const p = layer.feature.properties;
                    const nome = p.NM_BAIRRO || "Região";
                    const label = nome + " (" + (p.NM_DIST || "Santo André") + ")";
                    layersMap[label] = {{ layer: layer, nome: nome }};
                    nomesBairros.push(label);

                    layer.on('click', function() {{
                        input.value = label;
                        aplicarDestaqueBairro(layer, nome);
                        map.fitBounds(layer.getBounds(), {{ maxZoom: 14, padding: [40, 40] }});
                    }});
                }}
            }});

            nomesBairros.sort();

            function renderizarDropdown(filtro = "") {{
                dropdown.innerHTML = "";
                const termo = filtro.toLowerCase();
                const filtrados = nomesBairros.filter(b => b.toLowerCase().includes(termo));

                if (filtrados.length === 0) {{
                    dropdown.style.display = "none";
                    return;
                }}

                filtrados.forEach(label => {{
                    const item = document.createElement('div');
                    item.className = 'dropdown-item';
                    item.innerText = label;
                    item.addEventListener('click', function() {{
                        input.value = label;
                        dropdown.style.display = 'none';
                        const dadosBairro = layersMap[label];
                        aplicarDestaqueBairro(dadosBairro.layer, dadosBairro.nome);
                        map.fitBounds(dadosBairro.layer.getBounds(), {{ maxZoom: 14, padding: [40, 40] }});
                    }});
                    dropdown.appendChild(item);
                }});
                dropdown.style.display = "block";
            }}

            input.addEventListener('focus', () => renderizarDropdown(input.value));
            input.addEventListener('input', () => renderizarDropdown(input.value));

            document.addEventListener('click', function(e) {{
                if (!input.contains(e.target) && !dropdown.contains(e.target)) {{
                    dropdown.style.display = "none";
                }}
            }});

            btnReset.addEventListener('click', limparSelecao);

            // ATUALIZA CARD DE DETALHES DO SENSOR (Embaixo da lista)
            function atualizarCardDetalhes(s) {{
                if (!s) {{
                    cardDetalhes.style.display = 'none';
                    return;
                }}
                const cor = s.decibeis_dba >= 70 ? '#e74c3c' : (s.decibeis_dba >= 55 ? '#d97706' : '#16a34a');
                cardDetalhes.innerHTML = `
                    <div style="font-weight:700; font-size:13px; color:#1e293b; display:flex; justify-content:space-between;">
                        <span>🔊 Sensor ${{s.sensor_id}}</span>
                        <span style="color:${{cor}};">${{s.decibeis_dba}} dBA</span>
                    </div>
                    <small style="color:#64748b;">${{s.bairro}} (${{s.distrito}})</small>
                    <hr>
                    <b>Status:</b> ${{s.status_ruido}}<br>
                    <b>Potência:</b> ${{s.eletrica.potencia_w}} W | <b>Tensão:</b> ${{s.eletrica.tensao_v}} V<br>
                    <b>Consumo Acumulado:</b> ${{s.eletrica.consumo_acumulado_kwh.toFixed(4)}} kWh
                `;
                cardDetalhes.style.display = 'block';
            }}

            function gerarHtmlPopup(s, cor) {{
                return `
                    <div style="font-family: sans-serif; font-size: 13px; line-height: 1.45;">
                        <b style="font-size: 14px; color: #1f2328;">🔊 Sensor ${{s.sensor_id}}</b><br>
                        <b>Bairro:</b> ${{s.bairro}} (${{s.distrito}})<br>
                        <b>Ruído:</b> <span style="color:${{cor}}; font-weight:bold;">${{s.decibeis_dba}} dBA</span> (${{s.status_ruido}})<br>
                        <hr style="margin: 6px 0; border: none; border-top: 1px solid #ddd;">
                        <b>⚡ Potência:</b> ${{s.eletrica.potencia_w}} W (${{s.eletrica.tensao_v}} V)<br>
                        <b>Consumo:</b> ${{s.eletrica.consumo_acumulado_kwh.toFixed(4)}} kWh<br>
                        <small style="color: #666;">Última leitura: ${{s.timestamp}}</small>
                    </div>
                `;
            }}

            // RENDERIZAÇÃO DA LISTA DE SENSORES
            function renderizarListaSensores() {{
                listaContainer.innerHTML = "";
                const sensoresFiltrados = telemetriaCache.filter(s => !bairroFiltrado || s.bairro === bairroFiltrado);
                contadorEl.innerText = sensoresFiltrados.length + " nó(s)";

                sensoresFiltrados.forEach(s => {{
                    const cor = s.decibeis_dba >= 70 ? '#e74c3c' : (s.decibeis_dba >= 55 ? '#f1c40f' : '#2ecc71');
                    const item = document.createElement('div');
                    item.className = 'item-sensor';
                    item.id = 'list-item-' + s.sensor_id;
                    item.style.borderLeftColor = cor;

                    item.innerHTML = `
                        <div><b>${{s.sensor_id}}</b> <span style="color:#777; font-size:11px;">• ${{s.bairro}}</span></div>
                        <span class="badge-dba" style="background:${{cor}};">${{s.decibeis_dba}} dB</span>
                    `;

                    item.addEventListener('mouseenter', () => {{
                        sensorHoverAtual = s.sensor_id;
                        atualizarCardDetalhes(s);
                        if (sensorMarkers[s.sensor_id]) {{
                            sensorMarkers[s.sensor_id].setRadius(10);
                            sensorMarkers[s.sensor_id].bringToFront();
                        }}
                    }});

                    item.addEventListener('mouseleave', () => {{
                        sensorHoverAtual = null;
                        atualizarCardDetalhes(null);
                        if (sensorMarkers[s.sensor_id]) {{
                            sensorMarkers[s.sensor_id].setRadius(s.status_ruido === 'ALERTA_RUIDO' ? 7 : 5);
                        }}
                    }});

                    item.addEventListener('click', () => {{
                        if (sensorMarkers[s.sensor_id]) {{
                            map.setView([s.latitude, s.longitude], 15);
                            sensorMarkers[s.sensor_id].openPopup();
                        }}
                    }});

                    listaContainer.appendChild(item);
                }});
            }}

            // POLLING CONTÍNUO (1 SEGUNDO)
            async function atualizarTelemetria() {{
                try {{
                    const response = await fetch('dados_sensores.json?t=' + Date.now());
                    const dados = await response.json();
                    telemetriaCache = dados;

                    const heatPoints = [];

                    dados.forEach(s => {{
                        const intensidade = Math.max(0.1, Math.min(1.0, (s.decibeis_dba - 30) / 60));
                        heatPoints.push([s.latitude, s.longitude, intensidade]);

                        const cor = s.decibeis_dba >= 70 ? '#e74c3c' : (s.decibeis_dba >= 55 ? '#f1c40f' : '#2ecc71');
                        const raioBase = s.status_ruido === 'ALERTA_RUIDO' ? 7 : 5;
                        const raio = (sensorHoverAtual === s.sensor_id) ? 10 : raioBase;

                        if (sensorMarkers[s.sensor_id]) {{
                            const m = sensorMarkers[s.sensor_id];
                            m.setStyle({{ fillColor: cor, radius: raio }});
                            if (m.getPopup()) {{ m.getPopup().setContent(gerarHtmlPopup(s, cor)); }}
                        }} else {{
                            const marker = L.circleMarker([s.latitude, s.longitude], {{
                                radius: raio, fillColor: cor, color: '#111', weight: 1, opacity: 0.9, fillOpacity: 0.85
                            }});
                            marker.bindPopup(gerarHtmlPopup(s, cor));
                            markersGroup.addLayer(marker);
                            sensorMarkers[s.sensor_id] = marker;
                        }}

                        const itemDom = document.getElementById('list-item-' + s.sensor_id);
                        if (itemDom) {{
                            itemDom.style.borderLeftColor = cor;
                            const badge = itemDom.querySelector('.badge-dba');
                            if (badge) {{ badge.innerText = s.decibeis_dba + ' dB'; badge.style.background = cor; }}
                        }}

                        if (sensorHoverAtual === s.sensor_id) {{ atualizarCardDetalhes(s); }}
                        horaEl.innerText = s.timestamp;
                    }});

                    heatLayer.setLatLngs(heatPoints);

                    if (listaContainer.children.length === 0) {{ renderizarListaSensores(); }}
                }} catch (e) {{
                    console.error("Aguardando pipeline...", e);
                }}
            }}

            setInterval(atualizarTelemetria, 1000);
            atualizarTelemetria();
        }});
    </script>
    """

  m.get_root().html.add_child(folium.Element(custom_ui))
  m.save(ARQUIVO_HTML)