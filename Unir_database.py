import os
import pandas as pd

# --- CONFIGURACIÓN ---
# Ruta a la carpeta que contiene TODOS tus archivos CSV generados
ruta_features = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot\features"
# Nombre del archivo final
archivo_salida = "dataset_emociones_completo.csv"

# Lista para almacenar los DataFrames
lista_de_dataframes = []

print(f"📂 Iniciando unión de archivos desde: {ruta_features}")

# Obtener lista de archivos CSV
archivos_csv = [f for f in os.listdir(ruta_features) if f.endswith(".csv")]
total_archivos = len(archivos_csv)

print(f"📊 Se detectaron {total_archivos} archivos CSV en la carpeta.")

if total_archivos == 0:
    print("❌ Error: La carpeta 'features' está vacía. Ejecuta primero el script de extracción.")
    exit()

# Recorrer cada archivo
for i, archivo_csv in enumerate(archivos_csv):
    try:
        # 1. Extraer la emoción (Todo lo que está antes del primer guion bajo)
        # Formato esperado: "emocion_loquesea.csv"
        emocion = archivo_csv.split('_')[0]
        
        # Ruta completa
        ruta_completa = os.path.join(ruta_features, archivo_csv)
        
        # 2. Leer CSV
        # IMPORTANTE: na_values='?' convierte los signos de interrogación de OpenSMILE en NaN reales
        df_audio = pd.read_csv(ruta_completa, header=None, na_values='?')
        
        # 3. Añadir columna de emoción al inicio
        df_audio.insert(0, 'emocion', emocion)
        
        lista_de_dataframes.append(df_audio)

        # Mostrar progreso cada 100 archivos para saber que no se trabó
        if (i + 1) % 100 == 0:
            print(f"   ... procesados {i + 1}/{total_archivos}")

    except Exception as e:
        print(f"   ⚠️ Error leyendo '{archivo_csv}': {e}")

# --- UNIÓN Y LIMPIEZA FINAL ---
if lista_de_dataframes:
    print("\n⏳ Uniendo todos los datos en un solo archivo...")
    dataset_completo = pd.concat(lista_de_dataframes, ignore_index=True)
    
    print(f"   Dimensiones iniciales: {dataset_completo.shape}")

    # 4. LIMPIEZA AUTOMÁTICA DE COLUMNAS BASURA
    # Si una columna entera está vacía (o tenía puros '?'), se borra.
    dataset_limpio = dataset_completo.dropna(axis=1, how='all')
    
    # Rellenar cualquier hueco pequeño restante con 0 (seguridad para SVM)
    dataset_limpio = dataset_limpio.fillna(0)

    # 5. Guardar
    dataset_limpio.to_csv(archivo_salida, index=False)
    
    print("\n" + "="*40)
    print(f"🎉 ¡ÉXITO! Dataset guardado en: {archivo_salida}")
    print(f"📏 Tamaño final: {dataset_limpio.shape[0]} filas x {dataset_limpio.shape[1]} columnas")
    print("-" * 20)
    print("📢 RESUMEN POR EMOCIÓN:")
    print(dataset_limpio['emocion'].value_counts())
    print("="*40)

else:
    print("\n❌ No se pudo generar el dataset (lista vacía).")