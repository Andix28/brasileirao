# %%
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
        # Carrega o arquivo CSV
        df = pd.read_csv('BRA DADOS 2425 B.csv', sep=';', encoding='utf-8')
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        # Remove linhas onde Home está vazio
        df = df[df['Home'].notna()]
        
        # Remove linhas onde não há dados de gols
        df = df[df['Gols Home'].notna()]
        
        # Converte colunas numéricas
        numeric_columns = ['Gols Home', 'Gols  Away', 'odd Home', 'odd Draw', 'odd Away', 
                         'Home Score HT', 'Away Score HT', 'Corner Home', 'Corner Away', 
                         'Total Corner Match']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Renomeia colunas para padronizar
        df = df.rename(columns={'Gols  Away': 'Gols Away'})
        
        # Adiciona ano baseado no ID do jogo (assumindo que jogos 1-190 são 2024, 191+ são 2025)
        df['Ano'] = df['Jogo ID'].apply(lambda x: 2024 if x <= 190 else 2025)
        
        # Calcula resultado
        df['Resultado Home'] = df.apply(lambda row: 
            'Vitória' if row['Gols Home'] > row['Gols Away'] else 
            'Empate' if row['Gols Home'] == row['Gols Away'] else 'Derrota', axis=1)
        
        # Calcula total de gols
        df['Total Gols'] = df['Gols Home'] + df['Gols Away']
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def calculate_team_stats(df, team, as_home=True):
    """Calcula estatísticas de um time"""
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
        team_df['Resultado Away'] = team_df['Resultado Home'].map({
            'Vitória': 'Derrota',
            'Derrota': 'Vitória',
            'Empate': 'Empate'
        })
        result_col = 'Resultado Away'
    
    if team_df.empty:
        return {}
    
    stats = {
        'jogos': len(team_df),
        'vitorias': len(team_df[team_df[result_col] == 'Vitória']),
        'empates': len(team_df[team_df[result_col] == 'Empate']),
        'derrotas': len(team_df[team_df[result_col] == 'Derrota']),
        'gols_feitos': team_df[goals_for].sum(),
        'gols_sofridos': team_df[goals_against].sum(),
        'media_gols_feitos': team_df[goals_for].mean(),
        'media_gols_sofridos': team_df[goals_against].mean(),
        'escanteios_feitos': team_df[corners_for].sum(),
        'escanteios_sofridos': team_df[corners_against].sum(),
        'media_escanteios_feitos': team_df[corners_for].mean(),
        'media_escanteios_sofridos': team_df[corners_against].mean(),
    }
    
    return stats

def calculate_implicit_probabilities(home_odd, draw_odd, away_odd):
    """Calcula probabilidades implícitas das odds"""
    home_prob = 1 / home_odd * 100
    draw_prob = 1 / draw_odd * 100
    away_prob = 1 / away_odd * 100
    
    return home_prob, draw_prob, away_prob

def predict_score_poisson(home_avg, away_avg, home_def, away_def):
    """Prediz placar usando distribuição de Poisson"""
    # Calcula força ofensiva e defensiva
    home_attack = home_avg
    away_attack = away_avg
    home_defense = home_def
    away_defense = away_def
    
    # Calcula gols esperados
    home_goals_expected = (home_attack + away_defense) / 2
    away_goals_expected = (away_attack + home_defense) / 2
    
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

def show_interactive_charts(df):
    """Exibe gráficos interativos (placeholder)"""
    st.header("📊 Gráficos Interativos")
    st.info("Funcionalidade de gráficos interativos ainda não implementada. Adicione seus gráficos aqui!")

def main():
    # Título principal
    st.markdown('<h1 class="main-header">⚽ Sistema de Análise de Futebol</h1>', unsafe_allow_html=True)
    
    # Carrega os dados
    df = load_data()
    
    if df.empty:
        st.error("Não foi possível carregar os dados. Verifique se o arquivo CSV está na pasta correta.")
        return
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("🔧 Configurações")
        
        # Filtro de ano
        year_filter = st.selectbox(
            "📅 Selecione o período:",
            ["Todos os anos", "2024", "2025"],
            index=0
        )
        
        # Aplica filtro de ano
        if year_filter != "Todos os anos":
            df_filtered = df[df['Ano'] == int(year_filter)]
        else:
            df_filtered = df.copy()
        
        st.info(f"📊 Total de jogos: {len(df_filtered)}")
        
        # Lista de times únicos
        teams = sorted(list(set(df_filtered['Home'].tolist() + df_filtered['Away'].tolist())))
        
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

def show_team_analysis(df, teams):
    """Análise de desempenho de um time específico"""
    st.header("📊 Análise de Desempenho de Time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_team = st.selectbox("🏆 Selecione o time:", teams)
    
    if selected_team:
        # Estatísticas como mandante
        home_stats = calculate_team_stats(df, selected_team, as_home=True)
        # Estatísticas como visitante
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
        
        # Tabs para diferentes análises
        tab1, tab2, tab3 = st.tabs(["🏠 Como Mandante", "✈️ Como Visitante", "📈 Estatísticas Gerais"])
        
        with tab1:
            if home_stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Resultados em Casa")
                    st.write(f"🎮 Jogos: {home_stats['jogos']}")
                    st.write(f"🏆 Vitórias: {home_stats['vitorias']}")
                    st.write(f"🤝 Empates: {home_stats['empates']}")
                    st.write(f"❌ Derrotas: {home_stats['derrotas']}")
                    
                with col2:
                    st.subheader("Médias em Casa")
                    st.write(f"⚽ Gols/jogo: {home_stats['media_gols_feitos']:.2f}")
                    st.write(f"🥅 Gols sofridos/jogo: {home_stats['media_gols_sofridos']:.2f}")
                    st.write(f"🚩 Escanteios/jogo: {home_stats['media_escanteios_feitos']:.2f}")
                    st.write(f"🚩 Escanteios sofridos/jogo: {home_stats['media_escanteios_sofridos']:.2f}")
        
        with tab2:
            if away_stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Resultados Fora de Casa")
                    st.write(f"🎮 Jogos: {away_stats['jogos']}")
                    st.write(f"🏆 Vitórias: {away_stats['vitorias']}")
                    st.write(f"🤝 Empates: {away_stats['empates']}")
                    st.write(f"❌ Derrotas: {away_stats['derrotas']}")
                    
                with col2:
                    st.subheader("Médias Fora de Casa")
                    st.write(f"⚽ Gols/jogo: {away_stats['media_gols_feitos']:.2f}")
                    st.write(f"🥅 Gols sofridos/jogo: {away_stats['media_gols_sofridos']:.2f}")
                    st.write(f"🚩 Escanteios/jogo: {away_stats['media_escanteios_feitos']:.2f}")
                    st.write(f"🚩 Escanteios sofridos/jogo: {away_stats['media_escanteios_sofridos']:.2f}")
        
        with tab3:
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox("🏆 Primeiro time:", teams, key="team1")
    with col2:
        team2 = st.selectbox("🏆 Second time:", teams, key="team2")
    
    if team1 and team2 and team1 != team2:
        # Confrontos diretos
        direct_matches = df[
            ((df['Home'] == team1) & (df['Away'] == team2)) |
            ((df['Home'] == team2) & (df['Away'] == team1))
        ]
        
        st.subheader(f"📊 Confrontos Diretos: {team1} vs {team2}")
        
        if not direct_matches.empty:
            # Estatísticas dos confrontos diretos
            team1_wins = len(direct_matches[
                ((direct_matches['Home'] == team1) & (direct_matches['Gols Home'] > direct_matches['Gols Away'])) |
                ((direct_matches['Away'] == team1) & (direct_matches['Gols Away'] > direct_matches['Gols Home']))
            ])
            
            team2_wins = len(direct_matches[
                ((direct_matches['Home'] == team2) & (direct_matches['Gols Home'] > direct_matches['Gols Away'])) |
                ((direct_matches['Away'] == team2) & (direct_matches['Gols Away'] > direct_matches['Gols Home']))
            ])
            
            draws = len(direct_matches[direct_matches['Gols Home'] == direct_matches['Gols Away']])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎮 Total de Jogos", len(direct_matches))
            with col2:
                st.metric(f"🏆 Vitórias {team1}", team1_wins)
            with col3:
                st.metric("🤝 Empates", draws)
            with col4:
                st.metric(f"🏆 Vitórias {team2}", team2_wins)
            
            # Histórico de confrontos
            st.subheader("📋 Histórico de Confrontos")
            confrontos_display = direct_matches[['Home', 'Gols Home', 'Gols Away', 'Away', 'Total Corner Match']].copy()
            st.dataframe(confrontos_display, use_container_width=True)
        else:
            st.info("Nenhum confronto direto encontrado entre esses times no período selecionado.")
        
        # Comparação geral
        st.subheader("📊 Comparação Geral de Desempenho")
        
        # Estatísticas gerais dos times
        team1_home = calculate_team_stats(df, team1, as_home=True)
        team1_away = calculate_team_stats(df, team1, as_home=False)
        team2_home = calculate_team_stats(df, team2, as_home=True)
        team2_away = calculate_team_stats(df, team2, as_home=False)
        
        # Cria DataFrame para comparação
        comparison_data = {
            'Métrica': [
                'Jogos Totais', 'Vitórias Totais', 'Média Gols/Jogo',
                'Média Gols Sofridos/Jogo', 'Média Escanteios/Jogo'
            ],
            team1: [
                team1_home.get('jogos', 0) + team1_away.get('jogos', 0),
                team1_home.get('vitorias', 0) + team1_away.get('vitorias', 0),
                (team1_home.get('media_gols_feitos', 0) + team1_away.get('media_gols_feitos', 0)) / 2,
                (team1_home.get('media_gols_sofridos', 0) + team1_away.get('media_gols_sofridos', 0)) / 2,
                (team1_home.get('media_escanteios_feitos', 0) + team1_away.get('media_escanteios_feitos', 0)) / 2
            ],
            team2: [
                team2_home.get('jogos', 0) + team2_away.get('jogos', 0),
                team2_home.get('vitorias', 0) + team2_away.get('vitorias', 0),
                (team2_home.get('media_gols_feitos', 0) + team2_away.get('media_gols_feitos', 0)) / 2,
                (team2_home.get('media_gols_sofridos', 0) + team2_away.get('media_gols_sofridos', 0)) / 2,
                (team2_home.get('media_escanteios_feitos', 0) + team2_away.get('media_escanteios_feitos', 0)) / 2
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)

def show_probability_analysis(df, teams):
    """Análise de probabilidades implícitas"""
    st.header("🎲 Cálculo de Probabilidades Implícitas")
    
    st.write("Selecione um jogo específico ou insira odds manualmente:")
    
    tab1, tab2 = st.tabs(["🎮 Jogos da Base", "✏️ Odds Manuais"])
    
    with tab1:
        # Selecionar jogo da base
        game_options = []
        for _, row in df.iterrows():
            if pd.notna(row['odd Home']) and pd.notna(row['odd Draw']) and pd.notna(row['odd Away']):
                game_options.append(f"{row['Home']} vs {row['Away']} (ID: {row['Jogo ID']})")
        
        if game_options:
            selected_game = st.selectbox("🎮 Selecione um jogo:", game_options)
            
            if selected_game:
                game_id = int(selected_game.split("ID: ")[1].replace(")", ""))
                game_row = df[df['Jogo ID'] == game_id].iloc[0]
                
                home_odd = game_row['odd Home']
                draw_odd = game_row['odd Draw']
                away_odd = game_row['odd Away']
                
                home_prob, draw_prob, away_prob = calculate_implicit_probabilities(home_odd, draw_odd, away_odd)
                
                st.subheader(f"📊 {game_row['Home']} vs {game_row['Away']}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(f"🏠 {game_row['Home']}", f"{home_prob:.1f}%", f"Odd: {home_odd}")
                with col2:
                    st.metric("🤝 Empate", f"{draw_prob:.1f}%", f"Odd: {draw_odd}")
                with col3:
                    st.metric(f"✈️ {game_row['Away']}", f"{away_prob:.1f}%", f"Odd: {away_odd}")
                
                # Gráfico das probabilidades
                fig = px.bar(
                    x=[game_row['Home'], 'Empate', game_row['Away']],
                    y=[home_prob, draw_prob, away_prob],
                    title="Probabilidades Implícitas",
                    labels={'x': 'Resultado', 'y': 'Probabilidade (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.write("Insira as odds para calcular as probabilidades:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            manual_home_odd = st.number_input("🏠 Odd Casa:", min_value=1.0, value=2.0, step=0.1)
        with col2:
            manual_draw_odd = st.number_input("🤝 Odd Empate:", min_value=1.0, value=3.0, step=0.1)
        with col3:
            manual_away_odd = st.number_input("✈️ Odd Visitante:", min_value=1.0, value=3.5, step=0.1)
        
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Time Mandante:", teams, key="corner_home")
    with col2:
        away_team = st.selectbox("✈️ Time Visitante:", teams, key="corner_away")
    
    if home_team and away_team and home_team != away_team:
        # Estatísticas de escanteios dos times
        home_stats_h = calculate_team_stats(df, home_team, as_home=True)
        home_stats_a = calculate_team_stats(df, home_team, as_home=False)
        away_stats_h = calculate_team_stats(df, away_team, as_home=True)
        away_stats_a = calculate_team_stats(df, away_team, as_home=False)
        
        # Médias de escanteios
        home_corners_avg = (home_stats_h.get('media_escanteios_feitos', 0) + home_stats_a.get('media_escanteios_feitos', 0)) / 2
        away_corners_avg = (away_stats_h.get('media_escanteios_feitos', 0) + away_stats_a.get('media_escanteios_feitos', 0)) / 2
        
        # Confrontos diretos
        direct_matches = df[
            ((df['Home'] == home_team) & (df['Away'] == away_team)) |
            ((df['Home'] == away_team) & (df['Away'] == home_team))
        ]
        
        st.subheader("📊 Estatísticas de Escanteios")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"🚩 Média {home_team}", f"{home_corners_avg:.1f}")
        with col2:
            st.metric(f"🚩 Média {away_team}", f"{away_corners_avg:.1f}")
        with col3:
            predicted_total = home_corners_avg + away_corners_avg
            st.metric("🚩 Previsão Total", f"{predicted_total:.1f}")
        
        if not direct_matches.empty:
            st.subheader("📋 Histórico de Escanteios nos Confrontos Diretos")
            
            corner_history = []
            for _, match in direct_matches.iterrows():
                if match['Home'] == home_team:
                    corner_history.append({
                        'Jogo': f"{match['Home']} {match['Gols Home']}-{match['Gols Away']} {match['Away']}",
                        f'Escanteios {home_team}': match['Corner Home'],
                        f'Escanteios {away_team}': match['Corner Away'],
                        'Total': match['Total Corner Match']
                    })
                else:
                    corner_history.append({
                        'Jogo': f"{match['Home']} {match['Gols Home']}-{match['Gols Away']} {match['Away']}",
                        f'Escanteios {home_team}': match['Corner Away'],
                        f'Escanteios {away_team}': match['Corner Home'],
                        'Total': match['Total Corner Match']
                    })
            
            if corner_history:
                corner_df = pd.DataFrame(corner_history)
                st.dataframe(corner_df, use_container_width=True)
                
                avg_direct_total = corner_df['Total'].mean()
                st.info(f"🚩 Média de escanteios nos confrontos diretos: {avg_direct_total:.1f}")

def show_score_prediction(df, teams):
    """Predição de placar usando Poisson"""
    st.header("🎯 Predição de Placar (Distribuição de Poisson)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Time Mandante:", teams, key="poisson_home")
    with col2:
        away_team = st.selectbox("✈️ Time Visitante:", teams, key="poisson_away")
    
    if home_team and away_team and home_team != away_team:
        # Estatísticas gerais (70% do peso)
        home_stats_h = calculate_team_stats(df, home_team, as_home=True)
        home_stats_a = calculate_team_stats(df, home_team, as_home=False)
        away_stats_h = calculate_team_stats(df, away_team, as_home=True)
        away_stats_a = calculate_team_stats(df, away_team, as_home=False)
        
        # Médias gerais
        home_attack_general = (home_stats_h.get('media_gols_feitos', 0) + home_stats_a.get('media_gols_feitos', 0)) / 2
        home_defense_general = (home_stats_h.get('media_gols_sofridos', 0) + home_stats_a.get('media_gols_sofridos', 0)) / 2
        away_attack_general = (away_stats_h.get('media_gols_feitos', 0) + away_stats_a.get('media_gols_feitos', 0)) / 2
        away_defense_general = (away_stats_h.get('media_gols_sofridos', 0) + away_stats_a.get('media_gols_sofridos', 0)) / 2
        
        # Confrontos diretos (30% do peso)
        direct_matches = df[
            ((df['Home'] == home_team) & (df['Away'] == away_team)) |
            ((df['Home'] == away_team) & (df['Away'] == home_team))
        ]
        
        if not direct_matches.empty:
            home_goals_direct = []
            away_goals_direct = []
            
            for _, match in direct_matches.iterrows():
                if match['Home'] == home_team:
                    home_goals_direct.append(match['Gols Home'])
                    away_goals_direct.append(match['Gols Away'])
                else:
                    home_goals_direct.append(match['Gols Away'])
                    away_goals_direct.append(match['Gols Home'])
            # Médias dos confrontos diretos
            home_attack_direct = np.mean(home_goals_direct) if home_goals_direct else 0
            away_attack_direct = np.mean(away_goals_direct) if away_goals_direct else 0
        else:
            home_attack_direct = 0
            away_attack_direct = 0

        # Combina médias gerais e dos confrontos diretos (70% geral, 30% direto)
        home_attack = 0.7 * home_attack_general + 0.3 * home_attack_direct
        away_attack = 0.7 * away_attack_general + 0.3 * away_attack_direct
        home_defense = 0.7 * home_defense_general + 0.3 * (away_attack_direct if away_attack_direct else away_defense_general)
        away_defense = 0.7 * away_defense_general + 0.3 * (home_attack_direct if home_attack_direct else home_defense_general)

        # Predição usando Poisson
        best_score, max_prob, home_goals_exp, away_goals_exp = predict_score_poisson(
            home_attack, away_attack, home_defense, away_defense
        )

        # Exibir previsão de placar mais provável
        st.subheader("🔮 Previsão de Placar Mais Provável")
        st.markdown(
            f"<h2 style='text-align:center'>{home_team} {best_score[0]} x {best_score[1]} {away_team}</h2>",
            unsafe_allow_html=True
        )
        st.write(f"Probabilidade do placar exato: {max_prob * 100:.2f}%")
        st.write(f"Gols esperados: {home_team} {home_goals_exp:.2f} x {away_goals_exp:.2f} {away_team}")

        # Criar matriz de calor de probabilidades de placares (0 a 5 gols)
        score_matrix = np.zeros((6, 6))

        # Calcular probabilidades para todos os placares de 0x0 a 5x5
        for i in range(6):
            for j in range(6):
                score_matrix[i, j] = poisson.pmf(i, home_goals_exp) * poisson.pmf(j, away_goals_exp)

        # Gráfico de calor com Plotly
        fig = go.Figure(data=go.Heatmap(
            z=score_matrix,
            x=[str(i) for i in range(6)],
            y=[str(i) for i in range(6)],
            colorscale='Blues'
        ))
        fig.update_layout(
            title="Probabilidade de Placar Exato",
            xaxis_title=f"Gols {away_team}",
            yaxis_title=f"Gols {home_team}"
        )

        # Exibir no Streamlit
        st.plotly_chart(fig, use_container_width=True)

# %%



