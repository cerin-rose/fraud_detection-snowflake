import streamlit as st
import pandas as pd
import snowflake.connector
from datetime import datetime, timedelta

# ---------------------------
# 🔐 SNOWFLAKE CONFIG
# ---------------------------
# Fill these with your actual values.
SNOWFLAKE_USER = "YOUR_USERNAME"
SNOWFLAKE_PASSWORD = "YOUR_PASSWORD"
SNOWFLAKE_ACCOUNT = "YOUR_ACCOUNT"      # e.g. "abcde-xy12345"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "FRAUDLAB"
SNOWFLAKE_SCHEMA_ANALYTICS = "ANALYTICS"

# ---------------------------
# 🎨 STREAMLIT PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    layout="wide"
)

st.title("🕵️‍♀️ Credit Card Fraud Detection – Snowflake Dashboard")
st.caption("Built on top of FRAUDLAB · RAW → STREAM → RULE ENGINE → RULE_HITS")


# ---------------------------
# 🔌 SNOWFLAKE CONNECTION
# ---------------------------
@st.cache_resource(show_spinner=False)
def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA_ANALYTICS,
    )
    return conn


@st.cache_data(ttl=60, show_spinner=False)
def run_query(query, params=None):
    conn = get_snowflake_connection()
    with conn.cursor() as cur:
        cur.execute(query, params or {})
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    return df


# ---------------------------
# 🧊 SIDEBAR FILTERS / ACTIONS
# ---------------------------
st.sidebar.header("Controls")

# Date filter for hits (last N days)
days_back = st.sidebar.slider(
    "Show fraud hits from last N days",
    min_value=1, max_value=90, value=7
)
start_date = datetime.utcnow() - timedelta(days=days_back)

refresh = st.sidebar.button("🔄 Refresh data")

st.sidebar.markdown("---")
st.sidebar.markdown("**Connection Info**")
st.sidebar.code(
    f"DB: {SNOWFLAKE_DATABASE}\nSCHEMA: {SNOWFLAKE_SCHEMA_ANALYTICS}",
    language="bash"
)


# ---------------------------
# 📊 TOP METRICS
# ---------------------------
st.subheader("Overview")

# Total fraud hits
total_hits_df = run_query("""
    SELECT COUNT(*) AS TOTAL_HITS
    FROM ANALYTICS.RULE_HITS
""")

# Hits in last N days
recent_hits_df = run_query("""
    SELECT COUNT(*) AS RECENT_HITS
    FROM ANALYTICS.RULE_HITS
    WHERE EVENT_TS >= :start_ts
""", {"start_ts": start_date})

total_hits = int(total_hits_df["TOTAL_HITS"].iloc[0]) if not total_hits_df.empty else 0
recent_hits = int(recent_hits_df["RECENT_HITS"].iloc[0]) if not recent_hits_df.empty else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Fraud Hits (All Time)", f"{total_hits:,}")
with col2:
    st.metric(f"Fraud Hits (Last {days_back} days)", f"{recent_hits:,}")


# ---------------------------
# 📌 HITS BY RULE
# ---------------------------
st.subheader("Rule Performance – Which rules are firing?")

rules_df = run_query("""
    SELECT 
        h.RULE_ID,
        COALESCE(r.RULE_NAME, 'Unknown Rule') AS RULE_NAME,
        COALESCE(r.DESCRIPTION, '') AS DESCRIPTION,
        COUNT(*) AS HIT_COUNT,
        MIN(h.EVENT_TS) AS FIRST_SEEN,
        MAX(h.EVENT_TS) AS LAST_SEEN
    FROM ANALYTICS.RULE_HITS h
    LEFT JOIN ANALYTICS.FRAUD_RULES r
        ON h.RULE_ID = r.RULE_ID
    GROUP BY h.RULE_ID, r.RULE_NAME, r.DESCRIPTION
    ORDER BY HIT_COUNT DESC
""")

if rules_df.empty:
    st.info("No fraud hits found yet. Run your pipeline in Snowflake to generate data.")
else:
    # Show table
    st.dataframe(rules_df, use_container_width=True)

    # Simple bar chart
    chart_df = rules_df[["RULE_NAME", "HIT_COUNT"]].set_index("RULE_NAME")
    st.bar_chart(chart_df)


# ---------------------------
# 📅 HITS OVER TIME
# ---------------------------
st.subheader("Fraud Hits Over Time")

hits_over_time_df = run_query("""
    SELECT 
        DATE_TRUNC('day', EVENT_TS) AS DAY,
        COUNT(*) AS HIT_COUNT
    FROM ANALYTICS.RULE_HITS
    GROUP BY DAY
    ORDER BY DAY
""")

if not hits_over_time_df.empty:
    hits_over_time_df["DAY"] = pd.to_datetime(hits_over_time_df["DAY"])
    hits_over_time_df = hits_over_time_df.set_index("DAY")
    st.line_chart(hits_over_time_df["HIT_COUNT"])
else:
    st.info("No time series data yet – need some RULE_HITS first.")


# ---------------------------
# 🔍 LATEST FRAUD HITS
# ---------------------------
st.subheader("Latest Fraud Hits (Most Recent First)")

latest_hits_df = run_query("""
    SELECT 
        h.EVENT_TS,
        h.RULE_ID,
        COALESCE(r.RULE_NAME, 'Unknown Rule') AS RULE_NAME,
        h.ROW_ID,
        h.TXN_AMOUNT,
        h.CARD_ID,
        h.MERCHANT_ID,
        h.COUNTRY,
        h.CHANNEL
    FROM ANALYTICS.RULE_HITS h
    LEFT JOIN ANALYTICS.FRAUD_RULES r
        ON h.RULE_ID = r.RULE_ID
    WHERE h.EVENT_TS >= :start_ts
    ORDER BY h.EVENT_TS DESC
    LIMIT 200
""", {"start_ts": start_date})

if latest_hits_df.empty:
    st.info(f"No fraud hits in the last {days_back} days.")
else:
    # Optional dropdown filter by rule
    rule_filter = st.selectbox(
        "Filter by rule (optional)",
        options=["All"] + sorted(latest_hits_df["RULE_NAME"].unique().tolist())
    )

    if rule_filter != "All":
        filtered_hits_df = latest_hits_df[latest_hits_df["RULE_NAME"] == rule_filter]
    else:
        filtered_hits_df = latest_hits_df

    st.dataframe(filtered_hits_df, use_container_width=True)


# ---------------------------
# 🧪 PIPELINE DIAGNOSTICS (Optional)
# ---------------------------
st.subheader("Pipeline Diagnostics (Optional)")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Stream Status (RAW.CREDITCARD_TXNS_STREAM)**")
    try:
        stream_df = run_query("""
            SHOW STREAMS IN SCHEMA RAW;
        """)
        st.dataframe(stream_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching stream info: {e}")

with col_b:
    st.markdown("**Recent Task History (if you added a TASK)**")
    try:
        task_history_df = run_query("""
            SELECT *
            FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
                RESULT_LIMIT => 20
            ));
        """)
        if task_history_df.empty:
            st.write("No task history found. Maybe no tasks defined yet.")
        else:
            st.dataframe(task_history_df, use_container_width=True)
    except Exception as e:
        st.info("No tasks configured or no permission to view task history.")


st.markdown("---")
st.caption("End-to-end fraud detection demo • Snowflake + Streamlit")
