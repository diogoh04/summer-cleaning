import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🫧 Summer DeepClean")

    # Upload múltiplos arquivos
files = st.file_uploader("Upload Excel", type=["xlsx"], accept_multiple_files=True)

if not files:
    st.info("Faz upload de um ficheiro para começar")
    st.stop()

    dfs = []

    # 🔄 Ler todos os arquivos
for file in files:
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.str.lower().str.strip()

    # 🔍 detectar tiposs
if "questions" in df.columns:
        file_type = "audit"
        df = df.rename(columns={
            "checkpoint type": "house",
            "unnamed: 1": "area",
            "unnamed: 2": "room",
            "questions": "details"
            })

        df["house"] = df["house"].astype(str).str.strip()
        df["area"] = df["area"].astype(str)

        df["apartment"] = df["area"].str.extract(r"(Apt \d+)")
        df["room"] = df["room"].astype(str)  

elif "clean type" in df.columns:
        file_type = "cleaning"

        df = df.rename(columns={
            "room": "full_room",
            "clean type": "clean_type",
            "complete?": "status",
            "checkpoint type": "house"
        })

        df["full_room"] = df["full_room"].astype(str)

        # 🔥 extrair dados
        df["apartment"] = df["full_room"].str.extract(r"(Apt \d+)")
        df["room"] = df["full_room"].str.extract(r"(Room \d+)")

else:
        continue

    # 🟡 status default
if "status" not in df.columns:
        df["status"] = "pending"

    dfs.append(df)

    # 🔗 juntar tudo
    df = pd.concat(dfs, ignore_index=True)

    # limpar
    df["house"] = df["house"].astype(str).str.strip()
    df["apartment"] = df["apartment"].astype(str).str.strip()

    # FILTROS

    houses = sorted(df["house"].dropna().unique())
    selected_house = st.selectbox("House", houses)

    df_house = df[df["house"] == selected_house]

    apartments = sorted(df_house["apartment"].dropna().unique())
    selected_apartment = st.selectbox("Apartment", apartments)

    df_apartment = df_house[df_house["apartment"] == selected_apartment]

    # proteção
if df_apartment.empty:
    st.warning("Sem dados para este filtro")
    st.stop()

    # 📊 MÉTRICAS

    done = (df_apartment["status"].str.upper() == "DONE").sum()
    refusal = (df_apartment["status"].str.upper() == "REFUSAL").sum()
    total = len(df_apartment)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total)
    col2.metric("Done", done)
    col3.metric("Refusal", refusal)

    # LISTA

    status_color = {
    "done": "🟢 DONE",
    "refusal": "🔴 REFUSAL",
    "pending": "🟡 PENDING"
    }

for i, row in df_apartment.iterrows():
    col1, col2, col3 = st.columns([3,1,1])

with col1:
        st.write(f"🏠 {row['room']} - {status_color.get(str(row['status']).lower(), '🟡 PENDING')}")

with col2:
    if st.button("✅", key=f"done_{i}"):
            df.at[i, "status"] = "done"

with col3:
    if st.button("❌", key=f"refusal_{i}"):
            df.at[i, "status"] = "refusal"

    # 📤 Exportar
if st.button("Exportar Excel"):
    df.to_excel("updated.xlsx", index=False)

with open("updated.xlsx", "rb") as f:
        st.download_button("Download", f, "housekeeping_updated.xlsx")