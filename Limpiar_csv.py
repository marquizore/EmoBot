import os
import subprocess
import threading
import pandas as pd # Usaremos pandas para una limpieza más robusta y sencilla

# --- CONFIGURACIÓN ---
ruta_opensmile = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\opensmile-3.0.2-windows-x86_64\opensmile-3.0.2-windows-x86_64\bin\SMILExtract.exe"
ruta_config = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\opensmile-3.0.2-windows-x86_64\opensmile-3.0.2-windows-x86_64\config\emobase\emobase.conf"

# Carpeta base donde están audios organizados por emoción
ruta_audios = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\audios"

# Carpeta donde se guardarán los CSV generados
ruta_salida = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\features"
os.makedirs(ruta_salida, exist_ok=True)


# --- FUNCIÓN QUE LIMPIA EL ENCABEZADO DEL CSV ---
def limpiar_csv(ruta_csv):
    """
    Lee un archivo CSV generado por OpenSMILE, elimina el encabezado ARFF
    y lo guarda de nuevo conteniendo únicamente los valores numéricos.
    """
    try:
        # Lee el archivo buscando la línea que no comienza con '@' ni es un espacio en blanco
        with open(ruta_csv, 'r') as f:
            lineas = f.readlines()
        
        # Filtra para encontrar la línea de datos (la última, usualmente)
        linea_de_datos = None
        for linea in reversed(lineas):
            linea_limpia = linea.strip()
            if linea_limpia and not linea_limpia.startswith('@'):
                linea_de_datos = linea_limpia
                break

        # Si se encontró la línea de datos, se sobrescribe el archivo
        if linea_de_datos:
            with open(ruta_csv, 'w') as f:
                f.write(linea_de_datos)
        else:
            # Si no hay datos, se podría eliminar el archivo o dejarlo vacío
            os.remove(ruta_csv) 
            print(f"   ⚠️ No se encontraron datos en {os.path.basename(ruta_csv)}, archivo eliminado.")

    except Exception as e:
        print(f"   ❌ Error al limpiar el archivo {os.path.basename(ruta_csv)}: {e}")


# --- FUNCIÓN QUE PROCESA UN SOLO ARCHIVO ---
def procesar_audio(ruta_audio, emocion, archivo):
    """Ejecuta OpenSMILE para extraer características de un audio y luego limpia el CSV."""
    nombre_salida = f"{emocion}_{os.path.splitext(archivo)[0]}.csv"
    ruta_csv = os.path.join(ruta_salida, nombre_salida)

    # El argumento -O ya define el archivo de salida. 
    # El argumento -output no es necesario y puede causar conflictos.
    comando = [
        ruta_opensmile,
        "-C", ruta_config,
        "-I", ruta_audio,
        "-O", ruta_csv,
        "-instname", f"{emocion}_{archivo}",
        "-nologfile",
    ]

    print(f"   🎙️ Analizando (hilo): {archivo}")
    # Se oculta la salida de la consola para no saturar la terminal
    subprocess.run(comando, capture_output=True, text=True)

    if os.path.exists(ruta_csv):
        print(f"   ✅ CSV generado: {os.path.basename(ruta_csv)}. Limpiando encabezado...")
        # Llama a la nueva función para limpiar el archivo
        limpiar_csv(ruta_csv)
    else:
        print(f"   ❌ Error al procesar {archivo}")


# --- 1. RECORRER CARPETAS DE EMOCIONES ---
print("🎧 Procesando audios automáticamente con hilos...\n")
hilos = []

# Obtiene la lista de emociones y la ordena para un procesamiento consistente
emociones = sorted([d for d in os.listdir(ruta_audios) if os.path.isdir(os.path.join(ruta_audios, d))])

for emocion in emociones:
    carpeta_emocion = os.path.join(ruta_audios, emocion)
    
    print(f"🎭 Procesando emoción: {emocion}")

    # Obtiene la lista de archivos y la ordena
    archivos_wav = sorted([f for f in os.listdir(carpeta_emocion) if f.lower().endswith(".wav")])

    for archivo in archivos_wav:
        ruta_audio = os.path.join(carpeta_emocion, archivo)

        # Crear hilo para cada audio
        hilo = threading.Thread(target=procesar_audio, args=(ruta_audio, emocion, archivo))
        hilos.append(hilo)
        hilo.start()

# --- 2. ESPERAR A QUE TERMINEN TODOS LOS HILOS ---
for hilo in hilos:
    hilo.join()

print("\n🏁 Proceso completado. Todos los audios fueron analizados y convertidos a CSV.")

# --- 3. REVISAR CUÁNTOS CSV SE GENERARON ---
archivos_generados = len([f for f in os.listdir(ruta_salida) if f.endswith(".csv")])
print(f"\n📊 Total de archivos CSV limpios generados: {archivos_generados}")