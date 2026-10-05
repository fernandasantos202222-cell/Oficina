import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# BANCO DE DADOS

conn = sqlite3.connect("oficina.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS servicos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    descricao TEXT,
    valor REAL
)
""")

conn.commit()

# FUNÇÕES

def cadastrar_cliente():
    nome = entry_nome.get()
    telefone = entry_telefone.get()

    if nome == "":
        messagebox.showerror("Erro", "Digite o nome")
        return

    cursor.execute(
        "INSERT INTO clientes(nome, telefone) VALUES (?, ?)",
        (nome, telefone)
    )

    conn.commit()

    entry_nome.delete(0, tk.END)
    entry_telefone.delete(0, tk.END)

    carregar_clientes()

def carregar_clientes():

    tabela_clientes.delete(*tabela_clientes.get_children())

    cursor.execute("SELECT * FROM clientes")

    for linha in cursor.fetchall():
        tabela_clientes.insert("", "end", values=linha)

def cadastrar_servico():

    cliente = entry_cliente.get()
    descricao = entry_descricao.get()
    valor = entry_valor.get()

    if cliente == "":
        messagebox.showerror("Erro", "Digite o cliente")
        return

    cursor.execute("""
    INSERT INTO servicos(cliente, descricao, valor)
    VALUES (?, ?, ?)
    """, (cliente, descricao, valor))

    conn.commit()

    entry_cliente.delete(0, tk.END)
    entry_descricao.delete(0, tk.END)
    entry_valor.delete(0, tk.END)

    carregar_servicos()
    atualizar_financeiro()

def carregar_servicos():

    tabela_servicos.delete(*tabela_servicos.get_children())

    cursor.execute("SELECT * FROM servicos")

    for linha in cursor.fetchall():
        tabela_servicos.insert("", "end", values=linha)

def atualizar_financeiro():

    cursor.execute("SELECT SUM(valor) FROM servicos")

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    lbl_total.config(
        text=f"
