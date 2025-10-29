# dashboards/streamlit_app.py
# Run with:
#   streamlit run dashboards/streamlit_app.py

from __future__ import annotations
import os
import subprocess
from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------- Page config ----------
st.set_page_config(page_title="Job Skills Demand Monitor", layout="wide")

DEFAULT_CSV = os.getenv("OUTPUT_CSV", "data/jobs.csv")

# ---------- Helpers ----------
@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        return pd.DataFrame(
            columns=[
                "source",
                "title",
                "company",
                "location",
                "posted_at",
                "url",
                "skills",
                "fetched_at",
            ]
        )
    df = pd.read_csv(csv_path)
    # Coerce timestamps (UTC) and clean strings
    for col in ("posted_at", "fetched_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    for c in ("source", "title", "company", "location", "url", "skills"):
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)
    return df


def explode_skills(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "skills" not in df.columns:
        return df.assign(skill=[]).iloc[0:0]
    tmp = df.copy()
    tmp["skills"] = tmp["skills"].fillna("")
    tmp = tmp.assign(skill=tmp["skills"].str.split(",")).explode("skill")
    tmp["skill"] = tmp["skill"].astype(str).str.strip()
    tmp = tmp[tmp["skill"] != ""]
    return tmp


def filter_df(
    df: pd.DataFrame,
    date_range: Tuple[pd.Timestamp, pd.Timestamp] | None,
    sources: List[str] | None,
    companies: List[str] | None,
    skills: List[str] | None,
) -> pd.DataFrame:
    out = df.copy()
    time_col = (
        "fetched_at"
        if "fetched_at" in out.columns
        else ("posted_at" if "posted_at" in out.columns else None)
    )
    if time_col and date_range:
        start, end = date_range
        out = out[(out[time_col] >= start) & (out[time_col] <= end)]

    if sources:
        out = out[out["source"].str.lower().isin([s.lower() for s in sources])]
    if companies:
        out = out[out["company"].str.lower().isin([c.lower() for c in companies])]

    if skills:
        target = {s.lower() for s in skills}
        out = out[out["skills"].str.lower().apply(
            lambda x: any(tok.strip() in target for tok in x.split(","))
        )]

    return out


def run_scraper() -> tuple[bool, str]:
    """
    Attempt to run `python -m src.scraper` from repo root.
    Gracefully handle environments where subprocess is blocked.
    """
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        proc = subprocess.run(
            ["python", "-m", "src.scraper"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=180,
        )
        ok = proc.returncode == 0
        out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return ok, out.strip()
    except Exception as e:
        return False, f"Error: {e}"


def df_download_link(df: pd.DataFrame, filename: str = "filtered_jobs.csv"):
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# ---------- Sidebar ----------
st.sidebar.title("⚙️ Controls")
csv_path = st.sidebar.text_input(
    "CSV path", value=DEFAULT_CSV, help="Path to your data/jobs.csv"
)
refresh_btn = st.sidebar.button("🔄 Reload data", use_container_width=True)

with st.sidebar.expander("Run scraper (optional)"):
    st.caption("Runs `python -m src.scraper` in the repo root.")
    if st.button("🚀 Run scraper now", type="primary", use_container_width=True):
        with st.status("Running scraper...", expanded=True):
            ok, out = run_scraper()
            if ok:
                st.success("Scraper finished.")
            else:
                st.error("Scraper failed.")
            st.code(out or "(no output)")

# Load data (cache-aware)
df = load_data(csv_path) if not refresh_btn else load_data.clear() or load_data(csv_path)

# ---------- Date range (robust to single-day data) ----------
time_col = (
    "fetched_at"
    if "fetched_at" in df.columns
    else ("posted_at" if "posted_at" in df.columns else None)
)

def _to_utc_series(x):
    return pd.to_datetime(x, errors="coerce", utc=True)

if time_col and not df.empty:
    ts = _to_utc_series(df[time_col])
    if ts.notna().any():
        min_dt_utc = ts.min()
        max_dt_utc = ts.max()
        min_date = min_dt_utc.date()
        max_date = max_dt_utc.date()

        # Propose last 30 days, clamp to dataset bounds
        proposed_start = max_dt_utc.date() - timedelta(days=30)
        default_start_date = max(min_date, proposed_start)
        default_end_date = max_date

        start_date, end_date = st.sidebar.date_input(
            "Date range",
            value=(default_start_date, default_end_date),
            min_value=min_date,
            max_value=max_date,
        )

        # Build timezone-aware UTC timestamps at day bounds
        start_dt = pd.to_datetime(
            datetime.combine(start_date, datetime.min.time()), utc=True
        )
        end_dt = pd.to_datetime(
            datetime.combine(end_date, datetime.max.time()), utc=True
        )
        date_range = (start_dt, end_dt)
    else:
        date_range = None
else:
    date_range = None

# ---------- Filters ----------
sources_all = sorted([s for s in df["source"].unique() if s]) if not df.empty else []
companies_all = sorted([c for c in df["company"].unique() if c]) if not df.empty else []

sources_pick = st.sidebar.multiselect(
    "Filter by source", options=sources_all, default=sources_all[:3]
)
companies_pick = st.sidebar.multiselect("Filter by company", options=companies_all)

exploded_all = explode_skills(df)
skills_all = (
    sorted(exploded_all["skill"].unique().tolist()) if not exploded_all.empty else []
)
skills_pick = st.sidebar.multiselect("Filter by skill(s)", options=skills_all)

agg_period = st.sidebar.selectbox("Trend aggregation", options=["D (daily)", "W (weekly)"], index=0)
top_n = st.sidebar.slider("Top N skills", min_value=5, max_value=30, value=15)

# ---------- Main ----------
st.title("📈 Job Skills Demand Monitor")

if df.empty:
    st.info("No data found yet. Run the scraper, then refresh.")
    st.stop()

filtered = filter_df(df, date_range, sources_pick, companies_pick, skills_pick)
exploded = explode_skills(filtered)

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jobs (rows)", f"{len(filtered):,}")
c2.metric("Unique companies", f"{filtered['company'].nunique():,}")
c3.metric("Unique skills", f"{exploded['skill'].nunique():,}" if not exploded.empty else "0")
if date_range:
    c4.metric("Window", f"{date_range[0].date()} → {date_range[1].date()}")
else:
    c4.metric("Window", "All time")

st.divider()

# Top skills bar chart
st.subheader("Top skills in selection")
if exploded.empty:
    st.warning("No skills found in the current filter.")
else:
    top_counts = exploded["skill"].value_counts().head(top_n).sort_values()
    fig, ax = plt.subplots()
    top_counts.plot(kind="barh", ax=ax)  # default matplotlib style/colors
    ax.set_xlabel("Mentions")
    ax.set_ylabel("Skill")
    st.pyplot(fig, use_container_width=True)

st.divider()

# Trends over time
st.subheader("Skill trends over time")
if exploded.empty or not time_col:
    st.info("Need data with skills and timestamps to plot trends.")
else:
    ts = exploded[[time_col, "skill"]].copy().dropna(subset=[time_col])
    if ts.empty:
        st.info("No timestamps available to chart.")
    else:
        rule = "D" if agg_period.startswith("D") else "W"
        # Suggest popular skills (or all) for lines
        selectable = (
            top_counts.index.tolist()
            if "top_counts" in locals() and not top_counts.empty
            else skills_all
        )
        chosen_for_trend = st.multiselect(
            "Choose up to 6 skills for trend lines",
            options=selectable,
            default=selectable[:4] if selectable else [],
            max_selections=6,
        )
        if chosen_for_trend:
            fig2, ax2 = plt.subplots()
            for skill in chosen_for_trend:
                s = ts[ts["skill"] == skill].set_index(time_col).sort_index()
                s = s.resample(rule).size()
                ax2.plot(s.index, s.values, label=skill)  # default matplotlib style/colors
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Mentions")
            ax2.legend()
            st.pyplot(fig2, use_container_width=True)
        else:
            st.caption("Pick at least one skill to plot.")

st.divider()

# Table + download
st.subheader("Recent jobs (filtered)")
show_cols = [
    "source",
    "title",
    "company",
    "location",
    "posted_at",
    "url",
    "skills",
    "fetched_at",
]
show_cols = [c for c in show_cols if c in filtered.columns]

sort_col = time_col if time_col in filtered.columns else (show_cols[-1] if show_cols else None)
preview = (
    filtered.sort_values(by=[sort_col], ascending=False).head(200)
    if sort_col
    else filtered.head(200)
)

if "url" in preview.columns:
    preview = preview.copy()
    preview["link"] = preview["url"].apply(
        lambda u: "🔗" if isinstance(u, str) and u.startswith("http") else ""
    )

st.dataframe(
    preview[show_cols + (["link"] if "link" in preview.columns else [])],
    use_container_width=True,
    height=420,
)

df_download_link(filtered)

st.caption(
    "Tip: add more sources in src/sources/ and configure them via .env (LEVER_COMPANIES, GREENHOUSE_BOARDS)."
)
