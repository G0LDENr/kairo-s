import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import hash_password
from database.config import users_col

def migrate_passwords():
    """Migra contraseñas de texto plano a contraseñas hasheadas"""
    print("Iniciando migración de contraseñas...")
    
    # Buscar usuarios con contraseñas en texto plano
    # (asumiendo que las contraseñas hasheadas son bytes o Binary)
    users_with_plain_passwords = users_col.find({
        "contraseña": {"$type": "string"}
    })
    
    migrated_count = 0
    for user in users_with_plain_passwords:
        # Verificar si la contraseña parece ser texto plano (no un hash bcrypt)
        password = user["contraseña"]
        
        # Los hashes bcrypt generalmente comienzan con $2b$ y tienen una longitud específica
        if not password.startswith("$2b$") or len(password) < 50:
            try:
                hashed_password = hash_password(password)
                users_col.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"contraseña": hashed_password}}
                )
                print(f"✓ Contraseña migrada para: {user['correo']}")
                migrated_count += 1
            except Exception as e:
                print(f"✗ Error migrando contraseña para {user['correo']}: {e}")
    
    print(f"\nMigración completada. {migrated_count} contraseñas migradas.")

if __name__ == "__main__":
    # Preguntar confirmación antes de ejecutar
    respuesta = input("¿Estás seguro de que quieres migrar las contraseñas? (sí/no): ")
    if respuesta.lower() in ['sí', 'si', 's', 'yes', 'y']:
        migrate_passwords()
    else:
        print("Migración cancelada.")