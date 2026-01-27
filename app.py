import pandas as pd
import streamlit as st
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
# Styling (table + UI)
# ----------------------------
st.markdown(
    """
    <style>
      /* Make the page breathe */
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }

      /* Title */
      .title-wrap h1 { margin-bottom: 0.2rem; }
      .subtitle { opacity: 0.75; margin-top: 0.2rem; }

      /* KPI cards */
      .kpi-row { display: flex; gap: 16px; margin: 14px 0 18px 0; }
      .kpi {
        flex: 1;
        padding: 18px 18px;
        border-radius: 16px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
      }
      .kpi-label { font-size: 12px; opacity: 0.75; margin-bottom: 6px; }
      .kpi-value { font-size: 30px; font-weight: 700; }

      /* Table container */
      .table-wrap {
        border-radius: 18px;
        padding: 14px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        overflow-x: auto;
      }

      /* Table styling */
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
      }
      thead th {
        text-align: left;
        padding: 12px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.15);
        opacity: 0.85;
        white-space: nowrap;
      }
      tbody td {
        padding: 12px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        white-space: nowrap;
      }
      tbody tr:hover {
        background: rgba(255,255,255,0.06);
      }

      /* Team links */
      a.team-link {
        color: inherit;
        text-decoration: none;
        font-weight: 600;
      }
      a.team-link:hover {
        text-decoration: underline;
      }

      /* Rank left-align (explicit) */
      td.col-rank, th.col-rank { text-align: left !important; width: 60px; }
      
      /* Team left-align (explicit) */
      td.col-rank, th.col-rank { text-align: left ! }

      /* Points centre-align */
      td.col-pts, th.col-pts { text-align: center !important; width: 80px; }

      /* Number columns slightly right */
      td.num { text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Data loading
# ----------------------------
@st.cache_data
def load_points_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Clean column names if needed
    df.columns = [c.strip() for c in df.columns]
    return df

# Change this if your file name differs
DATA_FILE = "ipl_points_table.csv"

try:
    df_all = load_points_table(DATA_FILE)
except Exception as e:
    st.error(f"Could not read {DATA_FILE}. Make sure it is in the same folder as app.py.\n\nError: {e}")
    st.stop()

# ----------------------------
# Header
# ----------------------------
st.markdown('<div class="title-wrap"><h1>🏏 IPL Points Table</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Pick a season. Click a team name to open a Google search in a new tab.</div>', unsafe_allow_html=True)

# ----------------------------
# Season selector
# ----------------------------
if "season" not in df_all.columns:
    st.error("Your CSV must have a 'season' column.")
    st.stop()

seasons = list(pd.Series(df_all["season"].dropna().unique()).sort_values())
season = st.selectbox("Season", seasons, index=len(seasons) - 1)

df_season = df_all[df_all["season"] == season].copy()

# ----------------------------
# Basic validation for expected columns
# ----------------------------
required = {"team", "matches_played", "wins", "losses", "no_result", "points", "win_pct"}
missing = required - set(df_season.columns)
if missing:
    st.error(f"Missing columns in your CSV for this app: {sorted(list(missing))}")
    st.stop()

# Ensure a clean rank based on current ordering (or sort if you prefer)
# If your CSV is already correctly sorted, keep as-is.
# Otherwise you can uncomment sorting below:
# df_season = df_season.sort_values(["points", "win_pct"], ascending=[False, False]).reset_index(drop=True)

df_season = df_season.reset_index(drop=True)
df_season["rank"] = df_season.index + 1

# KPIs
teams_count = df_season["team"].nunique()
max_points = int(df_season["points"].max())
top_win = float(df_season["win_pct"].max())
top_win_str = f"{top_win:.1f}"

st.markdown(
    f"""
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-label">Teams</div>
        <div class="kpi-value">{teams_count}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Max Points</div>
        <div class="kpi-value">{max_points}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Top Win %</div>
        <div class="kpi-value">{top_win_str}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Build clickable Team (NO extra column)
# ----------------------------
def team_anchor(team: str) -> str:
    q = quote_plus(f"{team} IPL team")
    url = f"https://www.google.com/search?q={q}"
    return f'<a class="team-link" href="{url}" target="_blank" rel="noopener noreferrer">{team}</a>'

df_display = pd.DataFrame({
    "Rank": df_season["rank"],
    "Team": df_season["team"].astype(str).apply(team_anchor),
    "P": df_season["matches_played"],
    "W": df_season["wins"],
    "L": df_season["losses"],
    "NR": df_season["no_result"],
    "Pts": df_season["points"],
    "Win %": df_season["win_pct"].round(1),
})

# Convert to HTML and inject per-column classes for alignment control
html_table = df_display.to_html(index=False, escape=False)

# Add classes to Rank and Pts columns (both header + cells)
# This is a simple string replace approach for stable column order.
html_table = html_table.replace("<th>Rank</th>", '<th class="col-rank">Rank</th>')
html_table = html_table.replace("<th>Pts</th>", '<th class="col-pts">Pts</th>')

# Add classes to first column (Rank) and Pts column by targeting <td> positions
# Rank is col 1, Pts is col 7 in our df_display
def add_td_classes(table_html: str) -> str:
    out = []
    in_row = False
    td_index = 0
    for part in table_html.split("<td"):
        if not in_row:
            # before the first <td of the document
            out.append(part)
            in_row = True
            continue
        # Each split chunk starts at after "<td"
        # We need to know which td number we are in within a row. Reset after </tr>.
        chunk = "<td" + part
        # Reset on new row boundary
        if "</tr>" in out[-1]:
            td_index = 0

        td_index += 1
        if td_index == 1:
            chunk = chunk.replace("<td>", '<td class="col-rank">', 1)
        elif td_index == 7:
            chunk = chunk.replace("<td>", '<td class="col-pts">', 1)
        else:
            # numeric columns (P,W,L,NR,Win%) right align for readability
            # Team stays default because it's a link
            if td_index in (3,4,5,6,8):
                chunk = chunk.replace("<td>", '<td class="num">', 1)

        out.append(chunk)
    return "".join(out)

html_table = add_td_classes(html_table)

st.markdown(f"<h2>Points Table for {season}</h2>", unsafe_allow_html=True)
st.markdown(f'<div class="table-wrap">{html_table}</div>', unsafe_allow_html=True)
