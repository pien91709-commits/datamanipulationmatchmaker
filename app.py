import streamlit as st
import pandas as pd
import openpyxl

# =====================
# Data laden
# =====================
bestandspad = "Kopie van data manipulation .xlsx"
df = pd.read_excel(bestandspad, sheet_name="Matchmaker")
df["THEME RATING"] = pd.to_numeric(df["THEME RATING"], errors="coerce")
df["FACILITIES RATING"] = pd.to_numeric(df["FACILITIES RATING"], errors="coerce")

st.title("🎯 Museum Matchmaker")

# =====================
# Interactie
# =====================

# Provincie
provincies = sorted(df["Provincie"].dropna().unique())
gekozen_provincie = st.selectbox("📍 Kies een provincie", provincies)

# Budget
max_budget = st.slider(
    "💰 Wat is je maximale budget (€)?",
    min_value=0,
    max_value=40,  # aangepast van max(df["Prijs"].max()) naar 40
    value=20
)

# Aantal musea
aantal_musea = st.selectbox(
    "🏛️ Hoeveel musea wil je combineren?",
    list(range(1, 16))  # 1 t/m 15 musea
)

# Facilities voorkeur
min_facilities = st.slider(
    "♿ Minimale faciliteiten-score",
    min_value=float(df["FACILITIES RATING"].min()),
    max_value=float(df["FACILITIES RATING"].max()),
    value=float(df["FACILITIES RATING"].mean())
)

# =====================
# Thema selectie (checkboxes in 2 kolommen)
# =====================
themas = [
    "Geschiedenis en archeologie",
    "Wetenschap en technologie",
    "Mode",
    "Literatuur",
    "Architectuur",
    "Beeldende kunst",
    "Toegepaste kunst en design"
]

st.subheader("✨ Selecteer je favoriete thema's")

# 2 kolommen
col1, col2 = st.columns(2)
gekozen_themas = []
for i, thema in enumerate(themas):
    if i % 2 == 0:
        if col1.checkbox(thema):
            gekozen_themas.append(thema)
    else:
        if col2.checkbox(thema):
            gekozen_themas.append(thema)

# =====================
# Filteren
# =====================
filtered_df = df[
    (df["Provincie"] == gekozen_provincie) &
    (df["Prijs"] <= max_budget) &
    (df["FACILITIES RATING"] >= min_facilities)
]

# Filter op thema's met score 1 (alleen als er minimaal één thema is gekozen)
if gekozen_themas:
    mask = pd.Series([False] * len(filtered_df))
    for thema in gekozen_themas:
        if thema in filtered_df.columns:
            mask = mask | (filtered_df[thema] == 1)
        else:
            st.warning(f"Let op: kolom voor thema '{thema}' bestaat niet in de data.")
    filtered_df = filtered_df[mask]

# Drop rows zonder gewicht
filtered_df = filtered_df.dropna(subset=["WEIGHTED RATING"])

# =====================
# Match maken
# =====================
if st.button("✨ Maak match"):
    if len(filtered_df) < aantal_musea:
        st.warning("Niet genoeg musea binnen deze criteria.")
    else:
        match = (
            filtered_df
            .sort_values("WEIGHTED RATING", ascending=False)
            .head(aantal_musea)
        )

        totaalprijs = match["Prijs"].sum()

        st.subheader("🏆 Jouw match")
        st.dataframe(
            match[[
                "Musea - Nederlandse benaming (Title)",
                "Provincie",
                "Prijs",
                "THEME RATING",
                "FACILITIES RATING",
                "WEIGHTED RATING"
            ]]
        )

        st.success(f"💰 Totale prijs: €{totaalprijs:.2f}")

