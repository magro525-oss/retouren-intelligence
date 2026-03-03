import streamlit as st
import pandas as pd
import plotly.express as px
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
    st.success(f"✅ {len(df)} Zeilen geladen!")

    # Data Preview
    st.subheader("📋 Daten-Vorschau (erste 5 Zeilen)")
    st.dataframe(df.head(5))

    # Auto-Erkennung
    ret_col = next((col for col in df.columns if any(x in col for x in ['Retouren', 'Anz. R', 'RQ'])), None)
    cat_col = next((col for col in df.columns if any(x in col for x in ['Kategorie', 'Kat'])), None)
    name_col = next((col for col in df.columns if any(x in col for x in ['Artikelbezeichnung', 'Artikelname'])), None)

    st.subheader("Spalten zuordnen")
    col1, col2 = st.columns(2)
    with col1:
        ret_col = st.selectbox("Spalte mit Retouren-Anzahl", df.columns, index=list(df.columns).index(ret_col) if ret_col else 0)
        cat_col = st.selectbox("Spalte mit Kategorie", df.columns, index=list(df.columns).index(cat_col) if cat_col else 0)
    with col2:
        name_col = st.selectbox("Spalte mit Artikelname", df.columns, index=list(df.columns).index(name_col) if name_col else 0)

    df[ret_col] = pd.to_numeric(df[ret_col], errors='coerce').fillna(0)

    # === NEU: Pivot-Format erkennen und melt en ===
    reason_cols = [col for col in df.columns if col in ['Abbildung', 'Artikel gefällt nicht', 'Artikel passt nicht', 
                                                        'Lieferung / Bestellung', 'kein Retourengrund', 'Qualität', 'Sonstiges']]
    
    if reason_cols and st.button("🔄 Gründe melt en (für meine Datei – wichtig!)"):
        melted = df.melt(id_vars=[ret_col, cat_col, name_col], 
                         value_vars=reason_cols, 
                         var_name="Retourengrund", 
                         value_name="Anzahl")
        melted = melted[melted["Anzahl"] > 0]
        st.session_state["long_df"] = melted
        st.success("✅ Datei erfolgreich in lange Form umgewandelt!")

    # Charts
    long_df = st.session_state.get("long_df", None)
    if long_df is not None:
        st.subheader("Top 10 Retourengründe")
        chart_data = long_df.groupby("Retourengrund")["Anzahl"].sum().nlargest(10).reset_index()
        fig1 = px.bar(chart_data, x="Retourengrund", y="Anzahl", title="Top 10 Gründe")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Retouren nach Kategorie")
        fig2 = px.pie(long_df, names=cat_col, values="Anzahl", title="Verteilung nach Kategorie")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("👆 Klicke auf 'Gründe melt en' – dann werden die Charts gefüllt!")

    # KPIs
    total_ret = int(df[ret_col].sum())
    ret_quote = (total_ret / len(df) * 100) if len(df) > 0 else 0
    colA, colB, colC, colD = st.columns(4)
    with colA: st.metric("Retourenquote", f"{ret_quote:.1f}%")
    with colB: st.metric("Gesamt Retouren", total_ret)
    with colC: st.metric("Betroffene Artikel", df[name_col].nunique())

    st.caption("✅ Jetzt optimiert für deine Original-Dateien")
