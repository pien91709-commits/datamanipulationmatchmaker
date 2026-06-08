import streamlit as st
import pandas as pd

st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
    }

    h1 {
        color: rgb(11, 194, 157);
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
    }

    h2, h3 {
        color: rgb(11, 194, 157);
        font-weight: 600;
    }

    label {
        font-weight: 600 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: white !important;
        border: 2px solid rgb(11, 194, 157) !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background-color: rgb(11, 194, 157);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: rgb(8, 170, 137);
        color: white;
    }
    div[data-testid="stDataFrame"] {
        background-color: white !important;
        border: 2px solid rgb(11, 194, 157);
        border-radius: 12px;
        padding: 10px;
    }
    div[data-testid="stAlert"] {
        background-color: rgba(237, 44, 108, 0.08);
        border-left: 6px solid rgb(237, 44, 108);
        border-radius: 10px;
    }
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color: rgb(237, 44, 108);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        font-size: 18px;
        font-weight: 600;
    ">
        Ontdek musea die passen bij jou.
    </div>
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
df["Prijs"] = pd.to_numeric(df["Prijs"], errors="coerce")

nl_kolom = "Musea - Nederlandse benaming (Title)"
fr_kolom = "Musea - Franse benaming (Alternative Title)"

if nl_kolom not in df.columns:
    df[nl_kolom] = pd.NA

if fr_kolom not in df.columns:
    df[fr_kolom] = pd.NA

df["Naam"] = df[nl_kolom]
df["Naam"] = df["Naam"].replace(r'^\s*$', pd.NA, regex=True)
df["Naam"] = df["Naam"].fillna(df[fr_kolom])
df["Naam"] = df["Naam"].fillna("Onbekend museum")

st.title("Museum Matchmaker")

provincies = sorted(df["Provincie"].dropna().unique())

gekozen_provincie = st.selectbox(
    "Kies een provincie",
    provincies
)

max_budget = st.slider(
    "Wat is je maximale budget (€)?",
    min_value=0,
    max_value=80,
    value=80
)

aantal_musea = st.selectbox(
    "Hoeveel musea wil je combineren?",
    list(range(1, 11))
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
    (df["Provincie"] == gekozen_provincie)
].copy()

if gekozen_themas:

    geldige_themas = [
        thema for thema in gekozen_themas
        if thema in filtered_df.columns
    ]

    if geldige_themas:

        filtered_df = filtered_df[
            filtered_df[geldige_themas].eq(1).any(axis=1)
        ].copy()

        filtered_df["Aantal matches"] = (
            filtered_df[geldige_themas]
            .fillna(0)
            .sum(axis=1)
        )

        def match_themas(rij):
            matches = [
                thema
                for thema in geldige_themas
                if pd.notna(rij[thema]) and rij[thema] == 1
            ]
            return ", ".join(matches)

        filtered_df["Overeenkomende thema's"] = (
            filtered_df.apply(match_themas, axis=1)
        )

    else:
        filtered_df["Aantal matches"] = 0
        filtered_df["Overeenkomende thema's"] = "Geen match"

else:
    filtered_df["Aantal matches"] = 0
    filtered_df["Overeenkomende thema's"] = "Geen selectie"

filtered_df = filtered_df.dropna(subset=["WEIGHTED RATING"])
filtered_df = filtered_df.dropna(subset=["Prijs"])

if st.button("Maak match"):

    kandidaten = (
        filtered_df
        .sort_values(
            ["Aantal matches", "WEIGHTED RATING"],
            ascending=False
        )
    )

    geselecteerd = []
    totaalprijs = 0

    for _, museum in kandidaten.iterrows():

        prijs = museum["Prijs"]

        if totaalprijs + prijs <= max_budget:
            geselecteerd.append(museum)
            totaalprijs += prijs

        if len(geselecteerd) == aantal_musea:
            break

    if len(geselecteerd) < aantal_musea:

        st.warning(
            f"Er konden slechts {len(geselecteerd)} musea gevonden worden "
            f"binnen een totaalbudget van €{max_budget:.2f}."
        )

    else:

        match = pd.DataFrame(geselecteerd)

        st.subheader("Jouw match")

        st.dataframe(
            match[
                [
                    "Naam",
                    "Provincie",
                    "Prijs [€]",
                    "Overeenkomende thema's"
                ]
             ],
                    hide_index=True
        )

        st.success(
            f"Totale prijs: €{totaalprijs:.2f} van maximaal €{max_budget:.2f}"
        )
