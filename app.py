from flask import Flask, render_template
import requests
import json
from datetime import datetime
import os
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            matches = []
            
            for event in data.get('events', []):
                if event.get('status', {}).get('type') == 'inprogress':
                    event_id = str(event.get('id'))
                    # Gerar slug do jogo para o widget
                    home_name = event.get('homeTeam', {}).get('name', '').lower().replace(' ', '-')
                    away_name = event.get('awayTeam', {}).get('name', '').lower().replace(' ', '-')
                    # Simplificar o widget_id removendo caracteres especiais e limitando o tamanho
                    widget_id = f"{home_name}-{away_name}".lower().replace('-', '').replace('_', '')[:10]
                    print(f"ID do jogo: {event_id}, Widget ID: {widget_id}")
                    # Obter scores diretamente do evento
                    print(f"Evento completo: {json.dumps(event, indent=2)}")
                    
                    # Debug detalhado do status do jogo
                    print("\nStatus do jogo:")
                    print(f"Descrição: {event.get('status', {}).get('description')}")
                    print(f"Tempo decorrido: {event.get('status', {}).get('elapsed')}")
                    print(f"Período: {event.get('status', {}).get('period')}")
                    print(f"Segundo tempo? {event.get('status', {}).get('elapsed', 0) > 45}")
                    
                    # Analisar a estrutura do evento para debug
                    print("\nEstrutura do score no evento:")
                    print(f"homeScore: {event.get('homeScore')}")
                    print(f"awayScore: {event.get('awayScore')}")
                    print(f"score: {event.get('score')}")
                    
                    # Obter scores do objeto score principal
                    home_score = event.get('score', {}).get('home', 0)
                    away_score = event.get('score', {}).get('away', 0)
                    
                    print(f"Scores da API para {event_id} - Casa: {home_score}, Fora: {away_score}")
                    
                    formatted_match = {
                        'id': event_id,
                        'widget_id': widget_id,
                        'status': {
                            'type': 'inprogress',
                            'description': event.get('status', {}).get('description', 'Em andamento'),
                            'elapsed': event.get('status', {}).get('elapsed', 0),
                            'addedTime': event.get('status', {}).get('addedTime', 0),
                            'period': event.get('status', {}).get('period', 1)  # Período vem do status
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
                    print(f"Match formatado na origem: {event_id} - {home_score} x {away_score}")
                    matches.append(formatted_match)
            
            return matches
        else:
            print(f"Erro ao buscar jogos. Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro ao buscar jogos: {e}")
        return []

def format_match_time(match):
    try:
        status = match['status']
        
        # Verificar diferentes estados do jogo
        if status['description'] == 'Halftime':
            return 'Int'
        elif status['description'] == 'Ended':
            return 'Fim'
        elif status['description'] == 'Not started':
            return 'Início'
            
        # Verificar se o jogo está em andamento
        if status['type'] == 'inprogress':
            # Obter o tempo atual do jogo
            elapsed = status.get('elapsed', 0)
            
            # Determinar o tempo do jogo
            print(f"Tempo decorrido: {elapsed} minutos")
            print(f"Status completo: {json.dumps(status, indent=2)}")
            
            # Verificar período do jogo
            period = status.get('period', 1)
            print(f"Período do jogo: {period}")
            print(f"Status description: {status.get('description')}")
            
            # Verificar se está no segundo tempo baseado no tempo decorrido
            if elapsed > 45 or status.get('description', '').lower().startswith('2nd'):
                return "2ºT"
            # Caso contrário, está no primeiro tempo
            else:
                return "1ºT"
        
        return 'Início'
    except Exception as e:
        print(f"Erro ao formatar tempo: {e}")
        return 'Tempo indisponível'

def format_match_for_response(match):
    """
    Formata um jogo para resposta.
    
    Args:
        match: Dicionário com dados do jogo
    Returns:
        dict: Match formatado ou None se não estiver em andamento
    """
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
            print(f"Match processado: {match['id']} - {match['score']['home']} x {match['score']['away']}")
            formatted_matches.append(formatted_match)
    
    return {'matches': formatted_matches}

@app.route('/')
def index():
    matches = get_live_matches()
    formatted_matches = []
    
    for match in matches:
        formatted_match = format_match_for_response(match)
        if formatted_match:
            print(f"Match processado (index): {match['id']} - {match['score']['home']} x {match['score']['away']}")
            formatted_matches.append(formatted_match)
    
    return render_template('index.html', matches=formatted_matches)

if __name__ == '__main__':
    app.run(debug=True)
