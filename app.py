# app.py
import os
import pandas as pd
import streamlit as st
from urllib.parse import quote_plus

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="IPL Points Table",
    page_icon="🏏",
    layout="wide",
)

# -----------------------------
# CSS (look & feel)
# -----------------------------
st.markdown(
    """
    <style>
      /* Background & overall */
      .stApp {
        background: radial-gradient(1200px 600px at 10% 10%, #1b1f2a 0%, #0b0f17 55%, #070a10 100%);
        color: #e8eefc;
      }

      /* Title spacing */
      .block-container { padding-top: 2rem; }

      /* Remove extra whitespace */
      header { visibility: hidden; height: 0; }
      footer { visibility: hidden; height: 0; }

      /* Labels */
      label, .stMarkdown, .stText { color: #e8eefc !important; }

      /* Metric cards */
      div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 14px 14px;
      }

      /* Table container look */
      div[data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 8px;
      }

      /* Links inside table */
      a {
        color: #79b8ff !important;
        text-decoration: none !important;
        font-weight: 600;
      }
      a:hover { text-decoration: underline !important; }

      /* Make selectbox nicer */
      div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def google_search_url(team_name: str) -> str:
    q = quote_plus(f"{team_name} IPL team")
    return f"https://www.google.com/search?q={q}"

@st.cache_data
def load_points_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalise column names (just in case)
    df.columns = [c.strip() for c in df.columns]
    return df

# -----------------------------
# Load data
# -----------------------------
DATA_FILE = "ipl_points_table.csv"

if not os.path.exists(DATA_FILE):
    st.error(
        f"File not found: **{DATA_FILE}**\n\n"
        "Keep `app.py` and `ipl_points_table.csv` in the **same folder**."
    )
    st.stop()

pt = load_points_table(DATA_FILE)

required_cols = {"season", "team", "matches_played", "wins", "losses", "no_result", "points", "win_pct"}
missing = required_cols - set(pt.columns)

if missing:
    st.error(f"Your CSV is missing these required columns: {sorted(list(missing))}")
    st.stop()

# -----------------------------
# Header
# -----------------------------
st.markdown("## 🏏 IPL Points Table")
st.caption("Pick a season. Click a team to open a Google search in a new tab.")

# Season selector (sorted, newest first where possible)
seasons = sorted(pt["season"].dropna().unique(), reverse=True)
default_season = seasons[0] if seasons else None

season = st.selectbox("Season", seasons, index=0)

# -----------------------------
# Filter + compute view
# -----------------------------
pt_season = pt[pt["season"] == season].copy()

# Rank (1..n), sort by points desc then win_pct desc
pt_season = pt_season.sort_values(by=["points", "win_pct"], ascending=[False, False]).reset_index(drop=True)
pt_season.insert(0, "rank", range(1, len(pt_season) + 1))

# Make team clickable: keep display name, but also add link column for Streamlit
pt_season["team_search_link"] = pt_season["team"].apply(google_search_url)

# -----------------------------
# Top metrics (visual, no graphs)
# -----------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Teams", f"{pt_season['team'].nunique()}")
with col2:
    st.metric("Max Points", f"{int(pt_season['points'].max())}")
with col3:
    st.metric("Top Win %", f"{pt_season['win_pct'].max():.1f}")

st.markdown("---")
st.markdown(f"### Points Table for {season}")

# -----------------------------
# Display table
# -----------------------------
cols_to_show = ["rank", "team", "matches_played", "wins", "losses", "no_result", "points", "win_pct", "team_search_link"]
display_df = pt_season[cols_to_show].copy()

# Round win_pct if needed
display_df["win_pct"] = display_df["win_pct"].round(1)

# Styling: rank left, points centre
styler = (
    display_df.style
    .set_properties(subset=["rank"], **{"text-align": "left"})
    .set_properties(subset=["team"], **{"text-align": "left"})
    .set_properties(subset=["points"], **{"text-align": "center"})
    .set_properties(subset=["matches_played", "wins", "losses", "no_result", "win_pct"], **{"text-align": "right"})
)

# Rename link column header to be hidden-ish
display_df = display_df.rename(columns={"team_search_link": "Search"})

st.dataframe(
    styler,
    use_container_width=True,
    hide_index=True,
    column_config={
        "team": st.column_config.TextColumn("Team"),
        "Search": st.column_config.LinkColumn(
            "Search",
            help="Opens Google search in a new tab",
            display_text="Open",
        ),
        "rank": st.column_config.NumberColumn("Rank"),
        "matches_played": st.column_config.NumberColumn("P"),
        "wins": st.column_config.NumberColumn("W"),
        "losses": st.column_config.NumberColumn("L"),
        "no_result": st.column_config.NumberColumn("NR"),
        "points": st.column_config.NumberColumn("Pts"),
        "win_pct": st.column_config.NumberColumn("Win %"),
    },
)

st.caption("Tip: Click **Open** in the Search column to jump to Google for that team.")
