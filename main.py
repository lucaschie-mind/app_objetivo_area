import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os

st.set_page_config(page_title="Gestão de Áreas e Objetivos", layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://usuario:senha@host:porta/dbname")
engine = create_engine(DATABASE_URL)

def carregar_dados():
    query = "SELECT * FROM areas_objetivos ORDER BY id;"
    return pd.read_sql(query, engine)

def atualizar_campo(id_, campo, valor):
    sql = text(f"UPDATE areas_objetivos SET {campo} = :valor WHERE id = :id")
    with engine.begin() as conn:
        conn.execute(sql, {"valor": valor, "id": id_})

st.title("📋 Edição de Áreas e Objetivos")
st.caption("Gerencie responsáveis, objetivos e períodos diretamente no banco do Railway.")

df = carregar_dados()
if df.empty:
    st.warning("Nenhum registro encontrado na tabela 'areas_objetivos'.")
    st.stop()

edit_cols = ["responsavel", "objetivo", "periodo_inicio", "periodo_fim"]
df_editable = df.copy()

st.write("### Editar informações")
edited_df = st.data_editor(
    df_editable,
    column_config={
        "responsavel": st.column_config.TextColumn("Responsável"),
        "objetivo": st.column_config.TextColumn("Objetivo"),
        "periodo_inicio": st.column_config.DateColumn("Período Início"),
        "periodo_fim": st.column_config.DateColumn("Período Fim"),
    },
    num_rows="fixed",
    hide_index=True,
    key="editor",
)

if st.button("💾 Salvar alterações"):
    alteracoes = 0
    for idx, row in edited_df.iterrows():
        orig = df.loc[df["id"] == row["id"]].iloc[0]
        for campo in edit_cols:
            novo = row[campo]
            antigo = orig[campo]
            if pd.isna(novo) and pd.isna(antigo):
                continue
            if novo != antigo:
                atualizar_campo(row["id"], campo, novo)
                alteracoes += 1

    if alteracoes > 0:
        st.success(f"✅ {alteracoes} alteração(ões) salva(s) com sucesso!")
    else:
        st.info("Nenhuma modificação detectada.")

if st.button("🔄 Recarregar tabela"):
    st.experimental_rerun()
