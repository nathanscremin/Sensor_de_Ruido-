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
        html, body {{
            height: auto !important;
            min-height: 100vh !important;
            background-color: #f1f5f9 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0 !important;
            padding: 16px 24px 40px 24px !important;
            box-sizing: border-box !important;
            overflow-y: auto !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 16px !important;
        }}

        path.leaflet-interactive:focus, .leaflet-interactive:focus, svg:focus {{ outline: none !important; }}

        /* 1. CABEÇALHO COM GRID DE 3 COLUNAS (Busca Rigorosamente Centralizada) */
        #top-header-card {{
            order: 1 !important;
            background: #ffffff;
            border-radius: 12px;
            padding: 10px 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 16px;
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 8px;
            justify-self: start;
        }}

        .search-container {{
            position: relative;
            width: 440px;
            display: flex;
            gap: 6px;
            justify-self: center;
        }}

        .header-right {{
            justify-self: end;
            font-size: 12px;
            color: #475569;
        }}

        #bairro-input {{
            flex: 1;
            padding: 7px 12px;
            font-size: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            outline: none;
            background: #f8fafc;
            transition: all 0.2s;
        }}
        #bairro-input:focus {{ border-color: #0284c7; background: #fff; box-shadow: 0 0 0 2px rgba(2,132,199,0.15); }}

        #btn-reset {{
            padding: 7px 14px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 12px;
            transition: background 0.15s;
        }}
        #btn-reset:hover {{ background: #c0392b; }}

        #bairros-dropdown {{
            position: absolute;
            top: calc(100% + 4px);
            left: 0;
            right: 76px;
            max-height: 160px;
            overflow-y: auto;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            z-index: 2000;
            display: none;
        }}
        .dropdown-item {{
            padding: 8px 12px;
            font-size: 12px;
            color: #334155;
            cursor: pointer;
            border-bottom: 1px solid #f1f5f9;
        }}
        .dropdown-item:hover {{ background: #f0f9ff; color: #0284c7; font-weight: 600; }}

        /* 2. MAPA ISOLADO E ARREDONDADO */
        .folium-map {{
            order: 2 !important;
            position: relative !important;
            width: 100% !important;
            height: 72vh !important;
            border-radius: 16px !important;
            overflow: hidden !important;
            border: 1px solid #cbd5e1 !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
            background: #ffffff !important;
        }}

        /* 3. BASE: 2 QUADRADOS LADO A LADO */
        #bottom-analytics-grid {{
            order: 3 !important;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            width: 100%;
            margin-top: 4px;
        }}

        .dashboard-box {{
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            min-height: 280px;
            display: flex;
            flex-direction: column;
        }}

        .box-title {{
            font-size: 13px;
            font-weight: 700;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 10px;
            margin-bottom: 12px;
        }}

        /* Lista de Sensores da Região (Esquerda) */
        #lista-sensores-grid {{
            flex: 1;
            max-height: 240px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding-right: 4px;
        }}
        #lista-sensores-grid::-webkit-scrollbar {{ width: 5px; }}
        #lista-sensores-grid::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}

        .item-sensor {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 10px;
            background: #f8fafc;
            border-radius: 6px;
            border-left: 4px solid #2ecc71;
            cursor: pointer;
            font-size: 12px;
            border-top: 1px solid #f1f5f9;
            border-right: 1px solid #f1f5f9;
            border-bottom: 1px solid #f1f5f9;
            transition: all 0.15s;
        }}
        .item-sensor:hover {{
            background: #e2e8f0;
            transform: translateX(3px);
        }}
        .badge-dba {{
            font-weight: bold;
            padding: 2px 7px;
            border-radius: 4px;
            color: #fff;
            background: #2ecc71;
            font-size: 11px;
        }}

        /* Informações do Sensor Selecionado (Direita) */
        #painel-sensor-selecionado {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px dashed #e2e8f0;
            font-size: 13px;
        }}
        .metric-row:last-child {{ border-bottom: none; }}
        .metric-label {{ color: #64748b; }}
        .metric-value {{ font-weight: 600; color: #0f172a; }}

        .live-dot {{
            display: inline-block; width: 8px; height: 8px; background: #2ecc71;
            border-radius: 50%; margin-right: 6px; animation: blink 1s infinite;
        }}
        @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
    </style>

    <!-- 1. Header do Topo com a busca centralizada -->
    <div id="top-header-card">
        <div class="header-left">
            <span class="live-dot"></span>
            <b style="font-size: 14px; color: #0f172a;">NoiseSensor Santo André</b>
        </div>

        <div class="search-container">
            <input id="bairro-input" placeholder="Filtrar por região / bairro..." autocomplete="off" />
            <button id="btn-reset">Limpar</button>
            <div id="bairros-dropdown"></div>
        </div>

        <div class="header-right">
            Atualização: <b id="hora-atual">--:--:--</b>
        </div>
    </div>

    <!-- 2. Grid Analítico Inferior -->
    <div id="bottom-analytics-grid">
        <div class="dashboard-box">
            <div class="box-title">
                <span>📍 Sensores na Região</span>
                <span id="contador-regiao" style="font-size: 11px; color: #64748b; font-weight: normal;">60 nós</span>
            </div>
            <div id="lista-sensores-grid"></div>
        </div>

        <div class="dashboard-box">
            <div class="box-title">
                <span>⚡ Telemetria do Sensor Selecionado</span>
                <span id="status-tag" style="font-size: 11px; color: #64748b;">Nenhum sensor em foco</span>
            </div>
            <div id="painel-sensor-selecionado">
                <div style="text-align: center; color: #94a3b8; font-size: 13px;">
                    Clique ou passe o mouse sobre um sensor no mapa ou na lista ao lado para inspecionar métricas acústicas e elétricas.
                </div>
            </div>
        </div>
    </div>

    <script>
        window.addEventListener('load', function() {{
            const map = {m.get_name()};
            const geoLayer = {geo_layer.get_name()};

            setTimeout(() => map.invalidateSize(), 200);
            window.addEventListener('resize', () => map.invalidateSize());

            const input = document.getElementById('bairro-input');
            const dropdown = document.getElementById('bairros-dropdown');
            const btnReset = document.getElementById('btn-reset');
            const horaEl = document.getElementById('hora-atual');
            const listaGrid = document.getElementById('lista-sensores-grid');
            const contadorRegiaoEl = document.getElementById('contador-regiao');
            const painelSensorEl = document.getElementById('painel-sensor-selecionado');
            const statusTagEl = document.getElementById('status-tag');

            const layersMap = {{}};
            const nomesBairros = [];
            let highlightedPolygon = null;
            let bairroFiltrado = null;
            let sensorSelecionadoId = null;

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

            function atualizarPainelDireito(s) {{
                if (!s) return;
                const cor = s.decibeis_dba >= 70 ? '#e74c3c' : (s.decibeis_dba >= 55 ? '#d97706' : '#16a34a');
                statusTagEl.innerHTML = `<span style="color: ${{cor}}; font-weight: bold;">${{s.status_ruido}}</span>`;

                painelSensorEl.innerHTML = `
                    <div class="metric-row">
                        <span class="metric-label">Identificador:</span>
                        <span class="metric-value">${{s.sensor_id}}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Localização:</span>
                        <span class="metric-value">${{s.bairro}} (${{s.distrito}})</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Nível de Pressão Sonora:</span>
                        <span class="metric-value" style="color: ${{cor}}; font-size: 15px;">${{s.decibeis_dba}} dBA</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Potência Ativa Instantânea:</span>
                        <span class="metric-value">${{s.eletrica.potencia_w}} W</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Tensão da Rede:</span>
                        <span class="metric-value">${{s.eletrica.tensao_v}} V</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Consumo Elétrico Acumulado:</span>
                        <span class="metric-value">${{s.eletrica.consumo_acumulado_kwh.toFixed(4)}} kWh</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Última Leitura:</span>
                        <span class="metric-value" style="font-size: 11px; color: #64748b;">${{s.timestamp}}</span>
                    </div>
                `;
            }}

            function renderizarListaSensores() {{
                listaGrid.innerHTML = "";
                const sensoresFiltrados = telemetriaCache.filter(s => !bairroFiltrado || s.bairro === bairroFiltrado);
                contadorRegiaoEl.innerText = sensoresFiltrados.length + " nó(s)";

                sensoresFiltrados.forEach(s => {{
                    const cor = s.decibeis_dba >= 70 ? '#e74c3c' : (s.decibeis_dba >= 55 ? '#f1c40f' : '#2ecc71');
                    const item = document.createElement('div');
                    item.className = 'item-sensor';
                    item.id = 'grid-item-' + s.sensor_id;
                    item.style.borderLeftColor = cor;

                    item.innerHTML = `
                        <div>
                            <b>${{s.sensor_id}}</b>
                            <span style="color:#64748b; margin-left: 6px;">${{s.bairro}}</span>
                        </div>
                        <span class="badge-dba" style="background:${{cor}};">${{s.decibeis_dba}} dB</span>
                    `;

                    item.addEventListener('mouseenter', () => {{
                        atualizarPainelDireito(s);
                        if (sensorMarkers[s.sensor_id]) {{
                            sensorMarkers[s.sensor_id].setRadius(9);
                            sensorMarkers[s.sensor_id].bringToFront();
                        }}
                    }});

                    item.addEventListener('mouseleave', () => {{
                        if (sensorMarkers[s.sensor_id]) {{
                            sensorMarkers[s.sensor_id].setRadius(s.status_ruido === 'ALERTA_RUIDO' ? 7 : 5);
                        }}
                    }});

                    item.addEventListener('click', () => {{
                        sensorSelecionadoId = s.sensor_id;
                        atualizarPainelDireito(s);
                        if (sensorMarkers[s.sensor_id]) {{
                            map.setView([s.latitude, s.longitude], 15);
                            sensorMarkers[s.sensor_id].openPopup();
                        }}
                    }});

                    listaGrid.appendChild(item);
                }});
            }}

            function gerarHtmlPopup(s, cor) {{
                return `
                    <div style="font-family: sans-serif; font-size: 13px; line-height: 1.45;">
                        <b style="font-size: 14px; color: #1f2328;">🔊 Sensor ${{s.sensor_id}}</b><br>
                        <b>Bairro:</b> ${{s.bairro}} (${{s.distrito}})<br>
                        <b>Ruído:</b> <span style="color:${{cor}}; font-weight:bold;">${{s.decibeis_dba}} dBA</span> (${{s.status_ruido}})<br>
                        <hr style="margin: 6px 0; border: none; border-top: 1px solid #ddd;">
                        <b>⚡ Potência:</b> ${{s.eletrica.potencia_w}} W (${{s.eletrica.tensao_v}} V)<br>
                        <b>Consumo:</b> ${{s.eletrica.consumo_acumulado_kwh.toFixed(4)}} kWh
                    </div>
                `;
            }}

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

                        if (sensorMarkers[s.sensor_id]) {{
                            const m = sensorMarkers[s.sensor_id];
                            m.setStyle({{ fillColor: cor }});
                            if (m.getPopup()) {{ m.getPopup().setContent(gerarHtmlPopup(s, cor)); }}
                        }} else {{
                            const marker = L.circleMarker([s.latitude, s.longitude], {{
                                radius: raioBase, fillColor: cor, color: '#111', weight: 1, opacity: 0.9, fillOpacity: 0.85
                            }});
                            marker.bindPopup(gerarHtmlPopup(s, cor));

                            marker.on('click', () => {{
                                sensorSelecionadoId = s.sensor_id;
                                atualizarPainelDireito(s);
                            }});

                            markersGroup.addLayer(marker);
                            sensorMarkers[s.sensor_id] = marker;
                        }}

                        const itemDom = document.getElementById('grid-item-' + s.sensor_id);
                        if (itemDom) {{
                            itemDom.style.borderLeftColor = cor;
                            const badge = itemDom.querySelector('.badge-dba');
                            if (badge) {{ badge.innerText = s.decibeis_dba + ' dB'; badge.style.background = cor; }}
                        }}

                        if (sensorSelecionadoId === s.sensor_id) {{
                            atualizarPainelDireito(s);
                        }}

                        horaEl.innerText = s.timestamp;
                    }});

                    heatLayer.setLatLngs(heatPoints);

                    if (listaGrid.children.length === 0) {{ renderizarListaSensores(); }}
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