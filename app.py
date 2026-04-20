from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# 🔐 clave secreta para sesiones
app.secret_key = "colegio123"


# 🔑 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

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


# 🔒 PROTEGER PÁGINA PRINCIPAL
@app.route("/")
def index():
    if "admin" not in session:
        return redirect("/login")

    conexion = sqlite3.connect("database.db")
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


# ➕ AÑADIR ESTUDIANTE
@app.route("/add", methods=["POST"])
def add():
    nombre = request.form["nombre"]
    curso = request.form["curso"]
    pago = request.form["pago"]

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO estudiantes (nombre, curso, pago)
        VALUES (?, ?, ?)
    """, (nombre, curso, pago))

    conexion.commit()
    conexion.close()

    return redirect("/")


# 🔎 FILTRO PAGADOS / PENDIENTES
@app.route("/filtro/<estado>")
def filtro(estado):
    if "admin" not in session:
        return redirect("/login")

    conexion = sqlite3.connect("database.db")
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

    conexion = sqlite3.connect("database.db")
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

    conexion = sqlite3.connect("database.db")
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

    nombre = request.form["nombre"]
    curso = request.form["curso"]
    pago = request.form["pago"]

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE estudiantes
        SET nombre = ?, curso = ?, pago = ?
        WHERE id = ?
    """, (nombre, curso, pago, id))

    conexion.commit()
    conexion.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)