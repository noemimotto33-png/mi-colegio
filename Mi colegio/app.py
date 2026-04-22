from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import traceback

app = Flask(__name__)
app.secret_key = "colegio123"

# 🔥 RUTA CORRECTA BASE DE DATOS (IMPORTANTE PARA RENDER)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")


# 🟢 CREAR BASE DE DATOS AUTOMÁTICAMENTE
def init_db():
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            curso TEXT,
            pago TEXT
        )
    """)

    conexion.commit()
    conexion.close()

init_db()


# 🔴 MOSTRAR ERROR REAL (MUY IMPORTANTE)
@app.errorhandler(500)
def error_500(e):
    return f"<pre>{traceback.format_exc()}</pre>", 500


# 🧪 RUTA DE PRUEBA
@app.route("/test")
def test():
    return "FUNCIONA CORRECTAMENTE"


# 🔑 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        if usuario == "admin" and password == "1234":
            session["admin"] = True
            return redirect("/")
        else:
            return "Usuario o contraseña incorrectos"

    return render_template("login.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


# 🔒 PÁGINA PRINCIPAL
@app.route("/")
def index():
    if "admin" not in session:
        return redirect("/login")

    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM estudiantes")
    datos = cursor.fetchall()
    conexion.close()

    cursos = {}

    for estudiante in datos:
        curso = estudiante[2]
        if curso not in cursos:
            cursos[curso] = []
        cursos[curso].append(estudiante)

    return render_template("index.html", cursos=cursos)


# ➕ AÑADIR
@app.route("/add", methods=["POST"])
def add():
    nombre = request.form.get("nombre")
    curso = request.form.get("curso")
    pago = request.form.get("pago")

    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO estudiantes (nombre, curso, pago)
        VALUES (?, ?, ?)
    """, (nombre, curso, pago))

    conexion.commit()
    conexion.close()

    return redirect("/")


# 🔎 FILTRO
@app.route("/filtro/<estado>")
def filtro(estado):
    if "admin" not in session:
        return redirect("/login")

    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM estudiantes WHERE pago = ?", (estado,))
    estudiantes = cursor.fetchall()
    conexion.close()

    return render_template("filtro.html", estudiantes=estudiantes, estado=estado)


# 🗑️ ELIMINAR
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if "admin" not in session:
        return redirect("/login")

    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM estudiantes WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()

    return redirect("/")


# ✏️ EDITAR
@app.route("/editar/<int:id>")
def editar(id):
    if "admin" not in session:
        return redirect("/login")

    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM estudiantes WHERE id = ?", (id,))
    estudiante = cursor.fetchone()
    conexion.close()

    return render_template("editar.html", estudiante=estudiante)


# 💾 ACTUALIZAR
@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    if "admin" not in session:
        return redirect("/login")

    nombre = request.form.get("nombre")
    curso = request.form.get("curso")
    pago = request.form.get("pago")

    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE estudiantes
        SET nombre = ?, curso = ?, pago = ?
        WHERE id = ?
    """, (nombre, curso, pago, id))

    conexion.commit()
    conexion.close()

    return redirect("/")


# 🚀 PRODUCCIÓN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)