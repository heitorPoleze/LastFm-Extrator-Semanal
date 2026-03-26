import os
from dotenv import load_dotenv
import requests
import pandas as pd
import json
from datetime import datetime

load_dotenv()
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")

def pegarUltimaSemanaCadastrada(user):
    url = f"{api_url}/2.0/?method=user.getWeeklyChartList&user={user}&api_key={api_key}&format=json"
    response = requests.get(url).json()
    data = response['weeklychartlist']['chart']
    ultimaSemana = data[-1]
    return ultimaSemana['from'], ultimaSemana['to']


def pegarArtistasEscutadosNaSemana(user):
    intervaloDeData = pegarUltimaSemanaCadastrada(user)

    url = f"{api_url}/2.0/?method=user.getweeklyartistchart&user={user}&api_key={api_key}&from={intervaloDeData[0]}&to={intervaloDeData[1]}&format=json"
    response = requests.get(url).json()
    artistas = response['weeklyartistchart']['artist']
    return artistas



#persistencia dos dados
def carregarArtistasEscutadosParaCSV(user):
    artistas = pegarArtistasEscutadosNaSemana(user)
    df = pd.DataFrame(artistas)
    df.to_csv('artistas.csv', index=False)

def pegarLogsDaExtracao(user):
    agora = datetime.now().isoformat()
    log = {
        'data_extracao': agora,
        'usuario_buscado': user,
        'quantidade_de_registros': None,
        'erro': None
    }
    return log

def fazerExtracaoDosDados(user):
    log = pegarLogsDaExtracao(user)
    try:
        carregarArtistasEscutadosParaCSV(user)
        df = pd.read_csv('artistas.csv')
        log['quantidade_de_registros'] = len(df)

    except Exception as e:
        log['erro'] = str(e)
    finally:
        historico = []
        if os.path.exists('extracoesDeDados.json') and os.path.getsize('extracoesDeDados.json') > 0:
            with open('extracoesDeDados.json', 'r', encoding='utf-8') as f:
                historico = json.load(f)

        historico.append(log)

        with open('extracoesDeDados.json', 'w', encoding='utf-8') as json_file:
            json.dump(historico, json_file, indent=4, ensure_ascii=False)


user = input("Digite o username desejado: ")
fazerExtracaoDosDados(user)

#amostra para bash
artistas = pegarArtistasEscutadosNaSemana(user)
for i in range(0, 6):
    print(f"Rank: {artistas[i]['@attr']['rank']} - Artista: {artistas[i]['name']} - Escutou: {artistas[i]['playcount']} vezes")