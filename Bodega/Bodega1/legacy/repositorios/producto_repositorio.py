from Bodega1.legacy.conexion import ConexionBD
from Bodega1.legacy.models.producto import Producto

class ProductoRepositorio:
    def __init__(self, conexion):
        self.conexion = conexion

    def crear(self, nombre, precio, categoria_id, stock_inicial=0):
        
        print(f" DIAGNOSTICO REPOSITORIO: stock_inicial recibido = {stock_inicial} ")
        
        
        nombre_limpio = nombre.strip()
        if not nombre_limpio or len(nombre_limpio) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")

        if nombre_limpio.isdigit():
            raise ValueError("El nombre no puede contener solo numeros")

        if not any(c.isalpha() for c in nombre_limpio):
            raise ValueError("El nombre debe contener al menos una letra")

        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0")

        print(f"DEBUG: Creando producto - Nombre: {nombre}, Precio: {precio}, Stock: {stock_inicial}, Categoria: {categoria_id}")

        cursor = self.conexion.conexion.cursor()

        # Convertir todo a tipos explícitos
        params = (
            str(nombre), 
            float(precio), 
            int(stock_inicial), 
            int(categoria_id)
        )

        cursor.execute("""
            INSERT INTO Producto (nombre, precio, stock, categoria_id, activo)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, 1)
        """, params)

        nuevo_id = cursor.fetchone()[0]

        # Verificación inmediata
        cursor.execute("SELECT stock FROM Producto WHERE id = ?", (nuevo_id,))
        stock_verificado = cursor.fetchone()[0]
        print(f"DEBUG VERIFICACION: Producto ID {nuevo_id} creado con stock = {stock_verificado}")

        self.conexion.conexion.commit()
        cursor.close()
        return nuevo_id 
    def obtener_todos(self):
        cursor = self.conexion.conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, precio, stock, categoria_id, activo
            FROM Producto
            WHERE activo = 1
        """)
        filas = cursor.fetchall()
        cursor.close()
        return [
            Producto(
                id=f[0], nombre=f[1], precio=f[2],
                stock=f[3], categoria_id=f[4], activo=bool(f[5])
            )
            for f in filas
        ]

    def obtener_por_id(self, id):
        cursor = self.conexion.conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, precio, stock, categoria_id, activo
            FROM Producto
            WHERE id = ? AND activo = 1
        """, (id,))
        fila = cursor.fetchone()
        cursor.close()
        if fila:
            return Producto(
                id=fila[0], nombre=fila[1], precio=fila[2],
                stock=fila[3], categoria_id=fila[4], activo=bool(fila[5])
            )
        return None

    def actualizar(self, id, nombre, precio, categoria_id):
        cursor = self.conexion.conexion.cursor()
        cursor.execute("""
            UPDATE Producto
            SET nombre = ?, precio = ?, categoria_id = ?
            WHERE id = ? AND activo = 1
        """, (nombre, precio, categoria_id, id))
        filas = cursor.rowcount
        self.conexion.conexion.commit()
        cursor.close()
        return filas > 0

    def eliminar(self, id):
        cursor = self.conexion.conexion.cursor()
        cursor.execute("""
            UPDATE Producto
            SET activo = 0
            WHERE id = ? AND activo = 1
        """, (id,))
        filas = cursor.rowcount
        self.conexion.conexion.commit()
        cursor.close()
        return filas > 0
    