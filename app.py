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
    max_value=int(df["Prijs"].max()),
    value=50
)

# Aantal musea
aantal_musea = st.selectbox(
    "🏛️ Hoeveel musea wil je combineren?",
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
)

# Facilities voorkeur
min_facilities = st.slider(
    "♿ Minimale faciliteiten-score",
    min_value=float(df["FACILITIES RATING"].min()),
    max_value=float(df["FACILITIES RATING"].max()),
    value=float(df["FACILITIES RATING"].mean())
)

# =====================
# Thema selectie (checkboxes)
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
gekozen_themas = [thema for thema in themas if st.checkbox(thema)]

# =====================
# Filteren
# =====================
filtered_df = df[
    (df["Provincie"] == gekozen_provincie) &
    (df["Prijs"] <= max_budget) &
    (df["FACILITIES RATING"] >= min_facilities)
]

# Filter op thema's met score 1
if gekozen_themas:
    # Maak een boolean mask voor elk gekozen thema en combineer met OR
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
