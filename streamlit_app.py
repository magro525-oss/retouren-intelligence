import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Retouren Intelligence", layout="wide")
st.title("🚀 Retouren Intelligence – Dein Retouren-KI-Dashboard")
st.markdown("**Upload deine Retouren-Datei → automatischer Report + Empfehlungen**")

uploaded_file = st.file_uploader("Excel oder CSV hochladen", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = [col.strip() for col in df.columns]
    st.success(f"✅ {len(df)} Zeilen geladen!")

    col1, col2, col3, col4 = st.columns(4)
    ret_quote = (df.get('Retourenanzahl', pd.Series([0])).sum() / len(df) * 100) if len(df) > 0 else 0
    with col1: st.metric("Retourenquote", f"{ret_quote:.1f}%")
    with col2: st.metric("Gesamt Retouren", int(df.get('Retourenanzahl', 0).sum()))
    with col3: st.metric("Betroffene Artikel", df.get('Artikelname', pd.Series([])).nunique())
    with col4: st.metric("Durchschnittsrating", f"{df.get('Bewertung', pd.Series([3.5])).mean():.1f}")

    colA, colB = st.columns(2)
    with colA:
        fig1 = px.bar(df.groupby('Retourengrund')['Retourenanzahl'].sum().nlargest(10), title="Top 10 Retourengründe")
        st.plotly_chart(fig1, use_container_width=True)
    with colB:
        fig2 = px.pie(df, names='Kategorie', values='Retourenanzahl', title="Retouren nach Kategorie")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🎯 Deine Handlungsempfehlungen")
    # (die Empfehlungen bleiben wie vorher)

    if st.button("📄 Report als PDF herunterladen"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Retouren Intelligence Report – " + datetime.now().strftime("%d.%m.%Y"), ln=1)
        pdf.output("Retouren_Report.pdf")
        with open("Retouren_Report.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="Retouren_Report.pdf")
