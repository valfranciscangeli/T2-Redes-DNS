""" Para manejar el caché de la parte 5 vamos a utilizar un archivo txt
En este modulo se encuentran las funciones necesarias para manejarlo """


nombre_archivo_cache = "resolver_cache.txt"
# ============================================================


def ordenar_registro(lista_de_registros, llave="n_consultas"):
    lista_ordenada = sorted(lista_de_registros, key=lambda x: x[llave])
    return lista_ordenada

# ============================================================


def buscar_ip_por_nombre(lista_de_registros, dominio):
    for registro in lista_de_registros:
        if registro['nombre_dominio'] == dominio:
            return registro['ip_dominio']
    return None  # si no se encuentra

# ============================================================


def escribir_cache(nombre_archivo_cache, lista_registros):
    with open(nombre_archivo_cache, 'w') as cache:
        for registro in lista_registros:
            linea = f"{registro['nombre_dominio']}, {registro['ip_dominio']}, {registro['n_consultas']}\n"
            cache.write(linea)

# ============================================================


def leer_cache(nombre_archivo_cache):
    registros = []

    with open(nombre_archivo_cache, 'r') as cache:
        for registro in cache:
            nombre_dominio, ip_dominio, n_consultas = registro.strip().split(',')

            datos = {
                'nombre_dominio': nombre_dominio,
                'ip_dominio': ip_dominio,
                'n_consultas': int(n_consultas)
            }
            registros.append(datos)

    return registros

# ============================================================


def actualizar_registros(lista_de_registros, nombre_dominio, ip_dominio):
    # buscamos si el dominio ya existe en la lista
    for registro in lista_de_registros:
        if registro['nombre_dominio'] == nombre_dominio:
            registro['n_consultas'] += 1  # Incrementar n_consultas
            
            escribir_cache(nombre_archivo_cache, lista_de_registros)
            return

    # si el dominio no está, se agrega --------------------

    # creamos un nuevo registro
    nuevo_diccionario = {
        'nombre_dominio': nombre_dominio,
        'ip_dominio': ip_dominio,
        'n_consultas': 1  # empieza en 1 ya que es la primera consulta
    }

    if len(lista_de_registros) >= 5:  # reemplazamos por el menor n_consultas
        menor_n_consultas = float('inf')  # infinito
        indice_menor = -1

        for indice, registro in enumerate(lista_de_registros):
            if registro['n_consultas'] < menor_n_consultas:
                menor_n_consultas = registro['n_consultas']
                indice_menor = indice

        if indice_menor != -1:
            lista_de_registros[indice_menor] = nuevo_diccionario
            return

    lista_de_registros.append(nuevo_diccionario)
    escribir_cache(nombre_archivo_cache, lista_de_registros)

# ============================================================
def borrar_todos_los_registros(nombre_archivo_cache):
    
    with open(nombre_archivo_cache, 'w') as cache:
        cache.truncate(0)  # Trunca el archivo, eliminando todo su contenido
    print("caché borrado con exito ...")
