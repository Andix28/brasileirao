# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import poisson
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="⚽ Análise de Futebol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
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
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("BRA_DADOS_2425_B.csv", sep=';', encoding='latin1')

        # Validação da coluna Ano
        if 'Ano' not in df.columns:
            st.error("❌ A coluna 'Ano' é obrigatória para filtrar os dados por período.")
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
                           'Corner Home', 'Corner Away', 'Total Corner Match']
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
    
    # Obter lista única de times
    teams = _get_unique_teams(df)
    
    if len(teams) < 2:
        st.warning("⚠️ É necessário pelo menos 2 times diferentes para comparação.")
        return
    
    # Interface de seleção de times
    team_home, team_away = _create_team_selection_interface(teams)
    
    if not _validate_team_selection(team_home, team_away):
        st.warning("⚠️ Por favor, selecione dois times diferentes.")
        return
    
    # Verificar colunas necessárias
    if not _validate_required_columns(df):
        return
    
    # Calcular estatísticas
    stats = _calculate_team_statistics(df, team_home, team_away)
    
    # Gerar gráficos
    _generate_comparative_charts(stats, team_home, team_away)


def _get_unique_teams(df):
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


def _create_team_selection_interface(teams):
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


def _validate_team_selection(team_home, team_away):
    """
    Valida se a seleção de times está correta.
    
    Args:
        team_home (str): Time mandante selecionado
        team_away (str): Time visitante selecionado
        
    Returns:
        bool: True se seleção válida, False caso contrário
    """
    return team_home and team_away and team_home != team_away


def _validate_required_columns(df):
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
        st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
        return False
    
    return True


def _calculate_team_statistics(df, team_home, team_away):
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


def _generate_comparative_charts(stats, team_home, team_away):
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
                _create_bar_chart(chart_configs[i], team_home, team_away)
        
        with col2:
            if i + 1 < len(chart_configs):
                _create_bar_chart(chart_configs[i + 1], team_home, team_away)
    
    # Exibir resumo estatístico
    _display_statistics_summary(stats, team_home, team_away)


def _create_bar_chart(config, team_home, team_away):
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


def _display_statistics_summary(stats, team_home, team_away):
    """
    Exibe resumo estatístico dos times.
    
    Args:
        stats (dict): Estatísticas calculadas
        team_home (str): Nome do time mandante
        team_away (str): Nome do time visitante
    """
    try:
        st.subheader("📋 Análise Estatística Detalhada")
        
        # Calcular métricas avançadas
        analysis = _calculate_advanced_metrics(stats, team_home, team_away)
        
        # Seção 1: Resumo Básico
        _display_basic_summary(stats, team_home, team_away, analysis)
        
        # Seção 2: Análise de Performance
        _display_performance_analysis(analysis, team_home, team_away)
        
        # Seção 3: Análise do Primeiro Tempo
        _display_first_half_analysis(stats, analysis, team_home, team_away)
        
        # Seção 4: Insights e Recomendações
        _display_insights_and_recommendations(analysis, team_home, team_away)
        
    except Exception as e:
        st.error(f"❌ Erro na análise estatística: {str(e)}")
        st.info("💡 Verifique se os dados estão completos e tente novamente.")
        # Debug: mostrar valores que causaram erro
        st.write("Debug - Valores recebidos:")
        st.write(f"Stats home: {stats.get('home', 'N/A')}")
        st.write(f"Stats away: {stats.get('away', 'N/A')}")


def _calculate_advanced_metrics(stats, team_home, team_away):
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
    home_ht_sofridos = safe_int(stats['home']['gols_sofridos_ht'])
    away_ht_marcados = safe_int(stats['away']['gols_marcados_ht'])
    away_ht_sofridos = safe_int(stats['away']['gols_sofridos_ht'])
    
    # Calcular saldos
    home_saldo = home_gols_marcados - home_gols_sofridos
    away_saldo = away_gols_marcados - away_gols_sofridos
    
    return {
        # Médias por jogo
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


def _display_basic_summary(stats, team_home, team_away, analysis):
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
        **🏠 {team_home} (Como Mandante)**
        - 🎮 Jogos analisados: **{analysis['home_jogos']}**
        - ⚽ Gols marcados: **{analysis['home_gols_total']}** (média: {analysis['home_media_gols']}/jogo)
        - 🥅 Gols sofridos: **{analysis['home_sofridos_total']}** (média: {analysis['home_media_sofridos']}/jogo)
        - {saldo_icon} Saldo de gols: **{saldo_text}**
        """)
    
    with col2:
        # Determinar ícone do saldo sem usar formatação problemática
        saldo_away = analysis['away_saldo']
        if saldo_away > 0:
            saldo_icon = "📈"
            saldo_text = f"+{saldo_away}"
        elif saldo_away < 0:
            saldo_icon = "📉"
            saldo_text = str(saldo_away)
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


def _display_performance_analysis(analysis, team_home, team_away):
    """Exibe análise de performance comparativa."""
    
    st.subheader("🎯 Análise de Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if analysis['melhor_ataque'] == team_home:
            st.success(f"🔥 **Melhor Ataque**: {team_home}\n\n{analysis['home_gols_total']} gols vs {analysis['away_gols_total']} gols")
        else:
            st.success(f"🔥 **Melhor Ataque**: {team_away}\n\n{analysis['away_gols_total']} gols vs {analysis['home_gols_total']} gols")
    
    with col2:
        if analysis['melhor_defesa'] == team_home:
            st.success(f"🛡️ **Melhor Defesa**: {team_home}\n\n{analysis['home_sofridos_total']} gols sofridos vs {analysis['away_sofridos_total']}")
        else:
            st.success(f"🛡️ **Melhor Defesa**: {team_away}\n\n{analysis['away_sofridos_total']} gols sofridos vs {analysis['home_sofridos_total']}")
    
    with col3:
        diferenca_saldo = abs(analysis['home_saldo'] - analysis['away_saldo'])
        if diferenca_saldo > 5:
            equilibrio = "Desequilibrado"
            cor = "warning"
        elif diferenca_saldo > 2:
            equilibrio = "Moderado"
            cor = "info"
        else:
            equilibrio = "Equilibrado"
            cor = "success"
            
        getattr(st, cor)(f"⚖️ **Confronto**: {equilibrio}\n\nDiferença de saldo: {diferenca_saldo} gols")


def _display_first_half_analysis(stats, analysis, team_home, team_away):
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
    
    # Análise da eficiência do primeiro tempo
    if analysis['home_ht_eficiencia'] > 60 or analysis['away_ht_eficiencia'] > 60:
        st.info("💡 **Insight**: Um ou ambos os times demonstram forte início de jogo, marcando mais de 60% dos gols no primeiro tempo.")
    elif analysis['home_ht_eficiencia'] < 30 and analysis['away_ht_eficiencia'] < 30:
        st.info("💡 **Insight**: Ambos os times tendem a ser mais efetivos no segundo tempo, com baixa produção inicial.")


def _display_insights_and_recommendations(analysis, team_home, team_away):
    """Exibe insights estratégicos e recomendações."""
    
    st.subheader("🧠 Insights Estratégicos")
    
    insights = []
    
    # Análise de força ofensiva
    if analysis['home_media_gols'] > 2.0:
        insights.append(f"🔥 {team_home} possui ataque muito forte como mandante (média de {analysis['home_media_gols']} gols/jogo)")
    elif analysis['home_media_gols'] < 1.0:
        insights.append(f"⚠️ {team_home} tem dificuldades ofensivas como mandante (média de {analysis['home_media_gols']} gols/jogo)")
    
    if analysis['away_media_gols'] > 1.5:
        insights.append(f"💪 {team_away} é eficiente jogando fora de casa (média de {analysis['away_media_gols']} gols/jogo)")
    elif analysis['away_media_gols'] < 0.8:
        insights.append(f"🚨 {team_away} tem baixo rendimento como visitante (média de {analysis['away_media_gols']} gols/jogo)")
    
    # Análise defensiva
    if analysis['home_media_sofridos'] < 1.0:
        insights.append(f"🛡️ {team_home} possui defesa sólida em casa (média de {analysis['home_media_sofridos']} gols sofridos/jogo)")
    elif analysis['home_media_sofridos'] > 2.0:
        insights.append(f"⚠️ {team_home} tem fragilidade defensiva como mandante")
    
    # Análise comparativa de eficiência
    if analysis['home_ht_eficiencia'] > analysis['away_ht_eficiencia'] + 20:
        insights.append(f"⚡ {team_home} é muito mais eficiente no primeiro tempo ({analysis['home_ht_eficiencia']}% vs {analysis['away_ht_eficiencia']}%)")
    elif analysis['away_ht_eficiencia'] > analysis['home_ht_eficiencia'] + 20:
        insights.append(f"⚡ {team_away} é muito mais eficiente no primeiro tempo ({analysis['away_ht_eficiencia']}% vs {analysis['home_ht_eficiencia']}%)")
    
    # Mostrar insights se houver algum
    if insights:
        st.write("### 📋 Recomendações Estratégicas:")
        for i, insight in enumerate(insights, 1):
            st.write(f"**{i}.** {insight}")
    else:
        st.info("📊 Times apresentam performance equilibrada nos critérios analisados.")
    
    # Previsão de jogo
    if analysis['home_gols_total'] > 0 and analysis['away_gols_total'] > 0:
        st.write("### 🎯 Cenário Provável de Confronto:")
        
        total_esperado = round((analysis['home_media_gols'] + analysis['away_media_gols']) / 2, 1)
        
        if total_esperado > 2.5:
            cenario = "🔥 Jogo com muitos gols esperado"
            cor_cenario = "success"
        elif total_esperado > 1.5:
            cenario = "⚽ Jogo com gols moderados"
            cor_cenario = "info"
        else:
            cenario = "🛡️ Jogo mais truncado e defensivo"
            cor_cenario = "warning"
            
        getattr(st, cor_cenario)(f"{cenario} (média esperada: {total_esperado} gols)")
        
        # Adicionar contexto sobre vantagem de campo
        if analysis['home_gols_total'] > 0:
            vantagem_casa = round((analysis['home_media_gols'] / max(analysis['away_media_gols'], 0.1)) * 100 - 100, 1)
            if abs(vantagem_casa) > 20:
                if vantagem_casa > 0:
                    st.info(f"🏠 **Vantagem do Mandante**: {team_home} marca {vantagem_casa:+.1f}% mais gols em casa")
                else:
                    st.info(f"✈️ **Eficiência do Visitante**: {team_away} supera expectativa visitante em {abs(vantagem_casa):.1f}%")
    else:
        st.warning("⚠️ Dados insuficientes para projeção de confronto.")

def show_team_analysis(df, teams):
    """Análise de desempenho de um time específico"""
    st.header("📊 Análise de Desempenho de Time")
    
    if not teams:
        st.warning("Nenhum time encontrado nos dados.")
        return
    
    selected_team = st.selectbox("🏆 Selecione o time:", teams)
    
    if selected_team:
        # Estatísticas como mandante e visitante
        home_stats = calculate_team_stats(df, selected_team, as_home=True)
        away_stats = calculate_team_stats(df, selected_team, as_home=False)
        
        # Combine estatísticas
        total_games = home_stats.get('jogos', 0) + away_stats.get('jogos', 0)
        total_wins = home_stats.get('vitorias', 0) + away_stats.get('vitorias', 0)
        total_draws = home_stats.get('empates', 0) + away_stats.get('empates', 0)
        total_losses = home_stats.get('derrotas', 0) + away_stats.get('derrotas', 0)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎮 Total de Jogos", total_games)
        with col2:
            st.metric("🏆 Vitórias", total_wins)
        with col3:
            st.metric("🤝 Empates", total_draws)
        with col4:
            st.metric("❌ Derrotas", total_losses)
        
        # Estatísticas detalhadas
        st.subheader("📈 Estatísticas Detalhadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Como Mandante:**")
            st.write(f"Jogos: {home_stats['jogos']}")
            st.write(f"Vitórias: {home_stats['vitorias']}")
            st.write(f"Empates: {home_stats['empates']}")
            st.write(f"Derrotas: {home_stats['derrotas']}")
            st.write(f"Gols/Jogo: {home_stats['media_gols_feitos']:.2f}")
            st.write(f"Gols Sofridos/Jogo: {home_stats['media_gols_sofridos']:.2f}")
        
        with col2:
            st.write("**Como Visitante:**")
            st.write(f"Jogos: {away_stats['jogos']}")
            st.write(f"Vitórias: {away_stats['vitorias']}")
            st.write(f"Empates: {away_stats['empates']}")
            st.write(f"Derrotas: {away_stats['derrotas']}")
            st.write(f"Gols/Jogo: {away_stats['media_gols_feitos']:.2f}")
            st.write(f"Gols Sofridos/Jogo: {away_stats['media_gols_sofridos']:.2f}")
        
        # Gráfico de pizza dos resultados
        if total_games > 0:
            fig = px.pie(
                values=[total_wins, total_draws, total_losses],
                names=['Vitórias', 'Empates', 'Derrotas'],
                title=f"Distribuição de Resultados - {selected_team}",
                color_discrete_sequence=['#2E8B57', '#FFD700', '#DC143C']
            )
            st.plotly_chart(fig, use_container_width=True)

def show_team_comparison(df, teams):
    """Análise Do Confronto"""
    st.header("⚔️ Comparação: Mandante vs Visitante")

    if len(teams) < 2:
        st.warning("Selecione pelo menos dois times.")
        return

    col1, col2 = st.columns(2)
    with col1:
        team_home = st.selectbox("🏠 Time Mandante:", teams, key="team1")
    with col2:
        team_away = st.selectbox("✈️ Time Visitante:", teams, key="team2")

    if not team_home or not team_away or team_home == team_away:
        st.warning("Selecione dois times diferentes.")
        return

    # Estatísticas específicas
    stats_home = calculate_team_stats(df, team_home, as_home=True)
    stats_away = calculate_team_stats(df, team_away, as_home=False)

    labels = [
        "Jogos",
        "Vitórias",
        "Empates",
        "Derrotas",
        "Gols Marcados/Jogo",
        "Gols Sofridos/Jogo"
    ]

    home_values = [
        stats_home['jogos'],
        stats_home['vitorias'],
        stats_home['empates'],
        stats_home['derrotas'],
        round(stats_home['media_gols_feitos'], 2),
        round(stats_home['media_gols_sofridos'], 2)
    ]

    away_values = [
        stats_away['jogos'],
        stats_away['vitorias'],
        stats_away['empates'],
        stats_away['derrotas'],
        round(stats_away['media_gols_feitos'], 2),
        round(stats_away['media_gols_sofridos'], 2)
    ]

    # Exibição da Tabela
    st.subheader("📊 Comparativo Estatístico")
    df_comparativo = pd.DataFrame({
        "Métrica": labels,
        f"{team_home} (Mandante)": home_values,
        f"{team_away} (Visitante)": away_values
    })

    st.dataframe(df_comparativo, use_container_width=True)

    # Gráfico de colunas
    st.subheader("📈 Gráfico Comparativo")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=home_values, name=f"{team_home} (Mandante)", marker_color='royalblue'))
    fig.add_trace(go.Bar(x=labels, y=away_values, name=f"{team_away} (Visitante)", marker_color='darkorange'))

    fig.update_layout(
        barmode='group',
        xaxis_title="Métrica",
        yaxis_title="Valor",
        legend_title="Times",
        title=f"Desempenho: {team_home} (Mandante) vs {team_away} (Visitante)"
    )

    st.plotly_chart(fig, use_container_width=True)

def show_probability_analysis(df, teams):
    """Análise de Valor baseada no Histórico de Performance por Faixas de Odds"""
    st.header("🎯 Análise de Valor - Histórico vs Odds Atuais")

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

    # Inserção das odds atuais
    st.subheader("📊 Odds do Confronto")
    col1, col2, col3 = st.columns(3)
    with col1:
        odd_home = st.number_input("🏠 Odd Mandante:", min_value=1.01, value=2.30, step=0.01, format="%.2f")
    with col2:
        odd_draw = st.number_input("🤝 Odd Empate:", min_value=1.01, value=3.10, step=0.01, format="%.2f")
    with col3:
        odd_away = st.number_input("✈️ Odd Visitante:", min_value=1.01, value=3.30, step=0.01, format="%.2f")

    if st.button("🔍 Analisar Valor nas Odds", type="primary"):
        
        # Probabilidades implícitas
        prob_home_imp = (1 / odd_home) * 100
        prob_draw_imp = (1 / odd_draw) * 100  
        prob_away_imp = (1 / odd_away) * 100

        st.subheader("📐 Probabilidades Implícitas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏠 Mandante", f"{prob_home_imp:.1f}%")
        with col2:
            st.metric("🤝 Empate", f"{prob_draw_imp:.1f}%")
        with col3:
            st.metric("✈️ Visitante", f"{prob_away_imp:.1f}%")

        st.divider()

        # Análise do Mandante
        st.subheader(f"🏠 Análise Histórica - {team_home} (Mandante)")
        home_analysis = analyze_team_odds_performance(df, team_home, "Home", odd_home)
        display_odds_analysis(home_analysis, "Mandante", odd_home, prob_home_imp)

        st.divider()

        # Análise do Visitante  
        st.subheader(f"✈️ Análise Histórica - {team_away} (Visitante)")
        away_analysis = analyze_team_odds_performance(df, team_away, "Away", odd_away)
        display_odds_analysis(away_analysis, "Visitante", odd_away, prob_away_imp)

        st.divider()

        # Análise do Empate (baseada no histórico geral dos times)
        st.subheader("🤝 Análise do Empate")
        draw_analysis = analyze_draw_performance(df, team_home, team_away, odd_draw)
        display_draw_analysis(draw_analysis, odd_draw, prob_draw_imp)

def analyze_team_odds_performance(df, team, position, current_odd):
    """Analisa performance do time em diferentes faixas de odds"""
    
    # Filtrar jogos do time na posição
    team_games = df[df[position] == team].copy()
    
    if len(team_games) < 10:  # Mínimo fixo de 10 jogos
        return {"error": f"Poucos dados históricos para {team} ({len(team_games)} jogos)"}
    
    # Mapear colunas corretas baseado na posição
    if position == "Home":
        odd_column = 'odd Home'
        result_column = 'Resultado Home'
    else:  # position == "Away"
        odd_column = 'odd Away'
        # Se não existir Resultado Away, criar baseado no Resultado Home
        if 'Resultado Away' not in team_games.columns:
            team_games['Resultado Away'] = team_games['Resultado Home'].map({
                'Vitória': 'Derrota',
                'Derrota': 'Vitória', 
                'Empate': 'Empate'
            })
        result_column = 'Resultado Away'
    
    if odd_column not in team_games.columns or result_column not in team_games.columns:
        return {"error": "Colunas necessárias não encontradas no dataset"}
    
    # Remover valores nulos
    team_games = team_games.dropna(subset=[odd_column, result_column])
    
    if len(team_games) < 10:
        return {"error": f"Dados insuficientes após limpeza para {team}"}
    
    # Definir faixas de odds baseadas na odd atual
    faixas = []
    
    # Faixa 1: Muito favorito (odds baixas)
    limite1 = current_odd * 0.7  # 30% abaixo da odd atual
    faixa1 = team_games[team_games[odd_column] <= limite1]
    if len(faixa1) >= 5:
        faixas.append(("Muito Favorito", f"≤ {limite1:.2f}", faixa1, "green"))
    
    # Faixa 2: Favorito moderado
    limite2 = current_odd * 0.9  # 10% abaixo da odd atual
    faixa2 = team_games[(team_games[odd_column] > limite1) & (team_games[odd_column] <= limite2)]
    if len(faixa2) >= 5:
        faixas.append(("Favorito Moderado", f"{limite1:.2f} - {limite2:.2f}", faixa2, "lightgreen"))
    
    # Faixa 3: Situação similar à atual
    limite3 = current_odd * 1.1  # 10% acima da odd atual
    faixa3 = team_games[(team_games[odd_column] > limite2) & (team_games[odd_column] <= limite3)]
    if len(faixa3) >= 3:
        faixas.append(("Situação Atual", f"{limite2:.2f} - {limite3:.2f}", faixa3, "yellow"))
    
    # Faixa 4: Menos favorito
    limite4 = current_odd * 1.3  # 30% acima da odd atual
    faixa4 = team_games[(team_games[odd_column] > limite3) & (team_games[odd_column] <= limite4)]
    if len(faixa4) >= 5:
        faixas.append(("Menos Favorito", f"{limite3:.2f} - {limite4:.2f}", faixa4, "orange"))
    
    # Faixa 5: Azarão
    faixa5 = team_games[team_games[odd_column] > limite4]
    if len(faixa5) >= 5:
        faixas.append(("Azarão", f"> {limite4:.2f}", faixa5, "red"))
    
    # Calcular estatísticas para cada faixa
    resultados = []
    for nome, range_str, dados, cor in faixas:
        total = len(dados)
        vitorias = len(dados[dados[result_column] == 'Vitória'])
        empates = len(dados[dados[result_column] == 'Empate'])
        derrotas = len(dados[dados[result_column] == 'Derrota'])
        
        perc_vitoria = (vitorias / total) * 100 if total > 0 else 0
        perc_empate = (empates / total) * 100 if total > 0 else 0
        odd_media = dados[odd_column].mean()
        
        resultados.append({
            'categoria': nome,
            'range': range_str,
            'total': total,
            'vitorias': vitorias,
            'perc_vitoria': perc_vitoria,
            'perc_empate': perc_empate,
            'odd_media': odd_media,
            'cor': cor,
            'is_current': limite2 < current_odd <= limite3 if nome == "Situação Atual" else False
        })
    
    return {
        'team': team,
        'total_games': len(team_games),
        'current_odd': current_odd,
        'faixas': resultados
    }

def analyze_draw_performance(df, team_home, team_away, current_odd):
    """Analisa performance de empates envolvendo os times"""
    
    # Jogos envolvendo qualquer um dos times
    games = df[
        (df['Home'] == team_home) | (df['Away'] == team_home) |
        (df['Home'] == team_away) | (df['Away'] == team_away)
    ].copy()
    
    if len(games) < 20:
        return {"error": "Poucos dados para análise de empates"}
    
    # Remover valores nulos na coluna de odd do empate
    games = games.dropna(subset=['odd Draw', 'Resultado Home'])
    
    if len(games) < 20:
        return {"error": "Dados insuficientes para análise de empates"}
    
    # Definir faixas baseadas na odd atual do empate
    faixas = []
    
    # Empate mais provável (odds baixas)
    limite1 = current_odd * 0.8
    faixa1 = games[games['odd Draw'] <= limite1]
    if len(faixa1) >= 5:
        faixas.append(("Empate Provável", f"≤ {limite1:.2f}", faixa1))
    
    # Situação similar
    limite2 = current_odd * 1.2
    faixa2 = games[(games['odd Draw'] > limite1) & (games['odd Draw'] <= limite2)]
    if len(faixa2) >= 3:
        faixas.append(("Situação Atual", f"{limite1:.2f} - {limite2:.2f}", faixa2))
    
    # Empate menos provável
    faixa3 = games[games['odd Draw'] > limite2]
    if len(faixa3) >= 5:
        faixas.append(("Empate Improvável", f"> {limite2:.2f}", faixa3))
    
    resultados = []
    for nome, range_str, dados in faixas:
        total = len(dados)
        empates = len(dados[dados['Resultado Home'] == 'Empate'])
        perc_empate = (empates / total) * 100 if total > 0 else 0
        odd_media = dados['odd Draw'].mean()
        
        resultados.append({
            'categoria': nome,
            'range': range_str,
            'total': total,
            'empates': empates,
            'perc_empate': perc_empate,
            'odd_media': odd_media,
            'is_current': limite1 < current_odd <= limite2 if nome == "Situação Atual" else False
        })
    
    return {
        'current_odd': current_odd,
        'total_games': len(games),
        'faixas': resultados
    }

def display_odds_analysis(analysis, position, current_odd, prob_implicita):
    """Exibe análise de odds do time"""
    
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.write(f"**Total de jogos analisados:** {analysis['total_games']}")
    st.write(f"**Odd atual:** {current_odd:.2f} (Probabilidade implícita: {prob_implicita:.1f}%)")
    
    # Tabela com as faixas
    if analysis['faixas']:
        df_display = []
        melhor_performance = None
        situacao_atual = None
        
        for faixa in analysis['faixas']:
            df_display.append({
                'Situação': faixa['categoria'],
                'Faixa de Odds': faixa['range'],
                'Jogos': faixa['total'],
                'Vitórias': faixa['vitorias'],
                'Taxa de Vitória': f"{faixa['perc_vitoria']:.1f}%",
                'Odd Média': f"{faixa['odd_media']:.2f}"
            })
            
            # Identificar melhor performance e situação atual
            if melhor_performance is None or faixa['perc_vitoria'] > melhor_performance['perc_vitoria']:
                melhor_performance = faixa
            
            if faixa['is_current']:
                situacao_atual = faixa
        
        # Exibir tabela
        df_display = pd.DataFrame(df_display)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Análise de valor
        st.subheader("💡 Análise de Valor")
        
        if situacao_atual:
            valor = situacao_atual['perc_vitoria'] - prob_implicita
            st.metric(
                "Taxa Histórica na Faixa Atual", 
                f"{situacao_atual['perc_vitoria']:.1f}%",
                delta=f"{valor:+.1f}% vs mercado"
            )
            
            if valor > 5:
                st.success(f"✅ **VALOR POSITIVO**: Histórico sugere {valor:.1f}% mais chance de vitória que o mercado indica!")
            elif valor < -5:
                st.error(f"⚠️ **VALOR NEGATIVO**: Histórico sugere {abs(valor):.1f}% menos chance de vitória que o mercado indica!")
            else:
                st.info("⚖️ **ODD EQUILIBRADA**: Probabilidades alinhadas com histórico")
        
        # Insight sobre melhor performance
        if melhor_performance:
            st.info(f"📊 **Melhor Performance Histórica**: {melhor_performance['categoria']} - {melhor_performance['perc_vitoria']:.1f}% de vitórias (Odds {melhor_performance['range']})")
    
    else:
        st.warning("Não foi possível criar faixas de análise com os dados disponíveis")

def display_draw_analysis(analysis, current_odd, prob_implicita):
    """Exibe análise de empates"""
    
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.write(f"**Total de jogos analisados:** {analysis['total_games']}")
    st.write(f"**Odd atual do empate:** {current_odd:.2f} (Probabilidade implícita: {prob_implicita:.1f}%)")
    
    if analysis['faixas']:
        df_display = []
        situacao_atual = None
        
        for faixa in analysis['faixas']:
            df_display.append({
                'Situação': faixa['categoria'],
                'Faixa de Odds': faixa['range'],
                'Jogos': faixa['total'],
                'Empates': faixa['empates'],
                'Taxa de Empate': f"{faixa['perc_empate']:.1f}%",
                'Odd Média': f"{faixa['odd_media']:.2f}"
            })
            
            if faixa['is_current']:
                situacao_atual = faixa
        
        df_display = pd.DataFrame(df_display)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Análise de valor para empate
        if situacao_atual:
            valor = situacao_atual['perc_empate'] - prob_implicita
            st.metric(
                "Taxa Histórica de Empate", 
                f"{situacao_atual['perc_empate']:.1f}%",
                delta=f"{valor:+.1f}% vs mercado"
            )
            
            if valor > 3:
                st.success(f"✅ **VALOR NO EMPATE**: Histórico sugere {valor:.1f}% mais chance de empate!")
            elif valor < -3:
                st.error(f"⚠️ **EMPATE SUPERVALORIZADO**: {abs(valor):.1f}% menos provável historicamente!")
            else:
                st.info("⚖️ **ODD DE EMPATE EQUILIBRADA**")
    else:
        st.warning("Dados insuficientes para análise de empates")

def show_corner_simulation(df, teams):
    """Simulação de escanteios com base nas médias"""
    st.header("🚩 Simulação de Escanteios por Time")

    if not teams:
        st.warning("Nenhum time disponível.")
        return

    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 Time Mandante:", teams, key="corner_home")
    with col2:
        away_team = st.selectbox("✈️ Time Visitante:", teams, key="corner_away")

    if home_team == away_team:
        st.warning("Por favor, selecione dois times diferentes.")
        return

    if st.button("🚩 Simular Escanteios"):
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
            fig.add_trace(go.Bar(x=list(corners_range), y=probabilities))
            fig.update_layout(
                title="Distribuição Poisson do Total de Escanteios",
                xaxis_title="Total de Escanteios no Jogo",
                yaxis_title="Probabilidade (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

def show_score_prediction(df, teams):
    """Predição de placar usando Distribuição de Poisson"""
    st.header("🎯 Predição de Placar (Distribuição de Poisson)")

    if not teams:
        st.warning("Nenhum time disponível.")
        return

    col1, col2 = st.columns(2)
    with col1:
        team_home = st.selectbox("🏠 Time Mandante:", teams, key="poisson_home")
    with col2:
        team_away = st.selectbox("✈️ Time Visitante:", teams, key="poisson_away")

    if team_home == team_away:
        st.warning("Por favor, selecione dois times diferentes.")
        return

    if st.button("🔮 Prever Placar"):
        # Obtém estatísticas dos times
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

        # Exibição de resultado
        st.success(f"Placar mais provável: {team_home} {resultado[0]} x {resultado[1]} {team_away}")
        st.metric(label="🎯 Probabilidade estimada do placar", value=f"{probabilidade*100:.2f}%")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Gols esperados para {team_home}: **{gols_esperados_home:.2f}**")
        with col2:
            st.info(f"Gols esperados para {team_away}: **{gols_esperados_away:.2f}**")

        # Tabela com top 10 placares prováveis
        st.subheader("📋 Top 10 placares mais prováveis")
        results = []
        for h in range(6):
            for a in range(6):
                prob = poisson.pmf(h, gols_esperados_home) * poisson.pmf(a, gols_esperados_away)
                results.append(((h, a), prob))
        results.sort(key=lambda x: x[1], reverse=True)
        
        for i, ((h, a), p) in enumerate(results[:10], 1):
            st.write(f"{i}. {team_home} {h} x {a} {team_away} — {p*100:.2f}%")

def main():
    # Título principal
    st.markdown('<h1 class="main-header">⚽ Sistema de Análise de Futebol</h1>', unsafe_allow_html=True)

    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df = load_data()

    if df.empty:
        st.error("❌ Não foi possível carregar os dados.")
        st.info("📁 Certifique-se de que o arquivo está na raiz do repositório.")
        st.info("🔍 Verifique também se o arquivo está com o encoding correto.")
        return

    st.success(f"✅ Dados carregados com sucesso! Total de jogos disponíveis: {len(df)}")

    # Sidebar para filtros e opções
    with st.sidebar:
        st.header("🔧 Configurações")

        # Filtro de ano com multiselect
        if 'Ano' in df.columns:
            year_options = sorted(df['Ano'].dropna().unique())
            selected_years = st.multiselect("📅 Selecione os anos desejados:", year_options, default=year_options)

            df_filtered = df[df['Ano'].isin(selected_years)].copy()
        else:
            st.warning("Coluna 'Ano' não encontrada nos dados.")
            df_filtered = df.copy()

        st.success(f"📊 Jogos no filtro: {len(df_filtered)} de {len(df)}")

        # Lista de times únicos
        try:
            if df_filtered.empty:
                teams = []
            else:
                home_teams = df_filtered['Home'].dropna().unique().tolist()
                away_teams = df_filtered['Away'].dropna().unique().tolist()
                teams = sorted(list(set(home_teams + away_teams)))
        except Exception as e:
            st.error(f"Erro ao processar times: {str(e)}")
            teams = []

        st.header("📋 Opções de Análise")
        analysis_option = st.selectbox(
            "Escolha o tipo de análise:",
            [
                "1. Análise de Desempenho de Time",
                "2. Comparação entre Times",
                "3. Cálculo de Probabilidades Implícitas",
                "4. Simulação de Escanteios",
                "5. Predição de Placar (Poisson)",
                "6. Gráficos Interativos"
            ]
        )

    # Conteúdo principal baseado na opção selecionada
    try:
        if analysis_option.startswith("1."):
            show_team_analysis(df_filtered, teams)
        elif analysis_option.startswith("2."):
            show_team_comparison(df_filtered, teams)
        elif analysis_option.startswith("3."):
            show_probability_analysis(df_filtered, teams)
        elif analysis_option.startswith("4."):
            show_corner_simulation(df_filtered, teams)
        elif analysis_option.startswith("5."):
            show_score_prediction(df_filtered, teams)
        elif analysis_option.startswith("6."):
            show_interactive_charts(df_filtered)
    except Exception as e:
        st.error(f"Erro na análise: {str(e)}")
        st.info("Tente selecionar uma opção diferente.")

    # Debug info (só aparece quando expandido)
    with st.expander("🔍 Informações de Debug"):
        st.write("Colunas do DataFrame:", list(df.columns))
        st.write("Shape do DataFrame original:", df.shape)
        st.write("Shape do DataFrame filtrado:", df_filtered.shape)
        
        if 'Ano' in df.columns:
            st.write("Distribuição por ano:")
            st.write(df['Ano'].value_counts().sort_index())
        
        st.write("Primeiras linhas do DataFrame filtrado:")
        st.write(df_filtered.head())

# Executa a aplicação
if __name__ == "__main__":
    main()
