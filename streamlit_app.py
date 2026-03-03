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

    st.success(f"✅ {len(df)} Zeilen geladen! Spalten: {list(df.columns)}")

    # KPIs (funktioniert mit deiner Datei)
    ret_col = next((col for col in df.columns if 'Retouren' in col or 'Anz. R' in col), df.columns[0])
    df[ret_col] = pd.to_numeric(df[ret_col], errors='coerce').fillna(0)

    total_ret = int(df[ret_col].sum())
    ret_quote = (total_ret / len(df) * 100) if len(df) > 0 else 0

    colA, colB, colC = st.columns(3)
    with colA: st.metric("Retourenquote", f"{ret_quote:.1f}%")
    with colB: st.metric("Gesamt Retouren", total_ret)
    with colC: st.metric("Betroffene Artikel", df['Artikelbezeichnung'].nunique() if 'Artikelbezeichnung' in df.columns else len(df))

    # Reason-Spalten für deine Pivot-Datei
    reason_cols = [col for col in df.columns if col in ['Abbildung', 'Artikel gefällt nicht', 'Artikel passt nicht', 
                                                        'Lieferung / Bestellung', 'kein Retourengrund', 'Qualität', 'Sonstiges']]

    if reason_cols:
        # Charts direkt aus Pivot (kein melt nötig)
        st.subheader("Top Retourengründe")
        reason_sums = df[reason_cols].sum().sort_values(ascending=False).head(10)
        fig1 = px.bar(x=reason_sums.index, y=reason_sums.values, title="Top 10 Gründe")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Retouren nach Kategorie")
        if 'Kategorie' in df.columns:
            fig2 = px.pie(df, names='Kategorie', values=ret_col, title="Verteilung nach Kategorie")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Kategorie-Spalte nicht gefunden – Charts für Gründe sind aber schon da.")

    st.subheader("🎯 Handlungsempfehlungen")
    if reason_cols:
        top_reason = reason_sums.idxmax()
        st.info(f"**Häufigster Grund:** {top_reason} → Hier solltest du zuerst ansetzen (z. B. bessere Anleitung, Akku-Upgrade etc.).")

    # Excel-Download (sicher)
    if st.button("📊 Report als Excel herunterladen"):
        output = pd.ExcelWriter("Retouren_Report.xlsx", engine="openpyxl")
        df.to_excel(output, sheet_name="Rohdaten", index=False)
        reason_sums.to_frame(name="Anzahl").to_excel(output, sheet_name="Top_Gründe")
        output.close()
        with open("Retouren_Report.xlsx", "rb") as f:
            st.download_button("Excel herunterladen", f, file_name=f"Retouren_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")

    st.caption("✅ Jetzt stabil mit deiner Pivot-Datei")
