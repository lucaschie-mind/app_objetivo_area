import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Gestão de Áreas e Objetivos", layout="wide")

# tenta criar o engine só quando precisar
def get_engine():
    from sqlalchemy import create_engine
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return None
    try:
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Erro ao criar engine do banco: {e}")
        return None

def carregar_dados(engine):
    from sqlalchemy import text
    try:
        query = "SELECT * FROM areas_objetivos ORDER BY id;"
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela 'areas_objetivos': {e}")
        return pd.DataFrame()

def atualizar_campo(engine, id_, campo, valor):
    from sqlalchemy import text
    sql = text(f"UPDATE areas_objetivos SET {campo} = :valor WHERE id = :id")
    with engine.begin() as conn:
        conn.execute(sql, {"valor": valor, "id": id_})

st.title("📋 Edição de Áreas e Objetivos")

engine = get_engine()
if engine is None:
    st.error("DATABASE_URL não configurada ou conexão não pôde ser criada. Configure no Railway.")
    st.stop()

df = carregar_dados(engine)

if df.empty:
    st.warning("Não há dados ou a tabela 'areas_objetivos' não existe nesse banco.")
    st.stop()

# garantir colunas editáveis
edit_cols = ["responsavel", "objetivo", "periodo_inicio", "periodo_fim"]
for c in edit_cols:
    if c not in df.columns:
        df[c] = None

st.write("### Editar informações")
edited_df = st.data_editor(
    df,
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
    for _, row in edited_df.iterrows():
        orig = df.loc[df["id"] == row["id"]].iloc[0]
        for campo in edit_cols:
            novo = row[campo]
            antigo = orig[campo]
            # normalizar NaN/NaT -> None
            if pd.isna(novo):
                novo = None
            if pd.isna(antigo):
                antigo = None
            if novo != antigo:
                atualizar_campo(engine, row["id"], campo, novo)
                alteracoes += 1
    if alteracoes:
        st.success(f"✅ {alteracoes} alteração(ões) salva(s)!")
    else:
        st.info("Nenhuma modificação detectada.")

if st.button("🔄 Recarregar"):
    st.experimental_rerun()