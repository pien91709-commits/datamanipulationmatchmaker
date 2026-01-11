import streamlit as st
import pandas as pd
import openpyxl

bestandspad = "Kopie van data manipulation .xlsx"
df = pd.read_excel(bestandspad, sheet_name="Matchmaker")

st.title("🎯 Museum Matchmaker")

provincies = sorted(df["Provincie"].dropna().unique())
gekozen_provincie = st.selectbox("Kies een provincie", provincies)

max_budget = st.slider(
    "Wat is je maximale budget (€)?",
    min_value=0,
    max_value=int(df["Prijs"].max()),
    value=20
)

aantal_musea = st.selectbox("Hoeveel musea wil je combineren?", [1, 2, 3])

filtered_df = df[
    (df["Provincie"] == gekozen_provincie) &
    (df["Prijs"] <= max_budget)
]

if st.button("✨ Maak match"):
    if len(filtered_df) < aantal_musea:
        st.warning("Niet genoeg musea binnen deze criteria.")
    else:
        match = filtered_df.sort_values(
            "WEIGHTED RATING", ascending=False
        ).head(aantal_musea)

        st.dataframe(match[
            [
                "Musea - Nederlandse benaming (Title)",
                "Provincie",
                "Prijs",
                "WEIGHTED RATING"
            ]
        ])

        st.success(f"Totale prijs: €{match['Prijs'].sum():.2f}")
