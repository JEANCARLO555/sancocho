3
# importamos los módulos necesarios
import json
from datetime import datetime, timedelta

# Nombres de los archivos donde se guardarán los datos
ARCHIVO_CLIENTES = "Clientes.json"
ARCHIVO_MESAS = "Mesas.json"
ARCHIVO_RESERVAS = "Reservas.json"

# Horario de apertura del restaurante (Regla R3)
HORA_APERTURA = "12:00"
HORA_CIERRE = "22:00"

# Antelación mínima exigida para reservar (Regla R4)
ANTELACION_MINIMA_MINUTOS = 30


#=========================================
# FUNCIONES GENÉRICAS PARA CARGAR Y GUARDAR
#=========================================

def cargar_datos(archivo):
    try:
        with open(archivo, "r") as f:
            return json.load(f)
    except:
        return []


def guardar_datos(archivo, datos):
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)


#==========================================
# FUNCIONES DE VALIDACIÓN
#==========================================

def validar_numerico(mensaje):
    while True:
        dato = input(mensaje)
        if dato.isdigit():
            return dato
        else:
            print("❌ Error: solo se permiten datos numéricos")


def validar_texto(mensaje):
    while True:
        dato = input(mensaje).strip()
        if dato != "":
            return dato
        else:
            print("❌ Error: no puede estar vacío")


def validar_fecha(mensaje):
    while True:
        dato = input(mensaje).strip()
        try:
            datetime.strptime(dato, "%Y-%m-%d")
            return dato
        except ValueError:
            print("❌ Error: formato de fecha inválido. Use AAAA-MM-DD")


def validar_hora(mensaje):
    while True:
        dato = input(mensaje).strip()
        try:
            datetime.strptime(dato, "%H:%M")
            return dato
        except ValueError:
            print("❌ Error: formato de hora inválido. Use HH:MM")


#==========================================
# GESTIÓN DE CLIENTES
#==========================================

def adicionar_cliente():
    datos = cargar_datos(ARCHIVO_CLIENTES)
    identificacion = validar_numerico("Número de identificación: ")

    for cliente in datos:
        if cliente["identificacion"] == identificacion:
            print("❌ Ya existe un cliente con esa identificación")
            return

    nuevo_cliente = {
        "identificacion": identificacion,
        "nombre": validar_texto("Nombre completo: "),
        "telefono": validar_numerico("Teléfono: "),
        "correo": validar_texto("Correo electrónico: ")
    }

    datos.append(nuevo_cliente)
    guardar_datos(ARCHIVO_CLIENTES, datos)
    print("✅ Cliente registrado correctamente.")


def mostrar_clientes():
    datos = cargar_datos(ARCHIVO_CLIENTES)
    if len(datos) == 0:
        print("No hay clientes registrados")
    else:
        for cliente in datos:
            print("------------------------------")
            for clave, valor in cliente.items():
                print(f"{clave}: {valor}")


def buscar_cliente(identificacion):
    datos = cargar_datos(ARCHIVO_CLIENTES)
    for cliente in datos:
        if cliente["identificacion"] == identificacion:
            return cliente
    return None


#==========================================
# GESTIÓN DE MESAS
#==========================================

def adicionar_mesa():
    datos = cargar_datos(ARCHIVO_MESAS)
    numero_mesa = validar_numerico("Número de mesa: ")

    for mesa in datos:
        if mesa["numero_mesa"] == numero_mesa:
            print("❌ Ya existe una mesa con ese número")
            return

    nueva_mesa = {
        "numero_mesa": numero_mesa,
        "capacidad_maxima": validar_numerico("Capacidad máxima: "),
        "zona": validar_texto("Zona del restaurante: ")
    }

    datos.append(nueva_mesa)
    guardar_datos(ARCHIVO_MESAS, datos)
    print("✅ Mesa registrada correctamente.")


def mostrar_mesas():
    datos = cargar_datos(ARCHIVO_MESAS)
    if len(datos) == 0:
        print("No hay mesas registradas")
    else:
        for mesa in datos:
            print("------------------------------")
            for clave, valor in mesa.items():
                print(f"{clave}: {valor}")


def buscar_mesa(numero_mesa):
    datos = cargar_datos(ARCHIVO_MESAS)
    for mesa in datos:
        if mesa["numero_mesa"] == numero_mesa:
            return mesa
    return None


#==========================================
# GESTIÓN DE RESERVAS
#==========================================

def adicionar_reserva():
    datos = cargar_datos(ARCHIVO_RESERVAS)

    # -------- R5: la reserva debe estar asociada a un cliente y una mesa existentes --------
    identificacion_cliente = validar_numerico("Identificación del cliente: ")
    cliente = buscar_cliente(identificacion_cliente)
    if cliente is None:
        print("❌ Error (R5): el cliente no existe. Regístrelo primero.")
        return

    numero_mesa = validar_numerico("Número de mesa: ")
    mesa = buscar_mesa(numero_mesa)
    if mesa is None:
        print("❌ Error (R5): la mesa no existe. Regístrela primero.")
        return

    # -------- R1: el número de comensales no puede superar la capacidad de la mesa --------
    numero_personas = validar_numerico("Número de personas: ")
    if int(numero_personas) > int(mesa["capacidad_maxima"]):
        print(f"❌ Error (R1): la mesa {numero_mesa} solo admite {mesa['capacidad_maxima']} personas")
        return

    fecha = validar_fecha("Fecha de la reserva (AAAA-MM-DD): ")
    hora = validar_hora("Hora de la reserva (HH:MM): ")

    # -------- R3: la reserva debe estar dentro del horario de apertura --------
    if not (HORA_APERTURA <= hora <= HORA_CIERRE):
        print(f"❌ Error (R3): el restaurante solo atiende entre {HORA_APERTURA} y {HORA_CIERRE}")
        return

    # -------- R4: la reserva debe hacerse con al menos 30 minutos de antelación --------
    fecha_hora_reserva = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    if fecha_hora_reserva < datetime.now() + timedelta(minutes=ANTELACION_MINIMA_MINUTOS):
        print(f"❌ Error (R4): la reserva debe hacerse con al menos {ANTELACION_MINIMA_MINUTOS} minutos de antelación")
        return

    # -------- R2: no se puede asignar la misma mesa al mismo cliente en el mismo horario --------
    for reserva in datos:
        if (reserva["numero_mesa"] == numero_mesa and
                reserva["identificacion_cliente"] == identificacion_cliente and
                reserva["fecha"] == fecha and
                reserva["hora"] == hora and
                reserva["estado"] != "cancelada"):
            print("❌ Error (R2): ya existe una reserva de este cliente para esa mesa en ese horario")
            return

    nueva_reserva = {
        "id_reserva": str(len(datos) + 1),
        "identificacion_cliente": identificacion_cliente,
        "nombre_cliente": cliente["nombre"],
        "numero_mesa": numero_mesa,
        "numero_personas": numero_personas,
        "fecha": fecha,
        "hora": hora,
        "duracion_estimada_minutos": validar_numerico("Duración estimada (minutos): "),
        "estado": "pendiente"
    }

    datos.append(nueva_reserva)
    guardar_datos(ARCHIVO_RESERVAS, datos)
    print("✅ Reserva registrada correctamente.")


def mostrar_reservas():
    datos = cargar_datos(ARCHIVO_RESERVAS)
    if len(datos) == 0:
        print("No hay reservas registradas")
    else:
        for reserva in datos:
            print("------------------------------")
            for clave, valor in reserva.items():
                print(f"{clave}: {valor}")


def confirmar_reserva():
    datos = cargar_datos(ARCHIVO_RESERVAS)
    id_reserva = validar_numerico("Ingrese el id de la reserva a confirmar: ")

    for reserva in datos:
        if reserva["id_reserva"] == id_reserva:
            reserva["estado"] = "confirmada"
            guardar_datos(ARCHIVO_RESERVAS, datos)
            print("✅ Reserva confirmada")
            return
    print("Reserva no encontrada.")


def cancelar_reserva():
    datos = cargar_datos(ARCHIVO_RESERVAS)
    id_reserva = validar_numerico("Ingrese el id de la reserva a cancelar: ")

    for reserva in datos:
        if reserva["id_reserva"] == id_reserva:
            op = input("¿Está seguro que desea cancelar la reserva? 1. Sí  2. No: ")
            if op == "1":
                reserva["estado"] = "cancelada"
                guardar_datos(ARCHIVO_RESERVAS, datos)
                print("✅ Reserva cancelada")
                return
            else:
                return
    print("Reserva no encontrada.")


#==========================================
# SUBMENÚS
#==========================================

def menu_clientes():
    while True:
        print("\n---- GESTIÓN DE CLIENTES ----")
        print("1. Adicionar cliente")
        print("2. Mostrar clientes")
        print("3. Volver")
        opcion = input("Selecciona la opción: ")
        if opcion == "1":
            adicionar_cliente()
        elif opcion == "2":
            mostrar_clientes()
        elif opcion == "3":
            break
        else:
            print("Opción no válida...")


def menu_mesas():
    while True:
        print("\n---- GESTIÓN DE MESAS ----")
        print("1. Adicionar mesa")
        print("2. Mostrar mesas")
        print("3. Volver")
        opcion = input("Selecciona la opción: ")
        if opcion == "1":
            adicionar_mesa()
        elif opcion == "2":
            mostrar_mesas()
        elif opcion == "3":
            break
        else:
            print("Opción no válida...")


def menu_reservas():
    while True:
        print("\n---- GESTIÓN DE RESERVAS ----")
        print("1. Adicionar reserva")
        print("2. Mostrar reservas")
        print("3. Confirmar reserva")
        print("4. Cancelar reserva")
        print("5. Volver")
        opcion = input("Selecciona la opción: ")
        if opcion == "1":
            adicionar_reserva()
        elif opcion == "2":
            mostrar_reservas()
        elif opcion == "3":
            confirmar_reserva()
        elif opcion == "4":
            cancelar_reserva()
        elif opcion == "5":
            break
        else:
            print("Opción no válida...")


#==========================================
# MENÚ PRINCIPAL
#==========================================

def menu():
    while True:
        print("\n----BIENVENIDO AL SISTEMA DE RESERVAS DE MESAS-----------")
        print("1. GESTIONAR CLIENTES")
        print("2. GESTIONAR MESAS")
        print("3. GESTIONAR RESERVAS")
        print("4. SALIR")

        opcion = input("Selecciona la opción: ")
        if opcion == "1":
            menu_clientes()
        elif opcion == "2":
            menu_mesas()
        elif opcion == "3":
            menu_reservas()
        elif opcion == "4":
            print("Good bye....")
            break
        else:
            print("Opción no válida...")


# ejecutamos el menú   #no se que estaoy haciendo
menu()
