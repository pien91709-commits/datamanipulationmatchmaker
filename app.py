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
    value=20
)

# Aantal musea
aantal_musea = st.selectbox(
    "🏛️ Hoeveel musea wil je combineren?",
    [1, 2, 3]
)

# Theme voorkeur
min_theme = st.slider(
    "🎨 Minimale thema-score",
    min_value=float(df["THEME RATING"].min()),
    max_value=float(df["THEME RATING"].max()),
    value=float(df["THEME RATING"].mean())
)

# Facilities voorkeur
min_facilities = st.slider(
    "♿ Minimale faciliteiten-score",
    min_value=float(df["FACILITIES RATING"].min()),
    max_value=float(df["FACILITIES RATING"].max()),
    value=float(df["FACILITIES RATING"].mean())
)

# =====================
# Filteren
# =====================
filtered_df = df[
    (df["Provincie"] == gekozen_provincie) &
    (df["Prijs"] <= max_budget) &
    (df["THEME RATING"] >= min_theme) &
    (df["FACILITIES RATING"] >= min_facilities)
].dropna(subset=["WEIGHTED RATING"])

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
