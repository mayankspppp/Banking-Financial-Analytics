CUSTOM_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(ellipse at 9% 0%, rgba(86, 214, 190, 0.075), transparent 34%),
            #0B1119;
    }
    [data-testid="stHeader"] {
        background: rgba(11, 17, 25, 0.82);
    }
    [data-testid="stSidebar"] {
        background: #0E1722;
        border-right: 1px solid rgba(147, 164, 184, 0.14);
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #121E2B, #0E1722);
        border: 1px solid rgba(147, 164, 184, 0.16);
        border-radius: 14px;
        padding: 17px 18px 15px;
        min-height: 128px;
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.16);
    }
    [data-testid="stMetricLabel"] p {
        color: #A8B6C7;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.015em;
    }
    [data-testid="stMetricValue"] {
        color: #E8EEF6;
        font-size: clamp(1.05rem, 1.6vw, 1.5rem) !important;
        line-height: 1.25;
        font-variant-numeric: tabular-nums;
        overflow-wrap: anywhere;
        white-space: normal;
    }
    h1, h2, h3 {
        letter-spacing: -0.025em;
    }
    h1 {
        font-size: clamp(1.8rem, 3vw, 2.45rem) !important;
    }
    [data-testid="stSubheader"] {
        margin-top: 1.15rem;
    }
    .dashboard-subtitle {
        color: #93A4B8;
        margin-top: -0.65rem;
        margin-bottom: 1.4rem;
    }
    .section-eyebrow {
        color: #56D6BE;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    div[data-testid="stDownloadButton"] button {
        border: 1px solid rgba(86, 214, 190, 0.36);
        background: rgba(86, 214, 190, 0.08);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(147, 164, 184, 0.16);
        border-radius: 12px;
        overflow: hidden;
    }
    @media (max-width: 900px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
            gap: 0.85rem;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 320px !important;
            min-width: min(100%, 320px) !important;
        }
    }
    @media (max-width: 560px) {
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        [data-testid="stMetric"] {
            min-height: 112px;
        }
        [data-testid="stMetricValue"] {
            font-size: clamp(1rem, 5vw, 1.35rem) !important;
        }
    }
</style>
"""
