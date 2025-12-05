# ============================================================
#  registro_seguro.py
#  Refactorización - Seguridad - Pruebas Unitarias
#  Autor: Tec. Sup. Carlos Andrés Genovez T.
# ============================================================

import re
import hashlib

# -------------------------------
# Simulación de Base de Datos (Hash Map O(1))
# -------------------------------
db_usuarios = {}   # {email: hash_password}

# -------------------------------
# Validación de Email
# -------------------------------
def validar_email(email: str) -> bool:
    """
    Valida el formato de correo electrónico usando Regex.
    Retorna True si el formato es válido, caso contrario False.
    """
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email) is not None

# -------------------------------
# Validación de Contraseña
# -------------------------------
def validar_password(password: str) -> bool:
    """
    Reglas:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos un número
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

# -------------------------------
# Generación de Hash SHA-256
# -------------------------------
def generar_hash(password: str) -> str:
    """
    Hashea la contraseña utilizando SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# Registrar Usuario
# -------------------------------
def registrar_usuario(email: str, password: str) -> bool:
    """
    Aplica validaciones, hashing y guarda en la simulación de BD.
    Retorna True si el registro es exitoso.
    """

    # FAIL FAST → si cualquier validación falla, detener de inmediato
    if not validar_email(email):
        return False
    
    if not validar_password(password):
        return False
    
    if email in db_usuarios:
        return False  # usuario ya existe

    # Hashing antes de guardar (Seguridad)
    password_hash = generar_hash(password)
    db_usuarios[email] = password_hash
    return True

# -------------------------------
# PRUEBAS UNITARIAS
# -------------------------------
def ejecutar_pruebas():
    print("=== INICIANDO PRUEBAS UNITARIAS ===\n")
    
    # Caso 1: Registro exitoso
    resultado1 = registrar_usuario("usuario@test.com", "Password123")
    print("Caso 1 - Registro exitoso:",
          "✅ PASÓ" if resultado1 else "❌ FALLÓ")

    # Caso 2: Email inválido
    resultado2 = registrar_usuario("usuario#invalido", "Password123")
    print("Caso 2 - Email inválido:",
          "✅ PASÓ" if resultado2 is False else "❌ FALLÓ")

    # Caso 3: Contraseña débil
    resultado3 = registrar_usuario("persona@test.com", "weak")
    print("Caso 3 - Contraseña débil:",
          "✅ PASÓ" if resultado3 is False else "❌ FALLÓ")

    print("\n=== FIN DE PRUEBAS ===")

# Autoejecución
if __name__ == "__main__":
    ejecutar_pruebas()
