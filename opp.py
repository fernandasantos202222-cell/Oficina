import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

# -------------------------
# BANCO DE DADOS
# -------------------------

conn = sqlite3.connect("oficina.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    descricao TEXT,
    valor REAL,
    data TEXT
)
""")

conn.commit()

# -------------------------
# CONFIG
# -------------------------

st.set_page_config(
    page_title="Oficina de Motos",
    page_icon="🏍️",
    layout="wide"
)

st.title("🏍️ Sistema da Oficina")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Clientes",
        "Serviços",
        "Financeiro"
    ]
)

# -------------------------
# DASHBOARD
# -------------------------

if menu == "Dashboard":

    total_clientes = cursor.execute(
        "SELECT COUNT(*) FROM clientes"
    ).fetchone()[0]

    total_servicos = cursor.execute(
        "SELECT COUNT(*) FROM servicos"
    ).fetchone()[0]

    faturamento = cursor.execute(
        "SELECT SUM(valor) FROM servicos"
    ).fetchone()[0]

    faturamento = faturamento or 0

    c1, c2, c3 = st.columns(3)

    c1.metric("Clientes", total_clientes)
    c2.metric("Serviços", total_servicos)
    c3.metric("Faturamento", f"R$ {faturamento:,.2f}")

    st.divider()

    df = pd.read_sql_query(
        "SELECT * FROM servicos ORDER BY id DESC",
        conn
    )

    st.subheader("Últimos Serviços")

    st.dataframe(df, use_container_width=True)

# -------------------------
# CLIENTES
# -------------------------

elif menu == "Clientes":

    st.subheader("Cadastro de Clientes")

    with st.form("cliente"):

        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")

        salvar = st.form_submit_button("Cadastrar")

        if salvar:

            cursor.execute(
                """
                INSERT INTO clientes(nome, telefone)
                VALUES (?, ?)
                """,
                (nome, telefone)
            )

            conn.commit()

            st.success("Cliente cadastrado!")

    st.divider()

    clientes = pd.read_sql_query(
        "SELECT * FROM clientes",
        conn
    )

    st.dataframe(clientes, use_container_width=True)

# -------------------------
# SERVIÇOS
# -------------------------

elif menu == "Serviços":

    st.subheader("Registrar Serviço")

    clientes = pd.read_sql_query(
        "SELECT nome FROM clientes",
        conn
    )

    lista_clientes = clientes["nome"].tolist()

    if len(lista_clientes) == 0:
        st.warning("Cadastre um cliente primeiro.")
    else:

        with st.form("servico"):

            cliente = st.selectbox(
                "Cliente",
                lista_clientes
            )

            descricao = st.text_area(
                "Descrição do Serviço"
            )

            valor = st.number_input(
                "Valor",
                min_value=0.0
            )

            salvar = st.form_submit_button(
                "Registrar Serviço"
            )

            if salvar:

                cursor.execute("""
                INSERT INTO servicos(
                    cliente,
                    descricao,
                    valor,
                    data
                )
                VALUES(?,?,?,?)
                """, (
                    cliente,
                    descricao,
                    valor,
                    datetime.now().strftime("%d/%m/%Y")
                ))

                conn.commit()

                st.success("Serviço registrado!")

        st.divider()

        servicos = pd.read_sql_query("""
        SELECT *
        FROM servicos
        ORDER BY id DESC
        """, conn)

        st.dataframe(
            servicos,
            use_container_width=True
        )

# -------------------------
# FINANCEIRO
# -------------------------

elif menu == "Financeiro":

    st.subheader("Resumo Financeiro")

    df = pd.read_sql_query(
        "SELECT * FROM servicos",
        conn
    )

    if len(df) > 0:

        total = df["valor"].sum()

        ticket = df["valor"].mean()

        quantidade = len(df)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Faturamento Total",
            f"R$ {total:,.2f}"
        )

        c2.metric(
            "Quantidade de Serviços",
            quantidade
        )

        c3.metric(
            "Ticket Médio",
            f"R$ {ticket:,.2f}"
        )

        arquivo = BytesIO()

        with pd.ExcelWriter(
            arquivo,
            engine="openpyxl"
        ) as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Serviços"
            )

        st.download_button(
            "📥 Baixar Planilha Excel",
            arquivo.getvalue(),
            file_name="relatorio_oficina.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    else:
        st.info("Nenhum serviço cadastrado.")
