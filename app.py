# app.py — IPL Points Table (clean UI + clickable team search)
# Place this file in the same folder as: ipl_points_table.csv

import streamlit as st
import pandas as pd
from urllib.parse import quote_plus

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="IPL Points Table",
    page_icon="🏏",
    layout="wide",
)

# ----------------------------
# Minimal styling
# ----------------------------
st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; padding-bottom: 2rem;}
      h1 {margin-bottom: .25rem;}
      .subtle {opacity: .75; margin-top: 0;}
      /* Make dataframe look nicer */
      [data-testid="stDataFrame"] {border-radius: 14px; overflow: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Helpers
# ----------------------------
def google_search_url(team_name: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(team_name + ' IPL team')}"

@st.cache_data
def load_points_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic clean-ups / type safety
    if "season" in df.columns:
        df["season"] = df["season"].astype(str)
    return df

# ----------------------------
# Load data
# ----------------------------
DATA_FILE = "ipl_points_table.csv"

try:
    pt = load_points_table(DATA_FILE)
except FileNotFoundError:
    st.error(f"File not found: {DATA_FILE}\n\nKeep **app.py** and **{DATA_FILE}** in the same folder.")
    st.stop()

required_cols = {"season", "team", "matches_played", "wins", "losses", "no_result", "points", "win_pct"}
missing = required_cols - set(pt.columns)
if missing:
    st.error(f"Your CSV is missing required columns: {sorted(missing)}")
    st.stop()

# ----------------------------
# Header
# ----------------------------
st.title("🏏 IPL Points Table")
st.markdown('<p class="subtle">Pick a season. Use the Search column to open Google results for a team.</p>', unsafe_allow_html=True)

# ----------------------------
# Season selector
# ----------------------------
seasons = sorted(pt["season"].unique(), reverse=True)
default_season = seasons[0] if seasons else None

season = st.selectbox("Season", seasons, index=0)

# Filter season
pt_season = pt[pt["season"] == season].copy()

# Sort (points desc, win_pct desc)
pt_season = pt_season.sort_values(["points", "win_pct"], ascending=[False, False]).reset_index(drop=True)
pt_season.insert(0, "rank", pt_season.index + 1)

# Create team search link
pt_season["team_search_link"] = pt_season["team"].apply(google_search_url)

# ----------------------------
# Quick stats cards
# ----------------------------
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Teams", int(pt_season["team"].nunique()))
with c2:
    st.metric("Max Points", int(pt_season["points"].max()) if len(pt_season) else 0)
with c3:
    top_win = float(pt_season["win_pct"].max()) if len(pt_season) else 0.0
    st.metric("Top Win %", f"{top_win:.1f}")

st.divider()

# ----------------------------
# Display table (clean clickable link)
# ----------------------------
st.subheader(f"Points Table for {season}")

cols_to_show = ["rank", "team", "matches_played", "wins", "losses", "no_result", "points", "win_pct", "team_search_link"]
display_df = pt_season[cols_to_show].copy()

# Round win %
display_df["win_pct"] = display_df["win_pct"].round(1)

# Rename columns to match IPL style a bit
display_df = display_df.rename(
    columns={
        "rank": "Rank",
        "team": "Team",
        "matches_played": "P",
        "wins": "W",
        "losses": "L",
        "no_result": "NR",
        "points": "Pts",
        "win_pct": "Win %",
        "team_search_link": "Search",
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank"),
        "Team": st.column_config.TextColumn("Team"),
        "P": st.column_config.NumberColumn("P"),
        "W": st.column_config.NumberColumn("W"),
        "L": st.column_config.NumberColumn("L"),
        "NR": st.column_config.NumberColumn("NR"),
        "Pts": st.column_config.NumberColumn("Pts"),
        "Win %": st.column_config.NumberColumn("Win %"),
        "Search": st.column_config.LinkColumn(
            "Search",
            display_text="Open",  # hides the ugly URL
            help="Open Google search in a new tab",
        ),
    },
)
