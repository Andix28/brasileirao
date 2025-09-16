# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import poisson
import warnings

warnings.filterwarnings('ignore')

# ====== SISTEMA DE LOGOS DOS TIMES ======
# Adicione este código logo após os imports no início do arquivo

import base64
import requests
from io import BytesIO
from textwrap import dedent

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
        "Atletico GO": "https://logodetimes.com/wp-content/uploads/atletico-goianiense.png",
        "Atlético-GO": "https://logodetimes.com/wp-content/uploads/atletico-goianiense.png",
        "A. Goianiense": "https://logodetimes.com/wp-content/uploads/atletico-goianiense.png",
        "Criciuma": "https://logodetimes.com/wp-content/uploads/criciuma.png",
        "Criciúma": "https://logodetimes.com/wp-content/uploads/criciuma.png",
        "Juventude": "https://logodetimes.com/wp-content/uploads/juventude-rs.png",
        "Palmeiras": "https://logodetimes.com/wp-content/uploads/palmeiras.png"
    }

def _clean_html(s: str) -> str:
    """Remove indentação comum e espaços extras no início/fim para evitar code blocks no Markdown."""
    return dedent(s).strip()

def get_team_display_name_with_logo(team_name, logo_size=(25, 25)):
    """
    Retorna HTML (string) para exibir o nome do time com logo.
    SEM indentação à esquerda para não virar bloco de código no Markdown.
    """
    logo_url = TEAM_LOGOS.get(team_name)
    if logo_url:
        return _clean_html(f"""
<div style="display:flex; align-items:center; gap:8px; margin:2px 0;">
  <img src="{logo_url}"
       style="width:{logo_size[0]}px; height:{logo_size[1]}px; border-radius:4px; object-fit:contain;"
       onerror="this.style.display='none';"
       alt="{team_name}">
  <span style="font-weight:500; color:#1f4e79;">{team_name}</span>
</div>
""")
    # fallback
    return _clean_html(f"""
<span>⚽</span> <span style="font-weight:500; color:#1f4e79;">{team_name}</span>
""")


def display_team_with_logo(team_name, logo_size=(25, 25)):
    """
    Exibe diretamente no Streamlit o time com logo.
    """
    st.markdown(get_team_display_name_with_logo(team_name, logo_size), unsafe_allow_html=True)


def create_team_selectbox_with_logos(label, teams, key, logo_size=(20, 20)):
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
    """
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
        **✈️ {team_away} (Como Visitante)**
        - 🎮 Jogos analisados: **{analysis['away_jogos']}**
        - ⚽ Gols marcados: **{analysis['away_gols_total']}** (média: {analysis['away_media_gols']}/jogo)
        - 🥅 Gols sofridos: **{analysis['away_sofridos_total']}** (média: {analysis['away_media_sofridos']}/jogo)
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
    """Análise de 1º Tempo HT"""
    st.header("📊 Análise 1º Tempo HT")
    
    if len(teams) < 2:
        st.warning("Selecione pelo menos dois times.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        team_home = st.selectbox("🏠 Time Mandante:", teams, key="ht_home")
    with col2:
        team_away = st.selectbox("✈️ Time Visitante:", teams, key="ht_away")
        
    if not team_home or not team_away or team_home == team_away:
        st.warning("Selecione dois times diferentes.")
        return
    
    # Verificar se as colunas necessárias existem
    required_cols = ['Home Score HT', 'Away Score HT', 'Gols Home', 'Gols Away']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠ Colunas necessárias não encontradas: {', '.join(missing_cols)}")
        return

    # Filtrar jogos
    home_games = df[df['Home'] == team_home].copy()
    away_games = df[df['Away'] == team_away].copy()
    
    # Calcular estatísticas do 1º tempo
    home_ht_stats = calculate_ht_stats(home_games, True)  # True = mandante
    away_ht_stats = calculate_ht_stats(away_games, False)  # False = visitante
    
    # Exibir tabela comparativa
    st.subheader("📊 Comparativo 1º Tempo")
    df_comparativo = pd.DataFrame({
        "Métrica": [
            "Jogos Analisados",
            "Gols Feitos no 1º Tempo", 
            "Gols Sofridos no 1º Tempo",
            "Média Gols Feitos/Jogo (1ºT)",
            "Média Gols Sofridos/Jogo (1ºT)"
        ],
        f"{team_home} (Mandante)": [
            home_ht_stats['jogos'],
            home_ht_stats['gols_feitos_ht'],
            home_ht_stats['gols_sofridos_ht'],
            f"{home_ht_stats['media_feitos_ht']:.2f}",
            f"{home_ht_stats['media_sofridos_ht']:.2f}"
        ],
        f"{team_away} (Visitante)": [
            away_ht_stats['jogos'],
            away_ht_stats['gols_feitos_ht'],
            away_ht_stats['gols_sofridos_ht'],
            f"{away_ht_stats['media_feitos_ht']:.2f}",
            f"{away_ht_stats['media_sofridos_ht']:.2f}"
        ]
    })
    st.dataframe(df_comparativo, use_container_width=True, hide_index=True)
    
    # Gráfico de colunas
    st.subheader("📈 Gráfico Comparativo - 1º Tempo")
    fig = go.Figure()
    
    metrics = ["Gols Feitos (1ºT)", "Gols Sofridos (1ºT)"]
    home_values = [home_ht_stats['gols_feitos_ht'], home_ht_stats['gols_sofridos_ht']]
    away_values = [away_ht_stats['gols_feitos_ht'], away_ht_stats['gols_sofridos_ht']]
    
    fig.add_trace(go.Bar(
        x=metrics, 
        y=home_values, 
        name=f"{team_home} (Mandante)", 
        marker_color='royalblue'
    ))
    fig.add_trace(go.Bar(
        x=metrics, 
        y=away_values, 
        name=f"{team_away} (Visitante)", 
        marker_color='darkorange'
    ))
    
    fig.update_layout(
        barmode='group',
        xaxis_title="Métrica",
        yaxis_title="Quantidade",
        legend_title="Times",
        title=f"Desempenho 1º Tempo: {team_home} vs {team_away}"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de reversões/manutenções de resultado
    st.subheader("🔄 Análise de Reversões de Resultado")
    show_result_reversions(home_games, away_games, team_home, team_away)

def calculate_ht_stats(games, is_home):
    """Calcula estatísticas do 1º tempo"""
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

def show_result_reversions(home_games, away_games, team_home, team_away):
    """Exibe análise de reversões de resultado entre 1º tempo e resultado final"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**🏠 {team_home} (Como Mandante)**")
        home_reversions = analyze_reversions(home_games, True)
        display_reversion_stats(home_reversions)
        
    with col2:
        st.write(f"**✈️ {team_away} (Como Visitante)**")  
        away_reversions = analyze_reversions(away_games, False)
        display_reversion_stats(away_reversions)

def analyze_reversions(games, is_home):
    """Analisa reversões de resultado"""
    if games.empty:
        return {
            'venceu_ht_perdeu_final': 0,
            'venceu_ht_empatou_final': 0,
            'perdeu_ht_venceu_final': 0,
            'perdeu_ht_empatou_final': 0,
            'empate_ht_venceu_final': 0,
            'empate_ht_perdeu_final': 0
        }
    
    reversions = {
        'venceu_ht_perdeu_final': 0,
        'venceu_ht_empatou_final': 0,
        'perdeu_ht_venceu_final': 0,
        'perdeu_ht_empatou_final': 0,
        'empate_ht_venceu_final': 0,
        'empate_ht_perdeu_final': 0
    }
    
    for _, game in games.iterrows():
        if is_home:
            ht_home = game['Home Score HT']
            ht_away = game['Away Score HT']
            final_home = game['Gols Home']
            final_away = game['Gols Away']
        else:
            # Para time visitante, inverter a perspectiva
            ht_home = game['Away Score HT']
            ht_away = game['Home Score HT']
            final_home = game['Gols Away']
            final_away = game['Gols Home']
        
        # Resultado no 1º tempo
        if ht_home > ht_away:
            ht_result = 'win'
        elif ht_home < ht_away:
            ht_result = 'loss'
        else:
            ht_result = 'draw'
        
        # Resultado final
        if final_home > final_away:
            final_result = 'win'
        elif final_home < final_away:
            final_result = 'loss'
        else:
            final_result = 'draw'
        
        # Contar reversões
        if ht_result == 'win' and final_result == 'loss':
            reversions['venceu_ht_perdeu_final'] += 1
        elif ht_result == 'win' and final_result == 'draw':
            reversions['venceu_ht_empatou_final'] += 1
        elif ht_result == 'loss' and final_result == 'win':
            reversions['perdeu_ht_venceu_final'] += 1
        elif ht_result == 'loss' and final_result == 'draw':
            reversions['perdeu_ht_empatou_final'] += 1
        elif ht_result == 'draw' and final_result == 'win':
            reversions['empate_ht_venceu_final'] += 1
        elif ht_result == 'draw' and final_result == 'loss':
            reversions['empate_ht_perdeu_final'] += 1
    
    return reversions

def display_reversion_stats(reversions):
    """Exibe estatísticas de reversão"""
    st.write("**Mudanças de Resultado:**")
    st.write(f"• Venceu no 1ºT → Perdeu no final: {reversions['venceu_ht_perdeu_final']}")
    st.write(f"• Venceu no 1ºT → Empatou no final: {reversions['venceu_ht_empatou_final']}")
    st.write(f"• Perdeu no 1ºT → Venceu no final: {reversions['perdeu_ht_venceu_final']}")
    st.write(f"• Perdeu no 1ºT → Empatou no final: {reversions['perdeu_ht_empatou_final']}")
    st.write(f"• Empatou no 1ºT → Venceu no final: {reversions['empate_ht_venceu_final']}")
    st.write(f"• Empatou no 1ºT → Perdeu no final: {reversions['empate_ht_perdeu_final']}")


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
    """Análise de escanteios com base nas médias"""
    st.header("🚩 Análise de Escanteios")
    
    if not teams:
        st.warning("Nenhum time disponível.")
        return
    
    # Abas para diferentes análises
    tab1, tab2 = st.tabs(["🎯 Simulador de Jogo", "📊 Classificação Geral"])
    
    with tab1:
        st.subheader("🚩 Simulação de Escanteios por Jogo")
        
        col1, col2 = st.columns(2)
        with col1:
            home_team = st.selectbox("🏠 Time Mandante:", teams, key="corner_home")
        with col2:
            away_team = st.selectbox("✈️ Time Visitante:", teams, key="corner_away")

        if home_team == away_team:
            st.warning("Por favor, selecione dois times diferentes.")
            return

        if st.button("🚩 Simular Escanteios do Jogo", key="simulate_game"):
            # Calcula estatísticas de escanteios
            home_stats = calculate_team_stats(df, home_team, as_home=True)
            away_stats = calculate_team_stats(df, away_team, as_home=False)

            if home_stats['jogos'] < 3 or away_stats['jogos'] < 3:
                st.warning("Dados insuficientes para simular escanteios com confiança.")
                return

            # Médias esperadas
            corner_home = (home_stats['media_escanteios_feitos'] + away_stats['media_escanteios_sofridos']) / 2
            corner_away = (away_stats['media_escanteios_feitos'] + home_stats['media_escanteios_sofridos']) / 2
            total_corners = corner_home + corner_away

            st.subheader("📊 Resultado da Simulação")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏠 Escanteios Mandante", f"{corner_home:.1f}")
            with col2:
                st.metric("✈️ Escanteios Visitante", f"{corner_away:.1f}")
            with col3:
                st.metric("📦 Total Esperado", f"{total_corners:.1f}")

            # Distribuição de probabilidade para número total de escanteios
            if total_corners > 0:
                st.subheader("📈 Distribuição de Probabilidades (Total de Escanteios)")
                corners_range = range(0, 21)
                probabilities = [poisson.pmf(total, total_corners) * 100 for total in corners_range]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(corners_range), 
                    y=probabilities,
                    marker_color='#1f77b4',
                    text=[f"{p:.1f}%" for p in probabilities],
                    textposition='auto'
                ))
                fig.update_layout(
                    title="Distribuição Poisson do Total de Escanteios",
                    xaxis_title="Total de Escanteios no Jogo",
                    yaxis_title="Probabilidade (%)",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Chama a nova função de classificação
        show_corner_classification(df, teams)
        
def show_corner_classification(df, teams):
    """Exibe classificação geral de escanteios por time"""
    st.subheader("📊 Classificação Geral de Escanteios")
    # Calcula médias de escanteios feitos e sofridos como mandante e visitante
    stats_list = []
    for team in teams:
        home_stats = calculate_team_stats(df, team, as_home=True)
        away_stats = calculate_team_stats(df, team, as_home=False)
        total_jogos = home_stats['jogos'] + away_stats['jogos']
        media_feitos = (
            home_stats['escanteios_feitos'] + away_stats['escanteios_feitos']
        ) / total_jogos if total_jogos > 0 else 0
        media_sofridos = (
            home_stats['escanteios_sofridos'] + away_stats['escanteios_sofridos']
        ) / total_jogos if total_jogos > 0 else 0
        stats_list.append({
            "Time": team,
            "Média Escanteios Feitos": round(media_feitos, 2),
            "Média Escanteios Sofridos": round(media_sofridos, 2),
            "Jogos Analisados": total_jogos
        })
    df_stats = pd.DataFrame(stats_list)
    df_stats = df_stats.sort_values(by="Média Escanteios Feitos", ascending=False)
    st.dataframe(df_stats, use_container_width=True)

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
            logo_home = TEAM_LOGOS.get(team_home, "")
            if logo_home:
                st.markdown(f'<img src="{logo_home}" width="25" style="border-radius: 3px;">', unsafe_allow_html=True)
            st.markdown(f"**{team_home}: {gols_esperados_home:.2f} gols**")
        with col2:
            st.info("✈️ Gols esperados - Visitante")  
            logo_away = TEAM_LOGOS.get(team_away, "")
            if logo_away:
                st.markdown(f'<img src="{logo_away}" width="25" style="border-radius: 3px;">', unsafe_allow_html=True)
            st.markdown(f"**{team_away}: {gols_esperados_away:.2f} gols**")

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

            html_home = get_team_display_name_with_logo(team_home, logo_size=(50, 50))
            html_away = get_team_display_name_with_logo(team_away, logo_size=(50, 50))

            ranking_html = _clean_html(f"""
<div style="display:flex; align-items:center; justify-content:space-between;
    background-color:{'#fff3cd' if i <= 3 else '#f8f9fa'};
    padding:8px 12px; margin:4px 0; border-radius:6px;
    border-left:3px solid {'#ffc107' if i <= 3 else '#dee2e6'};">
  <span style="font-weight:bold; min-width:30px;">{emoji}</span>
  <div style="display:flex; align-items:center; gap:10px;">
    {html_home}
    <span style="font-weight:bold; color:#1f4e79; margin:0 5px;">{h} x {a}</span>
    {html_away}
  </div>
  <span style="font-weight:bold; color:#28a745;">{p*100:.2f}%</span>
</div>
""")
            st.markdown(ranking_html, unsafe_allow_html=True)


def main():
    st.markdown('<h1 class="main-header">⚽ Análise & Estatística Brasileirão</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema completo de análise estatística do Campeonato Brasileiro</p>', unsafe_allow_html=True)

    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df = load_data()

    if df.empty:
        st.error("⚠ Não foi possível carregar os dados.")
        st.info("🔍 Certifique-se de que o arquivo está na raiz do repositório.")
        return

    # Filtro de ano no topo (sempre visível)
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">📅 Filtros de Temporada</h3>', unsafe_allow_html=True)
    col_filter = st.columns([1, 2, 1])[1]
    with col_filter:
        anos = sorted(df['Ano'].dropna().unique())
        
        # Criação das opções de filtro
        opcoes_anos = []
        
        # Adiciona anos individuais
        for ano in anos:
            opcoes_anos.append(f"{ano}")
        
        # Adiciona opção para ambos os anos (se existirem 2024 e 2025)
        if 2024 in anos and 2025 in anos:
            opcoes_anos.append("2024 + 2025 (Combinados)")
        
        # Se houver mais de 2 anos, adiciona opção "Todos os Anos"
        if len(anos) > 1:
            opcoes_anos.append("Todos os Anos")
        
        ano_selecionado = st.selectbox(
            "Selecione a Temporada:", 
            opcoes_anos, 
            key="ano_selecionado",
            help="Escolha um ano específico, combinação de anos ou todos os anos disponíveis"
        )
        
        # Aplicação do filtro baseado na seleção
        df_original = df.copy()  # Mantém cópia dos dados originais
        
        if ano_selecionado == "2024 + 2025 (Combinados)":
            df = df[df['Ano'].isin([2024, 2025])]
            st.info("📊 Analisando dados combinados de 2024 e 2025")
        elif ano_selecionado == "Todos os Anos":
            # Mantém todos os dados
            st.info(f"📊 Analisando dados de todos os anos: {', '.join(map(str, sorted(anos)))}")
        else:
            # Filtro por ano específico
            ano_num = int(ano_selecionado)
            df = df[df['Ano'] == ano_num]
            st.info(f"📊 Analisando dados de {ano_num}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Inicializa lista de times de forma segura
    if ('Home' in df.columns) and ('Away' in df.columns):
        home_teams = df['Home'].dropna().astype(str).str.strip()
        away_teams = df['Away'].dropna().astype(str).str.strip()
        teams = sorted(set(home_teams) | set(away_teams))
    else:
        teams = []

    # Exibe estatísticas do filtro aplicado
    if not df.empty:
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("🏟️ Total de Jogos", len(df))
        with col_stat2:
            st.metric("⚽ Times Únicos", len(teams))
        with col_stat3:
            if ano_selecionado == "2024 + 2025 (Combinados)":
                jogos_2024 = len(df[df['Ano'] == 2024])
                jogos_2025 = len(df[df['Ano'] == 2025])
                st.metric("📈 Distribuição", f"2024: {jogos_2024} | 2025: {jogos_2025}")
            elif ano_selecionado == "Todos os Anos":
                st.metric("📅 Período", f"{min(anos)} - {max(anos)}")
            else:
                # Verifica se as colunas existem antes de calcular
                if 'Gols Home' in df.columns and 'Gols  Away' in df.columns:
                    total_gols = df['Gols Home'].sum() + df['Gols  Away'].sum()
                    media_gols = total_gols / len(df) if len(df) > 0 else 0
                    st.metric("⚽ Média Gols/Jogo", f"{media_gols:.2f}")
                else:
                    st.metric("⚽ Média Gols/Jogo", "N/A")

    # Inicializa seleção de análise
    if 'selected_analysis' not in st.session_state:
        st.session_state.selected_analysis = None

    # Seleção de análise
    if st.session_state.selected_analysis is None:
        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📊 Opções de Análise</h2>', unsafe_allow_html=True)
        
        # Adiciona informação sobre o filtro ativo
        if ano_selecionado == "2024 + 2025 (Combinados)":
            st.markdown(
                '<div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #1f77b4;">'
                '<strong>🔄 Modo Combinado Ativo:</strong> As análises incluirão dados de 2024 e 2025 juntos'
                '</div>', 
                unsafe_allow_html=True
            )
        elif ano_selecionado == "Todos os Anos":
            st.markdown(
                '<div style="background-color: #f0f8e8; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #28a745;">'
                f'<strong>📊 Análise Completa:</strong> Incluindo todos os anos disponíveis ({", ".join(map(str, sorted(anos)))})'
                '</div>', 
                unsafe_allow_html=True
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏆 Análise de Desempenho", key="desempenho"):
                st.session_state.selected_analysis = "1. Análise de Desempenho de Time"
                st.rerun()
            if st.button("📊 Análise 1º Tempo", key="primeiro_tempo"):
                st.session_state.selected_analysis = "2. Análise 1º Tempo HT"
                st.rerun()
            if st.button("🚩 Análise de Escanteios", key="corner_analysis"):
                st.session_state.selected_analysis = "7. Análise de Escanteios"
                st.rerun()

        with col2:
            if st.button("🎯 Probabilidades", key="probabilidades"):
                st.session_state.selected_analysis = "3. Cálculo de Probabilidades Implícitas"
                st.rerun()
            if st.button("🤝 Confronto Direto", key="confronto"):
                st.session_state.selected_analysis = "4. Confronto Direto"
                st.rerun()

        with col3:
            if st.button("🔮 Predição de Placar", key="predicao"):
                st.session_state.selected_analysis = "5. Predição de Placar (Poisson)"
                st.rerun()
            if st.button("📊 Gráficos Interativos", key="graficos"):
                st.session_state.selected_analysis = "6. Gráficos Interativos"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # BOTÃO VOLTAR (sempre no topo quando uma análise está selecionada)
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
    """Exibe análise de desempenho de um time selecionado (COM LOGOS)."""
    st.header("🏆 Análise de Desempenho de Time")
    
    if not teams:
        st.warning("Nenhum time disponível.")
        return
        
    team = create_team_selectbox_with_logos("Selecione o time para análise:", teams, key="team_performance")
    if not team:
        st.warning("Selecione um time.")
        return
        
    stats_home = calculate_team_stats(df, team, as_home=True)
    stats_away = calculate_team_stats(df, team, as_home=False)
    
    # Header com logo
    st.markdown("---")
    col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
    with col_header2:
        st.markdown("### 📊 Estatísticas Detalhadas")
        display_team_with_logo(team, logo_size=(40, 40))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 Como Mandante")
        st.metric("Jogos", stats_home['jogos'])
        st.metric("Vitórias", stats_home['vitorias'])
        st.metric("Empates", stats_home['empates'])
        st.metric("Derrotas", stats_home['derrotas'])
        st.metric("Gols Feitos", stats_home['gols_feitos'])
        st.metric("Gols Sofridos", stats_home['gols_sofridos'])
        st.metric("Média Gols Feitos/Jogo", f"{stats_home['media_gols_feitos']:.2f}")
        st.metric("Média Gols Sofridos/Jogo", f"{stats_home['media_gols_sofridos']:.2f}")
        
        if 'escanteios_feitos' in stats_home:
            st.metric("Escanteios Feitos", stats_home['escanteios_feitos'])
            st.metric("Escanteios Sofridos", stats_home['escanteios_sofridos'])
            st.metric("Média Escanteios Feitos/Jogo", f"{stats_home['media_escanteios_feitos']:.2f}")
            st.metric("Média Escanteios Sofridos/Jogo", f"{stats_home['media_escanteios_sofridos']:.2f}")

    with col2:
        st.markdown("#### ✈️ Como Visitante")
        st.metric("Jogos", stats_away['jogos'])
        st.metric("Vitórias", stats_away['vitorias'])
        st.metric("Empates", stats_away['empates'])
        st.metric("Derrotas", stats_away['derrotas'])
        st.metric("Gols Feitos", stats_away['gols_feitos'])
        st.metric("Gols Sofridos", stats_away['gols_sofridos'])
        st.metric("Média Gols Feitos/Jogo", f"{stats_away['media_gols_feitos']:.2f}")
        st.metric("Média Gols Sofridos/Jogo", f"{stats_away['media_gols_sofridos']:.2f}")
        
        if 'escanteios_feitos' in stats_away:
            st.metric("Escanteios Feitos", stats_away['escanteios_feitos'])
            st.metric("Escanteios Sofridos", stats_away['escanteios_sofridos'])
            st.metric("Média Escanteios Feitos/Jogo", f"{stats_away['media_escanteios_feitos']:.2f}")
            st.metric("Média Escanteios Sofridos/Jogo", f"{stats_away['media_escanteios_sofridos']:.2f}")


# CHAMADA DA MAIN (adicionar no final do arquivo)
if __name__ == "__main__":
    main()

















