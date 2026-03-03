import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Retouren Intelligence", layout="wide")
st.title("🚀 Retouren Intelligence")
st.markdown("**Upload deine Retouren-Datei → automatischer Report**")

uploaded_file = st.file_uploader("Excel oder CSV hochladen", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = [str(col).strip() for col in df.columns]
    st.success(f"✅ {len(df)} Zeilen geladen! Gefundene Spalten: {list(df.columns)}")

    # === SPALTEN-MAPPING (das ist der neue Teil) ===
    st.subheader("Spalten zuordnen")
    col1, col2 = st.columns(2)
    with col1:
        ret_col = st.selectbox("Spalte mit Retouren-Anzahl", options=df.columns, index=0)
        cat_col = st.selectbox("Spalte mit Kategorie", options=df.columns, index=0)
    with col2:
        reason_col = st.selectbox("Spalte mit Retourengrund", options=df.columns, index=0)
        name_col = st.selectbox("Spalte mit Artikelname", options=df.columns, index=0)

    # Berechnungen
    df[ret_col] = pd.to_numeric(df[ret_col], errors='coerce').fillna(0)

    total_ret = int(df[ret_col].sum())
    ret_quote = (total_ret / len(df) * 100) if len(df) > 0 else 0

    colA, colB, colC, colD = st.columns(4)
    with colA: st.metric("Retourenquote", f"{ret_quote:.1f}%")
    with colB: st.metric("Gesamt Retouren", total_ret)
    with colC: st.metric("Betroffene Artikel", df[name_col].nunique())
    with colD: st.metric("Durchschnittsrating", "—")

    # Charts
    st.subheader("Top 10 Retourengründe")
    fig1 = px.bar(df.groupby(reason_col)[ret_col].sum().nlargest(10).reset_index(), 
                  x=reason_col, y=ret_col, title="Top 10 Gründe")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Retouren nach Kategorie")
    fig2 = px.pie(df, names=cat_col, values=ret_col, title="Verteilung nach Kategorie")
    st.plotly_chart(fig2, use_container_width=True)

    # Handlungsempfehlungen (bleiben generisch)
    st.subheader("🎯 Handlungsempfehlungen")
    top_reason = df[reason_col].value_counts().idxmax()
    st.info(f"**Häufigster Grund:** {top_reason} → Hier solltest du als Erstes ansetzen (Montage, Akku, Verpackung etc.).")

    # PDF Export
    if st.button("📄 Report als PDF herunterladen"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Retouren Intelligence Report – {datetime.now().strftime('%d.%m.%Y')}", ln=1)
        pdf.cell(200, 10, txt=f"Retourenquote: {ret_quote:.1f}%", ln=1)
        pdf.output("report.pdf")
        with open("report.pdf", "rb") as f:
            st.download_button("PDF herunterladen", f, file_name="Retouren_Report.pdf")

    st.caption("✅ Funktioniert jetzt mit deinen Original-Dateien")
