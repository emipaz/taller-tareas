from os import path
import json
from pickle import load , dump
from random import choice
from string import ascii_letters as letras
from string import digits as digitos
from string import punctuation as simbolos

# Funciones de gestión de usuarios
def cargar_datos(archivo):
    """Carga los datos desde un archivo .dat usando pickle."""
    if path.exists(archivo):
        with open(archivo, 'rb') as f:
            return load(f)
    return []

def guardar_datos(datos, archivo):
    """Guarda los datos en un archivo .dat usando pickle."""
    with open(archivo, 'wb') as f:
        dump(datos, f)

def guardar_json(dato, archivo):
    """Guarda los datos en un archivo .json."""
    if path.exists(archivo):
        with open(archivo, 'r') as f:
            datos = json.load(f)
    else:    
        datos = []
    datos.append(dato)
    with open(archivo, 'w') as f:
        json.dump(datos, f)

def hay_admin(usuario):
    if usuario:
        return any(x.rol == "admin" for x in usuario)
    else:
        return False

def generar_password(longitud=12):
    """Genera una contraseña aleatoria de la longitud especificada."""
    caracteres = letras + digitos # + simbolos
    return ''.join(choice(caracteres) for _ in range(longitud))

