import streamlit as st
import pandas as pd
import os

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

# 🟡 Criar status
if "status" not in df.columns:
    df["status"] = "pending"

# 🎯 Filtro
areas = df["area"].dropna().unique()
selected = st.selectbox("Filtrar área", areas)

filtered_df = df[df["area"] == selected]

st.subheader(f"Área: {selected}")

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