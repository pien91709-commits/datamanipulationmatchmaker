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

nl_kolom = "Musea - Nederlandse benaming (Title)"
fr_kolom = "Musea - Franse benaming (Title)"

if nl_kolom not in df.columns:
    df[nl_kolom] = pd.NA

if fr_kolom not in df.columns:
    df[fr_kolom] = pd.NA

df["Naam"] = df[nl_kolom]
df["Naam"] = df["Naam"].replace("", pd.NA)
df["Naam"] = df["Naam"].fillna(df[fr_kolom])


st.title("Museum Matchmaker")

provincies = sorted(df["Provincie"].dropna().unique())
gekozen_provincie = st.selectbox("Kies een provincie", provincies)

max_budget = st.slider(
    "Wat is je maximale budget (€)?",
    min_value=0,
    max_value=40,
    value=40
)

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
    geldige_themas = [t for t in gekozen_themas if t in filtered_df.columns]

    if geldige_themas:
        # Filter: minstens 1 match
        filtered_df = filtered_df[
            filtered_df[geldige_themas].eq(1).any(axis=1)
        ]

        filtered_df["Aantal matches"] = filtered_df[geldige_themas].sum(axis=1)

        def match_themas(row):
            matches = [t for t in geldige_themas if row[t] == 1]
            return ", ".join(matches)

        filtered_df["Overeenkomende thema's"] = filtered_df.apply(match_themas, axis=1)

    else:
        filtered_df["Aantal matches"] = 0
        filtered_df["Overeenkomende thema's"] = "Geen match"
else:
    filtered_df["Aantal matches"] = 0
    filtered_df["Overeenkomende thema's"] = "Geen selectie"

filtered_df = filtered_df.dropna(subset=["WEIGHTED RATING"])

if st.button("Maak match"):
    if len(filtered_df) < aantal_musea:
        st.warning("Niet genoeg musea binnen deze criteria.")
    else:
        match = (
            filtered_df
            .sort_values(["Aantal matches", "WEIGHTED RATING"], ascending=False)
            .head(aantal_musea)
        )

        totaalprijs = match["Prijs"].sum()

        st.subheader("Jouw match")
        st.dataframe(
            match[[
                "Naam",
                "Provincie",
                "Prijs",
                "THEME RATING",
                "Overeenkomende thema's"
            ]]
        )

        st.success(f"Totale prijs: €{totaalprijs:.2f}")
