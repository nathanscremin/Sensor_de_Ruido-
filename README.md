# NoiseSensor Santo André — MVP de Mapeamento Acústico

Prova de Conceito (PoC) para monitoramento em tempo real de poluição sonora e consumo elétrico de sensores inteligentes distribuídos pelo município de Santo André (incluindo distritos urbanos, Capuava e Paranapiacaba).

---

## Funcionalidades

* **Mapeamento Vetorial dos Bairros:** Delimitação geográfica oficial a partir de dados abertos do IBGE (`GeoJSON`).
* **Distribuição Espacial Automática:** Alocação de 60 sensores fixos através do algoritmo *Ray-Casting*, garantindo nós em todas as regiões e distritos.
* **Simulação de Telemetria Contínua (1s):**
  * Nível de pressão sonora em decibéis (`dBA`) e detecção de anomalias acústicas.
  * Modulação de ruído por período diurno/noturno e características ambientais da região.
  * Telemetria elétrica da rede pública: tensão (`V`), potência ativa (`W`) e consumo acumulado (`kWh`).
* **Dashboard Interativo em Tempo Real:**
  * Mapa de calor acústico dinâmico (*HeatMap*) com gradiente térmico adaptativo.
  * Filtro por região/bairro com busca inteligente sem recarregar a tela.
  * Painel com lista de nós ativos e card de inspeção ao passar o mouse (*hover*).
  * Persistência de estado: as camadas atualizam via JavaScript (`fetch`), sem fechar popups ou perder a navegação do usuário.

---

## Estrutura do Projeto

```text
├── config.py                     # Constantes, portas, cotas distritais e caminhos
├── simulador.py                  # Lógica espacial, Ray-Casting e geração de dados a 1s
├── mapa.py                       # Criação do mapa Folium e injeção do front-end Leaflet
├── main.py                       # Orquestrador (inicia simulação e servidor local)
├── santo_andre_dashboard.geojson # Malha de bairros de Santo André
└── dados_sensores.json           # Telemetria instantânea (gerada dinamicamente)
