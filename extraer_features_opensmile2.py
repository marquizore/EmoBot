import os
import subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN ---
ruta_opensmile = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\opensmile-3.0.2-windows-x86_64\opensmile-3.0.2-windows-x86_64\bin\SMILExtract.exe"
ruta_config = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\opensmile-3.0.2-windows-x86_64\opensmile-3.0.2-windows-x86_64\config\emobase\emobase.conf"
ruta_audios = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\audios"
ruta_salida = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\features"

os.makedirs(ruta_salida, exist_ok=True)

def limpiar_csv_con_pandas(ruta_csv):
    try:
        # Lee ignorando '@' y sin encabezado
        df = pd.read_csv(ruta_csv, comment='@', header=None)
        # Guarda eliminando la primera columna (texto)
        df.iloc[:, 1:].to_csv(ruta_csv, header=False, index=False)
    except Exception:
        if os.path.exists(ruta_csv):
            os.remove(ruta_csv)

def procesar_audio(args):
    ruta_audio_completa, emocion, nombre_archivo_unico = args
    
    # Creamos un nombre de salida único para evitar sobrescribir si hay nombres repetidos en subcarpetas
    nombre_salida = f"{emocion}_{nombre_archivo_unico}.csv"
    ruta_csv = os.path.join(ruta_salida, nombre_salida)

    if os.path.exists(ruta_csv):
        return # Ya existe, saltar

    comando = [
        ruta_opensmile, "-C", ruta_config, "-I", ruta_audio_completa, "-O", ruta_csv,
        "-instname", "dummy", "-nologfile"
    ]

    subprocess.run(comando, capture_output=True, text=True)

    if os.path.exists(ruta_csv):
        limpiar_csv_con_pandas(ruta_csv)
        print(f"✅ {nombre_archivo_unico}")
    else:
        print(f"❌ Falló: {nombre_archivo_unico}")

if __name__ == "__main__":
    print("🚀 Iniciando búsqueda PROFUNDA de archivos...")
    
    tareas = []
    
    # 1. Obtener lista de emociones (carpetas en la raíz)
    carpetas_emociones = [d for d in os.listdir(ruta_audios) if os.path.isdir(os.path.join(ruta_audios, d))]
    
    for emocion in carpetas_emociones:
        ruta_carpeta_emocion = os.path.join(ruta_audios, emocion)
        
        # 2. USAR OS.WALK PARA BUSCAR EN SUBCARPETAS
        for root, dirs, files in os.walk(ruta_carpeta_emocion):
            for archivo in files:
                if archivo.lower().endswith(".wav"):
                    ruta_completa = os.path.join(root, archivo)
                    
                    # Generar un ID único para el archivo (usando parte de la ruta para diferenciar)
                    # Ejemplo: si está en audios/feliz/sesion1/audio.wav -> id: sesion1_audio
                    padre = os.path.basename(root)
                    if padre == emocion:
                        nombre_unico = os.path.splitext(archivo)[0]
                    else:
                        nombre_unico = f"{padre}_{os.path.splitext(archivo)[0]}"
                    
                    tareas.append((ruta_completa, emocion, nombre_unico))

    total_encontrados = len(tareas)
    print(f"📂 Se encontraron {total_encontrados} archivos WAV en total (incluyendo subcarpetas).")
    
    if total_encontrados > 0:
        print("⚡ Procesando...")
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            executor.map(procesar_audio, tareas)
        print("🏁 Fin del proceso.")
    else:
        print("⚠️ No se encontraron archivos .wav. Verifica la ruta.")