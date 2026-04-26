import streamlit as st
import pandas as pd
import os
import openpyxl
st.write("openpyxl loaded")

SAVE_FILE = "data.csv"

st.set_page_config(layout="wide")
st.title("🫧 Summer DeepClean")

file = st.file_uploader("Upload Excel", type=["xlsx"])

# 📥 Carregar dados
if os.path.exists(SAVE_FILE):
    df = pd.read_csv(SAVE_FILE)
elif file is not None:
    df = pd.read_excel(file, engine="openpyxl")
else:
    st.info("Faz upload do ficheiro para começar")
    st.stop()

# 🧼 Ajustar colunas
df = df.rename(columns={
    "Checkpoint Type": "house",
    "Unnamed: 1": "area",
    "Unnamed: 2": "room",
    "Questions": "details"
})
# 🧼 limpar dados
df["house"] = df["house"].astype(str).str.strip()
df["area"] = df["area"].astype(str).str.strip()

# 🟡 Criar status
if "status" not in df.columns:
    df["status"] = "pending"

# 🎯 Filtro
# filtro house
houses = sorted(df["house"].dropna().unique())
selected_house = st.selectbox("House", houses)

df_house = df[df["house"] == selected_house]

# filtro apt (base_area)
areas = sorted(df_house["base_area"].dropna().unique())
selected_area = st.selectbox("Apartamento", areas)

filtered_df = df_house[df_house["base_area"] == selected_area]
# 🎨 Status visual
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