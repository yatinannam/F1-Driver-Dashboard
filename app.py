import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="F1 Driver Stats Explorer", layout="wide")

# Sleek F1-themed UI styling
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #121212;
            color: #e6e6e6;
        }

        .stApp {
            background-color: #121212;
        }

        h1, h2, h3, h4 {
            color: #ff1801;
        }

        section[data-testid="stSidebar"] {
            background-color: #1e1e1e;
            color: #ffffff;
            border-right: 1px solid #2c2c2c;
        }

        .stDataFrame thead {
            background-color: #222;
            color: #ff1801;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        .markdown-text-container p {
            color: #e6e6e6;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #555;
            border-radius: 4px;
        }

        .css-1v0mbdj {
            background-color: #1a1a1a !important;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 0 8px rgba(0,0,0,0.2);
        }

        .css-1d391kg {
            background-color: #1a1a1a !important;
            border-radius: 8px;
            padding: 1rem;
        }

        .css-q8sbsg p {
            color: #d1d1d1;
        }

        .css-1n76uvr a {
            color: #00b0f0;
        }
    </style>
""", unsafe_allow_html=True)

# Title & subtitle
st.title("🏎️ Formula 1 Driver Career Stats Explorer")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    drivers = pd.read_csv("data/drivers.csv")
    results = pd.read_csv("data/results.csv")
    races = pd.read_csv("data/races.csv")
    return drivers, results, races

drivers, results, races = load_data()

# Full name column
drivers['full_name'] = drivers['forename'] + ' ' + drivers['surname']
drivers = drivers.sort_values('full_name')

# Sidebar
st.sidebar.header("Select a Driver")
selected_driver_name = st.sidebar.selectbox("Driver", drivers['full_name'])
selected_driver = drivers[drivers['full_name'] == selected_driver_name].iloc[0]

# 👤 Profile Info
st.subheader("👤 Driver Profile")
st.markdown(f"**Name:** {selected_driver['full_name']}")
st.markdown(f"**Date of Birth:** {selected_driver['dob']}")
st.markdown(f"**Nationality:** {selected_driver['nationality']}")

# 📊 Career Stats
driver_results = results[results['driverId'] == selected_driver['driverId']]
total_races = driver_results['raceId'].nunique()
total_points = driver_results['points'].sum()
wins = driver_results[driver_results['position'] == 1].shape[0]
best_finish = pd.to_numeric(driver_results['position'], errors='coerce').dropna().astype(int).min()

st.subheader("📊 Career Summary")
st.markdown(f"**Total Races:** {total_races}")
st.markdown(f"**Total Career Points:** {int(total_points)}")
st.markdown(f"**Wins:** {wins}")
st.markdown(f"**Best Finish Position:** {best_finish}")

# 📋 Detailed Results
driver_race_results = driver_results.merge(races, on='raceId', how='left')
driver_race_results['position'] = pd.to_numeric(driver_race_results['position'], errors='coerce')

st.subheader("📋 Detailed Race Results")
st.dataframe(
    driver_race_results[['year', 'round', 'name', 'position', 'points']].rename(columns={
        'year': 'Year',
        'round': 'Round',
        'name': 'Grand Prix',
        'position': 'Finish Position',
        'points': 'Points'
    }).sort_values(['Year', 'Round'])
)

# 📊 Bar Chart: Points by Year
points_by_year = driver_race_results.groupby('year')['points'].sum().reset_index()

st.subheader("📊 Points by Year")
fig = px.bar(
    points_by_year,
    x='year',
    y='points',
    labels={'year': 'Year', 'points': 'Total Points'},
    title=f"{selected_driver['full_name']}'s Points Per Season",
    color='points',
    color_continuous_scale='reds'
)
st.plotly_chart(fig, use_container_width=True)

# 🥧 Pie Chart: Finish Distribution
finish_data = driver_race_results.copy()
finish_data['position'] = pd.to_numeric(finish_data['position'], errors='coerce').dropna()
finish_data = finish_data.dropna(subset=['position'])

def bucket(pos):
    if pos == 1:
        return '🥇 Win'
    elif pos <= 3:
        return '🏆 Podium'
    elif pos <= 10:
        return 'Top 10'
    else:
        return '11+'

finish_data['Category'] = finish_data['position'].apply(bucket)
finish_counts = finish_data['Category'].value_counts().reset_index()
finish_counts.columns = ['Category', 'Count']

st.subheader("🥧 Finish Position Distribution")
fig2 = px.pie(
    finish_counts,
    names='Category',
    values='Count',
    title="Distribution of Finishes",
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig2, use_container_width=True)
