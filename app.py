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
        text=f""Faturamento Total: R$ {total:.2f}"
)
 
# JANELA
 
janela = tk.Tk()
janela.title("Oficina de Motos")
janela.geometry("1000x700")
 
titulo = tk.Label(
janela,
text="Sistema da Oficina",
font=("Arial", 20, "bold")
)
 
titulo.pack(pady=10)
 
# CLIENTES
 
frame_clientes = tk.LabelFrame(
janela,
text="Cadastro de Clientes",
padx=10,
pady=10
)
 
frame_clientes.pack(fill="x", padx=10)
 
tk.Label(frame_clientes, text="Nome").grid(row=0, column=0)
 
entry_nome = tk.Entry(frame_clientes, width=30)
entry_nome.grid(row=0, column=1)
 
tk.Label(frame_clientes, text="Telefone").grid(row=1, column=0)
 
entry_telefone = tk.Entry(frame_clientes, width=30)
entry_telefone.grid(row=1, column=1)
 
btn_cliente = tk.Button(
frame_clientes,
text="Cadastrar Cliente",
command=cadastrar_cliente
)
 
btn_cliente.grid(row=2, column=1, pady=10)
 
# TABELA CLIENTES
 
tabela_clientes = ttk.Treeview(
janela,
columns=("id", "nome", "telefone"),
show="headings",
height=8
)
 
tabela_clientes.heading("id", text="ID")
tabela_clientes.heading("nome", text="Nome")
tabela_clientes.heading("telefone", text="Telefone")
 
tabela_clientes.pack(fill="x", padx=10, pady=10)
 
# SERVIÇOS
 
frame_servicos = tk.LabelFrame(
janela,
text="Registrar Serviço",
padx=10,
pady=10
)
 
frame_servicos.pack(fill="x", padx=10)
 
tk.Label(frame_servicos, text="Cliente").grid(row=0, column=0)
 
entry_cliente = tk.Entry(frame_servicos, width=30)
entry_cliente.grid(row=0, column=1)
 
tk.Label(frame_servicos, text="Descrição").grid(row=1, column=0)
 
entry_descricao = tk.Entry(frame_servicos, width=40)
entry_descricao.grid(row=1, column=1)
 
tk.Label(frame_servicos, text="Valor").grid(row=2, column=0)
 
entry_valor = tk.Entry(frame_servicos, width=20)
entry_valor.grid(row=2, column=1)
 
btn_servico = tk.Button(
frame_servicos,
text="Registrar Serviço",
command=cadastrar_servico
)
 
btn_servico.grid(row=3, column=1, pady=10)
 
# TABELA SERVIÇOS
 
tabela_servicos = ttk.Treeview(
janela,
columns=("id", "cliente", "descricao", "valor"),
show="headings",
height=10
)
 
tabela_servicos.heading("id", text="ID")
tabela_servicos.heading("cliente", text="Cliente")
tabela_servicos.heading("descricao", text="Serviço")
tabela_servicos.heading("valor", text="Valor")
 
tabela_servicos.pack(fill="x", padx=10, pady=10)
 
# FINANCEIRO
 
lbl_total = tk.Label(
janela,
text="Faturamento Total: R$ 0,00",
font=("Arial", 16, "bold"),
fg="green"
)
 
lbl_total.pack(pady=20)
 
# CARREGAR DADOS
 
carregar_clientes()
carregar_servicos()
atualizar_financeiro()
 
janela.mainloop()
