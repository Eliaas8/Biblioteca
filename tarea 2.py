import sqlite3
import unicodedata

def conectar_db():
    return sqlite3.connect('biblioteca.db')

def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def crear_tabla():
    with conectar_db() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT NOT NULL,
            estado TEXT NOT NULL CHECK (estado IN ('leído', 'no leído'))
        )
        ''')
    print("Tabla verificada/creada correctamente.")

def agregar_libro(titulo, autor, genero, estado):
    estado = normalizar_texto(estado)
    if estado == 'leido':
        estado = 'leído'
    elif estado == 'no leido':
        estado = 'no leído'
    elif estado not in ['leído', 'no leído']:
        print("Intenta otra vez. Solo se acepta 'leído' o 'no leído'.")
        return

    with conectar_db() as conn:
        conn.execute('''
            INSERT INTO libros (titulo, autor, genero, estado)
            VALUES (?, ?, ?, ?)
        ''', (titulo, autor, genero, estado))
    print(" Libro agregado.")

def actualizar_libro(libro_id, campo, nuevo_valor):
    if campo not in ['titulo', 'autor', 'genero', 'estado']:
        print(" Campo inválido. Solo puedes actualizar: titulo, autor, genero o estado.")
        return

    try:
        if campo == 'estado':
            nuevo_valor = normalizar_texto(nuevo_valor)
            if nuevo_valor == 'leido':
                nuevo_valor = 'leído'
            elif nuevo_valor == 'no leido':
                nuevo_valor = 'no leído'
            elif nuevo_valor not in ['leído', 'no leído']:
                print(" Estado inválido. Solo se acepta 'leído' o 'no leído'.")
                return

        with conectar_db() as conn:
            conn.execute(f'''
                UPDATE libros
                SET {campo} = ?
                WHERE id = ?
            ''', (nuevo_valor, libro_id))
        print(" Libro actualizado exitosamente.")
    except sqlite3.Error as e:
        print(f" Error al actualizar el libro: {e}")

def eliminar_libro(libro_id):
    with conectar_db() as conn:
        conn.execute('DELETE FROM libros WHERE id = ?', (libro_id,))
    print(" Libro eliminado.")

def ver_libros():
    with conectar_db() as conn:
        cursor = conn.execute('SELECT * FROM libros')
        libros = cursor.fetchall()

    if not libros:
        print(" No hay libros registrados.")
        return

    print("\nListado de libros:")

    for libro in libros:
        print(f"ID: {libro[0]:<3} | "
              f"Título: {libro[1]:<25} | "
              f"Autor: {libro[2]:<20} | "
              f"Género: {libro[3]:<15} | "
              f"Estado: {libro[4]}")

def buscar_libros(busqueda):
    busqueda_norm = normalizar_texto(busqueda)
    with conectar_db() as conn:
        cursor = conn.execute('SELECT * FROM libros')
        libros = cursor.fetchall()

    resultados = []
    for libro in libros:
        titulo, autor, genero = libro[1], libro[2], libro[3]
        if (busqueda_norm in normalizar_texto(titulo)
            or busqueda_norm in normalizar_texto(autor)
            or busqueda_norm in normalizar_texto(genero)):
            resultados.append(libro)

    if not resultados:
        print(" No se encontraron resultados.")
        return

    print("\n Resultados de búsqueda:")
    print("-" * 80)
    for libro in resultados:
        print(f"ID: {libro[0]:<3} | "
              f"Título: {libro[1]:<25} | "
              f"Autor: {libro[2]:<20} | "
              f"Género: {libro[3]:<15} | "
              f"Estado: {libro[4]}")
    print("-" * 80)

def menu():
    crear_tabla()
    while True:
        print("\n       === Biblioteca Personal ===\n")
        print("1. Agregar nuevo libro")
        print("2. Actualizar información de un libro")
        print("3. Eliminar libro existente")
        print("4. Ver listado de libros")
        print("5. Buscar libros")
        print("6. Salir")

        opcion = input("\nSelecciona que accion deseas realizar: ").strip()

        if opcion == '1':
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            genero = input("Género: ").strip()
            estado = input("Estado (leído/no leído): ").strip()
            agregar_libro(titulo, autor, genero, estado)

        elif opcion == '2':
            try:
                libro_id = int(input("ID del libro a actualizar: "))
                campo = input("Campo a actualizar (titulo, autor, genero, estado): ").strip().lower()
                nuevo_valor = input("Nuevo valor: ").strip()
                actualizar_libro(libro_id, campo, nuevo_valor)
            except ValueError:
                print(" ID inválido. Debe ser un número.")

        elif opcion == '3':
            try:
                libro_id = int(input("ID del libro a eliminar: "))
                eliminar_libro(libro_id)
            except ValueError:
                print(" ID inválido. Debe ser un número.")

        elif opcion == '4':
            ver_libros()

        elif opcion == '5':
            busqueda = input("Ingrese título, autor o género a buscar: ").strip()
            buscar_libros(busqueda)

        elif opcion == '6':
            print(" Saliendo.... ¡NO VUELAS :) !")
            break

        else:
            print(" Opción inválida, hazlo de nuevo.")

if __name__ == "__main__":
    menu()

