import streamlit as st
import pandas as pd
import re
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="CloudOps AI",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ CloudOps AI")
st.subheader("Intelligent Cloud Log Analyzer")
st.write("AI-powered server log monitoring and troubleshooting.")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.info("Upload your server log file to begin analysis.")

uploaded_file = st.file_uploader(
    "Upload Server Log File",
    type=["log", "txt"]
)

def classify_error(line):
    text = line.lower()

    if any(word in text for word in
           ["critical", "fatal", "emergency"]):
        return "Critical"

    elif any(word in text for word in
             ["error", "exception", "failed"]):
        return "High"

    elif any(word in text for word in
             ["warning", "warn"]):
        return "Medium"

    return "Low"


def analyze_logs(logs):
    results = []

    for line in logs:
        if line.strip():
            results.append({
                "Log Message": line.strip(),
                "Severity": classify_error(line)
            })

    return pd.DataFrame(results)


if uploaded_file is not None:

    content = uploaded_file.getvalue().decode(
        "utf-8", errors="replace"
    )

    logs = content.splitlines()
    df = analyze_logs(logs)

    st.success("Log file uploaded successfully!")

    # Dashboard metrics
    total = len(df)
    critical = len(df[df["Severity"] == "Critical"])
    high = len(df[df["Severity"] == "High"])
    medium = len(df[df["Severity"] == "Medium"])

    st.header("📊 Monitoring Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Logs", total)
    c2.metric("Critical Errors", critical)
    c3.metric("High Errors", high)
    c4.metric("Warnings", medium)

    st.divider()

    st.header("🔍 Log Analysis")

    st.dataframe(df, use_container_width=True)

    st.header("📈 Error Statistics")

    st.bar_chart(df["Severity"].value_counts())

    st.divider()

    st.header("🤖 AI Troubleshooting Assistant")

    if st.button("Analyze Logs with AI"):

        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            try:
                client = OpenAI(api_key=api_key)

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a cloud troubleshooting "
                                "assistant. Explain log errors, "
                                "possible causes, severity and "
                                "safe troubleshooting steps. "
                                "Do not claim certainty without evidence."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                "Analyze these server logs:\n"
                                + "\n".join(logs[:100])
                            )
                        }
                    ]
                )

                st.markdown(
                    response.choices[0].message.content
                )

            except Exception as e:
                st.error(f"AI analysis failed: {e}")

        else:
            st.warning(
                "OpenAI API key not configured. "
                "Showing basic local analysis instead."
            )

            st.write(
                "Total log entries:", total
            )
            st.write(
                "Critical errors:", critical
            )
            st.write(
                "High severity errors:", high
            )

            st.write(
                "Suggested action: Inspect the error "
                "messages and investigate the affected service."
            )

    # Download report
    st.divider()

    report = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Log Analysis Report",
        data=report,
        file_name="cloudops_report.csv",
        mime="text/csv"
    )

else:
    st.info(
        "Please upload a .log or .txt file to start analysis."
    )

    st.write("Your dashboard will appear after uploading logs.")