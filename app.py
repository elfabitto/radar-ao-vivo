from flask import Flask, render_template
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
        logging.StreamHandler(),
        logging.FileHandler('radar.log')
    ]
)
logger = logging.getLogger('radar-app')

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

def get_live_matches():
    # Força atualização do cache a cada 60 segundos
    _ = get_cached_timestamp()
    
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    max_retries = 5
    retry_delay_base = 3  # segundos (base)
    
    # Estratégias disponíveis
    estrategias = [
        "cloudscraper",  # Usar cloudscraper
        "requests_ua",   # Usar requests com fake-useragent
        "completo"       # Usar requests com headers completos
    ]
    
    for attempt in range(max_retries):
        # Escolher estratégia
        estrategia = random.choice(estrategias)
        logger.info(f"Tentativa {attempt + 1} de {max_retries} usando estratégia: {estrategia}")
        
        try:
            response = None
            
            # Estratégia 1: Usar cloudscraper
            if estrategia == "cloudscraper":
                scraper = criar_scraper()
                
                logger.info("Usando cloudscraper para contornar proteções")
                
                # Primeiro acessa a página principal
                logger.info("Acessando página principal do SofaScore...")
                scraper.get("https://www.sofascore.com/")
                
                # Delay para simular comportamento humano
                delay = random.uniform(2, 5)
                logger.info(f"Aguardando {delay:.2f} segundos...")
                time.sleep(delay)
                
                # Acessa a página de futebol
                logger.info("Acessando página de futebol...")
                scraper.get("https://www.sofascore.com/football/livescore")
                
                # Delay para simular comportamento humano
                delay = random.uniform(3, 7)
                logger.info(f"Aguardando {delay:.2f} segundos...")
                time.sleep(delay)
                
                # Faz a requisição para a API
                logger.info(f"Acessando API: {url}")
                response = scraper.get(url)
                
            # Estratégia 2: Usar requests com fake-useragent
            elif estrategia == "requests_ua":
                # Gera um User-Agent aleatório
                current_user_agent = ua.random
                
                # Headers básicos
                headers = {
                    "User-Agent": current_user_agent,
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Origin": "https://www.sofascore.com",
                    "Referer": "https://www.sofascore.com/football/livescore",
                }
                
                logger.info(f"Usando fake-useragent: {current_user_agent}")
                
                session = requests.Session()
                
                # Primeiro acessa a página principal
                logger.info("Acessando página principal do SofaScore...")
                session.get(
                    "https://www.sofascore.com/",
                    headers=headers,
                    timeout=15
                )
                
                # Delay para simular comportamento humano
                delay = random.uniform(2, 5)
                logger.info(f"Aguardando {delay:.2f} segundos...")
                time.sleep(delay)
                
                # Acessa a página de futebol
                logger.info("Acessando página de futebol...")
                session.get(
                    "https://www.sofascore.com/football/livescore",
                    headers=headers,
                    timeout=15
                )
                
                # Delay para simular comportamento humano
                delay = random.uniform(3, 7)
                logger.info(f"Aguardando {delay:.2f} segundos...")
                time.sleep(delay)
                
                # Faz a requisição para a API
                logger.info(f"Acessando API: {url}")
                response = session.get(
                    url,
                    headers=headers,
                    timeout=15
                )
                
            # Estratégia 3: Usar requests com headers completos
            else:  # completo
                # Gera um User-Agent aleatório
                current_user_agent = ua.random
                
                # Simula um timestamp real
                timestamp = int(time.time() * 1000)
                
                # Gera um ID de sessão aleatório
                session_id = ''.join(random.choices('0123456789abcdef', k=32))
                
                # Headers mais completos e realistas
                headers = {
                    "User-Agent": current_user_agent,
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Origin": "https://www.sofascore.com",
                    "Referer": f"https://www.sofascore.com/football/livescore/{timestamp}",
                    "Sec-Ch-Ua": f"\"Chromium\";v=\"{random.randint(100, 122)}\", \"Not(A:Brand\";v=\"{random.randint(8, 24)}\", \"Google Chrome\";v=\"{random.randint(100, 122)}\"",
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": f"\"{random.choice(['Windows', 'macOS', 'Linux'])}\"",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "If-None-Match": f"W/\"{random.randint(1000, 9999)}\"",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "X-Requested-With": "XMLHttpRequest",
                    "Cookie": f"_gid=GA1.2.{random.randint(100000, 999999)}; _ga=GA1.2.{random.randint(100000, 999999)}; __cf_bm={session_id}",
                    "Connection": "keep-alive",
                    "TE": "trailers"
                }
                
                logger.info(f"Usando headers completos com User-Agent: {current_user_agent}")
                
                session = requests.Session()
                
                # Primeiro acessa a página principal
                logger.info("Acessando página principal do SofaScore...")
                session.get(
                    "https://www.sofascore.com/",
                    headers=headers,
                    timeout=15
                )
                
                # Delay para simular comportamento humano
                delay = random.uniform(2, 5)
                logger.info(f"Aguardando {delay:.2f} segundos...")
                time.sleep(delay)
                
                # Acessa a página de futebol
                logger.info("Acessando página de futebol...")
                session.get(
                    "https://www.sofascore.com/football/livescore",
                    headers=headers,
                    timeout=15
                )
                
                # Delay para simular comportamento humano
                delay = random.uniform(3, 7)
                logger.info(f"Aguardando {delay:.2f} segundos...")
                time.sleep(delay)
                
                # Faz a requisição para a API
                logger.info(f"Acessando API: {url}")
                response = session.get(
                    url,
                    headers=headers,
                    timeout=15
                )
            
            # Verifica a resposta
            logger.info(f"Status code da resposta: {response.status_code}")
            
            if response and response.status_code == 200:
                data = response.json()
                matches = []
                
                for event in data.get('events', []):
                    if event.get('status', {}).get('type') == 'inprogress':
                        event_id = str(event.get('id'))
                        home_name = event.get('homeTeam', {}).get('name', '').lower().replace(' ', '-')
                        away_name = event.get('awayTeam', {}).get('name', '').lower().replace(' ', '-')
                        widget_id = f"{home_name}-{away_name}".lower().replace('-', '').replace('_', '')[:10]
                        
                        home_score = event.get('score', {}).get('home', 0)
                        away_score = event.get('score', {}).get('away', 0)
                        
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
                
                return matches
            else:
                status_code = response.status_code if response else "Sem resposta"
                logger.warning(f"Erro ao buscar jogos. Status: {status_code}")
                if attempt < max_retries - 1:
                    # Tempo de espera exponencial entre tentativas
                    retry_delay = retry_delay_base * (2 ** attempt) + random.uniform(1, 5)
                    logger.info(f"Aguardando {retry_delay:.2f} segundos antes de tentar novamente...")
                    time.sleep(retry_delay)
                    continue
        except Exception as e:
            logger.error(f"Erro ao buscar jogos: {e}")
            if attempt < max_retries - 1:
                # Tempo de espera exponencial entre tentativas
                retry_delay = retry_delay_base * (2 ** attempt) + random.uniform(1, 5)
                logger.info(f"Aguardando {retry_delay:.2f} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
                continue
    
    logger.error("Todas as tentativas falharam")
    return []

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
        print(f"Erro ao formatar tempo: {e}")
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

if __name__ == '__main__':
    app.run(debug=True)
