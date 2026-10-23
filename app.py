from flask import Flask, request
import sqlite3, os

app = Flask(__name__)
DB_NAME = "farmacia.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
    
        cursor.execute("""
        CREATE TABLE proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            direccion TEXT
        )
        """)
     
        cursor.execute("""
        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            precio REAL,
            stock INTEGER,
            proveedor_id INTEGER,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
        """)
       
        cursor.execute("""
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            email TEXT,
            telefono TEXT
        )
        """)
      
        cursor.execute("""
        CREATE TABLE ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha TEXT,
            total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            medicamento_id INTEGER,
            cantidad INTEGER,
            subtotal REAL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
        )
        """)
        
        cursor.execute("INSERT INTO proveedores (nombre, telefono, direccion) VALUES (?,?,?)",
                       ("Laboratorios ACME", "78945612", "Av. Central #123"))
        cursor.execute("INSERT INTO proveedores (nombre, telefono, direccion) VALUES (?,?,?)",
                       ("Farmacéutica Salud", "65478912", "Calle Salud #45"))

        cursor.execute("INSERT INTO medicamentos (nombre, precio, stock, proveedor_id) VALUES (?,?,?,?)",
                       ("Paracetamol 500mg", 2.5, 100, 1))
        cursor.execute("INSERT INTO medicamentos (nombre, precio, stock, proveedor_id) VALUES (?,?,?,?)",
                       ("Ibuprofeno 400mg", 3.0, 80, 1))
        cursor.execute("INSERT INTO medicamentos (nombre, precio, stock, proveedor_id) VALUES (?,?,?,?)",
                       ("Amoxicilina 500mg", 5.0, 50, 2))

        cursor.execute("INSERT INTO clientes (nombre, email, telefono) VALUES (?,?,?)",
                       ("Juan Pérez", "juan@example.com", "77788899"))
        cursor.execute("INSERT INTO clientes (nombre, email, telefono) VALUES (?,?,?)",
                       ("María López", "maria@example.com", "66655544"))

        cursor.execute("INSERT INTO ventas (cliente_id, fecha, total) VALUES (?,?,?)",
                       (1, "2026-10-23", 5.0))
        cursor.execute("INSERT INTO detalle_ventas (venta_id, medicamento_id, cantidad, subtotal) VALUES (?,?,?,?)",
                       (1, 1, 2, 5.0))

        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return """
    <h1>Farmacia Online HUGO´s</h1>
    <p>Bienvenido a nuestro servicio</p>
    <ul>
        <li><a href='/medicamentos'>Medicamentos</a></li>
        <li><a href='/clientes'>Clientes</a></li>
        <li><a href='/proveedores'>Proveedores</a></li>
        <li><a href='/ventas'>Ventas</a></li>
    </ul>
    """

@app.route("/medicamentos", methods=["GET"])
def listar_medicamentos():
    conn = get_db_connection()
    meds = conn.execute("SELECT m.id, m.nombre, m.precio, m.stock, p.nombre AS proveedor FROM medicamentos m LEFT JOIN proveedores p ON m.proveedor_id = p.id").fetchall()
    proveedores = conn.execute("SELECT * FROM proveedores").fetchall()
    conn.close()

    html = """
    <h2>Medicamentos en Almacen</h2>
    <table border="1">
      <tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Proveedor</th><th>Acciones</th></tr>
    """
    for m in meds:
        html += f"<tr><td>{m['id']}</td><td>{m['nombre']}</td><td>{m['precio']}</td><td>{m['stock']}</td><td>{m['proveedor']}</td>"
        html += f"<td><form action='/medicamentos/delete/{m['id']}' method='post'><button type='submit'>Eliminar</button></form></td></tr>"
    html += "</table>"

    
    html += """
    <h3>Agregar Medicamento al almacen</h3>
    <form action="/medicamentos/add" method="post">
      Nombre: <input type="text" name="nombre"><br>
      Precio: <input type="text" name="precio"><br>
      Stock: <input type="text" name="stock"><br>
      Proveedor: <select name="proveedor_id">
    """
    for p in proveedores:
        html += f"<option value='{p['id']}'>{p['nombre']}</option>"
    html += "</select><br><button type='submit'>Agregar</button></form>"

    return html

@app.route("/medicamentos/add", methods=["POST"])
def agregar_medicamento():
    nombre = request.form["nombre"]
    precio = float(request.form["precio"])
    stock = int(request.form["stock"])
    proveedor_id = int(request.form["proveedor_id"])
    conn = get_db_connection()
    conn.execute("INSERT INTO medicamentos (nombre, precio, stock, proveedor_id) VALUES (?,?,?,?)",
                 (nombre, precio, stock, proveedor_id))
    conn.commit()
    conn.close()
    return f"<p>Medicamento {nombre} agregado ✅</p><a href='/medicamentos'>Volver</a>"

@app.route("/medicamentos/delete/<int:id>", methods=["POST"])
def eliminar_medicamento(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM medicamentos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return f"<p>Medicamento {id} eliminado ❌</p><a href='/medicamentos'>Volver</a>"


@app.route("/clientes", methods=["GET"])
def listar_clientes():
    conn = get_db_connection()
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()
    html = "<h2>Clientes</h2><table border='1'><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Teléfono</th></tr>"
    for c in clientes:
        html += f"<tr><td>{c['id']}</td><td>{c['nombre']}</td><td>{c['email']}</td><td>{c['telefono']}</td></tr>"
    html += "</table>"
    return html

@app.route("/proveedores", methods=["GET"])
def listar_proveedores():
    conn = get_db_connection()
    proveedores = conn.execute("SELECT * FROM proveedores").fetchall()
    conn.close()
    html = "<h2>Proveedores</h2><table border='1'><tr><th>ID</th><th>Nombre</th><th>Teléfono</th><th>Dirección</th></tr>"
    for p in proveedores:
        html += f"<tr><td>{p['id']}</td><td>{p['nombre']}</td><td>{p['telefono']}</td><td>{p['direccion']}</td></tr>"
    html += "</table>"
    return html


@app.route("/ventas", methods=["GET"])
def listar_ventas():
    conn = get_db_connection()
    ventas = conn.execute("SELECT v.id, v.fecha, v.total, c.nombre AS cliente FROM ventas v JOIN clientes c ON v.cliente_id = c.id").fetchall()
    conn.close()
    html = "<h2>Ventas</h2><table border='1'><tr><th>ID</th><th>Cliente</th><th>Fecha</th><th>Total</th></tr>"
    for v in ventas:
        html += f"<tr><td>{v['id']}</td><td>{v['cliente']}</td><td>{v['fecha']}</td><td>{v['total']}</td></tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
