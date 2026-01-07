import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib  # Importante para guardar
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --- CONFIGURACIÓN ---
archivo_dataset = "dataset_emociones_completo.csv"
nombre_modelo = 'modelo_emociones_svm.joblib'
nombre_scaler = 'scaler_emociones.joblib'

print("🔄 Cargando dataset para ENTRENAR un nuevo modelo...")

# 1. Cargar el Dataset
try:
    data = pd.read_csv(archivo_dataset, na_values='?')
except FileNotFoundError:
    print(f"❌ Error: No se encontró '{archivo_dataset}'")
    exit()

print(f"✅ Dataset cargado: {len(data)} audios.")

# 2. PREPARACIÓN DE DATOS
y = data['emocion']
X_bruto = data.drop('emocion', axis=1)

# Limpieza: Solo números y quitar vacíos
X = X_bruto.select_dtypes(include=['float64', 'int64', 'float32', 'int32'])
X = X.dropna(axis=1, how='all').fillna(0)

print(f"🧹 Datos listos. Se usaran {len(X)} audios para el entrenamiento.")

# 3. ESCALAR (Ajustamos con el 100% de los datos para el modelo final)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. ENTRENAMIENTO (CREACIÓN DEL MODELO)
print("\n🧠 Entrenando el modelo (aprendiendo patrones)...")
print("   (Esto puede tardar unos minutos...)")

# verbose=True te mostrará el progreso
model = SVC(kernel='rbf', C=1.0, random_state=42, probability=True, verbose=True)
model.fit(X_scaled, y)  

print("\n¡Entrenamiento completado!")

# 5. EVALUACIÓN DE CONFIRMACIÓN (Verificamos qué aprendió)
print("🔍 Verificando aprendizaje (Matriz de Confusión)...")
y_pred_todos = model.predict(X_scaled)
acc = accuracy_score(y, y_pred_todos)

print(f"\nPrecisión sobre el dataset completo: {acc * 100:.2f}%")
print(classification_report(y, y_pred_todos))

# 6. GUARDAR (ESTA ES LA PARTE QUE FALTABA EN TU OTRO CÓDIGO)
print("\nGUARDANDO ARCHIVOS .JOBLIB...")
joblib.dump(model, nombre_modelo)
joblib.dump(scaler, nombre_scaler)
print(f"✅ ¡LISTO! Se crearon: '{nombre_modelo}' y '{nombre_scaler}'")

# 7. GENERAR LA GRÁFICA AZUL
cm = confusion_matrix(y, y_pred_todos)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=model.classes_, 
            yticklabels=model.classes_)
plt.title(f'Matriz de Confusión - Total {len(data)} Audios')
plt.ylabel('Verdadera')
plt.xlabel('Predicha')
plt.show()