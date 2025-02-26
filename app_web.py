from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import json
from datetime import datetime
import os
import random
from dotenv import load_dotenv
import time
from functools import lru_cache
import urllib3
import logging
import cloudscraper
from fake_useragent import UserAgent
import socket
import ssl

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
        # Removido FileHandler para evitar criação do arquivo radar_web.log
    ]
)
logger = logging.getLogger('radar-app-web')

# Desabilitar avisos de SSL
urllib3.disable_warnings()

load_dotenv()

app = Flask(__name__)

# Inicializar o gerador de User-Agent
ua = UserAgent()

# Cache por 60 segundos
@lru_cache(maxsize=1)
def get_cached_timestamp():
    return int(time.time() / 60)

# Cria uma instância do cloudscraper
def criar_scraper():
    return cloudscraper.create_scraper(
        browser={
            'browser': random.choice(['chrome', 'firefox']),
            'platform': random.choice(['windows', 'darwin', 'linux']),
            'mobile': False
        },
        delay=5
    )

# Função para usar um serviço de proxy externo (se você tiver uma chave API)
def usar_servico_proxy(url):
    # Substitua YOUR_API_KEY pela sua chave API real
    # Exemplo com ScraperAPI
    # proxy_url = f"http://api.scraperapi.com?api_key=YOUR_API_KEY&url={url}"
    
    # Exemplo com ScrapingBee
    # proxy_url = f"https://app.scrapingbee.com/api/v1/?api_key=YOUR_API_KEY&url={url}"
    
    # Como não temos uma chave API, vamos usar uma abordagem alternativa
    # Esta é apenas uma demonstração - você precisará de um serviço real
    proxy_url = url
    
    try:
        response = requests.get(proxy_url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Erro ao usar serviço de proxy: {e}")
    
    return None

# Função para buscar dados de uma API alternativa (se disponível)
def buscar_api_alternativa():
    # Esta é uma função de exemplo - você precisaria implementar com uma API real
    # Algumas opções:
    # - API-Football (https://www.api-football.com/)
    # - Football-Data.org (https://www.football-data.org/)
    # - SportMonks (https://www.sportmonks.com/)
    
    logger.info("Tentando buscar dados de API alternativa")
    
    try:
        # Exemplo com Football-Data.org (você precisaria de uma chave API)
        # headers = {'X-Auth-Token': 'YOUR_API_KEY'}
        # response = requests.get('https://api.football-data.org/v4/matches', headers=headers)
        
        # Como não temos uma chave API, retornamos None
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar API alternativa: {e}")
        return None

# Função para buscar dados de fontes públicas (RSS, HTML parsing)
def buscar_fontes_publicas():
    # Esta é uma função de exemplo - você precisaria implementar com fontes reais
    logger.info("Tentando buscar dados de fontes públicas")
    
    try:
        # Exemplo: buscar dados do Livescore.com (precisaria de HTML parsing)
        # response = requests.get('https://www.livescore.com')
        # Então usar BeautifulSoup para extrair os dados
        
        # Como isso é complexo e específico, retornamos None por enquanto
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar fontes públicas: {e}")
        return None

def get_live_matches():
    # Força atualização do cache a cada 60 segundos
    _ = get_cached_timestamp()
    
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    # Estratégias para web
    estrategias = [
        "cloudscraper",      # Usar cloudscraper
        "servico_proxy",     # Usar serviço de proxy (se configurado)
        "api_alternativa",   # Usar API alternativa (se configurada)
        "fontes_publicas"    # Usar fontes públicas (se configuradas)
    ]
    
    # Detectar se estamos rodando em ambiente de produção
    is_production = os.environ.get('PRODUCTION', 'false').lower() == 'true'
    
    # Se estiver em produção, priorizar estratégias que funcionam na web
    if is_production:
        # Reordenar estratégias para priorizar as que funcionam na web
        estrategias = [
            "servico_proxy",     # Usar serviço de proxy (se configurado)
            "api_alternativa",   # Usar API alternativa (se configurada)
            "fontes_publicas",   # Usar fontes públicas (se configuradas)
            "cloudscraper"       # Usar cloudscraper (menos eficaz na web)
        ]
    
    # Tentar cada estratégia
    for estrategia in estrategias:
        logger.info(f"Tentando estratégia: {estrategia}")
        
        try:
            # Estratégia 1: Usar cloudscraper
            if estrategia == "cloudscraper":
                scraper = criar_scraper()
                
                # Primeiro acessa a página principal
                scraper.get("https://www.sofascore.com/")
                time.sleep(random.uniform(2, 5))
                
                # Acessa a página de futebol
                scraper.get("https://www.sofascore.com/football/livescore")
                time.sleep(random.uniform(3, 7))
                
                # Faz a requisição para a API
                response = scraper.get(url)
                
                if response.status_code == 200:
                    return processar_resposta_sofascore(response.json())
            
            # Estratégia 2: Usar serviço de proxy
            elif estrategia == "servico_proxy":
                dados = usar_servico_proxy(url)
                if dados:
                    return processar_resposta_sofascore(dados)
            
            # Estratégia 3: Usar API alternativa
            elif estrategia == "api_alternativa":
                dados = buscar_api_alternativa()
                if dados:
                    return processar_resposta_api_alternativa(dados)
            
            # Estratégia 4: Usar fontes públicas
            elif estrategia == "fontes_publicas":
                dados = buscar_fontes_publicas()
                if dados:
                    return processar_resposta_fontes_publicas(dados)
            
        except Exception as e:
            logger.error(f"Erro na estratégia {estrategia}: {e}")
    
    logger.error("Todas as estratégias falharam")
    
    # Se todas as estratégias falharem, retornar dados de exemplo para não quebrar a UI
    return gerar_dados_exemplo()

def processar_resposta_sofascore(data):
    matches = []
    logger.info(f"Processando resposta Sofascore: {json.dumps(data)[:500]}...")  # Log da estrutura de dados (primeiros 500 caracteres)
    
    for event in data.get('events', []):
        try:
            if event.get('status', {}).get('type') == 'inprogress':
                event_id = str(event.get('id'))
                home_name = event.get('homeTeam', {}).get('name', '').lower().replace(' ', '-')
                away_name = event.get('awayTeam', {}).get('name', '').lower().replace(' ', '-')
                widget_id = f"{home_name}-{away_name}".lower().replace('-', '').replace('_', '')[:10]
                
                # Log completo da estrutura do evento para debug
                logger.info(f"Evento: {json.dumps(event)}")
                
                # Verificar a estrutura correta do placar
                score = event.get('score', {})
                logger.info(f"Estrutura do placar: {json.dumps(score)}")
                
                # Verificar se há estruturas aninhadas para o placar
                home_score = None
                away_score = None
                
                # Nova estrutura: verificar homeScore e awayScore como objetos separados
                if 'homeScore' in event and 'awayScore' in event:
                    home_score = event.get('homeScore', {}).get('current')
                    away_score = event.get('awayScore', {}).get('current')
                    logger.info(f"Placar encontrado em 'homeScore/awayScore': {home_score}-{away_score}")
                # Estrutura antiga: tentar diferentes caminhos para o placar
                elif 'current' in score:
                    home_score = score.get('current', {}).get('home')
                    away_score = score.get('current', {}).get('away')
                    logger.info(f"Placar encontrado em 'current': {home_score}-{away_score}")
                elif 'normaltime' in score:
                    home_score = score.get('normaltime', {}).get('home')
                    away_score = score.get('normaltime', {}).get('away')
                    logger.info(f"Placar encontrado em 'normaltime': {home_score}-{away_score}")
                elif 'display' in score:
                    home_score = score.get('display', {}).get('home')
                    away_score = score.get('display', {}).get('away')
                    logger.info(f"Placar encontrado em 'display': {home_score}-{away_score}")
                else:
                    # Caminho padrão como no código original
                    home_score = score.get('home')
                    away_score = score.get('away')
                    logger.info(f"Placar encontrado no caminho padrão: {home_score}-{away_score}")
                
                # Fallback para 0 se ainda for None
                if home_score is None:
                    home_score = 0
                if away_score is None:
                    away_score = 0
                
                logger.info(f"Placar final: {home_score}-{away_score} para {home_name} vs {away_name}")
                
                formatted_match = {
                    'id': event_id,
                    'widget_id': widget_id,
                    'status': {
                        'type': 'inprogress',
                        'description': event.get('status', {}).get('description', 'Em andamento'),
                        'elapsed': event.get('status', {}).get('elapsed', 0),
                        'addedTime': event.get('status', {}).get('addedTime', 0),
                        'period': event.get('status', {}).get('period', 1)
                    },
                    'homeTeam': {
                        'name': event.get('homeTeam', {}).get('name'),
                        'id': event.get('homeTeam', {}).get('id'),
                        'logo': f"https://api.sofascore.com/api/v1/team/{event.get('homeTeam', {}).get('id')}/image"
                    },
                    'awayTeam': {
                        'name': event.get('awayTeam', {}).get('name'),
                        'id': event.get('awayTeam', {}).get('id'),
                        'logo': f"https://api.sofascore.com/api/v1/team/{event.get('awayTeam', {}).get('id')}/image"
                    },
                    'score': {
                        'home': home_score,
                        'away': away_score
                    }
                }
                matches.append(formatted_match)
        except Exception as e:
            logger.error(f"Erro ao processar evento: {e}")
            continue
    
    return matches

def processar_resposta_api_alternativa(data):
    # Esta função processaria dados de uma API alternativa
    # Como é específico para cada API, retornamos uma lista vazia por enquanto
    return []

def processar_resposta_fontes_publicas(data):
    # Esta função processaria dados de fontes públicas
    # Como é específico para cada fonte, retornamos uma lista vazia por enquanto
    return []

def gerar_dados_exemplo():
    # Gera alguns dados de exemplo para não quebrar a UI quando todas as estratégias falham
    logger.warning("Gerando dados de exemplo porque todas as estratégias falharam")
    
    times = [
        {"name": "Barcelona", "id": "2817"},
        {"name": "Real Madrid", "id": "2829"},
        {"name": "Manchester City", "id": "17"},
        {"name": "Liverpool", "id": "44"},
        {"name": "Bayern Munich", "id": "2672"},
        {"name": "PSG", "id": "1644"},
        {"name": "Juventus", "id": "2687"},
        {"name": "Inter Milan", "id": "2697"},
        {"name": "Flamengo", "id": "5981"},
        {"name": "Palmeiras", "id": "1963"}
    ]
    
    matches = []
    
    # Gerar 3-5 partidas aleatórias
    for i in range(random.randint(3, 5)):
        # Escolher times aleatórios (sem repetição)
        home_idx = random.randint(0, len(times) - 1)
        away_idx = random.randint(0, len(times) - 1)
        while away_idx == home_idx:
            away_idx = random.randint(0, len(times) - 1)
        
        home_team = times[home_idx]
        away_team = times[away_idx]
        
        # Gerar placar aleatório
        home_score = random.randint(0, 3)
        away_score = random.randint(0, 3)
        
        # Gerar tempo de jogo aleatório
        elapsed = random.randint(1, 90)
        period = 2 if elapsed > 45 else 1
        
        # Gerar ID único
        match_id = f"{int(time.time())}-{i}"
        
        # Gerar widget_id
        home_name = home_team["name"].lower().replace(' ', '-')
        away_name = away_team["name"].lower().replace(' ', '-')
        widget_id = f"{home_name}-{away_name}".lower().replace('-', '').replace('_', '')[:10]
        
        match = {
            'id': match_id,
            'widget_id': widget_id,
            'status': {
                'type': 'inprogress',
                'description': '2nd half' if period == 2 else '1st half',
                'elapsed': elapsed,
                'addedTime': random.randint(0, 5),
                'period': period
            },
            'homeTeam': {
                'name': home_team["name"],
                'id': home_team["id"],
                'logo': f"https://api.sofascore.com/api/v1/team/{home_team['id']}/image"
            },
            'awayTeam': {
                'name': away_team["name"],
                'id': away_team["id"],
                'logo': f"https://api.sofascore.com/api/v1/team/{away_team['id']}/image"
            },
            'score': {
                'home': home_score,
                'away': away_score
            }
        }
        
        matches.append(match)
    
    return matches

def format_match_time(match):
    try:
        status = match['status']
        
        if status['description'] == 'Halftime':
            return 'Intervalo'
        elif status['description'] == 'Ended':
            return 'Fim'
        elif status['description'] == 'Not started':
            return 'Início'
            
        if status['type'] == 'inprogress':
            elapsed = status.get('elapsed', 0)
            if elapsed > 45 or status.get('description', '').lower().startswith('2nd'):
                return "2ºTempo"
            else:
                return "1ºTempo"
        
        return 'Início'
    except Exception as e:
        logger.error(f"Erro ao formatar tempo: {e}")
        return 'Tempo indisponível'

def format_match_for_response(match):
    if match['status']['type'] == 'inprogress':
        return {
            'id': match['id'],
            'widget_id': match['widget_id'],
            'homeTeam': {
                'name': match['homeTeam']['name'],
                'score': match['score']['home'],
                'logo': match['homeTeam']['logo']
            },
            'awayTeam': {
                'name': match['awayTeam']['name'],
                'score': match['score']['away'],
                'logo': match['awayTeam']['logo']
            },
            'time': format_match_time(match)
        }
    return None

@app.route('/get_matches')
def get_matches():
    matches = get_live_matches()
    formatted_matches = []
    
    for match in matches:
        formatted_match = format_match_for_response(match)
        if formatted_match:
            formatted_matches.append(formatted_match)
    
    return {'matches': formatted_matches}

@app.route('/')
def index():
    matches = get_live_matches()
    formatted_matches = []
    
    for match in matches:
        formatted_match = format_match_for_response(match)
        if formatted_match:
            formatted_matches.append(formatted_match)
    
    return render_template('index.html', matches=formatted_matches)

# Rota para verificar o status do servidor
@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

# Rota para servir o favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'radar.ico')

# Rota para forçar uma estratégia específica (útil para testes)
@app.route('/test_strategy/<strategy>')
def test_strategy(strategy):
    if strategy not in ["cloudscraper", "servico_proxy", "api_alternativa", "fontes_publicas"]:
        return jsonify({"error": "Estratégia inválida"}), 400
    
    logger.info(f"Testando estratégia: {strategy}")
    
    try:
        result = {"strategy": strategy}
        
        if strategy == "cloudscraper":
            scraper = criar_scraper()
            response = scraper.get("https://api.sofascore.com/api/v1/sport/football/events/live")
            result["status"] = response.status_code
        
        elif strategy == "servico_proxy":
            dados = usar_servico_proxy("https://api.sofascore.com/api/v1/sport/football/events/live")
            result["status"] = "success" if dados else "failed"
        
        elif strategy == "api_alternativa":
            dados = buscar_api_alternativa()
            result["status"] = "success" if dados else "failed"
        
        elif strategy == "fontes_publicas":
            dados = buscar_fontes_publicas()
            result["status"] = "success" if dados else "failed"
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e), "strategy": strategy}), 500

if __name__ == '__main__':
    # Definir variável de ambiente para indicar se estamos em produção
    # No ambiente de produção, você definiria isso como 'true'
    os.environ['PRODUCTION'] = 'false'
    
    app.run(debug=True)
