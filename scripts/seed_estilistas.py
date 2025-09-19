import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import estilistas_col
from faker import Faker
import random
from tqdm import tqdm

fake = Faker("es_MX")
apellidos = ["García", "López", "Martínez", "Hernández", "Pérez", "Sánchez", "Ramírez", "Cruz", "Flores", "Gómez"]

def generar_estilistas_masivo(cantidad=100):
    print(f"🚀 Generando {cantidad} estilistas...")
    estilistas_col.delete_many({})  # Opcional: limpia la colección antes de insertar

    docs = []
    batch_size = 100
    for i in tqdm(range(cantidad), desc="Creando estilistas"):
        nombre_completo = f"{fake.first_name()} {random.choice(apellidos)}"
        telefono = fake.msisdn()[:10]
        docs.append({
            "nombre": nombre_completo,
            "telefono": telefono,
            "horarios": {}
        })
        if len(docs) >= batch_size:
            estilistas_col.insert_many(docs)
            docs = []
    if docs:
        estilistas_col.insert_many(docs)
    print(f"✅ {cantidad} estilistas insertados correctamente.")

if __name__ == "__main__":
    generar_estilistas_masivo(100)
