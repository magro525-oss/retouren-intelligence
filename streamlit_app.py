import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Retouren Intelligence", layout="wide")
st.title("🚀 Retouren Intelligence")
st.markdown("**Upload deine Retouren-Datei → automatischer Report**")

uploaded_file = st.file_uploader("Excel oder CSV hochladen", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    df.columns = [str(col).strip() for col in df.columns]

    st.success(f"✅ {len(df)} Zeilen geladen!")

    # === SPEZIELL FÜR DEINE DATEI ===
    ret_col = 'Retouren' if 'Retouren' in df.columns else df.columns[0]
    cat_col = 'Kategorie' if 'Kategorie' in df.columns else df.columns[0]
    name_col = 'Artikelbezeichnung' if 'Artikelbezeichnung' in df.columns else df.columns[0]

    df[ret_col] = pd.to_numeric(df[ret_col], errors='coerce').fillna(0)

    # Reason-Spalten (Pivot-Format)
    reason_cols = [col for col in df.columns if col in [
        'Abbildung', 'Artikel gefällt nicht', 'Artikel passt nicht', 
        'Lieferung / Bestellung', 'kein Retourengrund', 'Qualität', 'Sonstiges'
    ]]

    # KPIs
    total_ret = int(df[ret_col].sum())
    ret_quote = (total_ret / len(df) * 100) if len(df) > 0 else 0

    colA, colB, colC = st.columns(3)
    with colA: st.metric("Retourenquote", f"{ret_quote:.1f}%")
    with colB: st.metric("Gesamt Retouren", total_ret)
    with colC: st.metric("Betroffene Artikel", df[name_col].nunique())

    # Charts
    if reason_cols:
        st.subheader("Top 10 Retourengründe")
        reason_sums = df[reason_cols].sum().sort_values(ascending=False).head(10)
        fig1 = px.bar(x=reason_sums.index, y=reason_sums.values, title="Top 10 Gründe")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Retouren nach Kategorie")
        fig2 = px.pie(df, names=cat_col, values=ret_col, title="Verteilung nach Kategorie")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🎯 Handlungsempfehlungen")
    if reason_cols:
        top_reason = df[reason_cols].sum().idxmax()
        st.info(f"**Häufigster Grund:** {top_reason} → Hier solltest du zuerst ansetzen.")

    # Excel-Download
    if st.button("📊 Report als Excel herunterladen"):
        output = pd.ExcelWriter("Retouren_Report.xlsx", engine="openpyxl")
        df.to_excel(output, sheet_name="Rohdaten", index=False)
        df[reason_cols].sum().to_frame(name="Anzahl").to_excel(output, sheet_name="Top_Gründe")
        output.close()
        with open("Retouren_Report.xlsx", "rb") as f:
            st.download_button("Excel herunterladen", f, file_name=f"Retouren_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")

    st.caption("✅ Endgültig stabil mit deiner Pivot-Datei")
