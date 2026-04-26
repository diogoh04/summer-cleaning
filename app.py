import streamlit as st
import pandas as pd
import os
import openpyxl

SAVE_FILE = "data.csv"

st.set_page_config(layout="wide")
st.title("🫧 Summer DeepClean")

files = st.file_uploader("Upload Excel", type=["xlsx"], accept_multiple_files=True)

if not files:
    st.info("Faz upload de ficheiros para começar")
    st.stop()

# juntar todos os ficheiros
df_list = []

for file in files:
    temp_df = pd.read_excel(file, engine="openpyxl")
    temp_df["source_file"] = file.name  # opcional (top)
    df_list.append(temp_df)

# juntar tudo
df = pd.concat(df_list, ignore_index=True)

# 🔍 detectar tipo de ficheiro
columns = df.columns.str.lower()

if "questions" in columns:
    file_type = "audit"

elif "clean type" in columns:
    file_type = "cleaning"

else:
    file_type = "unknown"

#  Ajustar colunas
if file_type == "audit":
    df = df.rename(columns={
    "Checkpoint Type": "house",
    "Unnamed: 1": "area",
    "Unnamed: 2": "room",
    "Questions": "details"
})
    # extrair dados
    df["area"] = df["area"].astype(str)
    df["house"] = df["area"].str.extract(r"(Ashfield House \d+|Belgove \d+)")
    df["apartment"] = df["area"].str.extract(r"(Apt \d+)")
    df["room"] = df["area"].str.extract(r"(Room \d+)")

elif file_type == "cleaning":
    df = df.rename(columns={
        "Room": "full_room",
        "Clean Type": "clean_type",
        "Complete?": "status"
    })
    # extrair dados
    df["house"] = df["full_room"].str.extract(r"(Ashfield House \d+|Belgove \d+)")
    df["apartment"] = df["full_room"].str.extract(r"(Apt \d+)")
    df["room"] = df["full_room"].str.extract(r"(Room \d+)")

# 🟡 Criar status
if "status" not in df.columns:
    df["status"] = "pending"

# Filtro
# HOUSE
houses = sorted(df["house"].dropna().unique())
selected_house = st.selectbox("House", houses)

df_house = df[df["house"] == selected_house]

# APARTAMENTO
apartments = sorted(df_house["apartment"].dropna().unique())
selected_apartment = st.selectbox("Apartment", apartments)

df_apartment = df_house[df_house["apartment"] == selected_apartment]

# Status visual
if file_type == "audit":
    st.subheader("Audit Mode")

elif file_type == "cleaning":
    st.subheader("Cleaning Mode")
    st.write("Tipo de limpeza:", df["clean_type"].unique())

if file_type == "cleaning":
    done = (df["status"] == "DONE").sum()
    refusal = (df["status"] == "REFUSAL").sum()
    total = len(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total)
    col2.metric("Done", done)
    col3.metric("Refusal", refusal)

status_color = {
    "done": "🟢 DONE",
    "refusal": "🔴 REFUSAL",
    "pending": "🟡 PENDING"
}

# 📱 Interface tipo app
for i, row in filtered_df.iterrows():
    col1, col2, col3 = st.columns([3,1,1])

    with col1:
        st.write(f"🏠 {row['room']} - {status_color[row['status']]}")

    with col2:
        if st.button("✅", key=f"done_{i}"):
            df.at[i, "status"] = "done"
            df.to_csv(SAVE_FILE, index=False)

    with col3:
        if st.button("❌", key=f"refusal_{i}"):
            df.at[i, "status"] = "refusal"
            df.to_csv(SAVE_FILE, index=False)

# 📤 Exportar
if st.button("Exportar Excel"):
    df.to_excel("updated.xlsx", index=False)

    with open("updated.xlsx", "rb") as f:
        st.download_button("Download", f, "housekeeping_updated.xlsx")