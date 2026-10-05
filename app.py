from flask import Flask, request, redirect, render_template_string, send_file
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# CRIAR BANCO

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
    cliente_id INTEGER,
    descricao TEXT,
    valor REAL,
    data TEXT
)
""")

conn.commit()
conn.close()


def conectar():
    return sqlite3.connect("oficina.db")


@app.route("/")
def home():

    conn = conectar()
    cur = conn.cursor()

    clientes = cur.execute(
        "SELECT COUNT(*) FROM clientes"
    ).fetchone()[0]

    servicos = cur.execute(
        "SELECT COUNT(*) FROM servicos"
    ).fetchone()[0]

    faturamento = cur.execute(
        "SELECT SUM(valor) FROM servicos"
    ).fetchone()[0]

    faturamento = faturamento if faturamento else 0

    conn.close()

    return render_template_string("""

<!DOCTYPE html>
<html>
<head>
<title>Oficina de Motos</title>
<style>
body{
font-family:Arial;
margin:40px;
background:#f5f5f5;
}
.card{
background:white;
padding:20px;
margin:10px;
border-radius:10px;
box-shadow:0 0 10px #ccc;
}
a{
padding:10px;
background:#007bff;
color:white;
text-decoration:none;
border-radius:5px;
}
</style>
</head>
<body>

<h1>🏍 Oficina de Motos</h1>

<div class="card">
<h2>Clientes: {{clientes}}</h2>
</div>

<div class="card">
<h2>Serviços: {{servicos}}</h2>
</div>

<div class="card">
<h2>Faturamento: R$ {{faturamento}}</h2>
</div>

/clientesClientes</a>
/servicosServiços</a>
/excelExportar Excel</a>

</body>
</html>

""", clientes=clientes,
     servicos=servicos,
     faturamento=faturamento)


@app.route("/clientes", methods=["GET", "POST"])
def clientes():

    conn = conectar()
    cur = conn.cursor()

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]

        cur.execute(
            "INSERT INTO clientes(nome,telefone) VALUES(?,?)",
            (nome, telefone)
        )

        conn.commit()

    lista = cur.execute(
        "SELECT * FROM clientes"
    ).fetchall()

    conn.close()

    html = """
    <h1>Cadastro de Clientes</h1>

    <form method="post">
    Nome:<br>
    <input type="text" name="nome"><br><br>

    Telefone:<br>
    <input type="text" name="telefone"><br><br>

    <button>Salvar</button>
    </form>

    <hr>

    <table border=1 cellpadding=10>
    <tr>
    <th>ID</th>
    <th>Nome</th>
    <th>Telefone</th>
    </tr>
    """

    for c in lista:
        html += f"""
        <tr>
        <td>{c[0]}</td>
        <td>{c[1]}</td>
        <td>{c[2]}</td>
        </tr>
        """

    html += """
    </table>

    <br>
    /Voltar</a>
    """

    return html


@app.route("/servicos", methods=["GET", "POST"])
def servicos():

    conn = conectar()
    cur = conn.cursor()

    if request.method == "POST":

        cliente_id = request.form["cliente"]
        descricao = request.form["descricao"]
        valor = request.form["valor"]

        cur.execute("""
            INSERT INTO servicos(
            cliente_id,
            descricao,
            valor,
            data)
            VALUES(?,?,?,?)
        """, (
            cliente_id,
            descricao,
            valor,
            datetime.now().strftime("%d/%m/%Y")
        ))

        conn.commit()

    clientes = cur.execute(
        "SELECT * FROM clientes"
    ).fetchall()

    servicos = cur.execute("""
    SELECT
    servicos.id,
    clientes.nome,
    servicos.descricao,
    servicos.valor,
    servicos.data
    FROM servicos
    INNER JOIN clientes
    ON clientes.id = servicos.cliente_id
    ORDER BY servicos.id DESC
    """).fetchall()

    conn.close()

    html = """

    <h1>Registrar Serviço</h1>

    <form method="post">

    Cliente:<br>

    <select name="cliente">
    """

    for c in clientes:
        html += f"""
        <option value="{c[0]}">{c[1]}</option>
        """

    html += """
    </select>

    <br><br>

    Serviço:<br>
    <textarea name="descricao"></textarea>

    <br><br>

    Valor:<br>
    <input type="number"
    step="0.01"
    name="valor">

    <br><br>

    <button>Salvar</button>

    </form>

    <hr>

    <table border=1 cellpadding=10>

    <tr>
    <th>ID</th>
    <th>Cliente</th>
    <th>Serviço</th>
    <th>Valor</th>
    <th>Data</th>
    </tr>
    """

    for s in servicos:
        html += f"""
        <tr>
        <td>{s[0]}</td>
        <td>{s[1]}</td>
        <td>{s[2]}</td>
        <td>R$ {s[3]}</td>
        <td>{s[4]}</td>
        </tr>
        """

    html += """
    </table>

    <br>

    /Voltar</a>
    """

    return html


@app.route("/excel")
def excel():

    conn = conectar()

    df = pd.read_sql_query("""
    SELECT
    servicos.id,
    clientes.nome AS cliente,
    servicos.descricao,
    servicos.valor,
    servicos.data
    FROM servicos
    INNER JOIN clientes
    ON clientes.id = servicos.cliente_id
    """, conn)

    arquivo = "relatorio_oficina.xlsx"

    df.to_excel(arquivo, index=False)

    conn.close()

    return send_file(
        arquivo,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
