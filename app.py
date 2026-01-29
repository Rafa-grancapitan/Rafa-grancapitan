import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "supersecret"
DB = "Basedatos/usuarios.db" 

# ---------------------------
# Conexión a BD
# ---------------------------
def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# PERFILES
# ---------------------------
@app.route("/perfiles")
def perfiles_list():
    conn = get_conn()
    perfiles = conn.execute("SELECT * FROM perfiles ORDER BY nombre ASC").fetchall()
    conn.close()
    return render_template("perfil_list.html", perfiles=perfiles)

@app.route("/perfil/<int:id>")
def perfil_detalle(id):
    conn = get_conn()
    perfil = conn.execute("SELECT * FROM perfiles WHERE id=?", (id,)).fetchone()
    usuarios = conn.execute("SELECT * FROM usuarios WHERE perfil_id=?", (id,)).fetchall()
    conn.close()
    return render_template("perfil_detalle.html", perfil=perfil, usuarios=usuarios)

@app.route("/perfil/nuevo", methods=["GET", "POST"])
def perfil_nuevo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        nivel = request.form["nivel"]
        activo = 1 if request.form.get("activo") else 0

        conn = get_conn()
        conn.execute(
            "INSERT INTO perfiles(nombre, descripcion, nivel, activo) VALUES (?, ?, ?, ?)",
            (nombre, descripcion, nivel, activo)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("perfiles_list"))
    return render_template("perfil_form.html", perfil=None)

@app.route("/perfil/editar/<int:id>", methods=["GET", "POST"])
def perfil_editar(id):
    conn = get_conn()
    perfil = conn.execute("SELECT * FROM perfiles WHERE id=?", (id,)).fetchone()
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        nivel = request.form["nivel"]
        activo = 1 if request.form.get("activo") else 0
        conn.execute(
            "UPDATE perfiles SET nombre=?, descripcion=?, nivel=?, activo=? WHERE id=?",
            (nombre, descripcion, nivel, activo, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("perfiles_list"))
    conn.close()
    return render_template("perfil_form.html", perfil=perfil)

@app.route("/perfil/borrar/<int:id>", methods=["GET", "POST"])
def perfil_borrar(id):
    conn = get_conn()
    perfil = conn.execute("SELECT * FROM perfiles WHERE id=?", (id,)).fetchone()
    usuarios = conn.execute("SELECT * FROM usuarios WHERE perfil_id=?", (id,)).fetchall()
    if request.method == "POST":
        if usuarios:
            flash("No se puede borrar un perfil con usuarios asociados.", "danger")
        else:
            conn.execute("DELETE FROM perfiles WHERE id=?", (id,))
            conn.commit()
            flash("Perfil eliminado.", "success")
        conn.close()
        return redirect(url_for("perfiles_list"))
    conn.close()
    return render_template("perfil_form.html", perfil=perfil, borrar=True)

# ---------------------------
# USUARIOS
# ---------------------------
@app.route("/")
def home():
    conn = get_conn()
    usuarios = conn.execute("""
        SELECT u.id, u.nombre, u.apellidos, u.email, u.telefono, p.nombre as perfil
        FROM usuarios u LEFT JOIN perfiles p ON u.perfil_id = p.id
        ORDER BY u.nombre ASC
    """).fetchall()
    conn.close()
    return render_template("home.html", usuarios=usuarios)

@app.route("/usuario/<int:id>")
def usuario_detalle(id):
    conn = get_conn()
    usuario = conn.execute("""
        SELECT u.*, p.nombre as perfil_nombre FROM usuarios u
        LEFT JOIN perfiles p ON u.perfil_id = p.id
        WHERE u.id = ?
    """, (id,)).fetchone()
    perfiles = conn.execute("SELECT * FROM perfiles").fetchall()
    conn.close()
    return render_template("usuario_detalle.html", usuario=usuario, perfiles=perfiles)

@app.route("/usuario/nuevo", methods=["GET", "POST"])
def usuario_nuevo():
    conn = get_conn()
    perfiles = conn.execute("SELECT * FROM perfiles").fetchall()
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        perfil_id = request.form["perfil_id"]
        conn.execute("""
            INSERT INTO usuarios(nombre, apellidos, email, telefono, perfil_id)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, apellidos, email, telefono, perfil_id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    conn.close()
    return render_template("usuario_form.html", usuario=None, perfiles=perfiles)

@app.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
def usuario_editar(id):
    conn = get_conn()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()
    perfiles = conn.execute("SELECT * FROM perfiles").fetchall()
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        perfil_id = request.form["perfil_id"]
        conn.execute("""
            UPDATE usuarios
            SET nombre=?, apellidos=?, email=?, telefono=?, perfil_id=?
            WHERE id=?
        """, (nombre, apellidos, email, telefono, perfil_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    conn.close()
    return render_template("usuario_form.html", usuario=usuario, perfiles=perfiles)

@app.route("/usuario/borrar/<int:id>", methods=["GET", "POST"])
def usuario_borrar(id):
    conn = get_conn()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()
    if request.method == "POST":
        conn.execute("DELETE FROM usuarios WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    conn.close()
    return render_template("usuario_detalle.html", usuario=usuario, borrar=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
