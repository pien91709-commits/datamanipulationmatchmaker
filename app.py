import streamlit as st
import pandas as pd

st.markdown(
    """
    <style>
    .stApp {
        background-color: #d8f3dc;
    }
    </style>
    """,
    unsafe_allow_html=True
)

bestandspad = "website.xlsx"

df1 = pd.read_excel(bestandspad, sheet_name="Blad1")
df2 = pd.read_excel(bestandspad, sheet_name="Blad2")

df = pd.concat([df1, df2], ignore_index=True)

df["THEME RATING"] = pd.to_numeric(df["THEME RATING"], errors="coerce")
df["FACILITIES RATING"] = pd.to_numeric(df["FACILITIES RATING"], errors="coerce")
df["WEIGHTED RATING"] = pd.to_numeric(df["WEIGHTED RATING"], errors="coerce")

st.title("Museum Matchmaker")

provincies = sorted(df["Provincie"].dropna().unique())
gekozen_provincie = st.selectbox("Kies een provincie", provincies)

max_budget = st.slider(
    "Wat is je maximale budget (€)?",
    min_value=0,
    max_value=40,
    value=40
)

# Aantal musea
aantal_musea = st.selectbox(
    "Hoeveel musea wil je combineren?",
    list(range(1, 16))
)

themas = [
    "Geschiedenis en archeologie",
    "Wetenschap en technologie",
    "Mode",
    "Literatuur",
    "Architectuur",
    "Beeldende kunst",
    "Toegepaste kunst en design"
]

st.subheader("Selecteer je favoriete thema's")

col1, col2 = st.columns(2)
gekozen_themas = []

for i, thema in enumerate(themas):
    if i % 2 == 0:
        if col1.checkbox(thema):
            gekozen_themas.append(thema)
    else:
        if col2.checkbox(thema):
            gekozen_themas.append(thema)

filtered_df = df[
    (df["Provincie"] == gekozen_provincie) &
    (df["Prijs"] <= max_budget)
]

if gekozen_themas:
    mask = pd.Series([False] * len(filtered_df))
    for thema in gekozen_themas:
        if thema in filtered_df.columns:
            mask = mask | (filtered_df[thema] == 1)
    filtered_df = filtered_df[mask]

filtered_df = filtered_df.dropna(subset=["WEIGHTED RATING"])

if st.button("Maak match"):
    if len(filtered_df) < aantal_musea:
        st.warning("Niet genoeg musea binnen deze criteria.")
    else:
        match = (
            filtered_df
            .sort_values("WEIGHTED RATING", ascending=False)
            .head(aantal_musea)
        )

        totaalprijs = match["Prijs"].sum()

        st.subheader("Jouw match")
        st.dataframe(
            match[[
                "Musea - Nederlandse benaming (Title)",
                "Provincie",
                "Prijs",
                "THEME RATING"
            ]]
        )

        st.success(f"Totale prijs: €{totaalprijs:.2f}")
                "Musea - Nederlandse benaming (Title)",
                "Provincie",
                "Prijs",
                "THEME RATING",
                "WEIGHTED RATING"
            ]]
        )

