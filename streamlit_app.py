# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import poisson
import numpy as np
import warnings
import base64
import requests
from io import BytesIO
from textwrap import dedent
warnings.filterwarnings('ignore')

# Mapeamento de nomes dos times para URLs dos logos
TEAM_LOGOS = {
        "Vasco": "https://logodetimes.com/wp-content/uploads/vasco-da-gama.png",
        "Fortaleza": "https://logodetimes.com/wp-content/uploads/fortaleza.png",
        "Internacional": "https://logodetimes.com/wp-content/uploads/internacional.png",
        "Fluminense": "https://logodetimes.com/wp-content/uploads/fluminense.png",
        "Santos": "https://logodetimes.com/wp-content/uploads/santos.png",
        "Cuiaba": "https://logodetimes.com/wp-content/uploads/cuiaba.png",
        "Bragantino": "https://logodetimes.com/wp-content/uploads/red-bull-bragantino.png",
        "Red Bull Bragantino": "https://logodetimes.com/wp-content/uploads/red-bull-bragantino.png",
        "Bragantino": "https://logodetimes.com/wp-content/uploads/red-bull-bragantino.png",
        "Botafogo": "https://logodetimes.com/wp-content/uploads/botafogo.png",
        "Cruzeiro": "https://logodetimes.com/wp-content/uploads/cruzeiro.png",
        "Bahia": "https://logodetimes.com/wp-content/uploads/bahia.png",
        "Athletico PR": "https://logodetimes.com/wp-content/uploads/athletico-paranaense.png",
        "Athletico-PR": "https://logodetimes.com/wp-content/uploads/athletico-paranaense.png",
        "A. Paranaense": "https://logodetimes.com/wp-content/uploads/athletico-paranaense.png",
        "Atletico MG": "https://logodetimes.com/wp-content/uploads/atletico-mineiro.png",
        "Atlético-MG": "https://logodetimes.com/wp-content/uploads/atletico-mineiro.png",
        "A. Mineiro": "https://logodetimes.com/wp-content/uploads/atletico-mineiro.png",
        "Sao Paulo": "https://logodetimes.com/wp-content/uploads/sao-paulo.png",
        "São Paulo": "https://logodetimes.com/wp-content/uploads/sao-paulo.png",
        "SÃ£o Paulo": "https://logodetimes.com/wp-content/uploads/sao-paulo.png",
        "Gremio": "https://logodetimes.com/wp-content/uploads/gremio.png",
        "Grêmio": "https://logodetimes.com/wp-content/uploads/gremio.png",
        "Flamengo": "https://logodetimes.com/wp-content/uploads/flamengo.png",
        "Corinthians": "https://logodetimes.com/wp-content/uploads/corinthians.png",
        "Ceara": "https://logodetimes.com/wp-content/uploads/ceara.png",
        "Ceará": "https://logodetimes.com/wp-content/uploads/ceara.png",
        "Vitoria": "https://logodetimes.com/wp-content/uploads/vitoria.png",
        "Vitória": "https://logodetimes.com/wp-content/uploads/vitoria.png",
        "Sport": "https://logodetimes.com/wp-content/uploads/sport-recife.png",
        "Sport Recife": "https://logodetimes.com/wp-content/uploads/sport-recife.png",
        "Mirassol": "https://logodetimes.com/wp-content/uploads/mirassol.png",
        "Mirasol": "https://logodetimes.com/wp-content/uploads/mirassol.png",
        "Atletico GO": "https://logodetimes.com/wp-content/uploads/atletico-goianiense.png",
        "Atlético-GO": "https://logodetimes.com/wp-content/uploads/atletico-goianiense.png",
        "A. Goianiense": "https://logodetimes.com/wp-content/uploads/atletico-goianiense.png",
        "Criciuma": "https://logodetimes.com/wp-content/uploads/criciuma.png",
        "Criciúma": "https://logodetimes.com/wp-content/uploads/criciuma.png",
        "Juventude": "https://logodetimes.com/wp-content/uploads/juventude-rs.png",
        "Palmeiras": "https://logodetimes.com/wp-content/uploads/palmeiras.png",
        "Remo": "https://logodetimes.com/wp-content/uploads/remo.png",
        "Coritiba": "https://logodetimes.com/wp-content/uploads/coritiba.png",
        "Chapecoense" : "https://logodetimes.com/wp-content/uploads/chapecoense.png",
    }

def normalize_team_name(team_name):
    """Normaliza nome do time para buscar logo e exibição correta"""
    replacements = {
        'SÃ£o': 'São',
        'Ã¡': 'á',
        'Ã ': 'à',
        'Ã³': 'ó',
        'Ãª': 'ê',
        'Ã¢': 'â',
        'Ã§': 'ç',
        'Ã­': 'í',
        'Ãº': 'ú'
    }
    
    normalized = team_name
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized

def _clean_html(s: str) -> str:
    """Remove indentação comum e espaços extras no início/fim para evitar code blocks no Markdown."""
    return dedent(s).strip()

def get_team_display_name_with_logo(team_name, logo_size=(80, 80)):
    """
    Retorna HTML (string) para exibir o nome do time com logo.
    SEM indentação à esquerda para não virar bloco de código no Markdown.
    """
    normalized_name = normalize_team_name(team_name)
    logo_url = TEAM_LOGOS.get(normalized_name) or TEAM_LOGOS.get(team_name)
    if logo_url:
        return f'<div style="display:flex; align-items:center; gap:8px; margin:2px 0;"><div style="background-color:transparent; display:flex; align-items:center;"><img src="{logo_url}" style="width:{logo_size[0]}px; height:{logo_size[1]}px; object-fit:contain; background:none;" onerror="this.style.display=\'none\';" alt="{normalized_name}"></div><span style="font-weight:500; color:#FFFFFF; font-size:28px;">{normalized_name}</span></div>'
    # fallback
    return f'<span>⚽</span> <span style="font-weight:500; color:#FFFFFF; font-size:28px;">{normalized_name}</span>'
def display_team_with_logo(team_name, logo_size=(80, 80)):
    """
    Exibe diretamente no Streamlit o time com logo.
    """
    st.markdown(get_team_display_name_with_logo(team_name, logo_size), unsafe_allow_html=True)

def create_team_selectbox_with_logos(label, teams, key, logo_size=(80, 80)):
    """
    Cria selectbox e exibe abaixo o time selecionado com logo (HTML limpo).
    """
    if not teams:
        return st.selectbox(label, [], key=key)

    selected_team = st.selectbox(label, teams, key=key)

    if selected_team:
        st.markdown(
            _clean_html(f"""
<div style="margin-top:-10px; margin-bottom:10px;">
  {get_team_display_name_with_logo(selected_team, logo_size)}
</div>
"""),
            unsafe_allow_html=True,
        )
    return selected_team

def display_vs_matchup(team_home, team_away):
    """
    Exibe confronto entre dois times com logos, centralizado.
    """
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown(
            _clean_html(f"""
<div style="text-align:right;">
  {get_team_display_name_with_logo(team_home, logo_size=(70, 70))}
</div>
"""),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            _clean_html("""
<h3 style="text-align:center; color:#1f4e79; margin:10px 0;">VS</h3>
"""),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            _clean_html(f"""
<div style="text-align:left;">
  {get_team_display_name_with_logo(team_away, logo_size=(70, 70))}
</div>
"""),
            unsafe_allow_html=True,
        )

def display_score_result_with_logos(team_home, score_home, score_away, team_away):
    """
    Exibe resultado do placar com logos dos times.
    IMPORTANTE: sem indentação à esquerda no HTML.
    """
    logo_url_home = TEAM_LOGOS.get(team_home, "")
    logo_url_away = TEAM_LOGOS.get(team_away, "")

    result_html = _clean_html(f"""
<div style="display:flex; align-items:center; justify-content:center; gap:15px;
            background:linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            padding:20px; border-radius:12px; margin:15px 0;
            border:2px solid #4caf50; box-shadow:0 4px 12px rgba(0,0,0,0.15);">

  <div style="display:flex; align-items:center; gap:10px;">
    <img src="{logo_url_home}"
         style="width:70px; height:70px; border-radius:5px; object-fit:contain;"
         onerror="this.style.display='none';"
         alt="{team_home}">
    <span style="font-weight:bold; font-size:1.1em; color:#2e7d32;">{team_home}</span>
  </div>

  <div style="font-size:2em; font-weight:bold; color:#1b5e20;
              background-color:white; padding:10px 20px; border-radius:25px;
              box-shadow:0 2px 6px rgba(0,0,0,0.1); min-width:120px; text-align:center;">
    {score_home} × {score_away}
  </div>

  <div style="display:flex; align-items:center; gap:10px;">
    <span style="font-weight:bold; font-size:1.1em; color:#2e7d32;">{team_away}</span>
    <img src="{logo_url_away}"
         style="width:70px; height:70px; border-radius:5px; object-fit:contain;"
         onerror="this.style.display='none';"
         alt="{team_away}">
  </div>
</div>
""")

    st.markdown(result_html, unsafe_allow_html=True)

# Configuração da página atualizada
st.set_page_config(
    page_title="⚽ Análise & Estatística Brasileirão",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado atualizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .stSelectbox label {
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
    }
    
    .analysis-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .filter-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-left: 4px solid #1f4e79;
    }
    
    .option-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .option-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f4e79;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .year-selector {
        text-align: center;
        margin: 1rem 0;
    }
    
    .start-button {
        background: linear-gradient(45deg, #1f4e79, #2d5aa0);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .start-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("BRA_DADOS_2425_B.csv", sep=';', encoding='latin1')

        # Validação da coluna Ano
        if 'Ano' not in df.columns:
            st.error("⚠ A coluna 'Ano' é obrigatória para filtrar os dados por período.")
            return pd.DataFrame()

        # Renomear colunas problemáticas, se necessário
        if 'Gols  Away' in df.columns:
            df = df.rename(columns={'Gols  Away': 'Gols Away'})

        # Limpeza básica
        df = df.dropna(subset=['Home', 'Away', 'Ano'])
        df = df[df['Home'].str.strip() != '']
        df = df[df['Away'].str.strip() != '']

        # Conversão de tipos
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
        numeric_columns = ['Gols Home', 'Gols Away', 'odd Home', 'odd Draw', 'odd Away',
                           ' Home', ' Away', 'Total  Match', 'Home Score HT', 'Away Score HT']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Coluna Resultado e Total Gols
        df['Resultado Home'] = df.apply(
            lambda row: 'Vitória' if row['Gols Home'] > row['Gols Away']
            else 'Empate' if row['Gols Home'] == row['Gols Away']
            else 'Derrota', axis=1)
        df['Total Gols'] = df['Gols Home'] + df['Gols Away']

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

def calculate_team_stats(df, team_name, as_home=True):
    """
    Calcula estatísticas de um time específico
    
    Args:
        df: DataFrame com os dados dos jogos
        team_name: Nome do time
        as_home: True para estatísticas como mandante, False como visitante
    
    Returns:
        dict: Dicionário com as estatísticas do time
    """
    try:
        if as_home:
            # Jogos como mandante
            team_games = df[df['Home'] == team_name].copy()
            gols_feitos_col = 'Gols Home'
            gols_sofridos_col = 'Gols Away'
            escanteios_feitos_col = ' Home'
            escanteios_sofridos_col = ' Away'
        else:
            # Jogos como visitante
            team_games = df[df['Away'] == team_name].copy()
            gols_feitos_col = 'Gols Away'
            gols_sofridos_col = 'Gols Home'
            escanteios_feitos_col = 'Corner Away'
            escanteios_sofridos_col = 'Corner Home'
        
        if team_games.empty:
            return {
                'jogos': 0,
                'vitorias': 0,
                'empates': 0,
                'derrotas': 0,
                'gols_feitos': 0,
                'gols_sofridos': 0,
                'media_gols_feitos': 0,
                'media_gols_sofridos': 0,
                'escanteios_feitos': 0,
                'escanteios_sofridos': 0,
                'media_escanteios_feitos': 0,
                'media_escanteios_sofridos': 0
            }
        
        # Calcula resultados
        if as_home:
            vitorias = len(team_games[team_games['Resultado Home'] == 'Vitória'])
            empates = len(team_games[team_games['Resultado Home'] == 'Empate'])
            derrotas = len(team_games[team_games['Resultado Home'] == 'Derrota'])
        else:
            vitorias = len(team_games[team_games['Resultado Home'] == 'Derrota'])  # Vitória do visitante
            empates = len(team_games[team_games['Resultado Home'] == 'Empate'])
            derrotas = len(team_games[team_games['Resultado Home'] == 'Vitória'])  # Derrota do visitante
        
        # Calcula gols
        gols_feitos = team_games[gols_feitos_col].sum() if gols_feitos_col in team_games.columns else 0
        gols_sofridos = team_games[gols_sofridos_col].sum() if gols_sofridos_col in team_games.columns else 0
        
        # Calcula escanteios
        escanteios_feitos = team_games[escanteios_feitos_col].sum() if escanteios_feitos_col in team_games.columns else 0
        escanteios_sofridos = team_games[escanteios_sofridos_col].sum() if escanteios_sofridos_col in team_games.columns else 0
        
        jogos = len(team_games)
        
        return {
            'jogos': jogos,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_feitos': gols_feitos,
            'gols_sofridos': gols_sofridos,
            'media_gols_feitos': gols_feitos / jogos if jogos > 0 else 0,
            'media_gols_sofridos': gols_sofridos / jogos if jogos > 0 else 0,
            'escanteios_feitos': escanteios_feitos,
            'escanteios_sofridos': escanteios_sofridos,
            'media_escanteios_feitos': escanteios_feitos / jogos if jogos > 0 else 0,
            'media_escanteios_sofridos': escanteios_sofridos / jogos if jogos > 0 else 0
        }
        
    except Exception as e:
        st.error(f"Erro ao calcular estatísticas do time {team_name}: {str(e)}")
        return {
            'jogos': 0,
            'vitorias': 0,
            'empates': 0,
            'derrotas': 0,
            'gols_feitos': 0,
            'gols_sofridos': 0,
            'media_gols_feitos': 0,
            'media_gols_sofridos': 0,
            'escanteios_feitos': 0,
            'escanteios_sofridos': 0,
            'media_escanteios_feitos': 0,
            'media_escanteios_sofridos': 0
        }

def calculate_implicit_probabilities(home_odd, draw_odd, away_odd):
    """Calcula probabilidades implícitas das odds"""
    try:
        if home_odd <= 0 or draw_odd <= 0 or away_odd <= 0:
            return 0, 0, 0
        home_prob = 1 / home_odd * 100
        draw_prob = 1 / draw_odd * 100
        away_prob = 1 / away_odd * 100
        return home_prob, draw_prob, away_prob
    except Exception as e:
        st.error(f"Erro no cálculo de probabilidades: {str(e)}")
        return 0, 0, 0

def predict_score_poisson(home_avg, away_avg, home_def, away_def):
    """Prediz placar usando distribuição de Poisson"""
    try:
        # Calcula gols esperados
        home_goals_expected = max(0.1, (home_avg + away_def) / 2)
        away_goals_expected = max(0.1, (away_avg + home_def) / 2)
        
        # Encontra o placar mais provável
        max_prob = 0
        best_score = (0, 0)
        
        for home_goals in range(6):
            for away_goals in range(6):
                prob = poisson.pmf(home_goals, home_goals_expected) * poisson.pmf(away_goals, away_goals_expected)
                if prob > max_prob:
                    max_prob = prob
                    best_score = (home_goals, away_goals)
        
        return best_score, max_prob, home_goals_expected, away_goals_expected
    except Exception as e:
        st.error(f"Erro na predição: {str(e)}")
        return (0, 0), 0, 0, 0

def show_interactive_charts(df):
    """
    Gera gráficos comparativos entre equipes mandante e visitante.
    
    Args:
        df (DataFrame): DataFrame contendo os dados dos jogos
    """
    
    st.header("📊 Gráficos Comparativos (Mandante x Visitante)")
    
    # Verificar se há dados suficientes
    if df.empty:
        st.warning("⚠️ Não há dados disponíveis para análise.")
        return
    
    # CORREÇÃO: Adicionar indentação correta (4 espaços)
    # Obter lista única de times
    teams = get_unique_teams(df)
    if len(teams) < 2:
        st.warning("⚠️ É necessário pelo menos 2 times diferentes para comparação.")
        return
    
    # Interface de seleção de times
    team_home, team_away = create_team_selection_interface(teams)
    if not validate_team_selection(team_home, team_away):
        st.warning("⚠️ Por favor, selecione dois times diferentes.")
        return
    
# Verificar colunas necessárias
    if not validate_required_columns(df):
        return
    
    # CORREÇÃO: Adicionar indentação correta (4 espaços)
    # Calcular estatísticas
    stats = calculate_team_statistics(df, team_home, team_away)
    
    # Gerar gráficos
    generate_comparative_charts(stats, team_home, team_away)


def get_unique_teams(df):
    """
    Extrai lista única de times dos dados.
    
    Args:
        df (DataFrame): DataFrame com dados dos jogos
    
    Returns:
        list: Lista ordenada de times únicos
    """
    home_teams = df['Home'].dropna().unique().tolist()
    away_teams = df['Away'].dropna().unique().tolist()
    all_teams = set(home_teams + away_teams)
    return sorted(list(all_teams))


def create_team_selection_interface(teams):
    """
    Cria interface para seleção de times.
    
    Args:
        teams (list): Lista de times disponíveis
    
    Returns:
        tuple: (team_home, team_away)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        team_home = st.selectbox(
            "🏠 Selecione o Time Mandante:",
            options=teams,
            key="chart_home",
            help="Time que jogará como mandante na comparação"
        )
    
    with col2:
        team_away = st.selectbox(
            "✈️ Selecione o Time Visitante:",
            options=teams,
            key="chart_away",
            help="Time que jogará como visitante na comparação"
        )
    
    return team_home, team_away

def validate_team_selection(team_home, team_away):
    """
    Valida se a seleção de times está correta.
    
    Args:
        team_home (str): Time mandante selecionado
        team_away (str): Time visitante selecionado
    
    Returns:
        bool: True se seleção válida, False caso contrário
    """
    return team_home and team_away and team_home != team_away

def validate_required_columns(df):
    """
    Verifica se todas as colunas necessárias estão presentes no DataFrame.
    
    Args:
        df (DataFrame): DataFrame a ser validado
    
    Returns:
        bool: True se todas as colunas existem, False caso contrário
    """
    required_columns = ['Home', 'Away', 'Gols Home', 'Gols Away', 'Home Score HT', 'Away Score HT']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"⚠ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
        return False
    
    return True


def calculate_team_statistics(df, team_home, team_away):
    """
    Calcula estatísticas para os times selecionados.
    
    Args:
        df (DataFrame): DataFrame com dados dos jogos
        team_home (str): Time mandante
        team_away (str): Time visitante
        
    Returns:
        dict: Dicionário com estatísticas calculadas
    """
    # Filtrar jogos onde cada time atua em sua respectiva condição
    home_games = df[df['Home'] == team_home].copy()
    away_games = df[df['Away'] == team_away].copy()
    
    # Calcular estatísticas do time mandante (quando joga em casa)
    home_stats = {
        'gols_marcados': home_games['Gols Home'].sum(),
        'gols_sofridos': home_games['Gols Away'].sum(),
        'gols_marcados_ht': home_games['Home Score HT'].sum(),
        'gols_sofridos_ht': home_games['Away Score HT'].sum(),
        'total_jogos': len(home_games)
    }
    
    # Calcular estatísticas do time visitante (quando joga fora)
    away_stats = {
        'gols_marcados': away_games['Gols Away'].sum(),
        'gols_sofridos': away_games['Gols Home'].sum(),
        'gols_marcados_ht': away_games['Away Score HT'].sum(),
        'gols_sofridos_ht': away_games['Home Score HT'].sum(),
        'total_jogos': len(away_games)
    }
    
    return {
        'home': home_stats,
        'away': away_stats
    }

def generate_comparative_charts(stats, team_home, team_away):
    """
    Gera todos os gráficos comparativos.
    
    Args:
        stats (dict): Estatísticas calculadas
        team_home (str): Nome do time mandante
        team_away (str): Nome do time visitante
    """
    
    # Definir configurações dos gráficos
    chart_configs = [
        {
            'title': '⚽ Total de Gols Marcados',
            'subtitle': f'{team_home} (Mandante) vs {team_away} (Visitante)',
            'home_value': stats['home']['gols_marcados'],
            'away_value': stats['away']['gols_marcados'],
            'y_label': 'Gols Marcados',
            'color_home': '#1f77b4',
            'color_away': '#ff7f0e'
        },
        {
            'title': '🥅 Total de Gols Sofridos',
            'subtitle': f'{team_home} (Mandante) vs {team_away} (Visitante)',
            'home_value': stats['home']['gols_sofridos'],
            'away_value': stats['away']['gols_sofridos'],
            'y_label': 'Gols Sofridos',
            'color_home': '#d62728',
            'color_away': '#ff9896'
        },
        {
            'title': '🕐 Gols Marcados no 1º Tempo',
            'subtitle': f'{team_home} (Mandante) vs {team_away} (Visitante)',
            'home_value': stats['home']['gols_marcados_ht'],
            'away_value': stats['away']['gols_marcados_ht'],
            'y_label': 'Gols no 1º Tempo',
            'color_home': '#2ca02c',
            'color_away': '#98df8a'
        },
        {
            'title': '🕐 Gols Sofridos no 1º Tempo',
            'subtitle': f'{team_home} (Mandante) vs {team_away} (Visitante)',
            'home_value': stats['home']['gols_sofridos_ht'],
            'away_value': stats['away']['gols_sofridos_ht'],
            'y_label': 'Gols Sofridos no 1º Tempo',
            'color_home': '#9467bd',
            'color_away': '#c5b0d5'
        }
    ]
    
    # Criar layout em colunas para melhor visualização
    for i in range(0, len(chart_configs), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(chart_configs):
                create_bar_chart(chart_configs[i], team_home, team_away)
        
        with col2:
            if i + 1 < len(chart_configs):
                create_bar_chart(chart_configs[i + 1], team_home, team_away)
    
    # Exibir resumo estatístico
    display_statistics_summary(stats, team_home, team_away)

def create_bar_chart(config, team_home, team_away):
    """
    Cria um gráfico de barras individual.
    
    Args:
        config (dict): Configurações do gráfico
        team_home (str): Nome do time mandante
        team_away (str): Nome do time visitante
    """
    
    fig = go.Figure()
    
    # Adicionar barras
    fig.add_trace(go.Bar(
        x=[f"{team_home}\n(Mandante)", f"{team_away}\n(Visitante)"],
        y=[config['home_value'], config['away_value']],
        marker_color=[config['color_home'], config['color_away']],
        text=[config['home_value'], config['away_value']],
        textposition="auto",
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{x}</b><br>' +
                     f'{config["y_label"]}: %{{y}}<br>' +
                     '<extra></extra>'
    ))
    
    # Configurar layout
    fig.update_layout(
        title={
            'text': f"<b>{config['title']}</b><br><sub>{config['subtitle']}</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        yaxis_title=config['y_label'],
        xaxis_title="Times",
        showlegend=False,
        height=400,
        margin=dict(t=80, b=50, l=50, r=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    # Estilizar eixos
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    st.plotly_chart(fig, use_container_width=True)

def display_statistics_summary(stats, team_home, team_away):
    """
    Exibe resumo estatístico dos times.
    """
    try:
        st.subheader("📋 Análise Estatística Detalhada")
        analysis = calculate_advanced_metrics(stats, team_home, team_away)
        display_basic_summary(stats, team_home, team_away, analysis)
        display_first_half_analysis(stats, analysis, team_home, team_away)
    except Exception as e:
        st.error(f"⚠ Erro na análise estatística: {str(e)}")
        st.info("💡 Verifique se os dados estão completos e tente novamente.")
        st.write("Debug - Valores recebidos:")
        st.write(f"Stats home: {stats.get('home', 'N/A')}")
        st.write(f"Stats away: {stats.get('away', 'N/A')}")

def calculate_advanced_metrics(stats, team_home, team_away):
    """
    Calcula metricas avancadas para analise profissional.
    
    Args:
        stats (dict): Estatisticas basicas
        team_home (str): Nome do time mandante
        team_away (str): Nome do time visitante
        
    Returns:
        dict: Metricas avancadas calculadas
    """
    
    # Funcao auxiliar para converter valores de forma segura
    def safe_int(value):
        try:
            if pd.isna(value):
                return 0
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def safe_float(value):
        try:
            if pd.isna(value):
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
            
    # Converter valores de forma segura
    home_gols_marcados = safe_int(stats['home']['gols_marcados'])
    home_gols_sofridos = safe_int(stats['home']['gols_sofridos'])
    away_gols_marcados = safe_int(stats['away']['gols_marcados'])
    away_gols_sofridos = safe_int(stats['away']['gols_sofridos'])
    
    home_jogos = max(safe_int(stats['home']['total_jogos']), 1)  # Evitar divisão por zero
    away_jogos = max(safe_int(stats['away']['total_jogos']), 1)
    
    home_ht_marcados = safe_int(stats['home']['gols_marcados_ht'])
    away_ht_marcados = safe_int(stats['away']['gols_marcados_ht'])

    # Saldos de gols
    home_saldo = home_gols_marcados - home_gols_sofridos
    away_saldo = away_gols_marcados - away_gols_sofridos

    return {
        'home_media_gols': round(home_gols_marcados / home_jogos, 2),
        'home_media_sofridos': round(home_gols_sofridos / home_jogos, 2),
        'away_media_gols': round(away_gols_marcados / away_jogos, 2),
        'away_media_sofridos': round(away_gols_sofridos / away_jogos, 2),

        # Saldos (garantindo que são inteiros)
        'home_saldo': home_saldo,
        'away_saldo': away_saldo,

        # Eficiência no primeiro tempo (%)
        'home_ht_eficiencia': round((home_ht_marcados / max(home_gols_marcados, 1)) * 100, 1),
        'away_ht_eficiencia': round((away_ht_marcados / max(away_gols_marcados, 1)) * 100, 1),

        # Valores absolutos para exibição
        'home_gols_total': home_gols_marcados,
        'home_sofridos_total': home_gols_sofridos,
        'away_gols_total': away_gols_marcados,
        'away_sofridos_total': away_gols_sofridos,
        'home_ht_gols': home_ht_marcados,
        'away_ht_gols': away_ht_marcados,
        'home_jogos': home_jogos,
        'away_jogos': away_jogos,

        # Comparativos
        'melhor_ataque': team_home if home_gols_marcados > away_gols_marcados else team_away,
        'melhor_defesa': team_home if home_gols_sofridos < away_gols_sofridos else team_away,
        'melhor_ht': team_home if home_ht_marcados > away_ht_marcados else team_away
    }


def display_basic_summary(stats, team_home, team_away, analysis):
    """Exibe resumo básico dos times."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Determinar ícone do saldo sem usar formatação problemática
        saldo_home = analysis['home_saldo']
        if saldo_home > 0:
            saldo_icon = "📈"
            saldo_text = f"+{saldo_home}"
        elif saldo_home < 0:
            saldo_icon = "📉"
            saldo_text = str(saldo_home)
        else:
            saldo_icon = "➖"
            saldo_text = "0"
            
        st.info(f"""
        **{team_away} (Como Visitante)**
        - Jogos analisados: **{analysis['away_jogos']}**
        - Gols marcados: **{analysis['away_gols_total']}** (média: {analysis['away_media_gols']}/jogo)
        - Gols sofridos: **{analysis['away_sofridos_total']}** (média: {analysis['away_media_sofridos']}/jogo)
        - {saldo_icon} Saldo de gols: **{saldo_text}**
        """)


def display_first_half_analysis(stats, analysis, team_home, team_away):
    """Exibe análise específica do primeiro tempo."""
    st.subheader("🕐 Análise do Primeiro Tempo")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=f"🏠 {team_home} - Eficiência 1º Tempo",
            value=f"{analysis['home_ht_eficiencia']}%",
            delta=f"{analysis['home_ht_gols']} de {analysis['home_gols_total']} gols"
        )
    with col2:
        st.metric(
            label=f"✈️ {team_away} - Eficiência 1º Tempo",
            value=f"{analysis['away_ht_eficiencia']}%",
            delta=f"{analysis['away_ht_gols']} de {analysis['away_gols_total']} gols"
        )

    # Estatísticas detalhadas
    st.subheader("📈 Estatísticas Detalhadas")
    
    # Usar os dados já calculados em stats
    col1, col2 = st.columns(2)
    with col1:
        st.write("**🏠 Como Mandante:**")
        st.write(f"Jogos: {analysis['home_jogos']}")
        st.write(f"Gols Marcados: {analysis['home_gols_total']}")
        st.write(f"Gols Sofridos: {analysis['home_sofridos_total']}")
        st.write(f"Gols/Jogo: {analysis['home_media_gols']:.2f}")
        st.write(f"Gols Sofridos/Jogo: {analysis['home_media_sofridos']:.2f}")
        st.write(f"Saldo de Gols: {analysis['home_saldo']}")
        
    with col2:
        st.write("**✈️ Como Visitante:**")
        st.write(f"Jogos: {analysis['away_jogos']}")
        st.write(f"Gols Marcados: {analysis['away_gols_total']}")
        st.write(f"Gols Sofridos: {analysis['away_sofridos_total']}")
        st.write(f"Gols/Jogo: {analysis['away_media_gols']:.2f}")
        st.write(f"Gols Sofridos/Jogo: {analysis['away_media_sofridos']:.2f}")
        st.write(f"Saldo de Gols: {analysis['away_saldo']}")

def show_first_half_analysis(df, teams):
    html_content = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
    <h1 style="color: white; margin: 0; text-align: center; font-size: 32px;">Analise Primeiro Tempo HT</h1>
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)
    
    if len(teams) < 2:
        st.warning("Selecione pelo menos dois times.")
        return
    
    # Seleção de times com logos
    st.subheader("⚽ Seleção de Times")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🏠 **Time Mandante:**")
        team_home = st.selectbox("Selecione o mandante:", teams, key="ht_home", label_visibility="collapsed")
        display_team_with_logo(team_home, logo_size=(40, 40))
    
    with col2:
        st.write("✈️ **Time Visitante:**")
        team_away = st.selectbox("Selecione o visitante:", teams, key="ht_away", label_visibility="collapsed")
        display_team_with_logo(team_away, logo_size=(40, 40))
    
    if not team_home or not team_away or team_home == team_away:
        st.warning("Selecione dois times diferentes.")
        return
    
    # Verificar colunas necessárias
    required_cols = ['Home Score HT', 'Away Score HT', 'Gols Home', 'Gols Away']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠ Colunas necessárias não encontradas: {', '.join(missing_cols)}")
        return

    st.markdown("---")
    
    # Filtrar jogos - TODOS os jogos do time na posição
    home_games = df[df['Home'] == team_home].copy()
    away_games = df[df['Away'] == team_away].copy()
    
    # Calcular estatísticas do 1º tempo
    home_ht_stats = calculate_ht_stats(home_games, True)
    away_ht_stats = calculate_ht_stats(away_games, False)
    
    # Tabela comparativa moderna
    display_modern_comparison_table(home_ht_stats, away_ht_stats, team_home, team_away)
    
    # Gráfico comparativo profissional
    display_professional_ht_chart(home_ht_stats, away_ht_stats, team_home, team_away)
    
    # Análise completa de cenários HT para FT
    display_complete_scenario_analysis(home_games, away_games, team_home, team_away)

def calculate_ht_stats(games, is_home):
    """Calcula estatísticas do Primeiro tempo"""
    if games.empty:
        return {
            'jogos': 0,
            'gols_feitos_ht': 0,
            'gols_sofridos_ht': 0,
            'media_feitos_ht': 0,
            'media_sofridos_ht': 0
        }
    
    jogos = len(games)
    
    if is_home:
        gols_feitos_ht = games['Home Score HT'].sum()
        gols_sofridos_ht = games['Away Score HT'].sum()
    else:
        gols_feitos_ht = games['Away Score HT'].sum()
        gols_sofridos_ht = games['Home Score HT'].sum()
    
    return {
        'jogos': jogos,
        'gols_feitos_ht': int(gols_feitos_ht),
        'gols_sofridos_ht': int(gols_sofridos_ht),
        'media_feitos_ht': gols_feitos_ht / jogos if jogos > 0 else 0,
        'media_sofridos_ht': gols_sofridos_ht / jogos if jogos > 0 else 0
    }

def display_modern_comparison_table(home_stats, away_stats, team_home, team_away):
    """Exibe tabela comparativa moderna e profissional"""
    
    st.markdown('<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"><h2 style="color: white; margin: 0; text-align: center; font-size: 26px;">Comparativo Estatistico - Primeiro Tempo</h2></div>', unsafe_allow_html=True)
    
    # Formatar valores antes de usar no HTML
    media_feitos_home = f"{home_stats['media_feitos_ht']:.2f}"
    media_feitos_away = f"{away_stats['media_feitos_ht']:.2f}"
    media_sofridos_home = f"{home_stats['media_sofridos_ht']:.2f}"
    media_sofridos_away = f"{away_stats['media_sofridos_ht']:.2f}"
    
    html_table = f"""
    <table class="custom-table">
        <thead>
            <tr>
                <th>Metrica</th>
                <th>{team_home} (Mandante)</th>
                <th>{team_away} (Visitante)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Jogos Analisados</td>
                <td>{home_stats['jogos']}</td>
                <td>{away_stats['jogos']}</td>
            </tr>
            <tr>
                <td>Gols Feitos no Primeiro Tempo</td>
                <td>{home_stats['gols_feitos_ht']}</td>
                <td>{away_stats['gols_feitos_ht']}</td>
            </tr>
            <tr>
                <td>Gols Sofridos no Primeiro Tempo</td>
                <td>{home_stats['gols_sofridos_ht']}</td>
                <td>{away_stats['gols_sofridos_ht']}</td>
            </tr>
            <tr>
                <td>Media Gols Feitos por Jogo</td>
                <td>{media_feitos_home}</td>
                <td>{media_feitos_away}</td>
            </tr>
            <tr>
                <td>Media Gols Sofridos por Jogo</td>
                <td>{media_sofridos_home}</td>
                <td>{media_sofridos_away}</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)
    
def display_professional_ht_chart(home_stats, away_stats, team_home, team_away):
    """Exibe grafico comparativo profissional"""
    
    header_html = """
<div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <h2 style="color: white; margin: 0; text-align: center; font-size: 26px;">Grafico Comparativo - Primeiro Tempo</h2>
</div>
"""
    st.markdown(header_html, unsafe_allow_html=True)
    
    fig = go.Figure()
    
    metrics = ["Gols Feitos<br>(1 T)", "Gols Sofridos<br>(1 T)", "Média Feitos<br>(1 T)", "Média Sofridos<br>(1 T)"]
    home_values = [
        home_stats['gols_feitos_ht'], 
        home_stats['gols_sofridos_ht'],
        home_stats['media_feitos_ht'],
        home_stats['media_sofridos_ht']
    ]
    away_values = [
        away_stats['gols_feitos_ht'], 
        away_stats['gols_sofridos_ht'],
        away_stats['media_feitos_ht'],
        away_stats['media_sofridos_ht']
    ]
    
    fig.add_trace(go.Bar(
        x=metrics, 
        y=home_values, 
        name=f"🏠 {team_home}", 
        marker_color='#2196F3',
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in home_values],
        textposition='auto',
        textfont=dict(size=14, color='white')
    ))
    
    fig.add_trace(go.Bar(
        x=metrics, 
        y=away_values, 
        name=f"✈️ {team_away}", 
        marker_color='#FF6B6B',
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in away_values],
        textposition='auto',
        textfont=dict(size=14, color='white')
    ))
    
    fig.update_layout(
        barmode='group',
        xaxis_title="Métricas",
        yaxis_title="Valores",
        xaxis=dict(
            gridcolor='#404040',
            color='white'
        ),
        yaxis=dict(
            gridcolor='#404040',
            color='white'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14, color='white')
        ),
        title=dict(
            text=f"Desempenho Primeiro Tempo: {team_home} vs {team_away}",
            font=dict(size=20, color='white')
        ),
        height=500,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#0d0d0d',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_complete_scenario_analysis(home_games, away_games, team_home, team_away):
    """Exibe analise completa de todos os cenarios HT para FT"""
    
    st.markdown('<div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"><h2 style="color: white; margin: 0; text-align: center; font-size: 26px;">Analise de Cenarios: Primeiro Tempo para Resultado Final</h2></div>', unsafe_allow_html=True)
    
    # Analisar cenários completos
    home_scenarios = analyze_all_scenarios(home_games, True)
    away_scenarios = analyze_all_scenarios(away_games, False)
    
    # Exibir lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        display_scenario_stats(home_scenarios, team_home, "🏠 Mandante", "#2196F3")
    
    with col2:
        display_scenario_stats(away_scenarios, team_away, "✈️ Visitante", "#FF6B6B")

def analyze_all_scenarios(games, is_home):
    """Analisa todos os cenários possíveis HT para FT"""
    scenarios = {
        # Vencendo no HT
        'ht_win_ft_win': 0,
        'ht_win_ft_draw': 0,
        'ht_win_ft_loss': 0,
        # Empatando no HT
        'ht_draw_ft_win': 0,
        'ht_draw_ft_draw': 0,
        'ht_draw_ft_loss': 0,
        # Perdendo no HT
        'ht_loss_ft_win': 0,
        'ht_loss_ft_draw': 0,
        'ht_loss_ft_loss': 0
    }
    
    if games.empty:
        return scenarios
    
    for _, game in games.iterrows():
        if is_home:
            ht_team = game['Home Score HT']
            ht_opp = game['Away Score HT']
            ft_team = game['Gols Home']
            ft_opp = game['Gols Away']
        else:
            ht_team = game['Away Score HT']
            ht_opp = game['Home Score HT']
            ft_team = game['Gols Away']
            ft_opp = game['Gols Home']
        
        # Resultado HT
        if ht_team > ht_opp:
            ht_result = 'win'
        elif ht_team < ht_opp:
            ht_result = 'loss'
        else:
            ht_result = 'draw'
        
        # Resultado FT
        if ft_team > ft_opp:
            ft_result = 'win'
        elif ft_team < ft_opp:
            ft_result = 'loss'
        else:
            ft_result = 'draw'
        
        # Mapear cenário
        scenario_key = f"ht_{ht_result}_ft_{ft_result}"
        if scenario_key in scenarios:
            scenarios[scenario_key] += 1
    
    return scenarios

def display_scenario_stats(scenarios, team_name, position, color):
    """Exibe estatisticas de cenarios de forma profissional"""
    total_games = sum(scenarios.values())
    
    st.markdown(f'<div style="background: linear-gradient(135deg, {color} 0%, {color}CC 100%); padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center;"><h3 style="color: white; margin: 0; font-size: 22px;">{position} {team_name}</h3><p style="color: white; margin: 5px 0; font-size: 16px;">Total: {total_games} jogos</p></div>', unsafe_allow_html=True)
    
    # Organizar cenarios por categoria
    scenarios_data = [
        ("Vencendo no 1T", [
            ("HT Vitoria para FT Vitoria", scenarios['ht_win_ft_win'], "Vitoria"),
            ("HT Vitoria para FT Empate", scenarios['ht_win_ft_draw'], "Empate"),
            ("HT Vitoria para FT Derrota", scenarios['ht_win_ft_loss'], "Derrota")
        ]),
        ("Empatando no 1T", [
            ("HT Empate para FT Vitoria", scenarios['ht_draw_ft_win'], "Vitoria"),
            ("HT Empate para FT Empate", scenarios['ht_draw_ft_draw'], "Empate"),
            ("HT Empate para FT Derrota", scenarios['ht_draw_ft_loss'], "Derrota")
        ]),
        ("Perdendo no 1T", [
            ("HT Derrota para FT Vitoria", scenarios['ht_loss_ft_win'], "Virada"),
            ("HT Derrota para FT Empate", scenarios['ht_loss_ft_draw'], "Empate"),
            ("HT Derrota para FT Derrota", scenarios['ht_loss_ft_loss'], "Derrota")
        ])
    ]
    
    for category_title, category_scenarios in scenarios_data:
        st.markdown(f"**{category_title}**")
        
        for label, count, emoji in category_scenarios:
            percentage = (count / total_games * 100) if total_games > 0 else 0
            
            # Definir cor baseada no resultado final
            if "FT Vitória" in label:
                text_color = "#4CAF50"  # Verde
                bar_color = "#4CAF50"
            elif "FT Empate" in label:
                text_color = "#FFD700"  # Amarelo
                bar_color = "#FFC107"
            else:  # FT Derrota
                text_color = "#F44336"  # Vermelho
                bar_color = "#F44336"
            
            bar_width = min(percentage, 100)
            
            html_content = f"""
<div style="margin: 8px 0;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
        <span style="font-size: 18px; font-weight: bold; color: {text_color};">{emoji} {label}</span>
        <span style="font-size: 18px; font-weight: bold; color: {color};">{count} ({percentage_formatted}%)</span>
    </div>
    <div style="background-color: #e0e0e0; border-radius: 10px; height: 12px; overflow: hidden;">
        <div style="background-color: {bar_color}; width: {bar_width}%; height: 100%; transition: width 0.3s ease;"></div>
    </div>
</div>
"""
            st.markdown(html_content, unsafe_allow_html=True)
    
    # Insights importantes
    st.markdown("### 💡 Destaques")
    
    viradas = scenarios['ht_loss_ft_win']
    manteve_vantagem = scenarios['ht_win_ft_win']
    perdeu_vantagem = scenarios['ht_win_ft_loss']
    
    if total_games > 0:
        st.info(f"🔄 **Viradas:** {viradas} vezes ({viradas/total_games*100:.1f}%) - Perdendo no HT e vencendo no FT")
        st.success(f"🛡️ **Manteve Vantagem:** {manteve_vantagem} vezes ({manteve_vantagem/total_games*100:.1f}%) - Vencendo do HT ao FT")
        if perdeu_vantagem > 0:
            st.warning(f"⚠️ **Perdeu Vantagem:** {perdeu_vantagem} vezes ({perdeu_vantagem/total_games*100:.1f}%) - Vencendo no HT e perdendo no FT")

def display_team_with_logo(team_name, logo_size=(25, 25)):
    """Exibe time com logo"""
    normalized_name = normalize_team_name(team_name)
    
    try:
        logo_url = TEAM_LOGOS.get(normalized_name) or TEAM_LOGOS.get(team_name)
    except NameError:
        logo_url = None
    
    if logo_url:
        html = f'<div style="display:flex; align-items:center; gap:8px; margin:2px 0; justify-content:center; background-color:#2E2E2E; padding:10px; border-radius:8px;"><div style="background-color:transparent; display:flex; align-items:center;"><img src="{logo_url}" style="width:{logo_size[0]}px; height:{logo_size[1]}px; object-fit:contain; background:none;" alt="{normalized_name}"></div><span style="font-weight:500; color:#FFFFFF; font-size:20px;">{normalized_name}</span></div>'
    else:
        html = f'<div style="text-align:center; background-color:#2E2E2E; padding:10px; border-radius:8px;"><span>⚽</span> <span style="font-weight:500; color:#FFFFFF; font-size:20px;">{normalized_name}</span></div>'
    
    st.markdown(html, unsafe_allow_html=True)

def normalize_team_name(team_name):
    """Normaliza nome do time"""
    replacements = {
        'SÃ£o': 'São',
        'Ã¡': 'á',
        'Ã ': 'à',
        'Ã³': 'ó',
        'Ãª': 'ê',
        'Ã¢': 'â',
        'Ã§': 'ç',
        'Ã­': 'í',
        'Ãº': 'ú'
    }
    
    normalized = team_name
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized

def show_direct_confrontation(df, teams):
    """Análise de Confronto Direto"""
    st.header("🤝 Confronto Direto")
    
    if len(teams) < 2:
        st.warning("Selecione pelo menos dois times.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("🏠 Primeiro Time:", teams, key="confronto_team1")
    with col2:
        team2 = st.selectbox("✈️ Segundo Time:", teams, key="confronto_team2")
        
    if not team1 or not team2 or team1 == team2:
        st.warning("Selecione dois times diferentes.")
        return
    
    # Buscar todos os confrontos diretos
    confrontos = df[
        ((df['Home'] == team1) & (df['Away'] == team2)) |
        ((df['Home'] == team2) & (df['Away'] == team1))
    ].copy()
    
    if confrontos.empty:
        st.warning(f"Nenhum confronto encontrado entre {team1} e {team2}.")
        return
    
    # Ordenar por data se disponível, senão por index
    confrontos = confrontos.sort_index()
    
    st.subheader(f"📊 Histórico de Confrontos: {team1} x {team2}")
    st.write(f"**Total de jogos encontrados:** {len(confrontos)}")
    
    # Preparar dados para exibição
    confrontos_display = []
    team1_wins = 0
    team2_wins = 0
    draws = 0
    
    for idx, game in confrontos.iterrows():
        home_team = game['Home']
        away_team = game['Away']
        home_score = game['Gols Home']
        away_score = game['Gols Away']
        
        # Determinar resultado na perspectiva dos times selecionados
        if home_team == team1:
            team1_score = home_score
            team2_score = away_score
            team1_condition = "Mandante"
            team2_condition = "Visitante"
        else:
            team1_score = away_score
            team2_score = home_score
            team1_condition = "Visitante"
            team2_condition = "Mandante"
        
        # Contar vitórias
        if team1_score > team2_score:
            team1_wins += 1
            resultado = f"Vitória {team1}"
        elif team2_score > team1_score:
            team2_wins += 1
            resultado = f"Vitória {team2}"
        else:
            draws += 1
            resultado = "Empate"
        
        # Obter odds se disponíveis
        odds_info = ""
        if all(col in game.index for col in ['odd Home', 'odd Draw', 'odd Away']):
            if pd.notna(game['odd Home']) and pd.notna(game['odd Draw']) and pd.notna(game['odd Away']):
                odds_info = f"Odds: H:{game['odd Home']:.2f} E:{game['odd Draw']:.2f} A:{game['odd Away']:.2f}"
        
        confrontos_display.append({
            'Confronto': f"{home_team} x {away_team}",
            'Placar': f"{int(home_score)} x {int(away_score)}",
            f'{team1}': f"{int(team1_score)} ({team1_condition})",
            f'{team2}': f"{int(team2_score)} ({team2_condition})",
            'Resultado': resultado,
            'Odds': odds_info
        })
    
    # Exibir resumo
    st.subheader("📈 Resumo dos Confrontos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Vitórias {team1}", team1_wins)
    with col2:
        st.metric("Empates", draws)
    with col3:
        st.metric(f"Vitórias {team2}", team2_wins)
    
    # Gráfico de resultados
    if team1_wins + team2_wins + draws > 0:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"Vitórias\n{team1}", "Empates", f"Vitórias\n{team2}"],
            y=[team1_wins, draws, team2_wins],
            marker_color=['#2E8B57', '#FFD700', '#DC143C'],
            text=[team1_wins, draws, team2_wins],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f"Distribuição de Resultados: {team1} x {team2}",
            xaxis_title="Resultado",
            yaxis_title="Quantidade de Jogos",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📋 Detalhes dos Confrontos")
    df_confrontos = pd.DataFrame(confrontos_display)
    st.dataframe(df_confrontos, use_container_width=True, hide_index=True)
    
    # Análise adicional se houver odds
    odds_available = any(row['Odds'] for row in confrontos_display)
    if odds_available:
        st.subheader("💰 Análise das Odds")
        analyze_confronto_odds(confrontos, team1, team2)

def analyze_confronto_odds(confrontos, team1, team2):
    """Analisa as odds dos confrontos diretos"""
    valid_odds = confrontos.dropna(subset=['odd Home', 'odd Draw', 'odd Away'])
    
    if valid_odds.empty:
        st.write("Dados de odds não disponíveis para análise.")
        return
    
    st.write(f"**Jogos com odds disponíveis:** {len(valid_odds)}")
    
    # Estatísticas das odds
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Odd Mandante Média", f"{valid_odds['odd Home'].mean():.2f}")
    with col2:
        st.metric("Odd Empate Média", f"{valid_odds['odd Draw'].mean():.2f}")
    with col3:
        st.metric("Odd Visitante Média", f"{valid_odds['odd Away'].mean():.2f}")


def calcular_value_gap(prob_historica, prob_implicita):
    """
    Calcula o Value Gap - métrica fundamental de valor.
    
    Value Gap = Probabilidade Histórica - Probabilidade Implícita (da odd)
    
    Positivo = mercado subvaloriza (OPORTUNIDADE)
    Negativo = mercado supervaloriza (EVITAR)
    """
    return prob_historica - prob_implicita


def calcular_forca_relativa(odd_time, odd_adversario):
    """
    Calcula força relativa entre dois times usando suas odds.
    
    Retorna:
        dict com: 'categoria', 'fator_confianca', 'descricao'
    """
    # Probabilidades implícitas
    prob_time = 1 / odd_time
    prob_adversario = 1 / odd_adversario
    
    # Normaliza
    total = prob_time + prob_adversario
    prob_time_norm = prob_time / total if total > 0 else 0.5
    
    # Classifica força relativa
    if prob_time_norm >= 0.65:
        return {
            'categoria': 'Dominante',
            'fator_confianca': 1.2,  # Aumenta confiança em vitória
            'descricao': 'Time muito favorito pelo mercado'
        }
    elif prob_time_norm >= 0.55:
        return {
            'categoria': 'Favorito',
            'fator_confianca': 1.1,
            'descricao': 'Time ligeiramente favorito'
        }
    elif prob_time_norm >= 0.45:
        return {
            'categoria': 'Equilibrado',
            'fator_confianca': 1.0,
            'descricao': 'Jogo equilibrado segundo mercado'
        }
    else:
        return {
            'categoria': 'Underdog',
            'fator_confianca': 0.8,  # Reduz confiança (mas não elimina valor!)
            'descricao': 'Time azarão pelo mercado'
        }


def calcular_ajuste_forma_recente(df, team, position, ultimos_n=5):
    """
    Calcula ajuste baseado em forma recente.
    
    Retorna fator multiplicativo (0.8 a 1.2) baseado em:
    - Taxa de vitórias recentes
    - Sequência atual
    - Gols marcados/sofridos
    
    NÃO deve inverter decisões de valor claras, apenas ajustar.
    """
    try:
        if position == "Home":
            games = df[df['Home'] == team].copy()
            gols_feitos_col = 'Gols Home'
            gols_sofridos_col = 'Gols Away'
        else:
            games = df[df['Away'] == team].copy()
            gols_feitos_col = 'Gols Away'
            gols_sofridos_col = 'Gols Home'
        
        if len(games) < ultimos_n:
            return {'fator': 1.0, 'descricao': 'Dados insuficientes'}
        
        # Ordena por data (assumindo ordem cronológica ou coluna 'Data')
        if 'Data' in games.columns:
            games = games.sort_values('Data', ascending=False)
        
        recentes = games.head(ultimos_n)
        
        # Calcula vitórias recentes
        if position == "Home":
            vitorias = len(recentes[recentes[gols_feitos_col] > recentes[gols_sofridos_col]])
        else:
            vitorias = len(recentes[recentes[gols_feitos_col] > recentes[gols_sofridos_col]])
        
        taxa_vitoria = vitorias / ultimos_n
        
        # Saldo de gols recente
        gols_feitos = recentes[gols_feitos_col].mean()
        gols_sofridos = recentes[gols_sofridos_col].mean()
        saldo = gols_feitos - gols_sofridos
        
        # Calcula fator (limitado entre 0.8 e 1.2)
        fator_base = 1.0
        
        # Ajuste por taxa de vitória (+/- 0.1)
        if taxa_vitoria >= 0.8:
            fator_base += 0.15
        elif taxa_vitoria >= 0.6:
            fator_base += 0.08
        elif taxa_vitoria <= 0.2:
            fator_base -= 0.15
        elif taxa_vitoria <= 0.4:
            fator_base -= 0.08
        
        # Ajuste por saldo de gols (+/- 0.05)
        if saldo >= 1.5:
            fator_base += 0.05
        elif saldo <= -1.5:
            fator_base -= 0.05
        
        # Limita entre 0.8 e 1.2
        fator_final = np.clip(fator_base, 0.8, 1.2)
        
        # Descrição
        if fator_final > 1.1:
            descricao = f"Excelente forma ({vitorias}/{ultimos_n} vitórias)"
        elif fator_final > 1.0:
            descricao = f"Boa forma ({vitorias}/{ultimos_n} vitórias)"
        elif fator_final < 0.9:
            descricao = f"Forma ruim ({vitorias}/{ultimos_n} vitórias)"
        else:
            descricao = f"Forma regular ({vitorias}/{ultimos_n} vitórias)"
        
        return {
            'fator': fator_final,
            'descricao': descricao,
            'vitorias': vitorias,
            'total': ultimos_n,
            'saldo_gols': saldo
        }
    
    except Exception as e:
        return {'fator': 1.0, 'descricao': f'Erro ao calcular: {str(e)}'}


def avaliar_coerencia_gols(perc_over25_historico, odd_resultado):
    """
    Avalia se o padrão de gols valida a odd do resultado.
    
    Lógica:
    - Times com alta taxa de Over 2.5 tendem a ter mais variação (menos empates)
    - Times com Under 2.5 alto tendem a ter mais empates
    
    Retorna fator de coerência (0.8 a 1.2)
    """
    # Odd baixa = favorito esperado para ganhar com mais gols
    # Odd alta = azarão, jogo tende a ser mais fechado
    
    if perc_over25_historico >= 65:
        # Jogo ofensivo - favorece vitórias claras
        if odd_resultado < 2.0:
            return {'fator': 1.1, 'descricao': 'Padrão ofensivo valida favoritismo'}
        else:
            return {'fator': 0.95, 'descricao': 'Padrão ofensivo incomum para azarão'}
    
    elif perc_over25_historico <= 40:
        # Jogo defensivo - favorece empates ou vitórias apertadas
        if odd_resultado >= 3.0:
            return {'fator': 1.05, 'descricao': 'Padrão defensivo coerente'}
        else:
            return {'fator': 0.95, 'descricao': 'Padrão defensivo pode limitar vitória'}
    
    else:
        return {'fator': 1.0, 'descricao': 'Padrão de gols neutro'}


def calcular_value_score(value_gap, forca_relativa, forma_recente, coerencia_gols):
    """
    Calcula Value Score composto.
    
    Value Score = 
        (Value Gap × 0.50) +
        (Força Relativa × 0.20) +
        (Forma Recente × 0.20) +
        (Coerência Gols × 0.10)
    
    Retorna:
        dict com: 'score', 'classificacao', 'confianca'
    """
    
    # Normaliza value gap para escala -100 a +100
    value_gap_norm = np.clip(value_gap, -30, 30)
    
    # Componente 1: Value Gap (peso 50%)
    componente_gap = value_gap_norm * 0.50
    
    # Componente 2: Força Relativa (peso 20%)
    # forca_relativa['fator_confianca'] varia de 0.8 a 1.2
    # Normaliza para -5 a +5
    componente_forca = (forca_relativa['fator_confianca'] - 1.0) * 25 * 0.20
    
    # Componente 3: Forma Recente (peso 20%)
    # forma_recente['fator'] varia de 0.8 a 1.2
    # Normaliza para -5 a +5
    componente_forma = (forma_recente['fator'] - 1.0) * 25 * 0.20
    
    # Componente 4: Coerência Gols (peso 10%)
    componente_gols = (coerencia_gols['fator'] - 1.0) * 25 * 0.10
    
    # Score final
    score = componente_gap + componente_forca + componente_forma + componente_gols
    
    # Classificação
    if score >= 8:
        classificacao = '🟢 Alto Valor'
        confianca = 'Alta'
    elif score >= 4:
        classificacao = '🟡 Valor Moderado'
        confianca = 'Média'
    elif score >= 0:
        classificacao = '⚪ Valor Marginal'
        confianca = 'Baixa'
    else:
        classificacao = '🔴 Sem Valor'
        confianca = 'Nenhuma'
    
    return {
        'score': score,
        'classificacao': classificacao,
        'confianca': confianca,
        'componentes': {
            'value_gap': componente_gap,
            'forca': componente_forca,
            'forma': componente_forma,
            'gols': componente_gols
        }
    }


# ============================================================================
# FUNÇÃO DE ANÁLISE REFINADA - SUBSTITUI analyze_team_comprehensive
# ============================================================================

def analyze_team_comprehensive_refinado(df, team, position, current_odd, odd_adversario=None):
    """
    VERSÃO REFINADA da análise de time.
    
    Mantém mesma assinatura, mas adiciona:
    - Value Gap como métrica principal
    - Análise condicional ao mando
    - Força relativa via odd do adversário
    - Forma recente como ajuste
    - Value Score composto
    """
    
    # Filtra jogos por posição (CONDICIONAL AO MANDO)
    if position == "Home":
        games = df[df['Home'] == team].copy()
        odd_col = 'odd Home'
        gols_feitos = 'Gols Home'
        gols_sofridos = 'Gols Away'
    else:
        games = df[df['Away'] == team].copy()
        odd_col = 'odd Away'
        gols_feitos = 'Gols Away'
        gols_sofridos = 'Gols Home'
    
    # Validação básica
    if games.empty or len(games) < 10:
        return {"error": "Dados insuficientes para análise"}
    
    required_cols = [odd_col, gols_feitos, gols_sofridos]
    missing_cols = [col for col in required_cols if col not in games.columns]
    if missing_cols:
        return {"error": f"Colunas não encontradas: {missing_cols}"}
    
    games = games.dropna(subset=required_cols)
    
    # Calcula resultado
    if position == "Home":
        games['Resultado'] = games.apply(lambda row: 
            'Vitoria' if row[gols_feitos] > row[gols_sofridos] else
            'Empate' if row[gols_feitos] == row[gols_sofridos] else
            'Derrota', axis=1)
    else:
        games['Resultado'] = games.apply(lambda row: 
            'Vitoria' if row[gols_feitos] > row[gols_sofridos] else
            'Empate' if row[gols_feitos] == row[gols_sofridos] else
            'Derrota', axis=1)
    
    # ========== CÁLCULO DE FORÇA RELATIVA ==========
    if odd_adversario:
        forca_relativa = calcular_forca_relativa(current_odd, odd_adversario)
    else:
        forca_relativa = {
            'categoria': 'Desconhecida',
            'fator_confianca': 1.0,
            'descricao': 'Odd do adversário não fornecida'
        }
    
    # ========== CÁLCULO DE FORMA RECENTE ==========
    forma_recente = calcular_ajuste_forma_recente(df, team, position, ultimos_n=5)
    
    # Categorização por odds (mantém lógica original)
    faixas_odds = categorize_odds(games, odd_col, current_odd)
    
    # Análise detalhada por faixa
    resultados = []
    for categoria, filtro_games in faixas_odds.items():
        if len(filtro_games) >= 3:
            total = len(filtro_games)
            vitorias = len(filtro_games[filtro_games['Resultado'] == 'Vitoria'])
            empates = len(filtro_games[filtro_games['Resultado'] == 'Empate'])
            derrotas = len(filtro_games[filtro_games['Resultado'] == 'Derrota'])
            
            perc_vitoria = (vitorias / total) * 100
            perc_empate = (empates / total) * 100
            perc_derrota = (derrotas / total) * 100
            
            # Análise de gols
            filtro_games['Total_Gols'] = filtro_games[gols_feitos] + filtro_games[gols_sofridos]
            over_15 = len(filtro_games[filtro_games['Total_Gols'] > 1.5])
            over_25 = len(filtro_games[filtro_games['Total_Gols'] > 2.5])
            under_25 = total - over_25
            
            perc_over_25 = (over_25 / total) * 100
            
            # ========== NOVA LÓGICA: VALUE SCORE ==========
            # Probabilidade implícita da odd atual
            prob_implicita = (1 / current_odd) * 100
            
            # Value Gap
            value_gap = calcular_value_gap(perc_vitoria, prob_implicita)
            
            # Coerência de gols
            coerencia_gols = avaliar_coerencia_gols(perc_over_25, current_odd)
            
            # Value Score composto
            value_score = calcular_value_score(
                value_gap, 
                forca_relativa, 
                forma_recente, 
                coerencia_gols
            )
            
            # Odd média da faixa
            odd_media = filtro_games[odd_col].mean()
            
            # Verifica se é faixa atual
            is_current = is_current_range(current_odd, categoria)
            
            resultados.append({
                'categoria': categoria,
                'total_jogos': total,
                'vitorias': vitorias,
                'empates': empates,
                'derrotas': derrotas,
                'perc_vitoria': perc_vitoria,
                'perc_empate': perc_empate,
                'perc_derrota': perc_derrota,
                'over_15': over_15,
                'over_25': over_25,
                'under_25': under_25,
                'perc_over_25': perc_over_25,
                'odd_media': odd_media,
                'is_current': is_current,
                # ========== NOVOS CAMPOS ==========
                'value_gap': value_gap,
                'value_score': value_score,
                'prob_implicita': prob_implicita
            })
    
    return {
        'current_odd': current_odd,
        'resultados': resultados,
        # ========== NOVOS CAMPOS ==========
        'forca_relativa': forca_relativa,
        'forma_recente': forma_recente,
        'position': position  # Adiciona para contexto
    }


# ============================================================================
# FUNÇÕES AUXILIARES ORIGINAIS (MANTIDAS PARA COMPATIBILIDADE)
# ============================================================================

def categorize_odds(games, odd_col, current_odd):
    """Categoriza jogos por faixas de odds - MANTIDA DO ORIGINAL"""
    faixas = {
        'Forte Favorito': games[games[odd_col] <= 1.5],
        'Favorito': games[(games[odd_col] > 1.5) & (games[odd_col] <= 2.0)],
        'Leve Favorito': games[(games[odd_col] > 2.0) & (games[odd_col] <= 2.5)],
        'Equilibrado': games[(games[odd_col] > 2.5) & (games[odd_col] <= 3.5)],
        'Azarão Leve': games[(games[odd_col] > 3.5) & (games[odd_col] <= 5.0)],
        'Azarão Forte': games[games[odd_col] > 5.0]
    }
    return faixas


def is_current_range(current_odd, categoria):
    """Verifica se a odd atual está na faixa da categoria - MANTIDA DO ORIGINAL"""
    ranges = {
        'Forte Favorito': (0, 1.5),
        'Favorito': (1.5, 2.0),
        'Leve Favorito': (2.0, 2.5),
        'Equilibrado': (2.5, 3.5),
        'Azarão Leve': (3.5, 5.0),
        'Azarão Forte': (5.0, float('inf'))
    }
    
    if categoria in ranges:
        min_val, max_val = ranges[categoria]
        return min_val < current_odd <= max_val
    return False


# ============================================================================
# FUNÇÃO DE EXIBIÇÃO REFINADA - SUBSTITUI display_professional_analysis
# ============================================================================

def display_professional_analysis_refinado(analysis, team_name, position_label, current_odd, prob_implicita):
    """
    VERSÃO REFINADA da exibição de análise.
    
    Mantém layout original, mas destaca:
    - Value Gap como métrica principal
    - Value Score composto
    - Força relativa e forma recente
    """
    
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.markdown("---")
    st.subheader(f"{position_label} - {team_name}")
    
    # ========== NOVA SEÇÃO: CONTEXTO DO TIME ==========
    with st.expander("📊 Contexto e Força Relativa", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Força Relativa:**")
            forca = analysis.get('forca_relativa', {})
            st.info(f"{forca.get('categoria', 'N/A')} - {forca.get('descricao', 'N/A')}")
        
        with col2:
            st.markdown("**Forma Recente (últimos 5):**")
            forma = analysis.get('forma_recente', {})
            st.info(f"{forma.get('descricao', 'N/A')}")
    
    # Histórico por faixas (mantém tabela original)
    if analysis.get('resultados'):
        st.markdown("#### 📊 Histórico por Faixa de Odds")
        
        df_resultado = pd.DataFrame([
            {
                'Situação': r['categoria'],
                'Jogos': r['total_jogos'],
                'Vitórias': f"{r['vitorias']} ({r['perc_vitoria']:.1f}%)",
                'Empates': f"{r['empates']} ({r['perc_empate']:.1f}%)",
                'Over 2.5': f"{r['over_25']} ({r['perc_over_25']:.1f}%)",
                'Odd Média': f"{r['odd_media']:.2f}",
                # ========== NOVA COLUNA ==========
                'Value Gap': f"{r.get('value_gap', 0):+.1f}%"
            } for r in analysis['resultados']
        ])
        
        st.dataframe(df_resultado, use_container_width=True, hide_index=True)
        
        # Situação atual
        situacao_atual = next((r for r in analysis['resultados'] if r['is_current']), None)
        
        if situacao_atual:
            st.markdown("---")
            st.subheader("🎯 Análise de Valor na Situação Atual")
            
            # ========== DESTAQUE PRINCIPAL: VALUE SCORE ==========
            value_score_data = situacao_atual.get('value_score', {})
            
            # Card de Value Score
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.metric(
                    label="VALUE SCORE",
                    value=f"{value_score_data.get('score', 0):.1f}",
                    delta=value_score_data.get('classificacao', '⚪ Indefinido')
                )
            
            with col2:
                st.metric(
                    label="Confiança",
                    value=value_score_data.get('confianca', 'N/A')
                )
            
            with col3:
                st.metric(
                    label="Value Gap",
                    value=f"{situacao_atual.get('value_gap', 0):+.1f}%"
                )
            
            # Detalhamento dos componentes
            with st.expander("🔬 Decomposição do Value Score", expanded=False):
                componentes = value_score_data.get('componentes', {})
                
                st.markdown("**Contribuição de cada fator:**")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Value Gap (50%)", f"{componentes.get('value_gap', 0):.2f}")
                with col2:
                    st.metric("Força (20%)", f"{componentes.get('forca', 0):.2f}")
                with col3:
                    st.metric("Forma (20%)", f"{componentes.get('forma', 0):.2f}")
                with col4:
                    st.metric("Gols (10%)", f"{componentes.get('gols', 0):.2f}")
            
            # Métricas tradicionais (mantidas)
            st.markdown("#### 📈 Probabilidades")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Taxa Histórica", 
                    f"{situacao_atual['perc_vitoria']:.1f}%"
                )
            
            with col2:
                st.metric(
                    "Prob. Implícita", 
                    f"{prob_implicita:.1f}%"
                )
            
            with col3:
                delta_valor = situacao_atual['perc_vitoria'] - prob_implicita
                st.metric(
                    "Diferença", 
                    f"{abs(delta_valor):.1f}%",
                    delta=f"{delta_valor:+.1f}%"
                )
            
            # ========== INTERPRETAÇÃO REFINADA ==========
            st.markdown("#### 💡 Interpretação")
            
            value_gap = situacao_atual.get('value_gap', 0)
            score = value_score_data.get('score', 0)
            
            if score >= 8:
                st.success(f"""
                    ✅ **FORTE OPORTUNIDADE DE VALOR**
                    
                    - Value Gap de {value_gap:+.1f}% indica subvalorização clara
                    - Value Score de {score:.1f} sugere alta confiança
                    - {analysis.get('forca_relativa', {}).get('descricao', '')}
                    - {analysis.get('forma_recente', {}).get('descricao', '')}
                    
                    **Recomendação:** Considere fortemente esta aposta.
                """)
            
            elif score >= 4:
                st.info(f"""
                    🟡 **OPORTUNIDADE MODERADA DE VALOR**
                    
                    - Value Gap de {value_gap:+.1f}% indica possível valor
                    - Value Score de {score:.1f} sugere confiança média
                    - Fatores de contexto são favoráveis mas não dominantes
                    
                    **Recomendação:** Valor presente, mas avalie risco cuidadosamente.
                """)
            
            elif score >= 0:
                st.warning(f"""
                    ⚪ **VALOR MARGINAL**
                    
                    - Value Gap de {value_gap:+.1f}% indica pouco valor
                    - Value Score de {score:.1f} sugere baixa confiança
                    - Mercado parece razoavelmente precificado
                    
                    **Recomendação:** Evite ou busque outras oportunidades.
                """)
            
            else:
                st.error(f"""
                    🔴 **SEM VALOR - EVITAR**
                    
                    - Value Gap de {value_gap:+.1f}% indica sobrevalorização
                    - Value Score de {score:.1f} sugere nenhuma vantagem
                    - Odd não oferece valor pelo histórico
                    
                    **Recomendação:** Não aposte nesta opção.
                """)


# ============================================================================
# FUNÇÃO PRINCIPAL show_probability_analysis - VERSÃO REFINADA
# ============================================================================

def show_probability_analysis(df, teams):

    st.header("🎯 Probabilidade com histórico das ODDs")
    
    if df is None or df.empty:
        st.error("Dados não disponíveis para análise.")
        return
        
    if not teams:
        st.warning("Nenhum time disponível.")
        return

    # ========== INTERFACE ORIGINAL MANTIDA ==========
    col1, col2 = st.columns(2)
    with col1:
        team_home = st.selectbox("🏠 Time Mandante:", teams, key="prob_home_simple")
    with col2:
        team_away = st.selectbox("✈️ Time Visitante:", teams, key="prob_away_simple")

    if team_home == team_away:
        st.error("⚠️ Selecione times diferentes para análise")
        return

    # ========== ODDS ==========
    st.subheader("📊 Odds do Confronto")

    # Inicialização do estado (uma vez)
    if "odd_home" not in st.session_state:
        st.session_state.odd_home = 2.30
    if "odd_draw" not in st.session_state:
        st.session_state.odd_draw = 3.10
    if "odd_away" not in st.session_state:
        st.session_state.odd_away = 3.30

    with st.container():
        col1, col2, col3 = st.columns(3)

        # -------- ODD MANDANTE --------
        with col1:
            st.write("🏠 **Odd Mandante**")
            st.slider(
                "Valor:",
                min_value=1.01,
                max_value=10.0,
                step=0.01,
                format="%.2f",
                key="odd_home",
                help="Use o slider ou digite diretamente o valor"
            )
            st.number_input(
                "Ou digite o valor exato:",
                min_value=1.01,
                max_value=50.0,
                step=0.01,
                format="%.2f",
                key="odd_home"
            )

        # -------- ODD EMPATE --------
        with col2:
            st.write("🤝 **Odd Empate**")
            st.slider(
                "Valor:",
                min_value=1.01,
                max_value=10.0,
                step=0.01,
                format="%.2f",
                key="odd_draw",
                help="Use o slider ou digite diretamente o valor"
            )
            st.number_input(
                "Ou digite o valor exato:",
                min_value=1.01,
                max_value=50.0,
                step=0.01,
                format="%.2f",
                key="odd_draw"
            )

        # -------- ODD VISITANTE --------
        with col3:
            st.write("✈️ **Odd Visitante**")
            st.slider(
                "Valor:",
                min_value=1.01,
                max_value=10.0,
                step=0.01,
                format="%.2f",
                key="odd_away",
                help="Use o slider ou digite diretamente o valor"
            )
            st.number_input(
                "Ou digite o valor exato:",
                min_value=1.01,
                max_value=50.0,
                step=0.01,
                format="%.2f",
                key="odd_away"
            )

    odd_home = st.session_state.odd_home
    odd_draw = st.session_state.odd_draw
    odd_away = st.session_state.odd_away

    st.info(
        f"**Valores selecionados:** "
        f"🏠 {odd_home:.2f} | 🤝 {odd_draw:.2f} | ✈️ {odd_away:.2f}"
    )
    if st.button("🔍 Analisar Valor nas Odds", type="primary"):
        # Probabilidades implícitas
        prob_home_imp = (1 / odd_home) * 100
        prob_draw_imp = (1 / odd_draw) * 100  
        prob_away_imp = (1 / odd_away) * 100

        st.subheader("🔍 Probabilidades Implícitas das Odds")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏠 Mandante", f"{prob_home_imp:.1f}%")
        with col2:
            st.metric("🤝 Empate", f"{prob_draw_imp:.1f}%")
        with col3:
            st.metric("✈️ Visitante", f"{prob_away_imp:.1f}%")

        # ========== ANÁLISES REFINADAS (LÓGICA NOVA) ==========
        home_analysis = analyze_team_comprehensive_refinado(
            df, team_home, "Home", odd_home, odd_adversario=odd_away
        )
        
        away_analysis = analyze_team_comprehensive_refinado(
            df, team_away, "Away", odd_away, odd_adversario=odd_home
        )
        
        # Empate (mantém lógica original por enquanto)
        draw_analysis = analyze_draw_comprehensive(df, team_home, team_away, odd_draw)
        
        # ========== EXIBIÇÃO REFINADA ==========
        display_professional_analysis_refinado(
            home_analysis, team_home, "🏠 Mandante", odd_home, prob_home_imp
        )
        
        display_professional_analysis_refinado(
            away_analysis, team_away, "✈️ Visitante", odd_away, prob_away_imp
        )
        
        # Empate (mantém display original)
        display_draw_professional_analysis(draw_analysis, odd_draw, prob_draw_imp)
        
        # ========== RECOMENDAÇÕES FINAIS REFINADAS ==========
        display_final_recommendations_refinado(
            home_analysis, away_analysis, draw_analysis, 
            odd_home, odd_away, odd_draw, 
            team_home, team_away
        )


def display_final_recommendations_refinado(home_analysis, away_analysis, draw_analysis, 
                                          odd_home, odd_away, odd_draw, 
                                          team_home, team_away):
    """
    VERSÃO REFINADA das recomendações finais.
    
    Usa Value Score como critério principal.
    """
    
    st.markdown("---")
    st.header("🎯 Recomendações Finais - Análise de Valor")
    
    recommendations = []
    
    # ========== MANDANTE ==========
    if home_analysis.get('resultados'):
        home_current = next((r for r in home_analysis['resultados'] if r['is_current']), None)
        if home_current:
            value_score_home = home_current.get('value_score', {})
            score_home = value_score_home.get('score', 0)
            
            if score_home >= 4:  # Threshold de valor moderado
                recommendations.append({
                    'tipo': f'🏠 Vitória {team_home}',
                    'odd': odd_home,
                    'value_score': score_home,
                    'classificacao': value_score_home.get('classificacao', ''),
                    'confianca': value_score_home.get('confianca', ''),
                    'value_gap': home_current.get('value_gap', 0),
                    'prob_historica': home_current['perc_vitoria'],
                    'prob_mercado': (1/odd_home) * 100
                })
    
    # ========== VISITANTE ==========
    if away_analysis.get('resultados'):
        away_current = next((r for r in away_analysis['resultados'] if r['is_current']), None)
        if away_current:
            value_score_away = away_current.get('value_score', {})
            score_away = value_score_away.get('score', 0)
            
            if score_away >= 4:
                recommendations.append({
                    'tipo': f'✈️ Vitória {team_away}',
                    'odd': odd_away,
                    'value_score': score_away,
                    'classificacao': value_score_away.get('classificacao', ''),
                    'confianca': value_score_away.get('confianca', ''),
                    'value_gap': away_current.get('value_gap', 0),
                    'prob_historica': away_current['perc_vitoria'],
                    'prob_mercado': (1/odd_away) * 100
                })
    
    # ========== EMPATE (lógica simplificada) ==========
    if draw_analysis.get('resultados'):
        draw_current = next((r for r in draw_analysis['resultados'] if r['is_current']), None)
        if draw_current:
            prob_draw_hist = draw_current['perc_empate']
            prob_draw_market = (1/odd_draw) * 100
            value_gap_draw = prob_draw_hist - prob_draw_market
            
            if value_gap_draw > 5:  # Threshold simples para empate
                recommendations.append({
                    'tipo': '🤝 Empate',
                    'odd': odd_draw,
                    'value_score': value_gap_draw,  # Usa value gap como score
                    'classificacao': '🟡 Valor Moderado' if value_gap_draw < 10 else '🟢 Alto Valor',
                    'confianca': 'Média' if value_gap_draw < 10 else 'Alta',
                    'value_gap': value_gap_draw,
                    'prob_historica': prob_draw_hist,
                    'prob_mercado': prob_draw_market
                })
    
    # ========== EXIBIÇÃO ==========
    if recommendations:
        # Ordena por value score
        recommendations.sort(key=lambda x: x['value_score'], reverse=True)
        
        st.success("🎯 **OPORTUNIDADES DE VALOR IDENTIFICADAS**")
        
        for rec in recommendations:
            with st.container():
                st.markdown(f"### {rec['classificacao']} - {rec['tipo']}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Odd", f"{rec['odd']:.2f}")
                
                with col2:
                    st.metric("Value Score", f"{rec['value_score']:.1f}")
                
                with col3:
                    st.metric("Value Gap", f"+{rec['value_gap']:.1f}%")
                
                with col4:
                    conf_icon = "🟢" if rec['confianca'] == 'Alta' else "🟡"
                    st.metric("Confiança", f"{conf_icon} {rec['confianca']}")
                
                st.caption(f"Histórico: {rec['prob_historica']:.1f}% | Mercado: {rec['prob_mercado']:.1f}%")
                st.markdown("---")
    
    else:
        st.info("⚖️ **Nenhuma oportunidade clara de valor identificada neste confronto.**")
        st.caption("Isso não significa que não há apostas possíveis, apenas que o mercado está razoavelmente precificado pelo histórico.")
    
    # ========== DICAS COMPLEMENTARES (mantém original) ==========
    st.subheader("💡 Análise Complementar")
    
    if home_analysis.get('resultados') and away_analysis.get('resultados'):
        home_current = next((r for r in home_analysis['resultados'] if r['is_current']), None)
        away_current = next((r for r in away_analysis['resultados'] if r['is_current']), None)
        
        if home_current and away_current:
            avg_over25 = (home_current['perc_over_25'] + away_current['perc_over_25']) / 2
            
            col1, col2 = st.columns(2)
            
            with col1:
                if avg_over25 > 60:
                    st.success(f"⚽ **OVER 2.5 GOLS**: {avg_over25:.1f}% média histórica")
                elif avg_over25 < 40:
                    st.info(f"🛡️ **UNDER 2.5 GOLS**: {100-avg_over25:.1f}% provável")
                else:
                    st.warning(f"⚖️ **TOTAL DE GOLS INCERTO**: {avg_over25:.1f}%")
            
            with col2:
                # Contexto de jogo
                if odd_home < 2.0:
                    st.info("🏠 Mandante dominante - Considere mercados derivados (HT/FT, gols)")
                elif odd_away < 2.0:
                    st.info("✈️ Visitante forte - Atenção a azarão em casa")
                else:
                    st.info("⚖️ Jogo equilibrado - Value pode estar em mercados alternativos")


# ============================================================================
# FUNÇÕES AUXILIARES ORIGINAIS (PARA EMPATE) - MANTIDAS
# ============================================================================

def analyze_draw_comprehensive(df, team_home, team_away, current_odd):
    """Análise de empates - MANTIDA DO CÓDIGO ORIGINAL"""
    # Esta função mantém a lógica original para empates
    # Pode ser refinada no futuro seguindo o mesmo padrão
    
    # Confrontos diretos
    direct_games = df[
        ((df['Home'] == team_home) & (df['Away'] == team_away)) |
        ((df['Home'] == team_away) & (df['Away'] == team_home))
    ].copy()
    
    direct_analysis = None
    if len(direct_games) >= 3:
        direct_games['Empate'] = direct_games['Gols Home'] == direct_games['Gols Away']
        total_direct = len(direct_games)
        empates_direct = len(direct_games[direct_games['Empate']])
        perc_empate_direct = (empates_direct / total_direct) * 100 if total_direct > 0 else 0
        
        direct_analysis = {
            'total': total_direct,
            'empates': empates_direct,
            'percentual': perc_empate_direct
        }
    
    # Histórico geral de empates dos times
    home_games = df[df['Home'] == team_home].copy()
    away_games = df[df['Away'] == team_away].copy()
    
    all_games = pd.concat([home_games, away_games])
    all_games['Empate'] = all_games['Gols Home'] == all_games['Gols Away']
    
    # Verifica se existe coluna de odd para empate
    odd_draw_col = 'odd Empate' if 'odd Empate' in all_games.columns else 'odd Draw'
    
    if odd_draw_col not in all_games.columns or len(all_games) < 10:
        return {
            'error': 'Dados insuficientes para análise de empates',
            'current_odd': current_odd,
            'direct_analysis': direct_analysis,
            'resultados': []
        }
    
    all_games = all_games.dropna(subset=[odd_draw_col])
    
    # Categorização por odds
    faixas = {
        'Empate Muito Provável': all_games[all_games[odd_draw_col] <= 2.5],
        'Empate Provável': all_games[(all_games[odd_draw_col] > 2.5) & (all_games[odd_draw_col] <= 3.2)],
        'Empate Possível': all_games[(all_games[odd_draw_col] > 3.2) & (all_games[odd_draw_col] <= 4.0)],
        'Empate Improvável': all_games[all_games[odd_draw_col] > 4.0]
    }
    
    resultados = []
    for categoria, filtro in faixas.items():
        if len(filtro) >= 3:
            total = len(filtro)
            empates = len(filtro[filtro['Empate']])
            perc_empate = (empates / total) * 100
            odd_media = filtro[odd_draw_col].mean()
            
            resultados.append({
                'categoria': categoria,
                'total': total,
                'empates': empates,
                'perc_empate': perc_empate,
                'odd_media': odd_media,
                'is_current': is_current_draw_range(current_odd, categoria)
            })
    
    return {
        'current_odd': current_odd,
        'direct_analysis': direct_analysis,
        'resultados': resultados
    }


def is_current_draw_range(current_odd, categoria):
    """Verifica range de empate - MANTIDA"""
    ranges = {
        'Empate Muito Provável': (0, 2.5),
        'Empate Provável': (2.5, 3.2),
        'Empate Possível': (3.2, 4.0),
        'Empate Improvável': (4.0, float('inf'))
    }
    
    if categoria in ranges:
        min_val, max_val = ranges[categoria]
        return min_val < current_odd <= max_val
    return False


def display_draw_professional_analysis(analysis, current_odd, prob_implicita):
    """Display de empates - MANTIDA DO ORIGINAL"""
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.markdown("---")
    st.subheader("🤝 Análise Histórica de Empates")
    
    if analysis['direct_analysis']:
        st.markdown("#### 🔄 Confrontos Diretos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Jogos", analysis['direct_analysis']['total'])
        with col2:
            st.metric("Empates", analysis['direct_analysis']['empates'])
        with col3:
            st.metric("% Empates", f"{analysis['direct_analysis']['percentual']:.1f}%")
    
    if analysis['resultados']:
        st.markdown("#### 📊 Histórico por Faixa de Odds")
        
        df_empates = pd.DataFrame([
            {
                'Situação': r['categoria'],
                'Jogos': r['total'],
                'Empates': f"{r['empates']} ({r['perc_empate']:.1f}%)",
                'Odd Média': f"{r['odd_media']:.2f}"
            } for r in analysis['resultados']
        ])
        
        st.dataframe(df_empates, use_container_width=True, hide_index=True)
        
        situacao_atual = next((r for r in analysis['resultados'] if r['is_current']), None)
        
        if situacao_atual:
            st.subheader("🎯 Análise do Empate na Situação Atual")
            
            valor_empate = situacao_atual['perc_empate'] - prob_implicita
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Taxa Histórica de Empate", 
                         f"{situacao_atual['perc_empate']:.1f}%",
                         delta=f"{valor_empate:+.1f}%")
            with col2:
                st.metric("Odd Atual vs Histórica", 
                         f"{current_odd:.2f}",
                         delta=f"vs {situacao_atual['odd_media']:.2f}")
            
            if valor_empate > 5:
                st.success(f"✅ **VALOR NO EMPATE**: Histórico indica {valor_empate:.1f}% mais chances!")
            elif valor_empate < -5:
                st.error(f"🚨 **EMPATE SUPERVALORIZADO**: {abs(valor_empate):.1f}% menos provável!")
            else:
                st.info("⚖️ **ODD EQUILIBRADA**: Alinhada com histórico.")

def calculate_team_corner_stats(df, team, as_home=True):
    """
    Calcula estatísticas de escanteios por posição (mandante ou visitante)
    """
    if as_home:
        games = df[df['Home'] == team].copy()
        corners_made_col = 'Corner Home'
        corners_conceded_col = 'Corner Away'
    else:
        games = df[df['Away'] == team].copy()
        corners_made_col = 'Corner Away'
        corners_conceded_col = 'Corner Home'
    
    if games.empty:
        return create_empty_corner_stats()
    
    games = games.dropna(subset=[corners_made_col, corners_conceded_col])
    
    if len(games) < 3:
        return create_empty_corner_stats()
    
    if 'Jogo ID' in games.columns:
        games = games.sort_values('Jogo ID', ascending=False)
    
    total_games = len(games)
    
    # Estatísticas FEITOS
    all_made = games[corners_made_col].values
    mean_made = np.mean(all_made)
    std_made = np.std(all_made)
    last_3_made = np.mean(all_made[:3]) if len(all_made) >= 3 else mean_made
    last_5_made = np.mean(all_made[:5]) if len(all_made) >= 5 else mean_made
    
    # Estatísticas SOFRIDOS
    all_conceded = games[corners_conceded_col].values
    mean_conceded = np.mean(all_conceded)
    std_conceded = np.std(all_conceded)
    last_3_conceded = np.mean(all_conceded[:3]) if len(all_conceded) >= 3 else mean_conceded
    last_5_conceded = np.mean(all_conceded[:5]) if len(all_conceded) >= 5 else mean_conceded
    
    return {
        'total_games': total_games,
        'mean_made': mean_made,
        'std_made': std_made,
        'last_3_made': last_3_made,
        'last_5_made': last_5_made,
        'mean_conceded': mean_conceded,
        'std_conceded': std_conceded,
        'last_3_conceded': last_3_conceded,
        'last_5_conceded': last_5_conceded,
        'recent_made': all_made[:5].tolist() if len(all_made) >= 5 else all_made.tolist(),
        'recent_conceded': all_conceded[:5].tolist() if len(all_conceded) >= 5 else all_conceded.tolist()
    }


def create_empty_corner_stats():
    """Estrutura vazia para estatísticas"""
    return {
        'total_games': 0,
        'mean_made': 0,
        'std_made': 0,
        'last_3_made': 0,
        'last_5_made': 0,
        'mean_conceded': 0,
        'std_conceded': 0,
        'last_3_conceded': 0,
        'last_5_conceded': 0,
        'recent_made': [],
        'recent_conceded': []
    }

def calculate_lambda_home(home_stats, away_stats, odds_home=None, odds_away=None):
    """
    Calcula lambda (taxa esperada) de escanteios do MANDANTE
    Considera: o que o mandante FAZ em casa + o que o visitante SOFRE fora
    """
    w_general = 0.60
    w_last_5 = 0.25
    w_last_3 = 0.15
    
    # O que o mandante FAZ em casa
    home_attack = (
        home_stats['mean_made'] * w_general +
        home_stats['last_5_made'] * w_last_5 +
        home_stats['last_3_made'] * w_last_3
    )
    
    # O que o visitante SOFRE fora
    away_defense = (
        away_stats['mean_conceded'] * w_general +
        away_stats['last_5_conceded'] * w_last_5 +
        away_stats['last_3_conceded'] * w_last_3
    )
    
    lambda_base = (home_attack + away_defense) / 2
    
    # Ajuste leve por odds (se disponível)
    if odds_home is not None and odds_away is not None:
        prob_home = 1 / odds_home if odds_home > 0 else 0.5
        prob_away = 1 / odds_away if odds_away > 0 else 0.5
        total_prob = prob_home + prob_away
        
        if total_prob > 0:
            dominance_factor = (prob_home / total_prob) - 0.5
            adjustment = 1 + (dominance_factor * 0.20)
            lambda_adjusted = lambda_base * adjustment
        else:
            lambda_adjusted = lambda_base
    else:
        lambda_adjusted = lambda_base
    
    return max(0.1, lambda_adjusted)


def calculate_lambda_away(home_stats, away_stats, odds_home=None, odds_away=None):
    """
    Calcula lambda (taxa esperada) de escanteios do VISITANTE
    Considera: o que o visitante FAZ fora + o que o mandante SOFRE em casa
    """
    w_general = 0.60
    w_last_5 = 0.25
    w_last_3 = 0.15
    
    # O que o visitante FAZ fora
    away_attack = (
        away_stats['mean_made'] * w_general +
        away_stats['last_5_made'] * w_last_5 +
        away_stats['last_3_made'] * w_last_3
    )
    
    # O que o mandante SOFRE em casa
    home_defense = (
        home_stats['mean_conceded'] * w_general +
        home_stats['last_5_conceded'] * w_last_5 +
        home_stats['last_3_conceded'] * w_last_3
    )
    
    lambda_base = (away_attack + home_defense) / 2
    
    if odds_home is not None and odds_away is not None:
        prob_home = 1 / odds_home if odds_home > 0 else 0.5
        prob_away = 1 / odds_away if odds_away > 0 else 0.5
        total_prob = prob_home + prob_away
        
        if total_prob > 0:
            dominance_factor = (prob_away / total_prob) - 0.5
            adjustment = 1 + (dominance_factor * 0.15)
            lambda_adjusted = lambda_base * adjustment
        else:
            lambda_adjusted = lambda_base
    else:
        lambda_adjusted = lambda_base
    
    return max(0.1, lambda_adjusted)

def calculate_total_corners_distribution(lambda_home, lambda_away, max_corners=25):
    """
    Calcula distribuição de probabilidade do TOTAL de escanteios
    Usa Poisson para cada time
    """
    corner_range = np.arange(0, max_corners + 1)
    total_probs = {}
    
    for total in corner_range:
        prob_total = 0
        for home_corners in range(total + 1):
            away_corners = total - home_corners
            prob_home = poisson.pmf(home_corners, lambda_home)
            prob_away = poisson.pmf(away_corners, lambda_away)
            prob_total += prob_home * prob_away
        
        total_probs[total] = prob_total * 100
    
    return total_probs


def calculate_over_under_probabilities(lambda_home, lambda_away, lines=[8.5, 9.5, 10.5, 11.5]):
    """Calcula probabilidades de Over/Under"""
    lambda_total = lambda_home + lambda_away
    probabilities = {}
    
    for line in lines:
        threshold = int(np.floor(line))
        prob_under = poisson.cdf(threshold, lambda_total) * 100
        prob_over = (1 - poisson.cdf(threshold, lambda_total)) * 100
        
        probabilities[f'Over {line}'] = prob_over
        probabilities[f'Under {line}'] = prob_under
    
    return probabilities


def calculate_confidence_metric(lambda_home, lambda_away, home_stats, away_stats):
    """
    Calcula confiabilidade baseada em:
    - Quantidade de dados
    - Dispersão
    - Variância da distribuição
    """
    min_games = min(home_stats['total_games'], away_stats['total_games'])
    data_score = min(40, min_games * 2)
    
    avg_std = (home_stats['std_made'] + home_stats['std_conceded'] + 
               away_stats['std_made'] + away_stats['std_conceded']) / 4
    avg_mean = (home_stats['mean_made'] + home_stats['mean_conceded'] +
                away_stats['mean_made'] + away_stats['mean_conceded']) / 4
    
    if avg_mean > 0:
        cv = avg_std / avg_mean
        dispersion_score = max(0, 30 - (cv * 30))
    else:
        dispersion_score = 0
    
    lambda_total = lambda_home + lambda_away
    variance_total = lambda_total
    
    if lambda_total > 0:
        relative_variance = variance_total / lambda_total
        variance_score = max(0, 30 - (relative_variance * 3))
    else:
        variance_score = 0
    
    confidence = data_score + dispersion_score + variance_score
    return min(100, max(30, confidence))


def find_probable_range(total_probs, cumulative_threshold=0.70):
    """Encontra faixa que concentra ~70% da probabilidade"""
    sorted_totals = sorted(total_probs.items(), key=lambda x: x[1], reverse=True)
    
    cumulative_prob = 0
    range_values = []
    
    for total, prob in sorted_totals:
        range_values.append(total)
        cumulative_prob += prob
        
        if cumulative_prob >= cumulative_threshold * 100:
            break
    
    if range_values:
        return min(range_values), max(range_values), cumulative_prob
    else:
        return 0, 0, 0


# ===================================================================
# PARTE 4: VISUALIZAÇÃO (MANTÉM SEU LAYOUT ORIGINAL)
# ===================================================================

def display_team_statistics_table(stats, team_name, position="Mandante"):
    """Exibe tabela de estatísticas do time"""
    st.markdown(f"### {'🏠' if position == 'Mandante' else '✈️'} {team_name}")
    
    table_data = {
        'Métrica': [
            '📊 Média Geral (Feitos)',
            '📊 Média Geral (Sofridos)',
            f'🎯 Como {position} (Feitos)',
            f'🎯 Como {position} (Sofridos)',
            '🔥 Últimos 5 Jogos (Feitos)',
            '🔥 Últimos 5 Jogos (Sofridos)',
            '⚡ Últimos 3 Jogos (Feitos)',
            '⚡ Últimos 3 Jogos (Sofridos)',
            '📈 Desvio Padrão (Feitos)',
            '📉 Desvio Padrão (Sofridos)'
        ],
        'Valor': [
            f"{stats['mean_made']:.2f}",
            f"{stats['mean_conceded']:.2f}",
            f"{stats['mean_made']:.2f}",
            f"{stats['mean_conceded']:.2f}",
            f"{stats['last_5_made']:.2f}",
            f"{stats['last_5_conceded']:.2f}",
            f"{stats['last_3_made']:.2f}",
            f"{stats['last_3_conceded']:.2f}",
            f"{stats['std_made']:.2f}",
            f"{stats['std_conceded']:.2f}"
        ]
    }
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        trend_made = ((stats['last_3_made'] - stats['mean_made']) / stats['mean_made'] * 100) if stats['mean_made'] > 0 else 0
        st.metric("🎯 Forma Recente (Feitos)", f"{stats['last_3_made']:.1f}", delta=f"{trend_made:+.1f}%")
    
    with col2:
        trend_conceded = ((stats['last_3_conceded'] - stats['mean_conceded']) / stats['mean_conceded'] * 100) if stats['mean_conceded'] > 0 else 0
        st.metric("🛡️ Forma Recente (Sofridos)", f"{stats['last_3_conceded']:.1f}", delta=f"{trend_conceded:+.1f}%")


def display_comparative_corner_chart(home_stats, away_stats, home_team, away_team):
    """Exibe gráfico comparativo entre os times"""
    st.subheader("📈 Comparativo Estatístico")
    
    categories = [
        'Média Geral\n(Feitos)', 
        'Média Geral\n(Sofridos)', 
        'Últimos 5\n(Feitos)', 
        'Últimos 5\n(Sofridos)',
        'Últimos 3\n(Feitos)', 
        'Últimos 3\n(Sofridos)'
    ]
    
    home_values = [
        home_stats['mean_made'], 
        home_stats['mean_conceded'],
        home_stats['last_5_made'], 
        home_stats['last_5_conceded'],
        home_stats['last_3_made'], 
        home_stats['last_3_conceded']
    ]
    
    away_values = [
        away_stats['mean_made'], 
        away_stats['mean_conceded'],
        away_stats['last_5_made'], 
        away_stats['last_5_conceded'],
        away_stats['last_3_made'], 
        away_stats['last_3_conceded']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=f'🏠 {home_team}',
        x=categories,
        y=home_values,
        marker_color='#1f77b4',
        text=[f"{v:.1f}" for v in home_values],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name=f'✈️ {away_team}',
        x=categories,
        y=away_values,
        marker_color='#ff7f0e',
        text=[f"{v:.1f}" for v in away_values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Comparativo de Estatísticas de Escanteios",
        xaxis_title="Métricas",
        yaxis_title="Número de Escanteios",
        barmode='group',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_match_prediction(lambda_home, lambda_away, total_probs, home_team, away_team, confidence):
    """Exibe previsão do confronto com distribuição de probabilidades"""
    st.subheader("🎯 Previsão do Confronto")
    
    most_likely_total = max(total_probs.items(), key=lambda x: x[1])[0]
    most_likely_prob = total_probs[most_likely_total]
    min_range, max_range, cumulative_prob = find_probable_range(total_probs, 0.70)
    
    st.markdown("### 🎯 Taxas Esperadas (Lambda)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Lambda Mandante", f"{lambda_home:.2f}", help="Taxa esperada de escanteios do mandante (Poisson)")
    
    with col2:
        st.metric("✈️ Lambda Visitante", f"{lambda_away:.2f}", help="Taxa esperada de escanteios do visitante (Poisson)")
    
    with col3:
        st.metric("📊 Total Esperado", f"{lambda_home + lambda_away:.2f}", help="Soma dos lambdas (valor esperado matemático)")
    
    with col4:
        st.metric("🎯 Confiabilidade", f"{confidence:.0f}%", help="Baseada em: quantidade de dados, dispersão e variância")
    
    # Distribuição de Probabilidades
    st.markdown("### 📊 Distribuição de Probabilidades")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Total Mais Provável:** {most_likely_total} escanteios ({most_likely_prob:.1f}%)")
    
    with col2:
        st.info(f"**Faixa Provável (70%):** {min_range} a {max_range} escanteios")
    
    with col3:
        variance = lambda_home + lambda_away
        st.info(f"**Desvio Padrão:** ±{np.sqrt(variance):.1f} escanteios")
    
    # Gráfico de distribuição
    fig = go.Figure()
    
    corners_list = sorted(total_probs.keys())
    probs_list = [total_probs[c] for c in corners_list]
    
    colors = []
    for c in corners_list:
        if c == most_likely_total:
            colors.append('#ff6b6b')
        elif min_range <= c <= max_range:
            colors.append('#4dabf7')
        else:
            colors.append('#dee2e6')
    
    fig.add_trace(go.Bar(
        x=corners_list,
        y=probs_list,
        marker_color=colors,
        text=[f"{p:.1f}%" if p > 1.5 else "" for p in probs_list],
        textposition='auto',
        name='Probabilidade',
        hovertemplate='<b>%{x} escanteios</b><br>Probabilidade: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Distribuição de Probabilidades - Total de Escanteios",
        xaxis_title="Total de Escanteios no Jogo",
        yaxis_title="Probabilidade (%)",
        showlegend=False,
        height=400,
        xaxis=dict(dtick=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Probabilidades Over/Under
    st.markdown("### 📊 Probabilidades Over/Under")
    
    over_under_probs = calculate_over_under_probabilities(lambda_home, lambda_away)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Over 8.5", f"{over_under_probs['Over 8.5']:.1f}%")
    
    with col2:
        st.metric("Over 9.5", f"{over_under_probs['Over 9.5']:.1f}%")
    
    with col3:
        st.metric("Over 10.5", f"{over_under_probs['Over 10.5']:.1f}%")
    
    with col4:
        st.metric("Over 11.5", f"{over_under_probs['Over 11.5']:.1f}%")
    
    # Recomendações
    st.markdown("### 💡 Análise de Oportunidades")
    
    min_confidence = 60
    min_prob = 60
    
    recommendations = []
    
    if confidence >= min_confidence:
        if over_under_probs['Over 9.5'] >= min_prob:
            recommendations.append(
                ("✅ OVER 9.5 ESCANTEIOS", 
                 f"Probabilidade: {over_under_probs['Over 9.5']:.1f}% | Confiança: {confidence:.0f}%",
                 "success")
            )
        elif over_under_probs['Over 9.5'] <= 40:
            recommendations.append(
                ("✅ UNDER 9.5 ESCANTEIOS",
                 f"Probabilidade Under: {100-over_under_probs['Over 9.5']:.1f}% | Confiança: {confidence:.0f}%",
                 "success")
            )
        
        if over_under_probs['Over 10.5'] >= min_prob:
            recommendations.append(
                ("✅ OVER 10.5 ESCANTEIOS",
                 f"Probabilidade: {over_under_probs['Over 10.5']:.1f}% | Confiança: {confidence:.0f}%",
                 "success")
            )
    
    if recommendations:
        for title, description, msg_type in recommendations:
            st.success(f"**{title}**\n\n{description}")
    else:
        st.warning(
            f"⚖️ **JOGO INCERTO**\n\n"
            f"Faixa mais provável: {min_range} a {max_range} escanteios ({cumulative_prob:.1f}% de probabilidade)\n\n"
            f"Confiabilidade: {confidence:.0f}%\n\n"
            f"⚠️ Evite apostas binárias. Considere mercados de faixa."
        )
    
    st.markdown("---")
    st.caption(
        "⚠️ **Importante:** Esta análise trabalha com PROBABILIDADES, não certezas. "
        "Escanteios são eventos de alta variância. O sucesso está em identificar VALUE "
        "(quando a probabilidade estimada é maior que a odd sugere), não em acertar o número exato."
    )

def show_corner_analysis(df, teams):
    """Análise de Escanteios - Versão Refatorada"""
    
    st.header("🚩 Análise Avançada de Escanteios")
    st.markdown("---")
    
    # Seleção de times
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox(
            "🏠 Selecione o Time Mandante",
            options=sorted(teams),
            key="corner_home"
        )
    
    with col2:
        away_team = st.selectbox(
            "✈️ Selecione o Time Visitante",
            options=sorted([t for t in teams if t != home_team]),
            key="corner_away"
        )
    
    st.markdown("---")
    
    # Botão de análise
    if st.button("📊 Analisar Confronto de Escanteios", type="primary", use_container_width=True):
        # Chama a função principal do código novo
        analyze_corner_match(df, home_team, away_team)


def analyze_corner_match(df, home_team, away_team, odds_home=None, odds_draw=None, odds_away=None):
    
    st.title("⚽ Análise Avançada de Escanteios")
    st.markdown(f"**{home_team}** 🆚 **{away_team}**")
    st.markdown("---")
    
    # Calcular estatísticas
    home_stats = calculate_team_corner_stats(df, home_team, as_home=True)
    away_stats = calculate_team_corner_stats(df, away_team, as_home=False)
    
    # Verificar dados suficientes
    if home_stats['total_games'] < 3 or away_stats['total_games'] < 3:
        st.error(
            "❌ **Dados Insuficientes**\n\n"
            f"Jogos do {home_team} como mandante: {home_stats['total_games']}\n\n"
            f"Jogos do {away_team} como visitante: {away_stats['total_games']}\n\n"
            "São necessários pelo menos 3 jogos de cada time na posição específica."
        )
        return
    
    # Exibir estatísticas detalhadas
    st.subheader("📊 Estatísticas Detalhadas de Escanteios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_team_statistics_table(home_stats, home_team, "Mandante")
    
    with col2:
        display_team_statistics_table(away_stats, away_team, "Visitante")
    
    st.markdown("---")
    
    # Gráfico comparativo
    display_comparative_corner_chart(home_stats, away_stats, home_team, away_team)
    
    st.markdown("---")
    
    # Calcular lambdas
    lambda_home = calculate_lambda_home(home_stats, away_stats, odds_home, odds_away)
    lambda_away = calculate_lambda_away(home_stats, away_stats, odds_home, odds_away)
    
    # Distribuição de probabilidades
    total_probs = calculate_total_corners_distribution(lambda_home, lambda_away)
    
    # Confiabilidade
    confidence = calculate_confidence_metric(lambda_home, lambda_away, home_stats, away_stats)
    
    # Exibir previsão
    display_match_prediction(lambda_home, lambda_away, total_probs, home_team, away_team, confidence)


def get_team_display_name_with_logo(team_name, logo_size=(25, 25)):
    """
    Retorna HTML (string) para exibir o nome do time com logo.
    """
    # Assumindo que TEAM_LOGOS é um dicionário definido em outro lugar
    # Se não estiver disponível, use um dicionário vazio como fallback
    try:
        logo_url = TEAM_LOGOS.get(team_name)
    except NameError:
        logo_url = None
    
    if logo_url:
        return f"""
<div style="display:flex; align-items:center; gap:8px; margin:2px 0;">
  <img src="{logo_url}"
       style="width:{logo_size[0]}px; height:{logo_size[1]}px; border-radius:4px; object-fit:contain;"
       onerror="this.style.display='none';"
       alt="{team_name}">
  <span style="font-weight:500; color:#1f4e79;">{team_name}</span>
</div>
"""
    # fallback
    return f"""
<span></span> <span style="font-weight:500; color:#1f4e79;">{team_name}</span>
"""

def display_team_with_logo(team_name, logo_size=(25, 25)):
    """
    Exibe diretamente no Streamlit o time com logo.
    """
    st.markdown(get_team_display_name_with_logo(team_name, logo_size), unsafe_allow_html=True)

def calculate_team_stats_advanced(df, team_name):
    """Calcula estatísticas avançadas do time separando jogos como mandante e visitante"""
    
    # Jogos como mandante
    home_games = df[df['mandante'] == team_name].copy()
    if len(home_games) > 0:
        gols_marcados_casa = home_games['gols_mandante'].mean()
        gols_sofridos_casa = home_games['gols_visitante'].mean()
        jogos_casa = len(home_games)
    else:
        gols_marcados_casa = 0
        gols_sofridos_casa = 0
        jogos_casa = 0
    
    # Jogos como visitante
    away_games = df[df['visitante'] == team_name].copy()
    if len(away_games) > 0:
        gols_marcados_fora = away_games['gols_visitante'].mean()
        gols_sofridos_fora = away_games['gols_mandante'].mean()
        jogos_fora = len(away_games)
    else:
        gols_marcados_fora = 0
        gols_sofridos_fora = 0
        jogos_fora = 0
    
    return {
        'gols_marcados_casa': gols_marcados_casa,
        'gols_sofridos_casa': gols_sofridos_casa,
        'gols_marcados_fora': gols_marcados_fora,
        'gols_sofridos_fora': gols_sofridos_fora,
        'jogos_casa': jogos_casa,
        'jogos_fora': jogos_fora,
        'total_jogos': jogos_casa + jogos_fora
    }

def convert_odds_to_probabilities(odd_home, odd_draw, odd_away):
    """Converte odds para probabilidades implícitas normalizadas"""
    
    # Calcula probabilidades implícitas
    prob_home_raw = 1 / odd_home if odd_home > 0 else 0
    prob_draw_raw = 1 / odd_draw if odd_draw > 0 else 0
    prob_away_raw = 1 / odd_away if odd_away > 0 else 0
    
    # Normaliza as probabilidades
    total_prob = prob_home_raw + prob_draw_raw + prob_away_raw
    
    if total_prob > 0:
        prob_home = prob_home_raw / total_prob
        prob_draw = prob_draw_raw / total_prob
        prob_away = prob_away_raw / total_prob
    else:
        prob_home = prob_draw = prob_away = 1/3
    
    return prob_home, prob_draw, prob_away

def calculate_goal_expectations(home_stats, away_stats):
    """Calcula expectativa inicial de gols baseada nas médias históricas"""
    
    # Expectativa inicial do mandante: média entre gols marcados em casa e gols sofridos pelo visitante fora
    if home_stats['jogos_casa'] > 0 and away_stats['jogos_fora'] > 0:
        expectativa_mandante = (home_stats['gols_marcados_casa'] + away_stats['gols_sofridos_fora']) / 2
    elif home_stats['jogos_casa'] > 0:
        expectativa_mandante = home_stats['gols_marcados_casa']
    elif away_stats['jogos_fora'] > 0:
        expectativa_mandante = away_stats['gols_sofridos_fora']
    else:
        expectativa_mandante = 1.0  # Valor padrão
    
    # Expectativa inicial do visitante: média entre gols marcados fora e gols sofridos pelo mandante em casa
    if away_stats['jogos_fora'] > 0 and home_stats['jogos_casa'] > 0:
        expectativa_visitante = (away_stats['gols_marcados_fora'] + home_stats['gols_sofridos_casa']) / 2
    elif away_stats['jogos_fora'] > 0:
        expectativa_visitante = away_stats['gols_marcados_fora']
    elif home_stats['jogos_casa'] > 0:
        expectativa_visitante = home_stats['gols_sofridos_casa']
    else:
        expectativa_visitante = 1.0  # Valor padrão
    
    return expectativa_mandante, expectativa_visitante

def adjust_expectations_with_odds(exp_home, exp_away, prob_home, prob_draw, prob_away):
    """Ajusta as expectativas de gols usando as probabilidades das odds"""
    
    # Fator de ajuste baseado nas probabilidades
    # Quanto maior a probabilidade de vitória, maior o fator de ajuste
    fator_mandante = 0.8 + (prob_home * 0.6)  # Varia de 0.8 a 1.4
    fator_visitante = 0.8 + (prob_away * 0.6)  # Varia de 0.8 a 1.4
    
    # Aplica os fatores de ajuste
    exp_home_corrigida = exp_home * fator_mandante
    exp_away_corrigida = exp_away * fator_visitante
    
    return exp_home_corrigida, exp_away_corrigida

def generate_score_matrix(exp_home, exp_away):
    """Gera matriz de probabilidades para placares de 0-0 até 5-5"""
    
    matrix = []
    total_prob = 0
    
    for h in range(6):
        row = []
        for a in range(6):
            prob = poisson.pmf(h, exp_home) * poisson.pmf(a, exp_away)
            row.append(prob)
            total_prob += prob
        matrix.append(row)
    
    return np.array(matrix), total_prob

def find_most_probable_score(matrix):
    """Encontra o placar mais provável na matriz"""
    max_prob_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
    return max_prob_idx, matrix[max_prob_idx]

def predict_score_with_odds(df, team_home, team_away, odd_home, odd_draw, odd_away):
    """Realiza predição completa seguindo o modelo estatístico"""
    
    # 1. Calcula estatísticas dos times
    home_stats = calculate_team_stats_advanced(df, team_home)
    away_stats = calculate_team_stats_advanced(df, team_away)
    
    # 2. Converte odds em probabilidades
    prob_home, prob_draw, prob_away = convert_odds_to_probabilities(odd_home, odd_draw, odd_away)
    
    # 3. Calcula expectativas iniciais de gols
    exp_home, exp_away = calculate_goal_expectations(home_stats, away_stats)
    
    # 4. Corrige expectativas com as odds
    exp_home_final, exp_away_final = adjust_expectations_with_odds(
        exp_home, exp_away, prob_home, prob_draw, prob_away
    )
    
    # 5. Gera matriz de probabilidades
    matrix, total_prob = generate_score_matrix(exp_home_final, exp_away_final)
    
    # 6. Encontra placar mais provável
    most_prob_score, max_probability = find_most_probable_score(matrix)
    
    # 7. Calcula placar esperado (arredondamento)
    expected_score = (round(exp_home_final), round(exp_away_final))
    
    return {
        'expectativa_home': exp_home_final,
        'expectativa_away': exp_away_final,
        'placar_mais_provavel': most_prob_score,
        'probabilidade_max': max_probability,
        'placar_esperado': expected_score,
        'matriz_probabilidades': matrix,
        'probabilidades_odds': (prob_home, prob_draw, prob_away),
        'stats_home': home_stats,
        'stats_away': away_stats
    }

def calculate_team_stats_advanced(df, team_name):
    """Calcula estatísticas avançadas do time separando jogos como mandante e visitante"""
    
    # Jogos como mandante
    home_games = df[df['mandante'] == team_name].copy()
    if len(home_games) > 0:
        gols_marcados_casa = home_games['gols_mandante'].mean()
        gols_sofridos_casa = home_games['gols_visitante'].mean()
        jogos_casa = len(home_games)
    else:
        gols_marcados_casa = 0
        gols_sofridos_casa = 0
        jogos_casa = 0
    
    # Jogos como visitante
    away_games = df[df['visitante'] == team_name].copy()
    if len(away_games) > 0:
        gols_marcados_fora = away_games['gols_visitante'].mean()
        gols_sofridos_fora = away_games['gols_mandante'].mean()
        jogos_fora = len(away_games)
    else:
        gols_marcados_fora = 0
        gols_sofridos_fora = 0
        jogos_fora = 0
    
    return {
        'gols_marcados_casa': gols_marcados_casa,
        'gols_sofridos_casa': gols_sofridos_casa,
        'gols_marcados_fora': gols_marcados_fora,
        'gols_sofridos_fora': gols_sofridos_fora,
        'jogos_casa': jogos_casa,
        'jogos_fora': jogos_fora,
        'total_jogos': jogos_casa + jogos_fora
    }

def convert_odds_to_probabilities(odd_home, odd_draw, odd_away):
    """Converte odds para probabilidades implícitas normalizadas"""
    
    # Calcula probabilidades implícitas
    prob_home_raw = 1 / odd_home if odd_home > 0 else 0
    prob_draw_raw = 1 / odd_draw if odd_draw > 0 else 0
    prob_away_raw = 1 / odd_away if odd_away > 0 else 0
    
    # Normaliza as probabilidades
    total_prob = prob_home_raw + prob_draw_raw + prob_away_raw
    
    if total_prob > 0:
        prob_home = prob_home_raw / total_prob
        prob_draw = prob_draw_raw / total_prob
        prob_away = prob_away_raw / total_prob
    else:
        prob_home = prob_draw = prob_away = 1/3
    
    return prob_home, prob_draw, prob_away

def calculate_goal_expectations(home_stats, away_stats):
    """Calcula expectativa inicial de gols baseada nas médias históricas"""
    
    # Expectativa inicial do mandante: média entre gols marcados em casa e gols sofridos pelo visitante fora
    if home_stats['jogos_casa'] > 0 and away_stats['jogos_fora'] > 0:
        expectativa_mandante = (home_stats['gols_marcados_casa'] + away_stats['gols_sofridos_fora']) / 2
    elif home_stats['jogos_casa'] > 0:
        expectativa_mandante = home_stats['gols_marcados_casa']
    elif away_stats['jogos_fora'] > 0:
        expectativa_mandante = away_stats['gols_sofridos_fora']
    else:
        expectativa_mandante = 1.0  # Valor padrão
    
    # Expectativa inicial do visitante: média entre gols marcados fora e gols sofridos pelo mandante em casa
    if away_stats['jogos_fora'] > 0 and home_stats['jogos_casa'] > 0:
        expectativa_visitante = (away_stats['gols_marcados_fora'] + home_stats['gols_sofridos_casa']) / 2
    elif away_stats['jogos_fora'] > 0:
        expectativa_visitante = away_stats['gols_marcados_fora']
    elif home_stats['jogos_casa'] > 0:
        expectativa_visitante = home_stats['gols_sofridos_casa']
    else:
        expectativa_visitante = 1.0  # Valor padrão
    
    return expectativa_mandante, expectativa_visitante

def adjust_expectations_with_odds(exp_home, exp_away, prob_home, prob_draw, prob_away):
    """Ajusta as expectativas de gols usando as probabilidades das odds"""
    
    # Fator de ajuste baseado nas probabilidades
    # Quanto maior a probabilidade de vitória, maior o fator de ajuste
    fator_mandante = 0.8 + (prob_home * 0.6)  # Varia de 0.8 a 1.4
    fator_visitante = 0.8 + (prob_away * 0.6)  # Varia de 0.8 a 1.4
    
    # Aplica os fatores de ajuste
    exp_home_corrigida = exp_home * fator_mandante
    exp_away_corrigida = exp_away * fator_visitante
    
    return exp_home_corrigida, exp_away_corrigida

def generate_score_matrix(exp_home, exp_away):
    """Gera matriz de probabilidades para placares de 0-0 até 5-5"""
    
    matrix = []
    total_prob = 0
    
    for h in range(6):
        row = []
        for a in range(6):
            prob = poisson.pmf(h, exp_home) * poisson.pmf(a, exp_away)
            row.append(prob)
            total_prob += prob
        matrix.append(row)
    
    return np.array(matrix), total_prob

def find_most_probable_score(matrix):
    """Encontra o placar mais provável na matriz"""
    max_prob_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
    return max_prob_idx, matrix[max_prob_idx]

def predict_score_with_odds(df, team_home, team_away, odd_home, odd_draw, odd_away):
    """Realiza predição completa seguindo o modelo estatístico"""
    
    # 1. Calcula estatísticas dos times
    home_stats = calculate_team_stats_advanced(df, team_home)
    away_stats = calculate_team_stats_advanced(df, team_away)
    
    # 2. Converte odds em probabilidades
    prob_home, prob_draw, prob_away = convert_odds_to_probabilities(odd_home, odd_draw, odd_away)
    
    # 3. Calcula expectativas iniciais de gols
    exp_home, exp_away = calculate_goal_expectations(home_stats, away_stats)
    
    # 4. Corrige expectativas com as odds
    exp_home_final, exp_away_final = adjust_expectations_with_odds(
        exp_home, exp_away, prob_home, prob_draw, prob_away
    )
    
    # 5. Gera matriz de probabilidades
    matrix, total_prob = generate_score_matrix(exp_home_final, exp_away_final)
    
    # 6. Encontra placar mais provável
    most_prob_score, max_probability = find_most_probable_score(matrix)
    
    # 7. Calcula placar esperado (arredondamento)
    expected_score = (round(exp_home_final), round(exp_away_final))
    
    return {
        'expectativa_home': exp_home_final,
        'expectativa_away': exp_away_final,
        'placar_mais_provavel': most_prob_score,
        'probabilidade_max': max_probability,
        'placar_esperado': expected_score,
        'matriz_probabilidades': matrix,
        'probabilidades_odds': (prob_home, prob_draw, prob_away),
        'stats_home': home_stats,
        'stats_away': away_stats
    }

def calculate_team_stats_advanced(df, team_name):
    """Calcula estatísticas avançadas do time separando jogos como mandante e visitante"""
    
    # Jogos como mandante (Home)
    home_games = df[df['Home'] == team_name].copy()
    if len(home_games) > 0:
        gols_marcados_casa = home_games['Gols Home'].mean()
        gols_sofridos_casa = home_games['Gols  Away'].mean()  # Note o espaço extra em 'Gols  Away'
        jogos_casa = len(home_games)
    else:
        gols_marcados_casa = 0
        gols_sofridos_casa = 0
        jogos_casa = 0
    
    # Jogos como visitante (Away)
    away_games = df[df['Away'] == team_name].copy()
    if len(away_games) > 0:
        gols_marcados_fora = away_games['Gols  Away'].mean()  # Note o espaço extra em 'Gols  Away'
        gols_sofridos_fora = away_games['Gols Home'].mean()
        jogos_fora = len(away_games)
    else:
        gols_marcados_fora = 0
        gols_sofridos_fora = 0
        jogos_fora = 0
    
    return {
        'gols_marcados_casa': gols_marcados_casa,
        'gols_sofridos_casa': gols_sofridos_casa,
        'gols_marcados_fora': gols_marcados_fora,
        'gols_sofridos_fora': gols_sofridos_fora,
        'jogos_casa': jogos_casa,
        'jogos_fora': jogos_fora,
        'total_jogos': jogos_casa + jogos_fora
    }

def convert_odds_to_probabilities(odd_home, odd_draw, odd_away):
    """Converte odds para probabilidades implícitas normalizadas"""
    
    # Calcula probabilidades implícitas
    prob_home_raw = 1 / odd_home if odd_home > 0 else 0
    prob_draw_raw = 1 / odd_draw if odd_draw > 0 else 0
    prob_away_raw = 1 / odd_away if odd_away > 0 else 0
    
    # Normaliza as probabilidades
    total_prob = prob_home_raw + prob_draw_raw + prob_away_raw
    
    if total_prob > 0:
        prob_home = prob_home_raw / total_prob
        prob_draw = prob_draw_raw / total_prob
        prob_away = prob_away_raw / total_prob
    else:
        prob_home = prob_draw = prob_away = 1/3
    
    return prob_home, prob_draw, prob_away

def calculate_goal_expectations(home_stats, away_stats):
    """Calcula expectativa inicial de gols baseada nas médias históricas"""
    
    # Expectativa inicial do mandante: média entre gols marcados em casa e gols sofridos pelo visitante fora
    if home_stats['jogos_casa'] > 0 and away_stats['jogos_fora'] > 0:
        expectativa_mandante = (home_stats['gols_marcados_casa'] + away_stats['gols_sofridos_fora']) / 2
    elif home_stats['jogos_casa'] > 0:
        expectativa_mandante = home_stats['gols_marcados_casa']
    elif away_stats['jogos_fora'] > 0:
        expectativa_mandante = away_stats['gols_sofridos_fora']
    else:
        expectativa_mandante = 1.0  # Valor padrão
    
    # Expectativa inicial do visitante: média entre gols marcados fora e gols sofridos pelo mandante em casa
    if away_stats['jogos_fora'] > 0 and home_stats['jogos_casa'] > 0:
        expectativa_visitante = (away_stats['gols_marcados_fora'] + home_stats['gols_sofridos_casa']) / 2
    elif away_stats['jogos_fora'] > 0:
        expectativa_visitante = away_stats['gols_marcados_fora']
    elif home_stats['jogos_casa'] > 0:
        expectativa_visitante = home_stats['gols_sofridos_casa']
    else:
        expectativa_visitante = 1.0  # Valor padrão
    
    return expectativa_mandante, expectativa_visitante

def adjust_expectations_with_odds(exp_home, exp_away, prob_home, prob_draw, prob_away):
    """Ajusta as expectativas de gols usando as probabilidades das odds"""
    
    # Fator de ajuste baseado nas probabilidades
    # Quanto maior a probabilidade de vitória, maior o fator de ajuste
    fator_mandante = 0.8 + (prob_home * 0.6)  # Varia de 0.8 a 1.4
    fator_visitante = 0.8 + (prob_away * 0.6)  # Varia de 0.8 a 1.4
    
    # Aplica os fatores de ajuste
    exp_home_corrigida = exp_home * fator_mandante
    exp_away_corrigida = exp_away * fator_visitante
    
    return exp_home_corrigida, exp_away_corrigida

def generate_score_matrix(exp_home, exp_away):
    """Gera matriz de probabilidades para placares de 0-0 até 5-5"""
    
    matrix = []
    total_prob = 0
    
    for h in range(6):
        row = []
        for a in range(6):
            prob = poisson.pmf(h, exp_home) * poisson.pmf(a, exp_away)
            row.append(prob)
            total_prob += prob
        matrix.append(row)
    
    return np.array(matrix), total_prob

def find_most_probable_score(matrix):
    """Encontra o placar mais provável na matriz"""
    max_prob_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
    return max_prob_idx, matrix[max_prob_idx]

def predict_score_with_odds(df, team_home, team_away, odd_home, odd_draw, odd_away):
    """Realiza predição completa seguindo o modelo estatístico"""
    
    # 1. Calcula estatísticas dos times
    home_stats = calculate_team_stats_advanced(df, team_home)
    away_stats = calculate_team_stats_advanced(df, team_away)
    
    # 2. Converte odds em probabilidades
    prob_home, prob_draw, prob_away = convert_odds_to_probabilities(odd_home, odd_draw, odd_away)
    
    # 3. Calcula expectativas iniciais de gols
    exp_home, exp_away = calculate_goal_expectations(home_stats, away_stats)
    
    # 4. Corrige expectativas com as odds
    exp_home_final, exp_away_final = adjust_expectations_with_odds(
        exp_home, exp_away, prob_home, prob_draw, prob_away
    )
    
    # 5. Gera matriz de probabilidades
    matrix, total_prob = generate_score_matrix(exp_home_final, exp_away_final)
    
    # 6. Encontra placar mais provável
    most_prob_score, max_probability = find_most_probable_score(matrix)
    
    # 7. Calcula placar esperado (arredondamento)
    expected_score = (round(exp_home_final), round(exp_away_final))
    
    return {
        'expectativa_home': exp_home_final,
        'expectativa_away': exp_away_final,
        'placar_mais_provavel': most_prob_score,
        'probabilidade_max': max_probability,
        'placar_esperado': expected_score,
        'matriz_probabilidades': matrix,
        'probabilidades_odds': (prob_home, prob_draw, prob_away),
        'stats_home': home_stats,
        'stats_away': away_stats
    }

def show_advanced_score_prediction(df, teams):
    """Interface principal para predição com odds - COM LOGOS"""
    st.header("🎯 Predição Avançada com Odds")
    
    if not teams or len(teams) < 2:
        st.warning("É necessário pelo menos 2 times no dataset.")
        return
    
    # Seleção de times com logos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏠 Time Mandante")
        team_home = create_team_selectbox_with_logo("", teams, "advanced_home")
    with col2:
        st.markdown("### ✈️ Time Visitante")
        team_away = create_team_selectbox_with_logo("", teams, "advanced_away")
    
    if team_home == team_away:
        st.warning("Por favor, selecione dois times diferentes.")
        return
    
    # Exibe confronto selecionado
    if team_home and team_away:
        st.markdown("---")
        st.markdown("#### 🆚 Confronto Selecionado")
        st.markdown(display_team_vs_team(team_home, team_away), unsafe_allow_html=True)
    
    # Input das odds
    st.subheader("📊 Odds do Confronto")
    col1, col2, col3 = st.columns(3)
    with col1:
        odd_home = st.number_input("🏠 Odd Vitória Mandante", min_value=1.01, value=2.50, step=0.01)
    with col2:
        odd_draw = st.number_input("🤝 Odd Empate", min_value=1.01, value=3.20, step=0.01)
    with col3:
        odd_away = st.number_input("✈️ Odd Vitória Visitante", min_value=1.01, value=2.80, step=0.01)
    
    if st.button("🔮 Realizar Predição Avançada"):
        # Executa o modelo
        resultado = predict_score_with_odds(df, team_home, team_away, odd_home, odd_draw, odd_away)
        
        # Validação mínima
        if (resultado['stats_home']['total_jogos'] < 3 or 
            resultado['stats_away']['total_jogos'] < 3):
            st.warning("⚠️ Dados insuficientes para predição confiável (menos de 3 jogos por time).")
        
        # Exibição dos resultados
        st.success("✅ Predição realizada com sucesso!")
        
        # Métricas principais com logos
        col1, col2 = st.columns(2)
        with col1:
            exp_home_formatted = f"{resultado['expectativa_home']:.2f}"
            
            st.markdown(f"""
            <div style="padding: 15px; background-color: #e8f4fd; border-radius: 10px; border-left: 4px solid #1f77b4;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    {display_team_with_logo(team_home, (70, 70), show_name=False)}
                    <strong>Expectativa - {team_home}</strong>
                </div>
                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">
                    {exp_home_formatted} gols
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            exp_away_formatted = f"{resultado['expectativa_away']:.2f}"
            
            st.markdown(f"""
            <div style="padding: 15px; background-color: #fff3cd; border-radius: 10px; border-left: 4px solid #ffc107;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    {display_team_with_logo(team_away, (70, 70), show_name=False)}
                    <strong>Expectativa - {team_away}</strong>
                </div>
                <div style="font-size: 1.5em; font-weight: bold; color: #856404;">
                    {exp_away_formatted} gols
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Placares previstos com logos
        st.subheader("📋 Resultados da Predição")
        
        col1, col2 = st.columns(2)
        with col1:
            # Placar mais provável
            placar_html = display_match_result_with_logos(
                team_home, resultado['placar_mais_provavel'][0], 
                team_away, resultado['placar_mais_provavel'][1]
            )
            st.markdown("#### 🎲 Placar Mais Provável")
            st.markdown(placar_html, unsafe_allow_html=True)
            st.markdown(f"**Probabilidade: {resultado['probabilidade_max']*100:.2f}%**")
        
        with col2:
            # Placar esperado
            esperado_html = display_match_result_with_logos(
                team_home, resultado['placar_esperado'][0],
                team_away, resultado['placar_esperado'][1]
            )
            st.markdown("#### 📊 Placar Esperado")
            st.markdown(esperado_html, unsafe_allow_html=True)
            st.markdown("*(Baseado no arredondamento das expectativas)*")
        
        # Probabilidades das odds
        prob_home, prob_draw, prob_away = resultado['probabilidades_odds']
        st.subheader("🎰 Probabilidades Implícitas das Odds")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"Vitória {team_home}", f"{prob_home*100:.1f}%")
        with col2:
            st.metric("Empate", f"{prob_draw*100:.1f}%")
        with col3:
            st.metric(f"Vitória {team_away}", f"{prob_away*100:.1f}%")
        
        # Matriz de probabilidades
        st.subheader("📈 Matriz de Probabilidades (0-0 até 5-5)")
        
        # Cria DataFrame para exibir a matriz
        matrix_df = pd.DataFrame(
            resultado['matriz_probabilidades'] * 100,
            columns=[f"{i}" for i in range(6)],
            index=[f"{i}" for i in range(6)]
        )
        
        # Formata para exibir percentuais
        matrix_styled = matrix_df.style.format("{:.2f}%").background_gradient(
            cmap='Reds', axis=None
        )
        
        st.dataframe(matrix_styled, use_container_width=True)
        
        st.caption("🏠 Linhas: Gols do mandante | ✈️ Colunas: Gols do visitante")
        
        # Top 10 placares mais prováveis
        st.subheader("🏆 Top 10 Placares Mais Prováveis")
        
        # Gera lista ordenada
        scores_list = []
        for i in range(6):
            for j in range(6):
                prob = resultado['matriz_probabilidades'][i][j]
                scores_list.append(((i, j), prob))
        
        scores_list.sort(key=lambda x: x[1], reverse=True)
        
        # Exibe top 10
        for idx, ((h, a), prob) in enumerate(scores_list[:10], 1):
            emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            st.write(f"{emoji} {team_home} {h} x {a} {team_away} – **{prob*100:.2f}%**")
        
        # Estatísticas detalhadas dos times
        with st.expander("📊 Estatísticas Detalhadas dos Times"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{team_home} (Mandante)**")
                home_stats = resultado['stats_home']
                st.write(f"• Jogos em casa: {home_stats['jogos_casa']}")
                st.write(f"• Gols marcados em casa: {home_stats['gols_marcados_casa']:.2f}/jogo")
                st.write(f"• Gols sofridos em casa: {home_stats['gols_sofridos_casa']:.2f}/jogo")
                st.write(f"• Jogos fora: {home_stats['jogos_fora']}")
                st.write(f"• Gols marcados fora: {home_stats['gols_marcados_fora']:.2f}/jogo")
                st.write(f"• Gols sofridos fora: {home_stats['gols_sofridos_fora']:.2f}/jogo")
            
            with col2:
                st.write(f"**{team_away} (Visitante)**")
                away_stats = resultado['stats_away']
                st.write(f"• Jogos em casa: {away_stats['jogos_casa']}")
                st.write(f"• Gols marcados em casa: {away_stats['gols_marcados_casa']:.2f}/jogo")
                st.write(f"• Gols sofridos em casa: {away_stats['gols_sofridos_casa']:.2f}/jogo")
                st.write(f"• Jogos fora: {away_stats['jogos_fora']}")
                st.write(f"• Gols marcados fora: {away_stats['gols_marcados_fora']:.2f}/jogo")
                st.write(f"• Gols sofridos fora: {away_stats['gols_sofridos_fora']:.2f}/jogo")

# Função de compatibilidade com o modelo original de Poisson simples (sem odds)

def predict_score_poisson(home_avg, away_avg, home_def, away_def):
    """Predição simples com Poisson para compatibilidade com código original"""
    
    # Calcula expectativas básicas
    gols_esperados_home = (home_avg + away_def) / 2
    gols_esperados_away = (away_avg + home_def) / 2
    
    # Encontra placar mais provável
    max_prob = 0
    resultado = (0, 0)
    
    for h in range(6):
        for a in range(6):
            prob = poisson.pmf(h, gols_esperados_home) * poisson.pmf(a, gols_esperados_away)
            if prob > max_prob:
                max_prob = prob
                resultado = (h, a)
    
    return resultado, max_prob, gols_esperados_home, gols_esperados_away

# Função compatível com o código original

def calcular_lambda_home_ajustado(home_stats, away_stats, df=None, team_home=None, team_away=None):
    """
    Calcula lambda ajustado para o time mandante.
    
    Lógica:
    1. Ataque do mandante (em casa) vs Defesa do visitante (fora)
    2. Ajuste por forma recente
    3. Ajuste por força relativa (se dados disponíveis)
    
    Parâmetros:
        home_stats: dict com estatísticas do mandante
        away_stats: dict com estatísticas do visitante
        df: DataFrame opcional para análise temporal
        team_home: nome do time mandante
        team_away: nome do time visitante
    
    Retorna:
        float: lambda ajustado (gols esperados)
    """
    
    # ========== COMPONENTE 1: ATAQUE x DEFESA ==========
    # Média de gols que o mandante faz em casa
    ataque_mandante_casa = home_stats.get('media_gols_feitos', 1.5)
    
    # Média de gols que o visitante sofre fora
    defesa_visitante_fora = away_stats.get('media_gols_sofridos', 1.5)
    
    # Lambda base: média ponderada (60% ataque, 40% defesa adversária)
    lambda_base = (0.6 * ataque_mandante_casa) + (0.4 * defesa_visitante_fora)
    
    
    # ========== COMPONENTE 2: FORMA RECENTE ==========
    # Pesos: 60% geral, 25% últimos 5, 15% últimos 3
    forma_recente_home = _calcular_forma_recente_gols(
        df, team_home, as_home=True, ultimos_jogos=[5, 3]
    ) if df is not None and team_home else None
    
    if forma_recente_home:
        lambda_com_forma = (
            0.60 * lambda_base +
            0.25 * forma_recente_home['ultimos_5'] +
            0.15 * forma_recente_home['ultimos_3']
        )
    else:
        lambda_com_forma = lambda_base
    
    
    # ========== COMPONENTE 3: AJUSTE POR MANDO DE CAMPO ==========
    # Fator de mando: times geralmente fazem ~15-20% mais gols em casa
    fator_mando = 1.15
    lambda_ajustado = lambda_com_forma * fator_mando
    
    
    # ========== COMPONENTE 4: LIMITAÇÃO DE VARIAÇÃO ==========
    # Evita valores extremos: mínimo 0.3, máximo 4.0 gols esperados
    lambda_final = np.clip(lambda_ajustado, 0.3, 4.0)
    
    return lambda_final


def calcular_lambda_away_ajustado(home_stats, away_stats, df=None, team_home=None, team_away=None):
    """
    Calcula lambda ajustado para o time visitante.
    
    Lógica similar ao mandante, mas com penalização por jogar fora.
    """
    
    # ========== COMPONENTE 1: ATAQUE x DEFESA ==========
    ataque_visitante_fora = away_stats.get('media_gols_feitos', 1.2)
    defesa_mandante_casa = home_stats.get('media_gols_sofridos', 1.2)
    
    lambda_base = (0.6 * ataque_visitante_fora) + (0.4 * defesa_mandante_casa)
    
    
    # ========== COMPONENTE 2: FORMA RECENTE ==========
    forma_recente_away = _calcular_forma_recente_gols(
        df, team_away, as_home=False, ultimos_jogos=[5, 3]
    ) if df is not None and team_away else None
    
    if forma_recente_away:
        lambda_com_forma = (
            0.60 * lambda_base +
            0.25 * forma_recente_away['ultimos_5'] +
            0.15 * forma_recente_away['ultimos_3']
        )
    else:
        lambda_com_forma = lambda_base
    
    
    # ========== COMPONENTE 3: PENALIZAÇÃO POR JOGAR FORA ==========
    # Visitantes geralmente fazem ~15-20% menos gols
    fator_visitante = 0.85
    lambda_ajustado = lambda_com_forma * fator_visitante
    
    
    # ========== COMPONENTE 4: LIMITAÇÃO ==========
    lambda_final = np.clip(lambda_ajustado, 0.2, 3.5)
    
    return lambda_final


def _calcular_forma_recente_gols(df, team_name, as_home=True, ultimos_jogos=[5, 3]):
    """
    Calcula média de gols nos últimos N jogos.
    
    Retorna dict com médias para diferentes janelas temporais.
    """
    if df is None or team_name is None:
        return None
    
    try:
        # Filtra jogos do time
        if as_home:
            jogos_time = df[df['mandante'] == team_name].copy()
            coluna_gols = 'gols_mandante'
        else:
            jogos_time = df[df['visitante'] == team_name].copy()
            coluna_gols = 'gols_visitante'
        
        # Ordena por data (assumindo que há coluna 'data' ou similar)
        if 'data' in jogos_time.columns:
            jogos_time = jogos_time.sort_values('data', ascending=False)
        
        forma = {}
        
        # Calcula média para cada janela
        for n in ultimos_jogos:
            jogos_recentes = jogos_time.head(n)
            if len(jogos_recentes) >= max(1, n // 2):  # Pelo menos metade dos jogos
                forma[f'ultimos_{n}'] = jogos_recentes[coluna_gols].mean()
            else:
                # Fallback: usa a média geral se não houver dados suficientes
                forma[f'ultimos_{n}'] = jogos_time[coluna_gols].mean() if len(jogos_time) > 0 else 1.0
        
        return forma
    
    except Exception as e:
        # Em caso de erro, retorna None para usar apenas lambda base
        return None


def ajustar_lambda_por_odds(lambda_calculado, odd_time, odd_adversario, ajuste_maximo=0.15):
    """
    Ajusta lambda usando odds das casas de apostas (se disponível).
    
    Odds refletem expectativa do mercado sobre resultado.
    Usamos isso como ajuste leve, não como verdade absoluta.
    
    Parâmetros:
        lambda_calculado: lambda base calculado
        odd_time: odd do time em questão
        odd_adversario: odd do adversário
        ajuste_maximo: máximo de ajuste permitido (padrão 15%)
    
    Retorna:
        float: lambda ajustado por odds
    """
    if odd_time is None or odd_adversario is None:
        return lambda_calculado
    
    try:
        # Converte odds em probabilidade implícita
        prob_time = 1 / odd_time if odd_time > 0 else 0.5
        prob_adversario = 1 / odd_adversario if odd_adversario > 0 else 0.5
        
        # Normaliza probabilidades
        total_prob = prob_time + prob_adversario
        prob_time_norm = prob_time / total_prob if total_prob > 0 else 0.5
        
        # Calcula fator de ajuste baseado na força relativa
        # Se time tem 70% de prob, aplicamos ajuste positivo
        # Se tem 30%, aplicamos ajuste negativo
        fator = 1 + ((prob_time_norm - 0.5) * 2 * ajuste_maximo)
        
        # Limita o fator ao range permitido
        fator = np.clip(fator, 1 - ajuste_maximo, 1 + ajuste_maximo)
        
        return lambda_calculado * fator
    
    except Exception:
        return lambda_calculado


def ajustar_distribuicao_por_ht_pattern(lambda_home, lambda_away, df, team_home, team_away):
    """
    Ajusta distribuição de placares baseado em padrão de gols no HT.
    
    Times que marcam mais no primeiro tempo tendem a ter distribuições
    diferentes de times que marcam mais no segundo tempo.
    
    Esta função NÃO altera o total esperado de gols, apenas redistribui
    as probabilidades entre os placares.
    
    Retorna:
        tuple: (lambda_home_ajustado, lambda_away_ajustado, dict_ajustes)
    """
    if df is None:
        return lambda_home, lambda_away, {}
    
    try:
        # Analisa padrão HT dos times (se dados disponíveis)
        # Por simplicidade, retornamos os lambdas originais
        # Implementação completa exigiria colunas 'gols_ht_mandante', etc.
        
        ajustes = {
            'intensidade_ht_home': 1.0,  # 1.0 = neutro
            'intensidade_ht_away': 1.0,
            'nota': 'Ajuste HT não aplicado (requer dados detalhados)'
        }
        
        return lambda_home, lambda_away, ajustes
    
    except Exception:
        return lambda_home, lambda_away, {}


# ============================================================================
# FUNÇÃO PRINCIPAL - PREDIÇÃO COM LÓGICA REFINADA
# ============================================================================

def predict_score_poisson_refinado(home_stats, away_stats, df=None, team_home=None, team_away=None, 
                                   odd_home=None, odd_away=None):
    """
    Predição de placar usando Poisson com lambdas ajustados.
    
    MANTÉM A MESMA ASSINATURA DA FUNÇÃO ORIGINAL para compatibilidade.
    
    Parâmetros:
        home_stats: dict com estatísticas do mandante
        away_stats: dict com estatísticas do visitante
        df: DataFrame com histórico de partidas (opcional)
        team_home: nome do time mandante (opcional)
        team_away: nome do time visitante (opcional)
        odd_home: odd do mandante (opcional)
        odd_away: odd do visitante (opcional)
    
    Retorna:
        tuple: (placar_mais_provavel, probabilidade, gols_esp_home, gols_esp_away, detalhes)
    """
    
    # ========== CALCULA LAMBDAS AJUSTADOS ==========
    lambda_home = calcular_lambda_home_ajustado(
        home_stats, away_stats, df, team_home, team_away
    )
    
    lambda_away = calcular_lambda_away_ajustado(
        home_stats, away_stats, df, team_home, team_away
    )
    
    
    # ========== APLICA AJUSTE POR ODDS (SE DISPONÍVEL) ==========
    if odd_home is not None and odd_away is not None:
        lambda_home = ajustar_lambda_por_odds(lambda_home, odd_home, odd_away)
        lambda_away = ajustar_lambda_por_odds(lambda_away, odd_away, odd_home)
    
    
    # ========== AJUSTA POR PADRÃO HT (OPCIONAL) ==========
    lambda_home, lambda_away, ajustes_ht = ajustar_distribuicao_por_ht_pattern(
        lambda_home, lambda_away, df, team_home, team_away
    )
    
    
    # ========== ENCONTRA PLACAR MAIS PROVÁVEL ==========
    max_prob = 0
    resultado = (0, 0)
    
    # Explora placares até 6x6 (99%+ dos resultados reais)
    for h in range(7):
        for a in range(7):
            prob = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)
            if prob > max_prob:
                max_prob = prob
                resultado = (h, a)
    
    
    # ========== MONTA DETALHES PARA DEBUG/TRANSPARÊNCIA ==========
    detalhes = {
        'lambda_home_base': home_stats.get('media_gols_feitos', 0),
        'lambda_away_base': away_stats.get('media_gols_feitos', 0),
        'lambda_home_ajustado': lambda_home,
        'lambda_away_ajustado': lambda_away,
        'fator_mando_aplicado': True,
        'forma_recente_aplicada': df is not None,
        'odds_aplicadas': odd_home is not None,
        'ajustes_ht': ajustes_ht
    }
    
    return resultado, max_prob, lambda_home, lambda_away, detalhes


# ============================================================================
# FUNÇÃO COMPATÍVEL COM CÓDIGO ORIGINAL - SUBSTITUIÇÃO DIRETA
# ============================================================================

def predict_score_poisson(home_avg, away_avg, home_def, away_def, 
                         df=None, team_home=None, team_away=None):
    """
    VERSÃO REFINADA da função original predict_score_poisson.
    
    Mantém mesma assinatura para compatibilidade, mas usa cálculos aprimorados.
    
    COMO SUBSTITUIR NO CÓDIGO ORIGINAL:
    ------------------------------------
    Substitua a chamada:
        resultado, probabilidade, gols_esperados_home, gols_esperados_away = predict_score_poisson(
            home_avg=home_stats['media_gols_feitos'],
            away_avg=away_stats['media_gols_feitos'],
            home_def=home_stats['media_gols_sofridos'],
            away_def=away_stats['media_gols_sofridos']
        )
    
    Por:
        resultado, probabilidade, gols_esperados_home, gols_esperados_away = predict_score_poisson(
            home_avg=home_stats['media_gols_feitos'],
            away_avg=away_stats['media_gols_feitos'],
            home_def=home_stats['media_gols_sofridos'],
            away_def=away_stats['media_gols_sofridos'],
            df=df,  # Passa o DataFrame
            team_home=team_home,  # Passa nome do time mandante
            team_away=team_away   # Passa nome do time visitante
        )
    """
    
    # Converte parâmetros antigos para novo formato
    home_stats = {
        'media_gols_feitos': home_avg,
        'media_gols_sofridos': home_def,
        'jogos': 10  # Placeholder
    }
    
    away_stats = {
        'media_gols_feitos': away_avg,
        'media_gols_sofridos': away_def,
        'jogos': 10  # Placeholder
    }
    
    # Chama função refinada
    resultado, prob, lambda_h, lambda_a, detalhes = predict_score_poisson_refinado(
        home_stats, away_stats, df, team_home, team_away
    )
    
    # Retorna no formato original (sem detalhes extras)
    return resultado, prob, lambda_h, lambda_a


# ============================================================================
# FUNÇÃO PARA STREAMLIT - MANTÉM UI/UX ORIGINAL
# ============================================================================

def show_score_prediction(df, teams):
    """
    VERSÃO REFINADA da função show_score_prediction.
    
    MANTÉM 100% DO LAYOUT E INTERFACE ORIGINAL.
    Substitui apenas os cálculos internos.
    
    INSTRUÇÕES DE INTEGRAÇÃO:
    --------------------------
    1. Copie esta função para substituir a original
    2. Certifique-se de que as funções auxiliares estejam importadas
    3. Teste com alguns confrontos conhecidos
    4. Compare resultados antes/depois para validar melhorias
    """
    import streamlit as st
    
    st.header("🎯 Predição de Placar (Distribuição de Poisson)")

    if not teams:
        st.warning("Nenhum time disponível.")
        return

    col1, col2 = st.columns(2)
    with col1:
        team_home = create_team_selectbox_with_logos("🏠 Time Mandante:", teams, key="poisson_home")
    with col2:
        team_away = create_team_selectbox_with_logos("✈️ Time Visitante:", teams, key="poisson_away")

    if team_home == team_away:
        st.warning("Por favor, selecione dois times diferentes.")
        return

    # Exibe confronto
    if team_home and team_away:
        st.markdown("### ⚔️ Confronto")
        display_vs_matchup(team_home, team_away)

    if st.button("🔮 Prever Placar"):
        # Obtém estatísticas dos times
        home_stats = calculate_team_stats(df, team_home, as_home=True)
        away_stats = calculate_team_stats(df, team_away, as_home=False)

        # Validação mínima
        if home_stats['jogos'] < 3 or away_stats['jogos'] < 3:
            st.warning("Dados insuficientes para realizar predição com confiança.")
            return

        # ========== AQUI ESTÁ A MUDANÇA PRINCIPAL ==========
        # Usa função refinada ao invés da original
        resultado, probabilidade, gols_esperados_home, gols_esperados_away = predict_score_poisson(
            home_avg=home_stats['media_gols_feitos'],
            away_avg=away_stats['media_gols_feitos'],
            home_def=home_stats['media_gols_sofridos'],
            away_def=away_stats['media_gols_sofridos'],
            df=df,  # NOVO: passa DataFrame
            team_home=team_home,  # NOVO: passa nome do time
            team_away=team_away   # NOVO: passa nome do adversário
        )

        # ========== RESTO DO CÓDIGO MANTIDO IDÊNTICO ==========
        # Exibição de resultado com logos
        st.success("Placar Mais Provável:")
        display_score_result_with_logos(team_home, resultado[0], resultado[1], team_away)
        
        prob_formatted = f"{probabilidade*100:.2f}"
        st.metric(label="Probabilidade estimada do placar", value=f"{prob_formatted}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("Gols esperados - Mandante")
            normalized_home = normalize_team_name(team_home)
            logo_home = TEAM_LOGOS.get(normalized_home) or TEAM_LOGOS.get(team_home, "")
            gols_home_formatted = f"{gols_esperados_home:.2f}"
            
            html_home = f"""
            <div style="display:flex; align-items:center; gap:15px; padding:10px; background-color:#2E2E2E; border-radius:8px;">
                <div style="background-color:transparent; display:flex; align-items:center;">
                    <img src="{logo_home}" style="width:60px; height:60px; object-fit:contain; background:none;" alt="{normalized_home}">
                </div>
                <div style="color:white;">
                    <div style="font-weight:bold; font-size:18px;">{normalized_home}</div>
                    <div style="font-size:24px; color:#4CAF50; font-weight:bold;">{gols_home_formatted} gols</div>
                </div>
            </div>
            """
            st.markdown(html_home, unsafe_allow_html=True)
        
        with col2:
            st.info("Gols esperados - Visitante")
            normalized_away = normalize_team_name(team_away)
            logo_away = TEAM_LOGOS.get(normalized_away) or TEAM_LOGOS.get(team_away, "")
            gols_away_formatted = f"{gols_esperados_away:.2f}"
            
            html_away = f"""
            <div style="display:flex; align-items:center; gap:15px; padding:10px; background-color:#2E2E2E; border-radius:8px;">
                <div style="background-color:transparent; display:flex; align-items:center;">
                    <img src="{logo_away}" style="width:60px; height:60px; object-fit:contain; background:none;" alt="{normalized_away}">
                </div>
                <div style="color:white;">
                    <div style="font-weight:bold; font-size:18px;">{normalized_away}</div>
                    <div style="font-size:24px; color:#4CAF50; font-weight:bold;">{gols_away_formatted} gols</div>
                </div>
            </div>
            """
            st.markdown(html_away, unsafe_allow_html=True)

        # Tabela com top 10 placares prováveis
        st.subheader("Top 10 placares mais prováveis")
        results = []
        for h in range(7):  # Aumentado de 6 para 7
            for a in range(7):
                prob = poisson.pmf(h, gols_esperados_home) * poisson.pmf(a, gols_esperados_away)
                results.append(((h, a), prob))
        results.sort(key=lambda x: x[1], reverse=True)
        
        for i, ((h, a), p) in enumerate(results[:10], 1):
            if i == 1:
                emoji = "🥇"
            elif i == 2:
                emoji = "🥈"
            elif i == 3:
                emoji = "🥉"
            else:
                emoji = f"{i}."
            
            probabilidade_formatted = f"{p*100:.2f}"
            
            placar_html = f"""
            <div style="display: flex; align-items: center; background-color: #2E2E2E; padding: 10px; margin: 5px 0; border-radius: 8px; justify-content: space-between; flex-wrap: wrap; min-height: 50px; color: white;">
                <div style="font-size: 18px; min-width: 30px;">{emoji}</div>
                <div style="display: flex; align-items: center; gap: 8px; flex: 1; justify-content: center;">
                    <span style="color: white;">{team_home}</span>
                    <span style="font-size: 20px; color: #FFD700; margin: 0 10px;">{h} x {a}</span>
                    <span style="color: white;">{team_away}</span>
                </div>
                <div style="font-size: 16px; color: #28a745; min-width: 60px; text-align: right;">{probabilidade_formatted}%</div>
            </div>
            """
            st.markdown(placar_html, unsafe_allow_html=True)


# ============================================================================
# EXEMPLO DE USO E TESTES
# ============================================================================

if __name__ == "__main__":
    """
    Exemplos de uso e validação das melhorias.
    """
    
    # Simulação de estatísticas de times
    exemplo_home = {
        'media_gols_feitos': 1.8,
        'media_gols_sofridos': 1.2,
        'jogos': 15
    }
    
    exemplo_away = {
        'media_gols_feitos': 1.3,
        'media_gols_sofridos': 1.5,
        'jogos': 15
    }
    
    # Teste 1: Sem dados adicionais (comportamento básico)
    print("=" * 60)
    print("TESTE 1: Predição básica (sem DataFrame)")
    print("=" * 60)
    resultado, prob, lambda_h, lambda_a, detalhes = predict_score_poisson_refinado(
        exemplo_home, exemplo_away
    )
    print(f"Placar mais provável: {resultado[0]} x {resultado[1]}")
    print(f"Probabilidade: {prob*100:.2f}%")
    print(f"Lambda Home: {lambda_h:.2f} gols")
    print(f"Lambda Away: {lambda_a:.2f} gols")
    print(f"\nDetalhes: {detalhes}")
    
    # Teste 2: Com ajuste por odds
    print("\n" + "=" * 60)
    print("TESTE 2: Com ajuste por odds")
    print("=" * 60)
    resultado2, prob2, lambda_h2, lambda_a2, detalhes2 = predict_score_poisson_refinado(
        exemplo_home, exemplo_away,
        odd_home=1.80,  # Favorito
        odd_away=4.50   # Azarão
    )
    print(f"Placar mais provável: {resultado2[0]} x {resultado2[1]}")
    print(f"Probabilidade: {prob2*100:.2f}%")
    print(f"Lambda Home: {lambda_h2:.2f} gols")
    print(f"Lambda Away: {lambda_a2:.2f} gols")
    
    print("\n" + "=" * 60)
    print("MELHORIAS IMPLEMENTADAS:")
    print("=" * 60)
    print("✓ Lógica ataque x defesa contextual")
    print("✓ Ajuste por forma recente (últimos 3 e 5 jogos)")
    print("✓ Fator de mando de campo (+15% mandante, -15% visitante)")
    print("✓ Ajuste opcional por odds do mercado")
    print("✓ Limitação de valores extremos")
    print("✓ Estrutura preparada para ajuste HT vs FT")
    print("✓ Mantém 100% da interface original")



def main():
    st.markdown('<h1 class="main-header">Analise & Estatistica Brasileirao</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema completo de analise estatistica do Campeonato Brasileiro</p>', unsafe_allow_html=True)
    
    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df = load_data()
    
    if df.empty:
        st.error("Nao foi possivel carregar os dados.")
        st.info("Certifique-se de que o arquivo esta na raiz do repositorio.")
        return
    
        # Filtros de temporada
        header_filtros = """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
        <h3 style="color: white; margin: 0; text-align: center; font-size: 24px;">Filtros de Temporada</h3>
    </div>
    """
        st.markdown(header_filtros, unsafe_allow_html=True)
    
        css_filtros = """       
    <style>
    .filter-button {
        display: inline-block;
        padding: 12px 20px;
        margin: 5px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
     }
     .filter-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
     }
     </style>
     """
        st.markdown(css_filtros, unsafe_allow_html=True)
    
        st.markdown("<h4 style='text-align: center; color: #667eea; margin: 20px 0;'>Selecione Rapido:</h4>", unsafe_allow_html=True)
    
        col1, col2, col3, col4, col5 = st.columns(5)
    
        if 'ano_selecionado' not in st.session_state:
            st.session_state.ano_selecionado = "2025"
    
        css_botoes = """
    <style>
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #4CAF50 !important;
        border: 3px solid #45a049 !important;
    }
    </style>
    """
        st.markdown(css_botoes, unsafe_allow_html=True)
    
    st.markdown("<h4 style='text-align: center; color: #667eea; margin: 20px 0;'>Selecione Rapido:</h4>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if 'ano_selecionado' not in st.session_state:
        st.session_state.ano_selecionado = "2025"
    
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #4CAF50 !important;
        border: 3px solid #45a049 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with col1:
        is_selected = st.session_state.ano_selecionado == "2024"
        if st.button("📅 2024", key="btn_2024", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.ano_selecionado = "2024"
            st.rerun()
    with col2:
        is_selected = st.session_state.ano_selecionado == "2025"
        if st.button("📅 2025", key="btn_2025", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.ano_selecionado = "2025"
            st.rerun()

    with col3:
        is_selected = st.session_state.ano_selecionado == "2026"
        if st.button("📅 2026", key="btn_2026", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.ano_selecionado = "2026"
            st.rerun()

    with col4:
        is_selected = st.session_state.ano_selecionado == "2025 + 2026 (Combinados)"
        if st.button("🔄 2025+2026", key="btn_2025_2026", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.ano_selecionado = "2025 + 2026 (Combinados)"
            st.rerun()

    with col5:
        is_selected = st.session_state.ano_selecionado == "Todos os Anos"
        if st.button("📊 Todos", key="btn_todos", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.ano_selecionado = "Todos os Anos"
            st.rerun()
        
    # Exibir filtro selecionado
    ano_selecionado = st.session_state.ano_selecionado
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 15px;
                border-radius: 10px;
                margin: 15px auto;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h4 style="color: white; margin: 0; font-size: 18px;">
            ✅ Filtro Ativo: <strong>{ano_selecionado}</strong>
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Aplicação do filtro baseado na seleção
    df_original = df.copy()
    anos = sorted(df['Ano'].dropna().unique())
    
    if ano_selecionado == "2025 + 2026 (Combinados)":
        df = df[df['Ano'].isin([2025, 2026])]
    elif ano_selecionado == "Todos os Anos":
        # Mantém todos os dados
        pass
    else:
        # Filtro por ano específico
        ano_num = int(ano_selecionado)
        df = df[df['Ano'] == ano_num]

    # Inicializa lista de times
    if ('Home' in df.columns) and ('Away' in df.columns):
        home_teams = df['Home'].dropna().astype(str).str.strip()
        away_teams = df['Away'].dropna().astype(str).str.strip()
        teams = sorted(set(home_teams) | set(away_teams))
    else:
        teams = []

    # ==== ESTATÍSTICAS UNIFICADAS EM CARD COMPACTO ====
    if not df.empty:
        # Calcular estatísticas
        total_jogos = len(df)
        total_times = len(teams)
        
        if ano_selecionado == "2025 + 2026 (Combinados)":
            jogos_2025 = len(df[df['Ano'] == 2025])
            jogos_2026 = len(df[df['Ano'] == 2026])
            info_extra = f"2025: {jogos_2025} | 2026: {jogos_2026}"
        elif ano_selecionado == "Todos os Anos":
            info_extra = f"Período: {min(anos)} - {max(anos)}"
        else:
            if 'Gols Home' in df.columns and 'Gols  Away' in df.columns:
                total_gols = df['Gols Home'].sum() + df['Gols  Away'].sum()
                media_gols = total_gols / len(df) if len(df) > 0 else 0
                info_extra = f"Média: {media_gols:.2f} gols/jogo"
            else:
                info_extra = "N/A"
        
        # Card unificado e compacto
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 20px;
                    border-radius: 12px;
                    margin: 20px auto;
                    max-width: 800px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; padding: 10px; min-width: 150px;">
                    <div style="color: #ffd700; font-size: 36px; font-weight: bold;">{total_jogos}</div>
                    <div style="color: white; font-size: 14px; margin-top: 5px;">🏟️ Total de Jogos</div>
                </div>
                <div style="border-left: 2px solid rgba(255,255,255,0.3); height: 60px;"></div>
                <div style="text-align: center; padding: 10px; min-width: 150px;">
                    <div style="color: #4CAF50; font-size: 36px; font-weight: bold;">{total_times}</div>
                    <div style="color: white; font-size: 14px; margin-top: 5px;">⚽ Times Únicos</div>
                </div>
                <div style="border-left: 2px solid rgba(255,255,255,0.3); height: 60px;"></div>
                <div style="text-align: center; padding: 10px; min-width: 150px;">
                    <div style="color: #FF6B6B; font-size: 20px; font-weight: bold;">{info_extra}</div>
                    <div style="color: white; font-size: 14px; margin-top: 5px;">📊 Informação Extra</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Inicializa seleção de análise
    if 'selected_analysis' not in st.session_state:
        st.session_state.selected_analysis = None

    # ==== SELEÇÃO DE ANÁLISE ====
    if st.session_state.selected_analysis is None:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 25px;
                    border-radius: 15px;
                    margin: 30px 0 20px 0;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
            <h2 style="color: white; margin: 0; text-align: center; font-size: 28px;">
                📊 Opções de Análise
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Informação sobre filtro ativo
        if ano_selecionado == "2025 + 2026 (Combinados)":
            st.markdown(
                '<div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196F3;">'
                '<strong style="color: #1976D2;">🔄 Modo Combinado Ativo:</strong> <span style="color: #424242;">As análises incluirão dados de 2025 e 2026 juntos</span>'
                '</div>', 
                unsafe_allow_html=True
            )
        elif ano_selecionado == "Todos os Anos":
            st.markdown(
                '<div style="background-color: #f1f8e9; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #8BC34A;">'
                '<strong style="color: #558B2F;">📊 Análise Completa:</strong> <span style="color: #424242;">Incluindo todos os anos disponíveis (2024, 2025 e 2026)</span>'
                '</div>', 
                unsafe_allow_html=True
            )
        
        # Grid de botões proporcional e moderno
        col1, col2, col3 = st.columns(3)
        
        # Estilo CSS para botões maiores
        button_style = """
        <style>
        div.stButton > button {
            width: 100%;
            height: 80px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
        
        with col1:
            if st.button("🏆 Análise de Desempenho", key="desempenho", use_container_width=True):
                st.session_state.selected_analysis = "1. Análise de Desempenho de Time"
                st.rerun()
            
            if st.button("📊 Análise 1 Tempo", key="primeiro_tempo", use_container_width=True):
                st.session_state.selected_analysis = "2. Análise 1 Tempo HT"
                st.rerun()
            
            if st.button("🚩 Análise Escanteios", key="corner_analysis", use_container_width=True):
                st.session_state.selected_analysis = "7. Análise Escanteio"
                st.rerun()

        with col2:
            if st.button("🎯 Probabilidades", key="probabilidades", use_container_width=True):
                st.session_state.selected_analysis = "3. Cálculo de Probabilidades Implícitas"
                st.rerun()
            
            if st.button("🤝 Confronto Direto", key="confronto", use_container_width=True):
                st.session_state.selected_analysis = "4. Confronto Direto"
                st.rerun()

        with col3:
            if st.button("🔮 Predição de Placar", key="predicao", use_container_width=True):
                st.session_state.selected_analysis = "5. Predição de Placar (Poisson)"
                st.rerun()
            
            if st.button("📈 Gráficos Interativos", key="graficos", use_container_width=True):
                st.session_state.selected_analysis = "6. Gráficos Interativos"
                st.rerun()

    else:
        # BOTÃO VOLTAR (quando uma análise está selecionada)
        col_back, col_filter_info = st.columns([1, 3])
        with col_back:
            if st.button("🏠 Voltar ao Menu Principal", key="voltar_menu"):
                st.session_state.selected_analysis = None
                st.rerun()
        with col_filter_info:
            if ano_selecionado == "2024 + 2025 (Combinados)":
                st.info(f"🔄 Analisando: {ano_selecionado} | {len(df)} jogos")
            elif ano_selecionado == "Todos os Anos":
                st.info(f"📊 Analisando: {ano_selecionado} | {len(df)} jogos")
            else:
                st.info(f"📅 Analisando: {ano_selecionado} | {len(df)} jogos")
        
        st.markdown("---")
        
        # Roteamento das opções de análise
        try:
            if st.session_state.selected_analysis == "1. Análise de Desempenho de Time":
                show_team_performance(df, teams)
            elif st.session_state.selected_analysis == "2. Análise 1 Tempo HT":
                show_first_half_analysis(df, teams)
            elif st.session_state.selected_analysis == "3. Cálculo de Probabilidades Implícitas":
                show_probability_analysis(df, teams)
            elif st.session_state.selected_analysis == "4. Confronto Direto":
                show_direct_confrontation(df, teams)
            elif st.session_state.selected_analysis == "5. Predição de Placar (Poisson)":
                show_score_prediction(df, teams)
            elif st.session_state.selected_analysis == "6. Gráficos Interativos":
                show_interactive_charts(df)
            elif st.session_state.selected_analysis == "7. Análise Escanteio":
                show_corner_analysis(df, teams)
            else:
                st.error("Opção de análise inválida.")
        except Exception as e:
            st.error(f"⚠ Erro ao carregar análise: {str(e)}")
            st.info("🔄 Clique em 'Voltar ao Menu Principal' para tentar novamente.")

    # Debug info
    with st.expander("🔍 Informações de Debug"):
        st.write("**Filtro Aplicado:**", ano_selecionado)
        st.write("**Colunas do DataFrame:**", list(df.columns))
        st.write("**Shape do DataFrame filtrado:**", df.shape)
        st.write("**Shape do DataFrame original:**", df_original.shape)
        st.write("**Número de times encontrados:**", len(teams))
        if 'Ano' in df.columns:
            st.write("**Distribuição por ano (filtrado):**")
            st.write(df['Ano'].value_counts().sort_index())
            st.write("**Distribuição por ano (original):**")
            st.write(df_original['Ano'].value_counts().sort_index())

def show_team_performance(df, teams):
    """Exibe análise de desempenho de um time selecionado com logos e gráficos avançados."""
    st.header("🏆 Análise de Desempenho de Time")
    
    if not teams:
        st.warning("Nenhum time disponível.")
        return
        
    # Seleção do time com logo
    st.subheader("📋 Seleção de Time")
    team = st.selectbox("Escolha o time para análise:", teams, key="team_performance")
    
    if not team:
        st.warning("Selecione um time.")
        return
    
    # Exibir logo do time selecionado
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
    with col_logo2:
        display_team_with_logo(team, logo_size=(60, 60))
    
    st.markdown("---")
    
    # Calcular estatísticas avançadas
    stats_home = calculate_advanced_team_stats(df, team, as_home=True)
    stats_away = calculate_advanced_team_stats(df, team, as_home=False)
    
    # Verificar se há dados suficientes
    if stats_home['jogos'] == 0 and stats_away['jogos'] == 0:
        st.error("Nenhum dado encontrado para este time.")
        return
    
    # Seção de estatísticas detalhadas
    display_detailed_team_stats(stats_home, stats_away, team)
    
    # Seção de gráfico de evolução
    display_team_evolution_chart(df, teams, team)

def calculate_advanced_team_stats(df, team, as_home=True):
    """Calcula estatísticas avançadas incluindo primeiro tempo"""
    if as_home:
        games = df[df['Home'] == team].copy()
        gols_feitos_col = 'Gols Home'
        gols_sofridos_col = 'Gols Away'
        gols_ht_feitos_col = 'Home Score HT'
        gols_ht_sofridos_col = 'Away Score HT'
        corners_feitos_col = 'Corner Home'
        corners_sofridos_col = 'Corner Away'
    else:
        games = df[df['Away'] == team].copy()
        gols_feitos_col = 'Gols Away'
        gols_sofridos_col = 'Gols Home'
        gols_ht_feitos_col = 'Away Score HT'
        gols_ht_sofridos_col = 'Home Score HT'
        corners_feitos_col = 'Corner Away'
        corners_sofridos_col = 'Corner Home'
    
    if games.empty:
        return create_empty_team_stats()
    
    # Remove jogos com dados faltantes
    required_cols = [gols_feitos_col, gols_sofridos_col]
    available_cols = [col for col in required_cols if col in games.columns]
    
    if not available_cols:
        return create_empty_team_stats()
    
    games = games.dropna(subset=available_cols)
    
    if games.empty:
        return create_empty_team_stats()
    
    # Calcular resultados
    if as_home:
        games['Resultado'] = games.apply(lambda row: 
            'Vitoria' if row[gols_feitos_col] > row[gols_sofridos_col] else
            'Empate' if row[gols_feitos_col] == row[gols_sofridos_col] else
            'Derrota', axis=1)
    else:
        games['Resultado'] = games.apply(lambda row: 
            'Vitoria' if row[gols_feitos_col] > row[gols_sofridos_col] else
            'Empate' if row[gols_feitos_col] == row[gols_sofridos_col] else
            'Derrota', axis=1)
    
    # Estatísticas básicas
    total_jogos = len(games)
    vitorias = len(games[games['Resultado'] == 'Vitoria'])
    empates = len(games[games['Resultado'] == 'Empate'])
    derrotas = len(games[games['Resultado'] == 'Derrota'])
    
    gols_feitos = games[gols_feitos_col].sum()
    gols_sofridos = games[gols_sofridos_col].sum()
    
    # Estatísticas do primeiro tempo
    gols_ht_feitos = 0
    gols_ht_sofridos = 0
    if gols_ht_feitos_col in games.columns and gols_ht_sofridos_col in games.columns:
        games_ht = games.dropna(subset=[gols_ht_feitos_col, gols_ht_sofridos_col])
        if not games_ht.empty:
            gols_ht_feitos = games_ht[gols_ht_feitos_col].sum()
            gols_ht_sofridos = games_ht[gols_ht_sofridos_col].sum()
    
    # Estatísticas de s
    corners_feitos = 0
    corners_sofridos = 0
    if corners_feitos_col in games.columns and corners_sofridos_col in games.columns:
        games_corners = games.dropna(subset=[corners_feitos_col, corners_sofridos_col])
        if not games_corners.empty:
            corners_feitos = games_corners[corners_feitos_col].sum()
            corners_sofridos = games_corners[corners_sofridos_col].sum()
    
    return {
        'jogos': total_jogos,
        'vitorias': vitorias,
        'empates': empates,
        'derrotas': derrotas,
        'perc_vitorias': (vitorias / total_jogos * 100) if total_jogos > 0 else 0,
        'perc_empates': (empates / total_jogos * 100) if total_jogos > 0 else 0,
        'perc_derrotas': (derrotas / total_jogos * 100) if total_jogos > 0 else 0,
        'gols_feitos': gols_feitos,
        'gols_sofridos': gols_sofridos,
        'media_gols_feitos': gols_feitos / total_jogos if total_jogos > 0 else 0,
        'media_gols_sofridos': gols_sofridos / total_jogos if total_jogos > 0 else 0,
        'gols_ht_feitos': gols_ht_feitos,
        'gols_ht_sofridos': gols_ht_sofridos,
        'media_gols_ht_feitos': gols_ht_feitos / total_jogos if total_jogos > 0 else 0,
        'media_gols_ht_sofridos': gols_ht_sofridos / total_jogos if total_jogos > 0 else 0,
        'corners_feitos': corners_feitos,
        'corners_sofridos': corners_sofridos,
        'media_corners_feitos': corners_feitos / total_jogos if total_jogos > 0 else 0,
        'media_corners_sofridos': corners_sofridos / total_jogos if total_jogos > 0 else 0,
        'saldo_gols': gols_feitos - gols_sofridos
    }

def create_empty_team_stats():
    """Cria estrutura vazia para estatísticas do time"""
    return {
        'jogos': 0, 'vitorias': 0, 'empates': 0, 'derrotas': 0,
        'perc_vitorias': 0, 'perc_empates': 0, 'perc_derrotas': 0,
        'gols_feitos': 0, 'gols_sofridos': 0,
        'media_gols_feitos': 0, 'media_gols_sofridos': 0,
        'gols_ht_feitos': 0, 'gols_ht_sofridos': 0,
        'media_gols_ht_feitos': 0, 'media_gols_ht_sofridos': 0,
        'corners_feitos': 0, 'corners_sofridos': 0,
        'media_corners_feitos': 0, 'media_corners_sofridos': 0,
        'saldo_gols': 0
    }

def display_detailed_team_stats(stats_home, stats_away, team):
    """Exibe estatísticas detalhadas em formato profissional"""
    st.subheader("📊 Estatísticas Detalhadas")
    
    # Cards de resumo geral
    total_jogos = stats_home['jogos'] + stats_away['jogos']
    total_vitorias = stats_home['vitorias'] + stats_away['vitorias']
    total_empates = stats_home['empates'] + stats_away['empates']
    total_derrotas = stats_home['derrotas'] + stats_away['derrotas']
    
    if total_jogos > 0:
        aproveitamento = ((total_vitorias * 3 + total_empates) / (total_jogos * 3)) * 100
    else:
        aproveitamento = 0
    
    # Cards superiores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎮 Total de Jogos", total_jogos)
    with col2:
        st.metric("🏆 Aproveitamento", f"{aproveitamento:.1f}%")
    with col3:
        st.metric("⚽ Saldo de Gols", stats_home['saldo_gols'] + stats_away['saldo_gols'])
    with col4:
        total_media_gols = ((stats_home['media_gols_feitos'] + stats_away['media_gols_feitos']) + 
                           (stats_home['media_gols_sofridos'] + stats_away['media_gols_sofridos'])) / 2
        st.metric("📊 Média Gols/Jogo", f"{total_media_gols:.2f}")
    
    st.markdown("---")
    
    # Estatísticas detalhadas por posição
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Como Mandante")
        
        # Container estilizado para mandante
        with st.container():
            # Resultado geral
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                st.metric("✅ Vitórias", stats_home['vitorias'], 
                         delta=f"{stats_home['perc_vitorias']:.1f}%")
            with col1_2:
                st.metric("⚖️ Empates", stats_home['empates'],
                         delta=f"{stats_home['perc_empates']:.1f}%")
            with col1_3:
                st.metric("❌ Derrotas", stats_home['derrotas'],
                         delta=f"{stats_home['perc_derrotas']:.1f}%")
            
            st.markdown("**⚽ Gols - Tempo Integral**")
            col1_4, col1_5 = st.columns(2)
            with col1_4:
                st.metric("Feitos", stats_home['gols_feitos'],
                         delta=f"Média: {stats_home['media_gols_feitos']:.2f}")
            with col1_5:
                st.metric("Sofridos", stats_home['gols_sofridos'],
                         delta=f"Média: {stats_home['media_gols_sofridos']:.2f}")
            
            st.markdown("**🕐 Gols - Primeiro Tempo**")
            col1_6, col1_7 = st.columns(2)
            with col1_6:
                st.metric("Feitos HT", stats_home['gols_ht_feitos'],
                         delta=f"Média: {stats_home['media_gols_ht_feitos']:.2f}")
            with col1_7:
                st.metric("Sofridos HT", stats_home['gols_ht_sofridos'],
                         delta=f"Média: {stats_home['media_gols_ht_sofridos']:.2f}")
            
            st.markdown("**🚩 Escanteios**")
            col1_8, col1_9 = st.columns(2)
            with col1_8:
                st.metric("Feitos", stats_home['corners_feitos'],
                         delta=f"Média: {stats_home['media_corners_feitos']:.2f}")
            with col1_9:
                st.metric("Sofridos", stats_home['corners_sofridos'],
                         delta=f"Média: {stats_home['media_corners_sofridos']:.2f}")

    with col2:
        st.markdown("### ✈️ Como Visitante")
        
        # Container estilizado para visitante
        with st.container():
            # Resultado geral
            col2_1, col2_2, col2_3 = st.columns(3)
            with col2_1:
                st.metric("✅ Vitórias", stats_away['vitorias'],
                         delta=f"{stats_away['perc_vitorias']:.1f}%")
            with col2_2:
                st.metric("⚖️ Empates", stats_away['empates'],
                         delta=f"{stats_away['perc_empates']:.1f}%")
            with col2_3:
                st.metric("❌ Derrotas", stats_away['derrotas'],
                         delta=f"{stats_away['perc_derrotas']:.1f}%")
            
            st.markdown("**⚽ Gols - Tempo Integral**")
            col2_4, col2_5 = st.columns(2)
            with col2_4:
                st.metric("Feitos", stats_away['gols_feitos'],
                         delta=f"Média: {stats_away['media_gols_feitos']:.2f}")
            with col2_5:
                st.metric("Sofridos", stats_away['gols_sofridos'],
                         delta=f"Média: {stats_away['media_gols_sofridos']:.2f}")
            
            st.markdown("**🕐 Gols - Primeiro Tempo**")
            col2_6, col2_7 = st.columns(2)
            with col2_6:
                st.metric("Feitos HT", stats_away['gols_ht_feitos'],
                         delta=f"Média: {stats_away['media_gols_ht_feitos']:.2f}")
            with col2_7:
                st.metric("Sofridos HT", stats_away['gols_ht_sofridos'],
                         delta=f"Média: {stats_away['media_gols_ht_sofridos']:.2f}")
            
            st.markdown("**🚩 Escanteios**")
            col2_8, col2_9 = st.columns(2)
            with col2_8:
                st.metric("Feitos", stats_away['corners_feitos'],
                         delta=f"Média: {stats_away['media_corners_feitos']:.2f}")
            with col2_9:
                st.metric("Sofridos", stats_away['corners_sofridos'],
                         delta=f"Média: {stats_away['media_corners_sofridos']:.2f}")

def display_team_evolution_chart(df, teams, selected_team):
    """Exibe gráfico de evolução da posição ao longo das rodadas"""
    st.markdown("---")
    st.subheader("📈 Evolução na Tabela por Rodadas")
    
    # Verificar se há dados de rodada
    if 'Rodada' not in df.columns and 'Jogo ID' not in df.columns:
        st.warning("Dados de rodada não disponíveis para gráfico de evolução.")
        return
    
    # Seleção de anos e times para comparação
    anos_disponiveis = []
    if 'Ano' in df.columns:
        anos_disponiveis = sorted(df['Ano'].dropna().unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        if anos_disponiveis:
            anos_selecionados = st.multiselect(
                "📅 Selecione os anos:",
                anos_disponiveis,
                default=[max(anos_disponiveis)] if anos_disponiveis else [],
                key="years_evolution"
            )
        else:
            anos_selecionados = []
            st.info("Dados de ano não disponíveis")
    
    with col2:
        times_comparacao = st.multiselect(
            "⚽ Times para comparar:",
            teams,
            default=[selected_team],
            key="teams_comparison"
        )
    
    if not times_comparacao:
        st.warning("Selecione pelo menos um time para análise.")
        return
    
    # Criar gráfico de evolução
    create_position_evolution_chart(df, times_comparacao, anos_selecionados)

def create_position_evolution_chart(df, teams_selected, years_selected):
    """Cria gráfico de evolução das posições"""
    
    # Preparar dados
    evolution_data = []
    
    for team in teams_selected:
        for year in years_selected if years_selected else [None]:
            # Filtrar dados
            if year and 'Ano' in df.columns:
                team_games = df[((df['Home'] == team) | (df['Away'] == team)) & (df['Ano'] == year)].copy()
            else:
                team_games = df[(df['Home'] == team) | (df['Away'] == team)].copy()
            
            if team_games.empty:
                continue
            
            # Simular evolução da posição (baseado em pontos acumulados)
            team_games = team_games.sort_values('Jogo ID' if 'Jogo ID' in team_games.columns else team_games.index)
            
            points = 0
            positions = []
            rodadas = []
            
            for idx, (_, game) in enumerate(team_games.iterrows(), 1):
                # Calcular pontos do jogo
                if game['Home'] == team:
                    gols_feitos = game['Gols Home']
                    gols_sofridos = game['Gols Away']
                else:
                    gols_feitos = game['Gols Away']
                    gols_sofridos = game['Gols Home']
                
                if gols_feitos > gols_sofridos:
                    points += 3
                elif gols_feitos == gols_sofridos:
                    points += 1
                
                # Simular posição (simplificado - baseado em pontos por jogo)
                avg_points = points / idx
                # Converter para posição (simulada)
                if avg_points >= 2.0:
                    position = min(1 + (2.5 - avg_points) * 4, 4)
                elif avg_points >= 1.5:
                    position = 4 + (2.0 - avg_points) * 8
                elif avg_points >= 1.0:
                    position = 8 + (1.5 - avg_points) * 8
                else:
                    position = 16 + (1.0 - avg_points) * 4
                
                positions.append(max(1, min(20, int(position))))
                rodadas.append(idx)
            
            # Adicionar aos dados
            team_label = f"{team}" if not years_selected else f"{team} ({year})"
            evolution_data.extend([
                {
                    'Time': team_label,
                    'Rodada': rodada,
                    'Posicao': pos,
                    'Ano': year if year else 'N/A'
                }
                for rodada, pos in zip(rodadas, positions)
            ])
    
    if not evolution_data:
        st.warning("Não há dados suficientes para criar o gráfico de evolução.")
        return
    
    # Criar DataFrame
    df_evolution = pd.DataFrame(evolution_data)
    
    # Criar gráfico
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, team in enumerate(df_evolution['Time'].unique()):
        team_data = df_evolution[df_evolution['Time'] == team]
        
        fig.add_trace(go.Scatter(
            x=team_data['Rodada'],
            y=team_data['Posicao'],
            mode='lines+markers',
            name=team,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=6),
            hovertemplate=f'<b>{team}</b><br>' +
                         'Rodada: %{x}<br>' +
                         'Posição: %{y}<br>' +
                         '<extra></extra>'
        ))
    
    # Configurar layout
    fig.update_layout(
        title="Evolução da Posição na Tabela por Rodadas",
        xaxis_title="Rodadas",
        yaxis_title="Posição na Tabela",
        yaxis=dict(
            autorange='reversed',  # Inverter eixo Y (1º lugar no topo)
            dtick=1,
            range=[20.5, 0.5]
        ),
        xaxis=dict(dtick=2),
        hovermode='closest',
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.01
        ),
        plot_bgcolor='rgba(50,50,50,1)',
        paper_bgcolor='#1E1E1E',
        font=dict(color='white'),
        title_font=dict(color='white')
    )
    
    # Adicionar linhas de referência para zonas
    fig.add_hline(y=4.5, line_dash="dash", line_color="blue", 
                  annotation_text="Libertadores", annotation_position="left")
    fig.add_hline(y=6.5, line_dash="dash", line_color="green", 
                  annotation_text="Sul-Americana", annotation_position="left")
    fig.add_hline(y=16.5, line_dash="dash", line_color="red", 
                  annotation_text="Rebaixamento", annotation_position="left")
    
    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumo
    if len(teams_selected) > 1:
        st.subheader("📊 Resumo Comparativo")
        
        summary_data = []
        for team in df_evolution['Time'].unique():
            team_data = df_evolution[df_evolution['Time'] == team]
            
            summary_data.append({
                'Time': team,
                'Melhor Posição': int(team_data['Posicao'].min()),
                'Pior Posição': int(team_data['Posicao'].max()),
                'Posição Final': int(team_data['Posicao'].iloc[-1]),
                'Rodadas Analisadas': len(team_data)
            })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

def display_team_with_logo(team_name, logo_size=(80, 80)):
    """Exibe diretamente no Streamlit o time com logo."""
    normalized_name = normalize_team_name(team_name)
    
    try:
        logo_url = TEAM_LOGOS.get(normalized_name) or TEAM_LOGOS.get(team_name)
    except NameError:
        logo_url = None
    
    if logo_url:
        html = f'<div style="display:flex; align-items:center; gap:8px; margin:2px 0; justify-content:center; background-color:#2E2E2E; padding:10px; border-radius:8px;"><div style="background-color:transparent; display:flex; align-items:center;"><img src="{logo_url}" style="width:{logo_size[0]}px; height:{logo_size[1]}px; object-fit:contain; background:none;" alt="{normalized_name}"></div><span style="font-weight:500; color:#FFFFFF; font-size:28px;">{normalized_name}</span></div>'
    else:
        html = f'<div style="text-align:center; background-color:#2E2E2E; padding:10px; border-radius:8px;"><span>⚽</span> <span style="font-weight:500; color:#FFFFFF; font-size:28px;">{normalized_name}</span></div>'   
    
    st.markdown(html, unsafe_allow_html=True)

# CHAMADA DA MAIN (adicionar no final do arquivo)
if __name__ == "__main__":
    main()


















































































































