from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

# Leer las variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Verificar que existan
if not url or not key:
    print("❌ Error: No se leyeron SUPABASE_URL o SUPABASE_KEY del archivo .env")
    print(f"URL leída: {url}")
    print(f"Key leída: {key}")
    exit()

print(f"🔗 URL: {url}")
print(f"🔑 Key: {key[:20]}...")  # Muestra solo los primeros 20 caracteres

# Crear cliente
supabase = create_client(url, key)

# Probar conexión
try:
    response = supabase.table("Participantes").select("*").execute()
    print("\n✅ ¡Conexión exitosa con Supabase!")
    print(f"📊 Participantes encontrados: {len(response.data)}")
    for p in response.data:
        print(f"  - {p['nombre']} ({p['correo']})")
except Exception as e:
    print(f"\n❌ Error: {e}")
