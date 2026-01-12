import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib 
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --- CONFIGURACIÓN ---
ruta_proyecto = r"C:\Users\luisc\OneDrive\Documentos\Proyecto_EmoBot"
archivo_dataset = os.path.join(ruta_proyecto, "dataset_emociones_completo.csv")
nombre_modelo = os.path.join(ruta_proyecto, "modelo_emociones_svm.joblib")
nombre_scaler = os.path.join(ruta_proyecto, "scaler_emociones.joblib")

print(" Cargando dataset...")

# 1. Cargar
try:
    data = pd.read_csv(archivo_dataset, na_values='?')
except FileNotFoundError:
    print(f"Error: No se encontró '{archivo_dataset}'")
    exit()

print(f" Dataset cargado: {len(data)} audios.")

# 2. Preparación
y = data['emocion']
X_bruto = data.drop('emocion', axis=1)

X = X_bruto.select_dtypes(include=['float64', 'int64', 'float32', 'int32'])
X = X.dropna(axis=1, how='all').fillna(0)

print(f"Datos listos. Entrenando con el 100% ({len(X)} audios).")

# 3. Escalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. ENTRENAMIENTO EXTREMO
print("\n Iniciando entrenamiento...")
print("   (El modelo está buscando patrones muy finos)")

# C=100 para máxima precisión
model = SVC(kernel='rbf', C=100.0, gamma='scale', random_state=42, probability=True, verbose=True)
model.fit(X_scaled, y)  

print("\nEntrenamiento completado")

# 5. Evaluación
print(" Verificando aprendizaje...")
y_pred_todos = model.predict(X_scaled)
acc = accuracy_score(y, y_pred_todos)

print(f"\n Precisión FINAL: {acc * 100:.2f}%")
print(classification_report(y, y_pred_todos))

# 6. Guardar
print("\n Guardando archivos del modelo C=100...")
joblib.dump(model, nombre_modelo)
joblib.dump(scaler, nombre_scaler)
print(f" ¡LISTO! Modelo guardado en: {ruta_proyecto}")

# 7. Gráfica
cm = confusion_matrix(y, y_pred_todos)
plt.figure(figsize=(10, 8))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=model.classes_, 
            yticklabels=model.classes_)

plt.title(f'Matriz de Confusión - Total {len(data)} Audios')
plt.ylabel('Verdadera')
plt.xlabel('Predicha')
plt.show()

