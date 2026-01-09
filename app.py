import streamlit as st
import pandas as pd
from urllib.parse import quote_plus

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="IPL Points Table", page_icon="🏏", layout="wide")

# ----------------------------
# Load data
# ----------------------------
@st.cache_data
def load_points_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic cleanup (safe)
    df["season"] = df["season"].astype(str).str.strip()
    df["team"] = df["team"].astype(str).str.strip()
    return df

pt = load_points_table("ipl_points_table.csv")

# Columns to show (keep it clean)
cols_to_show = ["team", "matches_played", "wins", "losses", "no_result", "points", "win_pct"]

# ----------------------------
# Header
# ----------------------------
st.title("🏏 IPL Points Table")
st.caption("Pick a season. Use the button below to open a Google search for the selected team.")

# ----------------------------
# Season selector
# ----------------------------
seasons = sorted(pt["season"].unique(), reverse=True)
season = st.selectbox("Season", seasons, index=0)

pt_season = pt[pt["season"] == season].copy()
pt_season = pt_season.sort_values(["points", "win_pct"], ascending=[False, False]).reset_index(drop=True)

# Rank column for display
pt_season.insert(0, "rank", pt_season.index + 1)

# ----------------------------
# KPI cards (no charts)
# ----------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Teams", int(pt_season["team"].nunique()))

with c2:
    st.metric("Max Points", int(pt_season["points"].max()))

with c3:
    st.metric("Top Win %", float(pt_season["win_pct"].max()))

st.divider()

# ----------------------------
# Table (clean, no HTML)
# ----------------------------
st.subheader(f"Points Table for {season}")

display_cols = ["rank"] + cols_to_show
st.dataframe(
    pt_season[display_cols],
    use_container_width=True,
    hide_index=True
)

# ----------------------------
# Team search (interactive)
# ----------------------------
st.divider()
team_pick = st.selectbox("Open Google search for a team:", pt_season["team"].unique())

search_url = f"https://www.google.com/search?q={quote_plus(team_pick + ' IPL team')}"
st.link_button("Search this team on Google", search_url)
