# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import poisson
import warnings
warnings.filterwarnings('ignore')

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
        st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
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
        st.error(f"❌ Erro na análise estatística: {str(e)}")
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
    
    # Calcular estatísticas usando a função existente
    stats = calculate_team_statistics(df, team_home, team_away)
    analysis = calculate_advanced_metrics(stats, team_home, team_away)
    
    labels = [
        "Jogos",
        "Gols Marcados",
        "Gols Sofridos",
        "Saldo de Gols",
        "Gols Marcados/Jogo",
        "Gols Sofridos/Jogo"
    ]
    
    home_values = [
        analysis['home_jogos'],
        analysis['home_gols_total'],
        analysis['home_sofridos_total'],
        analysis['home_saldo'],
        analysis['home_media_gols'],
        analysis['home_media_sofridos']
    ]
    
    away_values = [
        analysis['away_jogos'],
        analysis['away_gols_total'],
        analysis['away_sofridos_total'],
        analysis['away_saldo'],
        analysis['away_media_gols'],
        analysis['away_media_sofridos']
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
    fig.add_trace(go.Bar(
        x=labels, 
        y=home_values, 
        name=f"{team_home} (Mandante)", 
        marker_color='royalblue'
    ))
    fig.add_trace(go.Bar(
        x=labels, 
        y=away_values, 
        name=f"{team_away} (Visitante)", 
        marker_color='darkorange'
    ))
    
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
        display_odds_analysis(home_analysis, odd_home, prob_home_imp)

        st.divider()

        # Análise do Visitante  
        st.subheader(f"✈️ Análise Histórica - {team_away} (Visitante)")
        away_analysis = analyze_team_odds_performance(df, team_away, "Away", odd_away)
        display_odds_analysis(away_analysis, odd_away, prob_away_imp)

        st.divider()

        # Análise do Empate (baseada no histórico geral dos times)
        st.subheader("🤝 Análise do Empate")
        draw_analysis = analyze_draw_performance(df, team_home, team_away, odd_draw)
        display_draw_analysis(draw_analysis, odd_draw, prob_draw_imp)

# Função para exibir análise de odds do time
def display_odds_analysis(analysis, current_odd, prob_implicita):
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    
    st.write(f"**Total de jogos analisados:** {analysis['total_games']}")
    st.write(f"**Odd atual:** {current_odd:.2f} (Probabilidade implícita: {prob_implicita:.1f}%)")
    
    if analysis['faixas']:
        df_display = []
        melhor_performance = None
        situacao_atual = None
        
        for faixa in analysis['faixas']:
            df_display.append({
                'Situação': faixa['categoria'],
                'Faixa de Odds': faixa['range'],
                'Jogos': faixa['total'],
                'Vitórias': faixa.get('vitorias', 0),
                'Taxa de Vitória': f"{faixa.get('perc_vitoria', 0):.1f}%",
                'Odd Média': f"{faixa.get('odd_media', 0):.2f}"
            })
            
            # CORREÇÃO: Adicionar indentação correta
            if (melhor_performance is None or 
                faixa.get('perc_vitoria', 0) > melhor_performance.get('perc_vitoria', 0)):
                melhor_performance = faixa.copy()
            
            if faixa.get('is_current', False):
                situacao_atual = faixa
        
        df_display = pd.DataFrame(df_display)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.subheader("💡 Análise de Valor")
        
        if situacao_atual:
            valor = situacao_atual.get('perc_vitoria', 0) - prob_implicita
            st.metric(
                "Taxa Histórica na Faixa Atual",
                f"{situacao_atual.get('perc_vitoria', 0):.1f}%",
                delta=f"{valor:+.1f}% vs mercado"
            )
            
            if valor > 5:
                st.success(f"✅ **VALOR POSITIVO**: Histórico sugere {valor:.1f}% mais chance de vitória que o mercado indica!")
            elif valor < -5:
                st.error(f"⚠️ **VALOR NEGATIVO**: Histórico sugere {abs(valor):.1f}% menos chance de vitória que o mercado indica!")
            else:
                st.info("⚖️ **ODD EQUILIBRADA**: Probabilidades alinhadas com histórico")
        
        if melhor_performance:
            st.info(f"📊 **Melhor Performance Histórica**: {melhor_performance['categoria']} - {melhor_performance.get('perc_vitoria', 0):.1f}% de vitórias (Odds {melhor_performance['range']})")
    else:
        st.warning("Não foi possível criar faixas de análise com os dados disponíveis")

# Função para analisar empates
def analyze_draw_performance(df, team_home, team_away, current_odd):
    # Filtra jogos entre os dois times
    games = df[((df['Home'] == team_home) & (df['Away'] == team_away)) | 
               ((df['Home'] == team_away) & (df['Away'] == team_home))].copy()
    
    if len(games) < 10:
        return {"error": "Dados insuficientes para análise de empates"}
    
    if 'odd Draw' not in games.columns or 'Resultado Home' not in games.columns:
        return {"error": "Colunas necessárias não encontradas para análise de empates"}
    
    games = games.dropna(subset=['odd Draw', 'Resultado Home'])
    
    # CORREÇÃO: Adicionar indentação correta
    if games.empty:
        return {"error": "Nenhum jogo encontrado entre estes times"}
    
    if len(games) < 5:
        return {"error": "Dados insuficientes após limpeza para análise de empates"}
    
    faixas = []
    
    # Faixa 1: Empate Provável
    limite1 = current_odd * 0.8
    faixa1 = games[games['odd Draw'] <= limite1]
    if len(faixa1) >= 3:
        faixas.append(("Empate Provável", f"≤ {limite1:.2f}", faixa1))
    
    # Faixa 2: Situação Atual
    limite2 = current_odd * 1.2
    faixa2 = games[(games['odd Draw'] > limite1) & (games['odd Draw'] <= limite2)]
    if len(faixa2) >= 3:
        faixas.append(("Situação Atual", f"{limite1:.2f} - {limite2:.2f}", faixa2))
    
    # Faixa 3: Empate Improvável
    faixa3 = games[games['odd Draw'] > limite2]
    if len(faixa3) >= 3:
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
            'is_current': (limite1 < current_odd <= limite2) and (nome == "Situação Atual")
        })
    
    return {
        'current_odd': current_odd,
        'total_games': len(games),
        'faixas': resultados
    }

# Função para exibir análise de empates
def display_draw_analysis(analysis, current_odd, prob_implicita):
    if "error" in analysis:
        st.warning(f"⚠️ {analysis['error']}")
        return
    st.write(f"**Total de jogos analisados:** {analysis['total_games']}")
    st.write(f"**Odd atual:** {current_odd:.2f} (Probabilidade implícita: {prob_implicita:.1f}%)")
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
            if faixa.get('is_current', False):
                situacao_atual = faixa
        df_display = pd.DataFrame(df_display)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
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

def analyze_team_odds_performance(df, team, position, current_odd):
    """Analisa performance do time em diferentes faixas de odds"""
    
    # Filtrar jogos do time na posição
    team_games = df[df[position] == team].copy()
    
    if len(team_games) < 5:  # Reduzido de 10 para 5 jogos
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
    
    if len(team_games) < 5:  # Reduzido de 10 para 5 jogos
        return {"error": f"Dados insuficientes após limpeza para {team}"}
    
    # Definir faixas de odds baseadas na odd atual
    faixas = []
    
    # Faixa 1: Muito favorito (odds baixas)
    limite1 = current_odd * 0.7  # 30% abaixo da odd atual
    faixa1 = team_games[team_games[odd_column] <= limite1]
    if len(faixa1) >= 3:  # Reduzido de 5 para 3
        faixas.append(("Muito Favorito", f"≤ {limite1:.2f}", faixa1, "#2E8B57"))  # Verde escuro
    
    # Faixa 2: Favorito moderado
    limite2 = current_odd * 0.9  # 10% abaixo da odd atual
    faixa2 = team_games[(team_games[odd_column] > limite1) & (team_games[odd_column] <= limite2)]
    if len(faixa2) >= 3:  # Reduzido de 5 para 3
        faixas.append(("Favorito Moderado", f"{limite1:.2f} - {limite2:.2f}", faixa2, "#32CD32"))  # Verde claro
    
    # Faixa 3: Situação similar à atual
    limite3 = current_odd * 1.1  # 10% acima da odd atual
    faixa3 = team_games[(team_games[odd_column] > limite2) & (team_games[odd_column] <= limite3)]
    if len(faixa3) >= 2:  # Reduzido de 3 para 2
        faixas.append(("Situação Atual", f"{limite2:.2f} - {limite3:.2f}", faixa3, "#FFD700"))  # Dourado
    
    # Faixa 4: Menos favorito
    limite4 = current_odd * 1.3  # 30% acima da odd atual
    faixa4 = team_games[(team_games[odd_column] > limite3) & (team_games[odd_column] <= limite4)]
    if len(faixa4) >= 3:  # Reduzido de 5 para 3
        faixas.append(("Menos Favorito", f"{limite3:.2f} - {limite4:.2f}", faixa4, "#FF8C00"))  # Laranja
    
    # Faixa 5: Azarão
    faixa5 = team_games[team_games[odd_column] > limite4]
    if len(faixa5) >= 3:  # Reduzido de 5 para 3
        faixas.append(("Azarão", f"> {limite4:.2f}", faixa5, "#DC143C"))  # Vermelho
    
    # Calcular estatísticas para cada faixa
    resultados = []
    for nome, range_str, dados, cor in faixas:
        total = len(dados)
        vitorias = len(dados[dados[result_column] == 'Vitória'])
        empates = len(dados[dados[result_column] == 'Empate'])
        derrotas = len(dados[dados[result_column] == 'Derrota'])

        perc_vitoria = (vitorias / total) * 100 if total > 0 else 0
        perc_empate = (empates / total) * 100 if total > 0 else 0
        perc_derrota = (derrotas / total) * 100 if total > 0 else 0
        odd_media = dados[odd_column].mean()

        resultados.append({
            'categoria': nome,
            'range': range_str,
            'total': total,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'perc_vitoria': perc_vitoria,
            'perc_empate': perc_empate,
            'perc_derrota': perc_derrota,
            'odd_media': odd_media,
            'is_current': nome == "Situação Atual",
            'cor': cor
        })
    return {
        'team': team,
        'position': position,
        'total_games': len(team_games),
        'current_odd': current_odd,
        'faixas': resultados
    }

def display_odds_analysis_victory(analysis, current_odd, prob_implicita):
    """Exibe análise de odds do time com design moderno"""
    if "error" in analysis:
        st.error(f"⚠️ {analysis['error']}")
        return

    # Header com informações principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📊 Total de Jogos",
            value=analysis['total_games'],
            help="Quantidade total de jogos analisados"
        )
    
    with col2:
        st.metric(
            label="🎯 Odd Atual",
            value=f"{current_odd:.2f}",
            help="Odd oferecida pela casa de apostas"
        )
    
    with col3:
        st.metric(
            label="📈 Prob. Implícita",
            value=f"{prob_implicita:.1f}%",
            help="Probabilidade implícita da odd atual"
        )

    st.divider()

    if analysis['faixas']:
        # Título da seção
        st.subheader("🏆 Performance por Faixa de Odds")
        
        # Cards modernos para cada faixa
        for faixa in analysis['faixas']:
            with st.container():
                # Criar um card estilizado
                card_color = faixa['cor']
                is_current = faixa.get('is_current', False)
                border_style = "border-left: 4px solid #FFD700;" if is_current else f"border-left: 4px solid {card_color};"
                
                st.markdown(f"""
                <div style="
                    background-color: rgba(255, 255, 255, 0.05);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px 0;
                    {border_style}
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h4 style="margin: 0 0 10px 0; color: {card_color};">
                        {'🎯 ' if is_current else '📊 '}{faixa['categoria']}
                        {' (SITUAÇÃO ATUAL)' if is_current else ''}
                    </h4>
                    <p style="margin: 5px 0; color: #666;">Faixa de Odds: {faixa['range']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas da faixa
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Jogos", faixa['total'])
                
                with col2:
                    st.metric(
                        "Vitórias", 
                        faixa['vitorias'],
                        delta=f"{faixa['perc_vitoria']:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Empates", 
                        faixa['empates'],
                        delta=f"{faixa['perc_empate']:.1f}%"
                    )
                
                with col4:
                    st.metric(
                        "Derrotas", 
                        faixa['derrotas'],
                        delta=f"{faixa['perc_derrota']:.1f}%"
                    )
                
                with col5:
                    st.metric("Odd Média", f"{faixa['odd_media']:.2f}")
                
                # Gráfico de barras horizontal para visualizar percentuais
                import plotly.express as px
                import plotly.graph_objects as go
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Vitórias',
                    y=['Resultado'],
                    x=[faixa['perc_vitoria']],
                    orientation='h',
                    marker_color='#2E8B57',
                    text=f"{faixa['perc_vitoria']:.1f}%",
                    textposition='inside'
                ))
                
                fig.add_trace(go.Bar(
                    name='Empates',
                    y=['Resultado'],
                    x=[faixa['perc_empate']],
                    orientation='h',
                    marker_color='#FFD700',
                    text=f"{faixa['perc_empate']:.1f}%",
                    textposition='inside'
                ))
                
                fig.add_trace(go.Bar(
                    name='Derrotas',
                    y=['Resultado'],
                    x=[faixa['perc_derrota']],
                    orientation='h',
                    marker_color='#DC143C',
                    text=f"{faixa['perc_derrota']:.1f}%",
                    textposition='inside'
                ))
                
                fig.update_layout(
                    barmode='stack',
                    height=100,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(range=[0, 100], visible=False),
                    yaxis=dict(visible=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                st.markdown("---")

        # Análise de Valor - Seção destacada
        st.subheader("💡 Análise de Valor da Aposta")
        
        situacao_atual = next((f for f in analysis['faixas'] if f.get('is_current', False)), None)
        melhor_performance = max(analysis['faixas'], key=lambda x: x.get('perc_vitoria', 0))
        
        if situacao_atual:
            valor = situacao_atual.get('perc_vitoria', 0) - prob_implicita
            
            # Card de valor destacado
            if valor > 5:
                valor_cor = "#2E8B57"
                valor_icon = "✅"
                valor_texto = "VALOR POSITIVO"
                valor_descricao = f"O histórico sugere {valor:.1f}% mais chances de vitória do que o mercado indica!"
            elif valor < -5:
                valor_cor = "#DC143C"
                valor_icon = "⚠️"
                valor_texto = "VALOR NEGATIVO"
                valor_descricao = f"O histórico sugere {abs(valor):.1f}% menos chances de vitória do que o mercado indica!"
            else:
                valor_cor = "#FFD700"
                valor_icon = "⚖️"
                valor_texto = "ODD EQUILIBRADA"
                valor_descricao = "As probabilidades estão alinhadas com o histórico do time!"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {valor_cor}22, {valor_cor}11);
                padding: 25px;
                border-radius: 15px;
                border: 2px solid {valor_cor};
                margin: 20px 0;
                text-align: center;
            ">
                <h3 style="color: {valor_cor}; margin: 0 0 10px 0;">
                    {valor_icon} {valor_texto}
                </h3>
                <p style="font-size: 18px; margin: 10px 0; color: #333;">
                    {valor_descricao}
                </p>
                <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px;">
                    <div>
                        <strong>Taxa Histórica:</strong><br>
                        <span style="font-size: 24px; color: {valor_cor};">
                            {situacao_atual.get('perc_vitoria', 0):.1f}%
                        </span>
                    </div>
                    <div>
                        <strong>Prob. Mercado:</strong><br>
                        <span style="font-size: 24px;">
                            {prob_implicita:.1f}%
                        </span>
                    </div>
                    <div>
                        <strong>Diferença:</strong><br>
                        <span style="font-size: 24px; color: {valor_cor};">
                            {valor:+.1f}%
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Informação sobre melhor performance
        st.info(f"""
        📊 **Melhor Performance Histórica**: {melhor_performance['categoria']} 
        
        • Taxa de vitória: **{melhor_performance.get('perc_vitoria', 0):.1f}%**
        • Faixa de odds: **{melhor_performance['range']}**
        • Jogos analisados: **{melhor_performance['total']}**
        """)
        
    else:
        st.warning("⚠️ Não foi possível criar faixas de análise com os dados disponíveis. Tente com um time que possui mais histórico de jogos.")

def show_corner_analysis(df, teams):
    """Simulação de escanteios com base nas médias"""
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

    if st.button("🚩 Simulador de Escanteios"):
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
    st.markdown('<h1 class="main-header">⚽ Análise & Estatística Brasileirão</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema completo de análise estatística do Campeonato Brasileiro</p>', unsafe_allow_html=True)

    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df = load_data()

    if df.empty:
        st.error("❌ Não foi possível carregar os dados.")
        st.info("📁 Certifique-se de que o arquivo está na raiz do repositório.")
        return

    # Filtro de ano no topo (sempre visível)
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">📅 Filtros de Temporada</h3>', unsafe_allow_html=True)
    col_filter = st.columns([1, 2, 1])[1]
    with col_filter:
        anos = sorted(df['Ano'].dropna().unique())
        ano_selecionado = st.selectbox("Selecione o Ano:", anos, key="ano_selecionado")
        df = df[df['Ano'] == ano_selecionado]
    st.markdown('</div>', unsafe_allow_html=True)

    # Inicializa lista de times de forma segura
    if ('Home' in df.columns) and ('Away' in df.columns):
        home_teams = df['Home'].dropna().astype(str).str.strip()
        away_teams = df['Away'].dropna().astype(str).str.strip()
        teams = sorted(set(home_teams) | set(away_teams))
    else:
        teams = []

    # Inicializa seleção de análise
    if 'selected_analysis' not in st.session_state:
        st.session_state.selected_analysis = None

    # Seleção de análise
    if st.session_state.selected_analysis is None:
        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📊 Opções de Análise</h2>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏆 Análise de Desempenho", key="desempenho"):
                st.session_state.selected_analysis = "1. Análise de Desempenho de Time"
                st.rerun()
            if st.button("🎯 Comparação de Times", key="comparacao"):
                st.session_state.selected_analysis = "2. Comparação entre Times"
                st.rerun()
            if st.button("🚩 Análise de Escanteios", key="corner_analysis"):
                st.session_state.selected_analysis = "7. Análise de Escanteios"
                st.rerun()

        with col2:
            if st.button("📈 Probabilidades", key="probabilidades"):
                st.session_state.selected_analysis = "3. Cálculo de Probabilidades Implícitas"
                st.rerun()
            if st.button("⚽ Simulação Escanteios", key="escanteios"):
                st.session_state.selected_analysis = "4. Simulação de Escanteios"
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
        if st.button("🏠 Voltar ao Menu Principal", key="voltar_menu"):
            st.session_state.selected_analysis = None
            st.rerun()
        
        st.markdown("---")
        
        # Roteamento das opções de análise
        try:
            if st.session_state.selected_analysis == "1. Análise de Desempenho de Time":
                show_team_performance(df, teams)
            elif st.session_state.selected_analysis == "2. Comparação entre Times":
                show_team_comparison(df, teams)
            elif st.session_state.selected_analysis == "3. Cálculo de Probabilidades Implícitas":
                show_probability_analysis(df, teams)
            elif st.session_state.selected_analysis == "4. Simulação de Escanteios":
                show_corner_simulation(df, teams)
            elif st.session_state.selected_analysis == "5. Predição de Placar (Poisson)":
                show_score_prediction(df, teams)
            elif st.session_state.selected_analysis == "6. Gráficos Interativos":
                show_interactive_charts(df)
            elif st.session_state.selected_analysis == "7. Análise de Escanteios":
                show_corner_analysis(df, teams)
            else:
                st.error("Opção de análise inválida.")
        except Exception as e:
            st.error(f"❌ Erro ao carregar análise: {str(e)}")
            st.info("🔄 Clique em 'Voltar ao Menu Principal' para tentar novamente.")

    # Debug info
    with st.expander("🔍 Informações de Debug"):
        st.write("Colunas do DataFrame:", list(df.columns))
        st.write("Shape do DataFrame original:", df.shape)
        st.write("Número de times encontrados:", len(teams))
        if 'Ano' in df.columns:
            st.write("Distribuição por ano:")
            st.write(df['Ano'].value_counts().sort_index())

def show_team_performance(df, teams):
    """Exibe análise de desempenho de um time selecionado."""
    st.header("🏆 Análise de Desempenho de Time")
    
    if not teams:
        st.warning("Nenhum time disponível.")
        return
        
    team = st.selectbox("Selecione o time para análise:", teams, key="team_performance")
    if not team:
        st.warning("Selecione um time.")
        return
        
    stats_home = calculate_team_stats(df, team, as_home=True)
    stats_away = calculate_team_stats(df, team, as_home=False)
    
    st.subheader(f"📊 Estatísticas de {team}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Como Mandante:**")
        st.write(f"Jogos: {stats_home['jogos']}")
        st.write(f"Vitórias: {stats_home['vitorias']}")
        st.write(f"Empates: {stats_home['empates']}")
        st.write(f"Derrotas: {stats_home['derrotas']}")
        st.write(f"Gols/Jogo: {stats_home['media_gols_feitos']:.2f}")
        st.write(f"Gols Sofridos/Jogo: {stats_home['media_gols_sofridos']:.2f}")
        st.write(f"Escanteios/Jogo: {stats_home['media_escanteios_feitos']:.2f}")
        st.write(f"Escanteios Sofridos/Jogo: {stats_home['media_escanteios_sofridos']:.2f}")
        
    with col2:
        st.write("**Como Visitante:**")
        st.write(f"Jogos: {stats_away['jogos']}")
        st.write(f"Vitórias: {stats_away['vitorias']}")
        st.write(f"Empates: {stats_away['empates']}")
        st.write(f"Derrotas: {stats_away['derrotas']}")
        st.write(f"Gols/Jogo: {stats_away['media_gols_feitos']:.2f}")
        st.write(f"Gols Sofridos/Jogo: {stats_away['media_gols_sofridos']:.2f}")
        st.write(f"Escanteios/Jogo: {stats_away['media_escanteios_feitos']:.2f}")
        st.write(f"Escanteios Sofridos/Jogo: {stats_away['media_escanteios_sofridos']:.2f}")

# CHAMADA DA MAIN (adicionar no final do arquivo)
if __name__ == "__main__":
    main()


