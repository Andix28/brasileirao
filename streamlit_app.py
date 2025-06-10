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
    """Carrega e processa os dados do CSV"""
    try:
        # Tenta diferentes encodings para o CSV
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('BRA_DADOS_2425_B.csv', sep=';', encoding=encoding)
                st.success(f"Arquivo carregado com encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                st.error("Arquivo 'BRA_DADOS_2425_B.csv' não encontrado!")
                return pd.DataFrame()
        
        if df is None:
            st.error("Não foi possível carregar o arquivo com nenhum encoding testado.")
            return pd.DataFrame()
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        # Verifica se as colunas necessárias existem
        required_columns = ['Home', 'Away', 'Gols Home']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Colunas obrigatórias não encontradas: {missing_columns}")
            st.info(f"Colunas disponíveis: {list(df.columns)}")
            return pd.DataFrame()
        
        # Remove linhas onde Home está vazio
        df = df[df['Home'].notna()]
        
        # Remove linhas onde não há dados de gols
        df = df[df['Gols Home'].notna()]
        
        # Converte colunas numéricas com tratamento de erro
        numeric_columns = ['Gols Home', 'Gols  Away', 'odd Home', 'odd Draw', 'odd Away', 
                         'Home Score HT', 'Away Score HT', 'Corner Home', 'Corner Away', 
                         'Total Corner Match']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Renomeia colunas para padronizar
        if 'Gols  Away' in df.columns:
            df = df.rename(columns={'Gols  Away': 'Gols Away'})
        
        # Verifica se Jogo ID existe antes de usar
        if 'Jogo ID' in df.columns:
            # Adiciona ano baseado no ID do jogo
            df['Ano'] = df['Jogo ID'].apply(lambda x: 2024 if x <= 190 else 2025)
        else:
            # Se não há Jogo ID, assume todos os jogos são de 2024
            df['Ano'] = 2024
            df['Jogo ID'] = range(1, len(df) + 1)
        
        # Calcula resultado apenas se as colunas de gols existem
        if 'Gols Home' in df.columns and 'Gols Away' in df.columns:
            df['Resultado Home'] = df.apply(lambda row: 
                'Vitória' if row['Gols Home'] > row['Gols Away'] else 
                'Empate' if row['Gols Home'] == row['Gols Away'] else 'Derrota', axis=1)
            
            # Calcula total de gols
            df['Total Gols'] = df['Gols Home'] + df['Gols Away']
        
        return df
    
    except Exception as e:
        st.error(f"Erro inesperado ao carregar dados: {str(e)}")
        return pd.DataFrame()

def calculate_team_stats(df, team, as_home=True):
    """Calcula estatísticas de um time"""
    try:
        if as_home:
            team_df = df[df['Home'] == team].copy()
            goals_for = 'Gols Home'
            goals_against = 'Gols Away'
            corners_for = 'Corner Home'
            corners_against = 'Corner Away'
            result_col = 'Resultado Home'
        else:
            team_df = df[df['Away'] == team].copy()
            goals_for = 'Gols Away'
            goals_against = 'Gols Home'
            corners_for = 'Corner Away'
            corners_against = 'Corner Home'
            # Inverte o resultado para visitante
            if 'Resultado Home' in team_df.columns:
                team_df['Resultado Away'] = team_df['Resultado Home'].map({
                    'Vitória': 'Derrota',
                    'Derrota': 'Vitória',
                    'Empate': 'Empate'
                })
                result_col = 'Resultado Away'
            else:
                result_col = None
        
        if team_df.empty:
            return {
                'jogos': 0, 'vitorias': 0, 'empates': 0, 'derrotas': 0,
                'gols_feitos': 0, 'gols_sofridos': 0,
                'media_gols_feitos': 0, 'media_gols_sofridos': 0,
                'escanteios_feitos': 0, 'escanteios_sofridos': 0,
                'media_escanteios_feitos': 0, 'media_escanteios_sofridos': 0
            }
        
        # Calcula estatísticas básicas
        stats = {
            'jogos': len(team_df),
            'gols_feitos': team_df[goals_for].sum() if goals_for in team_df.columns else 0,
            'gols_sofridos': team_df[goals_against].sum() if goals_against in team_df.columns else 0,
            'media_gols_feitos': team_df[goals_for].mean() if goals_for in team_df.columns and not team_df[goals_for].isna().all() else 0,
            'media_gols_sofridos': team_df[goals_against].mean() if goals_against in team_df.columns and not team_df[goals_against].isna().all() else 0,
            'escanteios_feitos': team_df[corners_for].sum() if corners_for in team_df.columns else 0,
            'escanteios_sofridos': team_df[corners_against].sum() if corners_against in team_df.columns else 0,
            'media_escanteios_feitos': team_df[corners_for].mean() if corners_for in team_df.columns and not team_df[corners_for].isna().all() else 0,
            'media_escanteios_sofridos': team_df[corners_against].mean() if corners_against in team_df.columns and not team_df[corners_against].isna().all() else 0,
        }
        
        # Calcula resultados se a coluna existe
        if result_col and result_col in team_df.columns:
            stats.update({
                'vitorias': len(team_df[team_df[result_col] == 'Vitória']),
                'empates': len(team_df[team_df[result_col] == 'Empate']),
                'derrotas': len(team_df[team_df[result_col] == 'Derrota']),
            })
        else:
            stats.update({
                'vitorias': 0,
                'empates': 0,
                'derrotas': 0,
            })
        
        return stats
    except Exception as e:
        st.error(f"Erro ao calcular estatísticas: {str(e)}")
        return {}

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
    """Exibe gráficos interativos"""
    st.header("📊 Gráficos Interativos")
    
    if df.empty:
        st.warning("Nenhum dado disponível para gráficos.")
        return
    
    # Gráfico de gols por rodada
    if 'Total Gols' in df.columns and 'Jogo ID' in df.columns:
        fig = px.line(df, x='Jogo ID', y='Total Gols', title='Gols por Jogo')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados insuficientes para gráficos interativos.")
        st.write("Colunas disponíveis:", list(df.columns))

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
    """Comparação entre dois times"""
    st.header("⚔️ Comparação entre Times")
    
    if len(teams) < 2:
        st.warning("É necessário ter pelo menos 2 times nos dados.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox("🏆 Primeiro time:", teams, key="team1")
    with col2:
        team2 = st.selectbox("🏆 Segundo time:", teams, key="team2")
    
    if team1 and team2 and team1 != team2:
        st.info(f"Comparação entre {team1} e {team2} - Funcionalidade em desenvolvimento")

def show_probability_analysis(df, teams):
    """Análise de probabilidades implícitas"""
    st.header("🎲 Cálculo de Probabilidades Implícitas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        manual_home_odd = st.number_input("🏠 Odd Casa:", min_value=1.01, value=2.0, step=0.1)
    with col2:
        manual_draw_odd = st.number_input("🤝 Odd Empate:", min_value=1.01, value=3.0, step=0.1)
    with col3:
        manual_away_odd = st.number_input("✈️ Odd Visitante:", min_value=1.01, value=3.5, step=0.1)
    
    if st.button("Calcular Probabilidades"):
        home_prob, draw_prob, away_prob = calculate_implicit_probabilities(
            manual_home_odd, manual_draw_odd, manual_away_odd
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏠 Casa", f"{home_prob:.1f}%")
        with col2:
            st.metric("🤝 Empate", f"{draw_prob:.1f}%")
        with col3:
            st.metric("✈️ Visitante", f"{away_prob:.1f}%")

def show_corner_simulation(df, teams):
    """Simulação de escanteios"""
    st.header("🚩 Simulação de Escanteios")
    st.info("Funcionalidade de simulação de escanteios - Em desenvolvimento")

def show_score_prediction(df, teams):
    """Predição de placar usando Poisson"""
    st.header("🎯 Predição de Placar (Distribuição de Poisson)")
    st.info("Funcionalidade de predição de placar - Em desenvolvimento")

def main():
    # Título principal
    st.markdown('<h1 class="main-header">⚽ Sistema de Análise de Futebol</h1>', unsafe_allow_html=True)
    
    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df = load_data()
    
    if df.empty:
        st.error("❌ Não foi possível carregar os dados.")
        st.info("📁 Certifique-se de que o arquivo 'BRA_DADOS_2425_B.csv' está na raiz do repositório.")
        st.info("🔍 Verifique também se o arquivo está no encoding correto (UTF-8 ou Latin-1).")
        return
    
    st.success(f"✅ Dados carregados com sucesso! Total de jogos: {len(df)}")
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("🔧 Configurações")
        
        # Filtro de ano
        if 'Ano' in df.columns:
            available_years = sorted(df['Ano'].unique())
            year_options = ["Todos os anos"] + [str(year) for year in available_years]
            year_filter = st.selectbox("📅 Selecione o período:", year_options, index=0)
        else:
            year_filter = "Todos os anos"
        
        # Aplica filtro de ano
        if year_filter != "Todos os anos":
            df_filtered = df[df['Ano'] == int(year_filter)]
        else:
            df_filtered = df.copy()
        
        st.info(f"📊 Total de jogos filtrados: {len(df_filtered)}")
        
        # Lista de times únicos
        try:
            home_teams = df_filtered['Home'].dropna().unique().tolist()
            away_teams = df_filtered['Away'].dropna().unique().tolist()
            teams = sorted(list(set(home_teams + away_teams)))
        except:
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
        
    # Debug info (remover em produção)
    with st.expander("🔍 Informações de Debug"):
        st.write("Colunas do DataFrame:", list(df.columns))
        st.write("Primeiras linhas:", df.head())

# Executa a aplicação
if __name__ == "__main__":
    main()
