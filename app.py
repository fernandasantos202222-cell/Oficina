import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

# ======================
# BANCO DE DADOS
# ======================

conn = sqlite3.connect("oficina.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    descricao TEXT,
    valor REAL,
    data TEXT
)
""")

conn.commit()

# ======================
# CONFIGURAÇÃO
# ======================

st.set_page_config(
    page_title="Oficina de Motos",
    page_icon="🏍️",
    layout="wide"
)

st.title("🏍️ Sistema da Oficina")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Clientes",
        "Serviços",
        "Financeiro"
    ]
)

# ======================
# DASHBOARD
# ======================

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

    if faturamento is None:
        faturamento = 0

    c1, c2, c3 = st.columns(3)

    c1.metric("Clientes", total_clientes)
    c2.metric("Serviços", total_servicos)
    c3.metric("Faturamento", f"R$ {faturamento:.2f}")

    st.divider()

    df = pd.read_sql_query("""
        SELECT
        s.id,
        c.nome AS cliente,
        s.descricao,
        s.valor,
        s.data
        FROM servicos s
        JOIN clientes c
        ON c.id = s.cliente_id
        ORDER BY s.id DESC
    """, conn)

    st.subheader("Últimos Serviços")

    st.dataframe(df, use_container_width=True)

# ======================
# CLIENTES
# ======================

elif menu == "Clientes":

    st.subheader("Cadastrar Cliente")

    with st.form("cliente_form"):

        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")

        salvar = st.form_submit_button("Salvar Cliente")

        if salvar:

            cursor.execute(
                """
                INSERT INTO clientes
                (nome, telefone)
                VALUES (?, ?)
                """,
                (nome, telefone)
            )

            conn.commit()

            st.success("Cliente cadastrado com sucesso!")

    st.divider()

    st.subheader("Lista de Clientes")

    clientes = pd.read_sql_query(
        "SELECT * FROM clientes",
        conn
    )

    st.dataframe(clientes, use_container_width=True)

# ======================
# SERVIÇOS
# ======================

elif menu == "Serviços":

    clientes_df = pd.read_sql_query(
        "SELECT * FROM clientes",
        conn
    )

    if clientes_df.empty:

        st.warning("Cadastre um cliente primeiro.")

    else:

        st.subheader("Registrar Serviço")

        nomes = clientes_df["nome"].tolist()

        with st.form("servico_form"):

            cliente_nome = st.selectbox(
                "Cliente",
                nomes
            )

            descricao = st.text_area(
                "Descrição do Serviço"
            )

            valor = st.number_input(
                "Valor (R$)",
                min_value=0.0
            )

            salvar = st.form_submit_button(
                "Registrar Serviço"
            )

            if salvar:

                cliente_id = clientes_df[
                    clientes_df["nome"] == cliente_nome
                ]["id"].values[0]

                cursor.execute("""
                    INSERT INTO servicos(
                        cliente_id,
                        descricao,
                        valor,
                        data
                    )
                    VALUES(?,?,?,?)
                """, (
                    int(cliente_id),
                    descricao,
                    valor,
                    datetime.now().strftime("%d/%m/%Y")
                ))

                conn.commit()

                st.success("Serviço registrado!")

        st.divider()

        servicos = pd.read_sql_query("""
            SELECT
            s.id,
            c.nome AS cliente,
            s.descricao,
            s.valor,
            s.data
            FROM servicos s
            JOIN clientes c
            ON c.id = s.cliente_id
            ORDER BY s.id DESC
        """, conn)

        st.dataframe(servicos, use_container_width=True)

# ======================
# FINANCEIRO
# ======================

elif menu == "Financeiro":

    dados = pd.read_sql_query("""
        SELECT
        s.id,
        c.nome AS cliente,
        s.descricao,
        s.valor,
        s.data
        FROM servicos s
        JOIN clientes c
        ON c.id = s.cliente_id
    """, conn)

    if not dados.empty:

        total = dados["valor"].sum()

        media = dados["valor"].mean()

        quantidade = len(dados)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Faturamento Total",
            f"R$ {total:.2f}"
        )

        c2.metric(
            "Qtd. Serviços",
            quantidade
        )

        c3.metric(
            "Ticket Médio",
            f"R$ {media:.2f}"
        )

        st.divider()

        st.dataframe(
            dados,
            use_container_width=True
        )

        arquivo = BytesIO()

        with pd.ExcelWriter(
            arquivo,
            engine='openpyxl'
        ) as writer:

            dados.to_excel(
                writer,
                index=False,
                sheet_name="Servicos"
            )

        st.download_button(
            "📥 Baixar Excel",
            data=arquivo.getvalue(),
            file_name="relatorio_oficina.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:

        st.info("Nenhum serviço registrado.")
