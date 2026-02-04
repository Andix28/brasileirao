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
                           'Corner Home', 'Corner Away', 'Total Corner Match', 'Home Score HT', 'Away Score HT']
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
            escanteios_feitos_col = 'Corner Home'
            escanteios_sofridos_col = 'Corner Away'
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
    ""
    Calcula métricas avançadas para análise profissional.
    
    Args:
        stats (dict): Estatísticas básicas
        team_home (str): Nome do time mandante
        team_away (str): Nome do time visitante
        
    Returns:
        dict: Métricas avançadas calculadas
    """
    
    # Função auxiliar para converter valores de forma segura
    def safe_int(value):
        try:
            if pd.isna(value):
                return 0
            return int(float(value))  # Converte para float primeiro, depois int
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
    """Analise de Primeiro Tempo HT - Versao Profissional"""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; 
                    border-radius: 15px; 
                    margin: 20px 0;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
             <h1 style="color: white; margin: 0; text-align: center; font-size: 32px;">
                Analise Primeiro Tempo HT
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
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
    
    # Análise completa de cenários HT → FT
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
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h2 style="color: white; margin: 0; text-align: center; font-size: 26px;">
                Comparativo Estatístico - Primeiro Tempo
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar tabela HTML customizada
    html_table = f"""
    <style>
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 16px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }}
    .custom-table thead tr {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
    }}
    .custom-table th, .custom-table td {{
        padding: 15px;
        text-align: center;
    }}
    .custom-table tbody tr {{
        border-bottom: 1px solid #dddddd;
    }}
    .custom-table tbody tr:nth-of-type(even) {{
        background-color: #f3f3f3;
    }}
    .custom-table tbody tr:last-of-type {{
        border-bottom: 2px solid #667eea;
    }}
    .metric-label {{
        font-weight: 600;
        color: #2c3e50;
        font-size: 17px;
        text-align: left !important;
        padding-left: 20px !important;
    }}
    .home-value {{
        color: #2196F3;
        font-weight: bold;
        font-size: 20px;
    }}
    .away-value {{
        color: #FF6B6B;
        font-weight: bold;
        font-size: 20px;
    }}
    </style>
    
    <table class="custom-table">
        <thead>
            <tr>
                <th style="text-align: left; padding-left: 20px;">📊 Métrica</th>
                <th>🏠 {team_home}<br/>(Mandante)</th>
                <th>✈️ {team_away}<br/>(Visitante)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="metric-label">🎮 Jogos Analisados</td>
                <td class="home-value">{home_stats['jogos']}</td>
                <td class="away-value">{away_stats['jogos']}</td>
            </tr>
            <tr>
                <td class="metric-label">⚽ Gols Feitos no 1º Tempo</td>
                <td class="home-value">{home_stats['gols_feitos_ht']}</td>
                <td class="away-value">{away_stats['gols_feitos_ht']}</td>
            </tr>
            <tr>
                <td class="metric-label">🛡️ Gols Sofridos no 1º Tempo</td>
                <td class="home-value">{home_stats['gols_sofridos_ht']}</td>
                <td class="away-value">{away_stats['gols_sofridos_ht']}</td>
            </tr>
            <tr>
                <td class="metric-label">📈 Média Gols Feitos/Jogo (1ºT)</td>
                <td class="home-value">{home_stats['media_feitos_ht']:.2f}</td>
                <td class="away-value">{away_stats['media_feitos_ht']:.2f}</td>
            </tr>
            <tr>
                <td class="metric-label">📉 Média Gols Sofridos/Jogo (1ºT)</td>
                <td class="home-value">{home_stats['media_sofridos_ht']:.2f}</td>
                <td class="away-value">{away_stats['media_sofridos_ht']:.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)

def display_professional_ht_chart(home_stats, away_stats, team_home, team_away):
    """Exibe gráfico comparativo profissional"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h2 style="color: white; margin: 0; text-align: center; font-size: 26px;">
            📈 Gráfico Comparativo - 1º Tempo
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    
    metrics = ["Gols Feitos<br>(1ºT)", "Gols Sofridos<br>(1ºT)", "Média Feitos<br>(1ºT)", "Média Sofridos<br>(1ºT)"]
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
            text=f"Desempenho 1º Tempo: {team_home} vs {team_away}",
            font=dict(size=20, color='white')
        ),
        height=500,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#0d0d0d',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_complete_scenario_analysis(home_games, away_games, team_home, team_away):
    """Exibe análise completa de todos os cenários HT → FT"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h2 style="color: white; margin: 0; text-align: center; font-size: 26px;">
            🔄 Análise de Cenários: 1º Tempo → Resultado Final
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
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
    """Analisa todos os cenários possíveis HT → FT"""
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
    """Exibe estatísticas de cenários de forma profissional"""
    total_games = sum(scenarios.values())
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color} 0%, {color}CC 100%);
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                text-align: center;">
        <h3 style="color: white; margin: 0; font-size: 22px;">
            {position} {team_name}
        </h3>
        <p style="color: white; margin: 5px 0; font-size: 16px;">
            Total: {total_games} jogos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Organizar cenários por categoria
    scenarios_data = [
        ("✅ Vencendo no 1ºT", [
            ("HT Vitória → FT Vitória", scenarios['ht_win_ft_win'], "🏆"),
            ("HT Vitória → FT Empate", scenarios['ht_win_ft_draw'], "⚖️"),
            ("HT Vitória → FT Derrota", scenarios['ht_win_ft_loss'], "❌")
        ]),
        ("⚖️ Empatando no 1ºT", [
            ("HT Empate → FT Vitória", scenarios['ht_draw_ft_win'], "🏆"),
            ("HT Empate → FT Empate", scenarios['ht_draw_ft_draw'], "⚖️"),
            ("HT Empate → FT Derrota", scenarios['ht_draw_ft_loss'], "❌")
        ]),
        ("❌ Perdendo no 1ºT", [
            ("HT Derrota → FT Vitória", scenarios['ht_loss_ft_win'], "🏆🔄"),
            ("HT Derrota → FT Empate", scenarios['ht_loss_ft_draw'], "⚖️"),
            ("HT Derrota → FT Derrota", scenarios['ht_loss_ft_loss'], "❌")
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
        <span style="font-size: 18px; font-weight: bold; color: {color};">{count} ({percentage:.1f}%)</span>
    </div>
    <div style="background-color: #e0e0e0; border-radius: 10px; height: 12px; overflow: hidden;">
        <div style="background-color: {bar_color}; width: {bar_width}%; height: 100%; transition: width 0.3s ease;"></div>
    </div>
</div>
""
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


def show_probability_analysis(df, teams):
    """Análise de Valor baseada no Histórico de Performance por Faixas de Odds"""
    st.header("🎯 Probabilidade com historico das ODDs")
    
    if df is None or df.empty:
        st.error("Dados não disponíveis para análise.")
        return
        
    if not teams:
        st.warning("Nenhum time disponível.")
        return

    # Escolha dos times
    col1, col2 = st.columns(2)
    with col1:
        team_home = st.selectbox("🏠 Time Mandante:", teams, key="prob_home_simple")
    with col2:
        team_away = st.selectbox("✈️ Time Visitante:", teams, key="prob_away_simple")

    if team_home == team_away:
        st.error("⚠️ Selecione times diferentes para análise")
        return

    # Inserção das odds atuais com sliders
    st.subheader("📊 Odds do Confronto")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("🏠 **Odd Mandante**")
            odd_home = st.slider(
                "Valor:",
                min_value=1.01,
                max_value=10.0,
                value=2.30,
                step=0.01,
                format="%.2f",
                key="slider_home",
                help="Use o slider ou digite diretamente o valor"
            )
            odd_home_input = st.number_input(
                "Ou digite o valor exato:",
                min_value=1.01,
                max_value=50.0,
                value=odd_home,
                step=0.01,
                format="%.2f",
                key="input_home"
            )
            if odd_home_input != odd_home:
                odd_home = odd_home_input

        with col2:
            st.write("🤝 **Odd Empate**")
            odd_draw = st.slider(
                "Valor:",
                min_value=1.01,
                max_value=10.0,
                value=3.10,
                step=0.01,
                format="%.2f",
                key="slider_draw",
                help="Use o slider ou digite diretamente o valor"
            )
            odd_draw_input = st.number_input(
                "Ou digite o valor exato:",
                min_value=1.01,
                max_value=50.0,
                value=odd_draw,
                step=0.01,
                format="%.2f",
                key="input_draw"
            )
            if odd_draw_input != odd_draw:
                odd_draw = odd_draw_input

        with col3:
            st.write("✈️ **Odd Visitante**")
            odd_away = st.slider(
                "Valor:",
                min_value=1.01,
                max_value=10.0,
                value=3.30,
                step=0.01,
                format="%.2f",
                key="slider_away",
                help="Use o slider ou digite diretamente o valor"
            )
            odd_away_input = st.number_input(
                "Ou digite o valor exato:",
                min_value=1.01,
                max_value=50.0,
                value=odd_away,
                step=0.01,
                format="%.2f",
                key="input_away"
            )
            if odd_away_input != odd_away:
                odd_away = odd_away_input

    st.info(f"**Valores selecionados:** 🏠 {odd_home:.2f} | 🤝 {odd_draw:.2f} | ✈️ {odd_away:.2f}")

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

        # Análises detalhadas
        home_analysis = analyze_team_comprehensive(df, team_home, "Home", odd_home)
        away_analysis = analyze_team_comprehensive(df, team_away, "Away", odd_away)
        draw_analysis = analyze_draw_comprehensive(df, team_home, team_away, odd_draw)
        
        # Exibir análises profissionais
        display_professional_analysis(home_analysis, team_home, "🏠 Mandante", odd_home, prob_home_imp)
        display_professional_analysis(away_analysis, team_away, "✈️ Visitante", odd_away, prob_away_imp)
        display_draw_professional_analysis(draw_analysis, odd_draw, prob_draw_imp)
        
        # Recomendações finais
        display_final_recommendations(home_analysis, away_analysis, draw_analysis, 
                                    odd_home, odd_away, odd_draw, 
                                    team_home, team_away)

def analyze_team_comprehensive(df, team, position, current_odd):
    """Análise abrangente do desempenho do time"""
    if position == "Home":
        games = df[df['Home'] == team].copy()
        odd_col = 'odd Home'
    else:
        games = df[df['Away'] == team].copy()
        odd_col = 'odd Away'
    
    if games.empty or len(games) < 10:
        return {"error": "Dados insuficientes para análise"}
    
    # Verifica se as colunas necessárias existem
    required_cols = [odd_col, 'Gols Home', 'Gols Away']
    missing_cols = [col for col in required_cols if col not in games.columns]
    if missing_cols:
        return {"error": f"Colunas não encontradas: {missing_cols}"}
    
    games = games.dropna(subset=required_cols)
    
    # Calcula o resultado baseado nos gols
    if position == "Home":
        games['Resultado'] = games.apply(lambda row: 
            'Vitoria' if row['Gols Home'] > row['Gols Away'] else
            'Empate' if row['Gols Home'] == row['Gols Away'] else
            'Derrota', axis=1)
    else:
        games['Resultado'] = games.apply(lambda row: 
            'Vitoria' if row['Gols Away'] > row['Gols Home'] else
            'Empate' if row['Gols Home'] == row['Gols Away'] else
            'Derrota', axis=1)
    
    # Categorização por odds
    faixas_odds = categorize_odds(games, odd_col, current_odd)
    
    # Análise detalhada por faixa
    resultados = []
    for categoria, filtro_games in faixas_odds.items():
        if len(filtro_games) >= 3:
            total = len(filtro_games)
            vitorias = len(filtro_games[filtro_games['Resultado'] == 'Vitoria'])
            empates = len(filtro_games[filtro_games['Resultado'] == 'Empate'])
            derrotas = len(filtro_games[filtro_games['Resultado'] == 'Derrota'])
            
            # Análise de gols
            filtro_games['Total_Gols'] = filtro_games['Gols Home'] + filtro_games['Gols Away']
            over_15 = len(filtro_games[filtro_games['Total_Gols'] > 1.5])
            over_25 = len(filtro_games[filtro_games['Total_Gols'] > 2.5])
            under_25 = total - over_25
            
            resultados.append({
                'categoria': categoria,
                'total_jogos': total,
                'vitorias': vitorias,
                'empates': empates,
                'derrotas': derrotas,
                'perc_vitoria': (vitorias / total) * 100,
                'perc_empate': (empates / total) * 100,
                'perc_derrota': (derrotas / total) * 100,
                'over_15': over_15,
                'over_25': over_25,
                'under_25': under_25,
                'perc_over_25': (over_25 / total) * 100 if total > 0 else 0,
                'perc_under_25': (under_25 / total) * 100 if total > 0 else 0,
                'odd_media': filtro_games[odd_col].mean(),
                'is_current': is_current_range(current_odd, categoria)
            })
    
    return {
        'team': team,
        'position': position,
        'current_odd': current_odd,
        'total_games': len(games),
        'resultados': resultados
    }

def categorize_odds(games, odd_col, current_odd):
    """Categoriza jogos por faixas de odds"""
    return {
        'Grande Favorito': games[games[odd_col] <= 1.5],
        'Favorito': games[(games[odd_col] > 1.5) & (games[odd_col] <= 2.0)],
        'Leve Favorito': games[(games[odd_col] > 2.0) & (games[odd_col] <= 2.5)],
        'Equilibrado': games[(games[odd_col] > 2.5) & (games[odd_col] <= 3.5)],
        'Azarão': games[(games[odd_col] > 3.5) & (games[odd_col] <= 5.0)],
        'Grande Azarão': games[games[odd_col] > 5.0]
    }

def is_current_range(current_odd, categoria):
    """Verifica se a odd atual está na faixa da categoria"""
    ranges = {
        'Grande Favorito': (0, 1.5),
        'Favorito': (1.5, 2.0),
        'Leve Favorito': (2.0, 2.5),
        'Equilibrado': (2.5, 3.5),
        'Azarão': (3.5, 5.0),
        'Grande Azarão': (5.0, float('inf'))
    }
    
    if categoria in ranges:
        min_val, max_val = ranges[categoria]
        return min_val < current_odd <= max_val
    return False

def display_professional_analysis(analysis, team_name, position_emoji, current_odd, prob_implicita):
    """Exibe análise profissional detalhada"""
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.markdown("---")
    st.subheader(f"{position_emoji} Análise Histórica Detalhada - {team_name}")
    
    # Informações gerais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total de Jogos", analysis['total_games'])
    with col2:
        st.metric("🎯 Odd Atual", f"{current_odd:.2f}")
    with col3:
        st.metric("📈 Prob. Implícita", f"{prob_implicita:.1f}%")
    
    # Tabela detalhada
    if analysis['resultados']:
        df_results = pd.DataFrame([
            {
                'Situação': r['categoria'],
                'Jogos': r['total_jogos'],
                'Vitórias': f"{r['vitorias']} ({r['perc_vitoria']:.1f}%)",
                'Empates': f"{r['empates']} ({r['perc_empate']:.1f}%)",
                'Derrotas': f"{r['derrotas']} ({r['perc_derrota']:.1f}%)",
                'Over 2.5': f"{r['perc_over_25']:.1f}%",
                'Under 2.5': f"{r['perc_under_25']:.1f}%",
                'Odd Média': f"{r['odd_media']:.2f}"
            } for r in analysis['resultados']
        ])
        
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        # Análise da situação atual
        situacao_atual = next((r for r in analysis['resultados'] if r['is_current']), None)
        
        if situacao_atual:
            st.subheader("🎯 Análise da Situação Atual")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                valor_vitoria = situacao_atual['perc_vitoria'] - prob_implicita
                cor_vitoria = "normal" if abs(valor_vitoria) <= 5 else ("inverse" if valor_vitoria > 0 else "off")
                st.metric("Taxa de Vitória Histórica", 
                         f"{situacao_atual['perc_vitoria']:.1f}%",
                         delta=f"{valor_vitoria:+.1f}%")
            
            with col2:
                st.metric("Empates Nesta Faixa", 
                         f"{situacao_atual['perc_empate']:.1f}%")
            
            with col3:
                st.metric("Over 2.5 Gols", 
                         f"{situacao_atual['perc_over_25']:.1f}%")
            
            with col4:
                st.metric("Jogos Analisados", 
                         f"{situacao_atual['total_jogos']}")
            
            # Interpretação clara
            st.markdown("### 📝 Interpretação dos Resultados")
            
            if valor_vitoria > 8:
                st.success(f"✅ **EXCELENTE OPORTUNIDADE**: Historicamente, {team_name} vence {situacao_atual['perc_vitoria']:.1f}% dos jogos nesta faixa de odd, indicando {valor_vitoria:.1f}% mais chances que o mercado sugere!")
            elif valor_vitoria > 3:
                st.info(f"💰 **BOA OPORTUNIDADE**: O histórico mostra {valor_vitoria:.1f}% mais chances de vitória que a odd atual sugere.")
            elif valor_vitoria < -8:
                st.error(f"🚨 **EVITAR APOSTA**: Historicamente, {team_name} tem {abs(valor_vitoria):.1f}% menos chances de vencer que o mercado indica nesta faixa.")
            elif valor_vitoria < -3:
                st.warning(f"⚠️ **CUIDADO**: O histórico sugere {abs(valor_vitoria):.1f}% menos chances de vitória.")
            else:
                st.info("⚖️ **ODDS EQUILIBRADAS**: As probabilidades históricas estão alinhadas com o mercado.")

def analyze_draw_comprehensive(df, team_home, team_away, current_odd):
    """Análise abrangente de empates"""
    # Jogos entre os times
    direct_games = df[((df['Home'] == team_home) & (df['Away'] == team_away)) | 
                     ((df['Home'] == team_away) & (df['Away'] == team_home))].copy()
    
    # Histórico geral de empates dos times
    home_games = df[df['Home'] == team_home].copy()
    away_games = df[df['Away'] == team_away].copy()
    
    if direct_games.empty and (home_games.empty or away_games.empty):
        return {"error": "Dados insuficientes"}
    
    # Verifica colunas necessárias
    required_cols = ['odd Draw', 'Gols Home', 'Gols Away']
    
    # Análise de confrontos diretos
    direct_analysis = None
    if len(direct_games) >= 5 and all(col in direct_games.columns for col in required_cols):
        direct_games = direct_games.dropna(subset=required_cols)
        # Calcula empates baseado nos gols
        direct_games['Resultado'] = direct_games.apply(lambda row: 
            'Empate' if row['Gols Home'] == row['Gols Away'] else 'Nao_Empate', axis=1)
        
        empates_diretos = len(direct_games[direct_games['Resultado'] == 'Empate'])
        total_diretos = len(direct_games)
        perc_empates_diretos = (empates_diretos / total_diretos) * 100 if total_diretos > 0 else 0
        
        direct_analysis = {
            'total': total_diretos,
            'empates': empates_diretos,
            'percentual': perc_empates_diretos
        }
    
    # Análise por faixas de odd
    all_games = pd.concat([home_games, away_games])
    all_games = all_games.dropna(subset=required_cols)
    
    if all_games.empty:
        return {"error": "Dados insuficientes após limpeza"}
    
    # Calcula resultados para todos os jogos
    all_games['Resultado'] = all_games.apply(lambda row: 
        'Empate' if row['Gols Home'] == row['Gols Away'] else 'Nao_Empate', axis=1)
    
    faixas_empate = {
        'Empate Muito Provável': all_games[all_games['odd Draw'] <= 2.5],
        'Empate Provável': all_games[(all_games['odd Draw'] > 2.5) & (all_games['odd Draw'] <= 3.2)],
        'Empate Possível': all_games[(all_games['odd Draw'] > 3.2) & (all_games['odd Draw'] <= 4.0)],
        'Empate Improvável': all_games[all_games['odd Draw'] > 4.0]
    }
    
    resultados = []
    for categoria, games in faixas_empate.items():
        if len(games) >= 3:
            total = len(games)
            empates = len(games[games['Resultado'] == 'Empate'])
            perc_empate = (empates / total) * 100 if total > 0 else 0
            
            resultados.append({
                'categoria': categoria,
                'total': total,
                'empates': empates,
                'perc_empate': perc_empate,
                'odd_media': games['odd Draw'].mean(),
                'is_current': is_current_draw_range(current_odd, categoria)
            })
    
    return {
        'current_odd': current_odd,
        'direct_analysis': direct_analysis,
        'resultados': resultados
    }

def is_current_draw_range(current_odd, categoria):
    """Verifica se a odd atual está na faixa da categoria de empate"""
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
    """Exibe análise profissional de empates"""
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.markdown("---")
    st.subheader("🤝 Análise Histórica de Empates")
    
    # Confrontos diretos
    if analysis['direct_analysis']:
        st.markdown("#### 🔄 Confrontos Diretos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Jogos", analysis['direct_analysis']['total'])
        with col2:
            st.metric("Empates", analysis['direct_analysis']['empates'])
        with col3:
            st.metric("% Empates", f"{analysis['direct_analysis']['percentual']:.1f}%")
    
    # Análise por faixas
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
        
        # Situação atual
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
            
            # Interpretação
            if valor_empate > 5:
                st.success(f"✅ **VALOR NO EMPATE**: O histórico indica {valor_empate:.1f}% mais chances de empate que a odd sugere!")
            elif valor_empate < -5:
                st.error(f"🚨 **EMPATE SUPERVALORIZADO**: Historicamente {abs(valor_empate):.1f}% menos provável!")
            else:
                st.info("⚖️ **ODD DE EMPATE EQUILIBRADA**: Probabilidades alinhadas com o histórico.")

def display_final_recommendations(home_analysis, away_analysis, draw_analysis, 
                                odd_home, odd_away, odd_draw, team_home, team_away):
    """Exibe recomendações finais baseadas em todas as análises"""
    
    st.markdown("---")
    st.header("🎯 Recomendações Finais do Confronto")
    
    recommendations = []
    
    # Análise do mandante
    if home_analysis.get('resultados'):
        home_current = next((r for r in home_analysis['resultados'] if r['is_current']), None)
        if home_current:
            prob_home_hist = home_current['perc_vitoria']
            prob_home_market = (1/odd_home) * 100
            valor_home = prob_home_hist - prob_home_market
            
            if valor_home > 8:
                recommendations.append({
                    'tipo': f'🏠 Vitória {team_home}',
                    'odd': odd_home,
                    'valor': valor_home,
                    'confianca': 'Alta',
                    'descricao': f'Histórico mostra {prob_home_hist:.1f}% vs {prob_home_market:.1f}% do mercado'
                })
    
    # Análise do visitante
    if away_analysis.get('resultados'):
        away_current = next((r for r in away_analysis['resultados'] if r['is_current']), None)
        if away_current:
            prob_away_hist = away_current['perc_vitoria']
            prob_away_market = (1/odd_away) * 100
            valor_away = prob_away_hist - prob_away_market
            
            if valor_away > 8:
                recommendations.append({
                    'tipo': f'✈️ Vitória {team_away}',
                    'odd': odd_away,
                    'valor': valor_away,
                    'confianca': 'Alta',
                    'descricao': f'Histórico mostra {prob_away_hist:.1f}% vs {prob_away_market:.1f}% do mercado'
                })
    
    # Análise do empate
    if draw_analysis.get('resultados'):
        draw_current = next((r for r in draw_analysis['resultados'] if r['is_current']), None)
        if draw_current:
            prob_draw_hist = draw_current['perc_empate']
            prob_draw_market = (1/odd_draw) * 100
            valor_draw = prob_draw_hist - prob_draw_market
            
            if valor_draw > 5:
                recommendations.append({
                    'tipo': '🤝 Empate',
                    'odd': odd_draw,
                    'valor': valor_draw,
                    'confianca': 'Média' if valor_draw < 8 else 'Alta',
                    'descricao': f'Histórico mostra {prob_draw_hist:.1f}% vs {prob_draw_market:.1f}% do mercado'
                })
    
    # Exibir recomendações
    if recommendations:
        st.success("🎯 **OPORTUNIDADES IDENTIFICADAS**")
        
        for rec in recommendations:
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{rec['tipo']}**")
                with col2:
                    st.write(f"Odd: **{rec['odd']:.2f}**")
                with col3:
                    st.write(f"Valor: **+{rec['valor']:.1f}%**")
                with col4:
                    confidence_color = "🟢" if rec['confianca'] == 'Alta' else "🟡"
                    st.write(f"{confidence_color} {rec['confianca']}")
                
                st.caption(rec['descricao'])
                st.markdown("---")
    else:
        st.info("⚖️ **Nenhuma oportunidade clara identificada neste confronto com base no histórico.**")
    
    # Dicas adicionais
    st.subheader("💡 Dicas Complementares")
    
    # Análise de gols (se disponível)
    if home_analysis.get('resultados') and away_analysis.get('resultados'):
        home_current = next((r for r in home_analysis['resultados'] if r['is_current']), None)
        away_current = next((r for r in away_analysis['resultados'] if r['is_current']), None)
        
        if home_current and away_current:
            avg_over25 = (home_current['perc_over_25'] + away_current['perc_over_25']) / 2
            
            col1, col2 = st.columns(2)
            with col1:
                if avg_over25 > 60:
                    st.success(f"⚽ **OVER 2.5 GOLS**: {avg_over25:.1f}% média histórica - Considere apostas em mais gols")
                elif avg_over25 < 40:
                    st.info(f"🛡️ **UNDER 2.5 GOLS**: {avg_over25:.1f}% média histórica - Jogo pode ter poucos gols")
                else:
                    st.warning(f"⚖️ **GOLS EQUILIBRADOS**: {avg_over25:.1f}% média histórica")
            
            with col2:
                # Análise de mercados alternativos
                if odd_home < 2.0:
                    st.info("🏠 **Mandante favorito**: Considere 1X (vitória ou empate do mandante)")
                elif odd_away < 2.0:
                    st.info("✈️ **Visitante favorito**: Considere X2 (empate ou vitória do visitante)")
                else:
                    st.info("⚖️ **Jogo equilibrado**: Todas as opções têm valor similar")

def show_corner_analysis(df, teams):
    """Análise de escanteios com base nas médias e tendências recentes"""
    st.header("🚩 Análise de Escanteios")
    
    if not teams:
        st.warning("Nenhum time disponível.")
        return
    
    # Abas para diferentes análises
    tab1, tab2 = st.tabs(["🎯 Simulador de Jogo", "📊 Classificação Geral"])
    
    with tab1:
        st.subheader("🚩 Simulação Avançada de Escanteios por Jogo")
        
        # Seleção de times com logos
        col1, col2 = st.columns(2)
        with col1:
            st.write("🏠 **Time Mandante:**")
            home_team = st.selectbox("Selecione o mandante:", teams, key="corner_home", label_visibility="collapsed")
            display_team_with_logo(home_team, logo_size=(100, 100))
            
        with col2:
            st.write("✈️ **Time Visitante:**")
            away_team = st.selectbox("Selecione o visitante:", teams, key="corner_away", label_visibility="collapsed")
            display_team_with_logo(away_team, logo_size=(100, 100))

        if home_team == away_team:
            st.warning("Por favor, selecione dois times diferentes.")
            return

        if st.button("🚩 Simular Escanteios do Jogo", key="simulate_game"):
            # Calcula estatísticas avançadas de escanteios
            home_stats = calculate_advanced_corner_stats(df, home_team, as_home=True)
            away_stats = calculate_advanced_corner_stats(df, away_team, as_home=False)

            if home_stats['total_jogos'] < 3 or away_stats['total_jogos'] < 3:
                st.warning("Dados insuficientes para simular escanteios com confiança.")
                return

            # Exibir tabelas estatísticas separadas
            display_corner_statistics_tables(home_stats, away_stats, home_team, away_team)
            
            # Gráfico comparativo
            display_comparative_corner_chart(home_stats, away_stats, home_team, away_team)
            
            # Previsão do confronto
            display_match_corner_prediction(home_stats, away_stats, home_team, away_team)
    
    with tab2:
        # Chama a função de classificação
        show_corner_classification(df, teams)

def calculate_advanced_corner_stats(df, team, as_home=True):
    """Calcula estatísticas avançadas de escanteios com tendências recentes"""
    if as_home:
        games = df[df['Home'] == team].copy()
        corners_made_col = 'Corner Home'
        corners_conceded_col = 'Corner Away'
    else:
        games = df[df['Away'] == team].copy()
        corners_made_col = 'Corner Away' 
        corners_conceded_col = 'Corner Home'
    
    if games.empty:
        return create_empty_stats()
    
    # Remove jogos com dados faltantes
    games = games.dropna(subset=[corners_made_col, corners_conceded_col])
    
    if len(games) < 3:
        return create_empty_stats()
    
    # Ordena por data/jogo ID para análise cronológica
    if 'Jogo ID' in games.columns:
        games = games.sort_values('Jogo ID', ascending=False)
    
    # Estatísticas gerais
    total_jogos = len(games)
    total_made = games[corners_made_col].sum()
    total_conceded = games[corners_conceded_col].sum()
    
    media_made = total_made / total_jogos
    media_conceded = total_conceded / total_jogos
    
    # Últimos 3 jogos (mais recentes)
    last_3_games = games.head(3)
    last_3_made = last_3_games[corners_made_col].sum()
    last_3_conceded = last_3_games[corners_conceded_col].sum()
    
    media_last_3_made = last_3_made / 3
    media_last_3_conceded = last_3_conceded / 3
    
    # Tendência (comparação últimos 3 vs média geral)
    trend_made = ((media_last_3_made - media_made) / media_made * 100) if media_made > 0 else 0
    trend_conceded = ((media_last_3_conceded - media_conceded) / media_conceded * 100) if media_conceded > 0 else 0
    
    # Estatísticas de posição específica (como mandante ou visitante)
    position_media_made = media_made
    position_media_conceded = media_conceded
    
    return {
        'total_jogos': total_jogos,
        'media_geral_made': media_made,
        'media_geral_conceded': media_conceded,
        'media_posicao_made': position_media_made,
        'media_posicao_conceded': position_media_conceded,
        'media_last_3_made': media_last_3_made,
        'media_last_3_conceded': media_last_3_conceded,
        'trend_made': trend_made,
        'trend_conceded': trend_conceded,
        'last_3_games': last_3_games[[corners_made_col, corners_conceded_col]].values.tolist()
    }

def create_empty_stats():
    """Cria estrutura vazia para estatísticas"""
    return {
        'total_jogos': 0,
        'media_geral_made': 0,
        'media_geral_conceded': 0,
        'media_posicao_made': 0,
        'media_posicao_conceded': 0,
        'media_last_3_made': 0,
        'media_last_3_conceded': 0,
        'trend_made': 0,
        'trend_conceded': 0,
        'last_3_games': []
    }

def display_corner_statistics_tables(home_stats, away_stats, home_team, away_team):
    """Exibe tabelas estatísticas detalhadas para cada time"""
    st.subheader("📊 Estatísticas Detalhadas de Escanteios")
    
    # Criar duas colunas para as tabelas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Time Mandante")
        display_team_with_logo(home_team, logo_size=(100, 100))
        
        # Dados para tabela do mandante
        home_data = {
            'Métrica': [
                '📊 Média Geral (Feitos)',
                '📊 Média Geral (Sofridos)', 
                '🎯 Média como Mandante (Feitos)',
                '🎯 Média como Mandante (Sofridos)',
                '🔥 Últimos 3 Jogos (Feitos)',
                '🔥 Últimos 3 Jogos (Sofridos)',
                '📈 Tendência (Feitos)',
                '📉 Tendência (Sofridos)'
            ],
            'Valor': [
                f"{home_stats['media_geral_made']:.1f}",
                f"{home_stats['media_geral_conceded']:.1f}",
                f"{home_stats['media_posicao_made']:.1f}",
                f"{home_stats['media_posicao_conceded']:.1f}",
                f"{home_stats['media_last_3_made']:.1f}",
                f"{home_stats['media_last_3_conceded']:.1f}",
                f"{home_stats['trend_made']:+.1f}%",
                f"{home_stats['trend_conceded']:+.1f}%"
            ]
        }
        
        df_home = pd.DataFrame(home_data)
        st.dataframe(df_home, use_container_width=True, hide_index=True)
        
        # Métricas de destaque
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            trend_color = "normal" if abs(home_stats['trend_made']) < 10 else ("inverse" if home_stats['trend_made'] > 0 else "off")
            st.metric("🎯 Forma Recente (Feitos)", 
                     f"{home_stats['media_last_3_made']:.1f}",
                     delta=f"{home_stats['trend_made']:+.1f}%")
        with col1_2:
            st.metric("🛡️ Forma Recente (Sofridos)", 
                     f"{home_stats['media_last_3_conceded']:.1f}",
                     delta=f"{home_stats['trend_conceded']:+.1f}%")
    
    with col2:
        st.markdown("### ✈️ Time Visitante")
        display_team_with_logo(away_team, logo_size=(100, 100))
        
        # Dados para tabela do visitante
        away_data = {
            'Métrica': [
                '📊 Média Geral (Feitos)',
                '📊 Média Geral (Sofridos)',
                '🎯 Média como Visitante (Feitos)',
                '🎯 Média como Visitante (Sofridos)',
                '🔥 Últimos 3 Jogos (Feitos)',
                '🔥 Últimos 3 Jogos (Sofridos)',
                '📈 Tendência (Feitos)',
                '📉 Tendência (Sofridos)'
            ],
            'Valor': [
                f"{away_stats['media_geral_made']:.1f}",
                f"{away_stats['media_geral_conceded']:.1f}",
                f"{away_stats['media_posicao_made']:.1f}",
                f"{away_stats['media_posicao_conceded']:.1f}",
                f"{away_stats['media_last_3_made']:.1f}",
                f"{away_stats['media_last_3_conceded']:.1f}",
                f"{away_stats['trend_made']:+.1f}%",
                f"{away_stats['trend_conceded']:+.1f}%"
            ]
        }
        
        df_away = pd.DataFrame(away_data)
        st.dataframe(df_away, use_container_width=True, hide_index=True)
        
        # Métricas de destaque
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("🎯 Forma Recente (Feitos)", 
                     f"{away_stats['media_last_3_made']:.1f}",
                     delta=f"{away_stats['trend_made']:+.1f}%")
        with col2_2:
            st.metric("🛡️ Forma Recente (Sofridos)", 
                     f"{away_stats['media_last_3_conceded']:.1f}",
                     delta=f"{away_stats['trend_conceded']:+.1f}%")

def display_comparative_corner_chart(home_stats, away_stats, home_team, away_team):
    """Exibe gráfico comparativo entre os times"""
    st.subheader("📈 Comparativo Estatístico")
    
    # Dados para o gráfico
    categories = ['Média Geral\n(Feitos)', 'Média Geral\n(Sofridos)', 
                 'Média Posição\n(Feitos)', 'Média Posição\n(Sofridos)',
                 'Últimos 3\n(Feitos)', 'Últimos 3\n(Sofridos)']
    
    home_values = [
        home_stats['media_geral_made'], home_stats['media_geral_conceded'],
        home_stats['media_posicao_made'], home_stats['media_posicao_conceded'],
        home_stats['media_last_3_made'], home_stats['media_last_3_conceded']
    ]
    
    away_values = [
        away_stats['media_geral_made'], away_stats['media_geral_conceded'],
        away_stats['media_posicao_made'], away_stats['media_posicao_conceded'],
        away_stats['media_last_3_made'], away_stats['media_last_3_conceded']
    ]
    
    # Criar gráfico comparativo
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

def display_match_corner_prediction(home_stats, away_stats, home_team, away_team):
    """Exibe previsão sofisticada do confronto"""
    st.subheader("🎯 Previsão do Confronto")
    
    # Cálculo sofisticado considerando forma recente e histórico
    # Peso maior para forma recente (60%) e menor para média geral (40%)
    weight_recent = 0.6
    weight_general = 0.4
    
    # Escanteios esperados do mandante
    home_corners_made = (home_stats['media_last_3_made'] * weight_recent + 
                        home_stats['media_posicao_made'] * weight_general)
    
    # Considera também o que o visitante costuma sofrer
    away_corners_conceded = (away_stats['media_last_3_conceded'] * weight_recent + 
                            away_stats['media_posicao_conceded'] * weight_general)
    
    # Média ponderada entre o que o mandante faz e o que o visitante sofre
    predicted_home_corners = (home_corners_made + away_corners_conceded) / 2
    
    # Escanteios esperados do visitante
    away_corners_made = (away_stats['media_last_3_made'] * weight_recent + 
                        away_stats['media_posicao_made'] * weight_general)
    
    # Considera também o que o mandante costuma sofrer
    home_corners_conceded = (home_stats['media_last_3_conceded'] * weight_recent + 
                            home_stats['media_posicao_conceded'] * weight_general)
    
    # Média ponderada entre o que o visitante faz e o que o mandante sofre
    predicted_away_corners = (away_corners_made + home_corners_conceded) / 2
    
    # Total esperado
    total_predicted = predicted_home_corners + predicted_away_corners
    
    # Ajuste baseado na tendência
    trend_adjustment = (home_stats['trend_made'] + away_stats['trend_made']) / 200  # Divisão por 200 para converter % em fator
    total_predicted = total_predicted * (1 + trend_adjustment)
    
    # Exibir previsão
    st.markdown("### 🎯 Resultado da Simulação Avançada")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Escanteios Mandante", 
                 f"{predicted_home_corners:.1f}",
                 help="Baseado em forma recente (60%) e histórico (40%)")
    
    with col2:
        st.metric("✈️ Escanteios Visitante", 
                 f"{predicted_away_corners:.1f}",
                 help="Baseado em forma recente (60%) e histórico (40%)")
    
    with col3:
        st.metric("📦 Total Esperado", 
                 f"{total_predicted:.1f}",
                 help="Soma dos escanteios esperados + ajuste de tendência")
    
    with col4:
        confidence = min(100, max(60, (home_stats['total_jogos'] + away_stats['total_jogos']) * 2))
        st.metric("🎯 Confiabilidade", 
                 f"{confidence:.0f}%",
                 help="Baseada na quantidade de dados disponíveis")
    
    # Análise de probabilidades
    st.markdown("### 📊 Análise de Probabilidades")
    
    if total_predicted > 0:
        # Distribuição de probabilidade para número total de escanteios
        corners_range = range(0, int(total_predicted * 2) + 5)
        probabilities = [poisson.pmf(total, total_predicted) * 100 for total in corners_range]
        
        # Encontrar valores mais prováveis
        max_prob_idx = probabilities.index(max(probabilities))
        most_likely = corners_range[max_prob_idx]
        
        # Probabilidades para apostas comuns
        prob_over_8_5 = sum(poisson.pmf(x, total_predicted) for x in range(9, 25)) * 100
        prob_over_9_5 = sum(poisson.pmf(x, total_predicted) for x in range(10, 25)) * 100
        prob_over_10_5 = sum(poisson.pmf(x, total_predicted) for x in range(11, 25)) * 100
        
        # Exibir probabilidades de apostas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"**Mais Provável:** {most_likely} escanteios ({probabilities[max_prob_idx]:.1f}%)")
        with col2:
            st.info(f"**Over 8.5:** {prob_over_8_5:.1f}%")
        with col3:
            st.info(f"**Over 9.5:** {prob_over_9_5:.1f}%")
        with col4:
            st.info(f"**Over 10.5:** {prob_over_10_5:.1f}%")
        
        # Gráfico de distribuição
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(corners_range), 
            y=probabilities,
            marker_color=['#ff6b6b' if x == most_likely else '#1f77b4' for x in corners_range],
            text=[f"{p:.1f}%" if p > 2 else "" for p in probabilities],
            textposition='auto',
            name='Probabilidade'
        ))
        
        fig.update_layout(
            title="Distribuição de Probabilidades - Total de Escanteios do Jogo",
            xaxis_title="Total de Escanteios no Jogo",
            yaxis_title="Probabilidade (%)",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recomendações baseadas na análise
        st.markdown("### 💡 Recomendações de Apostas")
        
        if prob_over_9_5 > 60:
            st.success(f"✅ **OVER 9.5 ESCANTEIOS** - {prob_over_9_5:.1f}% de probabilidade")
        elif prob_over_8_5 > 65:
            st.success(f"✅ **OVER 8.5 ESCANTEIOS** - {prob_over_8_5:.1f}% de probabilidade")
        elif total_predicted < 8:
            st.info(f"⚖️ **UNDER 8.5 ESCANTEIOS** pode ser uma boa opção - Total esperado: {total_predicted:.1f}")
        else:
            st.warning("⚠️ **JOGO EQUILIBRADO** - Escanteios podem variar muito")

def show_corner_classification(df, teams):
    """Exibe classificação geral de escanteios por time"""
    st.subheader("📊 Classificação Geral de Escanteios")
    
    # Calcula médias de escanteios feitos e sofridos como mandante e visitante
    stats_list = []
    for team in teams:
        home_stats = calculate_advanced_corner_stats(df, team, as_home=True)
        away_stats = calculate_advanced_corner_stats(df, team, as_home=False)
        
        total_jogos = home_stats['total_jogos'] + away_stats['total_jogos']
        
        if total_jogos > 0:
            media_feitos = (home_stats['media_geral_made'] * home_stats['total_jogos'] + 
                           away_stats['media_geral_made'] * away_stats['total_jogos']) / total_jogos
            
            media_sofridos = (home_stats['media_geral_conceded'] * home_stats['total_jogos'] + 
                             away_stats['media_geral_conceded'] * away_stats['total_jogos']) / total_jogos
        else:
            media_feitos = media_sofridos = 0
        
        stats_list.append({
            "Time": team,
            "Média Escanteios Feitos": round(media_feitos, 2),
            "Média Escanteios Sofridos": round(media_sofridos, 2),
            "Jogos Analisados": total_jogos
        })
    
    df_stats = pd.DataFrame(stats_list)
    df_stats = df_stats.sort_values(by="Média Escanteios Feitos", ascending=False)
    
    # Adicionar ranking
    df_stats.reset_index(drop=True, inplace=True)
    df_stats.index = df_stats.index + 1
    
    st.dataframe(df_stats, use_container_width=True)

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
<span>⚽</span> <span style="font-weight:500; color:#1f4e79;">{team_name}</span>
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
    """Gera matriz de probabilidades para placares de 0x0 até 5x5"""
    
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
    """Gera matriz de probabilidades para placares de 0x0 até 5x5"""
    
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
    """Gera matriz de probabilidades para placares de 0x0 até 5x5"""
    
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
            st.markdown(f"""
            <div style="padding: 15px; background-color: #e8f4fd; border-radius: 10px; border-left: 4px solid #1f77b4;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    {display_team_with_logo(team_home, (70, 70), show_name=False)}
                    <strong>Expectativa - {team_home}</strong>
                </div>
                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">
                    {resultado['expectativa_home']:.2f} gols
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div style="padding: 15px; background-color: #fff3cd; border-radius: 10px; border-left: 4px solid #ffc107;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    {display_team_with_logo(team_away, (70, 70), show_name=False)}
                    <strong>Expectativa - {team_away}</strong>
                </div>
                <div style="font-size: 1.5em; font-weight: bold; color: #856404;">
                    {resultado['expectativa_away']:.2f} gols
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
        st.subheader("📈 Matriz de Probabilidades (0x0 até 5x5)")
        
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
def show_score_prediction(df, teams):
    """Predição de placar usando Distribuição de Poisson (COM LOGOS)"""
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
        # Obtém estatísticas dos times usando as funções do código original
        home_stats = calculate_team_stats(df, team_home, as_home=True)
        away_stats = calculate_team_stats(df, team_away, as_home=False)

        # Validação mínima de dados
        if home_stats['jogos'] < 3 or away_stats['jogos'] < 3:
            st.warning("Dados insuficientes para realizar predição com confiança.")
            return

        # Calcula placar mais provável com Poisson
        resultado, probabilidade, gols_esperados_home, gols_esperados_away = predict_score_poisson(
            home_avg=home_stats['media_gols_feitos'],
            away_avg=away_stats['media_gols_feitos'],
            home_def=home_stats['media_gols_sofridos'],
            away_def=away_stats['media_gols_sofridos']
        )

        # Exibição de resultado com logos
        st.success("🎯 Placar Mais Provável:")
        display_score_result_with_logos(team_home, resultado[0], resultado[1], team_away)
        
        st.metric(label="🎯 Probabilidade estimada do placar", value=f"{probabilidade*100:.2f}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("🏠 Gols esperados - Mandante")
            normalized_home = normalize_team_name(team_home)
            logo_home = TEAM_LOGOS.get(normalized_home) or TEAM_LOGOS.get(team_home, "")

            html_home = f"""
            <div style="display:flex; align-items:center; gap:15px; padding:10px; background-color:#2E2E2E; border-radius:8px;">
                <div style="background-color:transparent; display:flex; align-items:center;">
                    <img src="{logo_home}" style="width:60px; height:60px; object-fit:contain; background:none;" alt="{normalized_home}">
                </div>
                <div style="color:white;">
                    <div style="font-weight:bold; font-size:18px;">{normalized_home}</div>
                    <div style="font-size:24px; color:#4CAF50; font-weight:bold;">{gols_esperados_home:.2f} gols</div>
                </div>
            </div>
            """
            st.markdown(html_home, unsafe_allow_html=True)

        with col2:
            st.info("✈️ Gols esperados - Visitante")
            normalized_away = normalize_team_name(team_away)
            logo_away = TEAM_LOGOS.get(normalized_away) or TEAM_LOGOS.get(team_away, "")
    
            html_away = f"""
            <div style="display:flex; align-items:center; gap:15px; padding:10px; background-color:#2E2E2E; border-radius:8px;">
                <div style="background-color:transparent; display:flex; align-items:center;">
                    <img src="{logo_away}" style="width:60px; height:60px; object-fit:contain; background:none;" alt="{normalized_away}">
                </div>
                <div style="color:white;">
                    <div style="font-weight:bold; font-size:18px;">{normalized_away}</div>
                    <div style="font-size:24px; color:#4CAF50; font-weight:bold;">{gols_esperados_away:.2f} gols</div>
                </div>
            </div>
            """
            st.markdown(html_away, unsafe_allow_html=True)

        # Tabela com top 10 placares prováveis
        st.subheader("📋 Top 10 placares mais prováveis")
        results = []
        for h in range(6):
            for a in range(6):
                prob = poisson.pmf(h, gols_esperados_home) * poisson.pmf(a, gols_esperados_away)
                results.append(((h, a), prob))
        results.sort(key=lambda x: x[1], reverse=True)

        for i, ((h, a), p) in enumerate(results[:10], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
    
            placar_html = f"""
            <div style="
                display: flex;
                align-items: center;
                background-color: #2E2E2E;
                padding: 10px;
                margin: 5px 0;
                border-radius: 8px;
                justify-content: space-between;
                flex-wrap: wrap;
                min-height: 50px;
                color: white;
            ">
                <div style="font-size: 18px; min-width: 30px;">{emoji}</div>
                <div style="display: flex; align-items: center; gap: 8px; flex: 1; justify-content: center;">
                    <span style="color: white;">{team_home}</span>
                    <span style="font-size: 20px; color: #FFD700; margin: 0 10px;">{h} x {a}</span>
                    <span style="color: white;">{team_away}</span>
                </div>
                <div style="font-size: 16px; color: #28a745; min-width: 60px; text-align: right;">{p*100:.2f}%</div>
            </div>
            """
            st.markdown(placar_html, unsafe_allow_html=True)


def main():
    st.markdown('<h1 class="main-header">⚽ Análise & Estatística Brasileirão</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema completo de análise estatística do Campeonato Brasileiro</p>', unsafe_allow_html=True)

    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df = load_data()

    if df.empty:
        st.error("⚠ Não foi possível carregar os dados.")
        st.info("📂 Certifique-se de que o arquivo está na raiz do repositório.")
        return

    # ==== SEÇÃO DE FILTROS MODERNA COM SELEÇÃO RÁPIDA ====
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 25px; 
                border-radius: 15px; 
                margin: 20px 0;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
        <h3 style="color: white; margin: 0; text-align: center; font-size: 24px;">
            📅 Filtros de Temporada
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Estilo CSS para os botões de filtro
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    # Container para filtros
    st.markdown("<h4 style='text-align: center; color: #667eea; margin: 20px 0;'>Selecione Rápido:</h4>", unsafe_allow_html=True)
    
    # Criar 5 colunas para os botões de filtro
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Inicializar estado do filtro se não existir
    if 'ano_selecionado' not in st.session_state:
        st.session_state.ano_selecionado = "2025"
    
    # Estilo para botão selecionado
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
            
            if st.button("📊 Análise 1º Tempo", key="primeiro_tempo", use_container_width=True):
                st.session_state.selected_analysis = "2. Análise 1º Tempo HT"
                st.rerun()
            
            if st.button("🚩 Análise de Escanteios", key="corner_analysis", use_container_width=True):
                st.session_state.selected_analysis = "7. Análise de Escanteios"
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
            elif st.session_state.selected_analysis == "2. Análise 1º Tempo HT":
                show_first_half_analysis(df, teams)
            elif st.session_state.selected_analysis == "3. Cálculo de Probabilidades Implícitas":
                show_probability_analysis(df, teams)
            elif st.session_state.selected_analysis == "4. Confronto Direto":
                show_direct_confrontation(df, teams)
            elif st.session_state.selected_analysis == "5. Predição de Placar (Poisson)":
                show_score_prediction(df, teams)
            elif st.session_state.selected_analysis == "6. Gráficos Interativos":
                show_interactive_charts(df)
            elif st.session_state.selected_analysis == "7. Análise de Escanteios":
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
    
    # Estatísticas de escanteios
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











































































