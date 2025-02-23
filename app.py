from flask import Flask, render_template
import requests
import json
from datetime import datetime
import os
import random
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)

def get_live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/",
        "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    max_retries = 3
    retry_delay = 2  # segundos
    
    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1} de {max_retries} para buscar jogos")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status code da resposta: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                
                for event in data.get('events', []):
                    if event.get('status', {}).get('type') == 'inprogress':
                        event_id = str(event.get('id'))
                        home_name = event.get('homeTeam', {}).get('name', '').lower().replace(' ', '-')
                        away_name = event.get('awayTeam', {}).get('name', '').lower().replace(' ', '-')
                        widget_id = f"{home_name}-{away_name}".lower().replace('-', '').replace('_', '')[:10]
                        print(f"ID do jogo: {event_id}, Widget ID: {widget_id}")
                        
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
                print(f"Erro ao buscar jogos. Status: {response.status_code}")
                if attempt < max_retries - 1:
                    print(f"Aguardando {retry_delay} segundos antes de tentar novamente...")
                    time.sleep(retry_delay)
                    continue
        except Exception as e:
            print(f"Erro ao buscar jogos: {e}")
            if attempt < max_retries - 1:
                print(f"Aguardando {retry_delay} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
                continue
    
    print("Todas as tentativas falharam")
    return []

def format_match_time(match):
    try:
        status = match['status']
        
        if status['description'] == 'Halftime':
            return 'Int'
        elif status['description'] == 'Ended':
            return 'Fim'
        elif status['description'] == 'Not started':
            return 'Início'
            
        if status['type'] == 'inprogress':
            elapsed = status.get('elapsed', 0)
            if elapsed > 45 or status.get('description', '').lower().startswith('2nd'):
                return "2ºT"
            else:
                return "1ºT"
        
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
