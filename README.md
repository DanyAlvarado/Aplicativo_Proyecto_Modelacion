# Gasolinera Shell — Aplicativo de Análisis para Simulación

Aplicativo desarrollado en Python con Streamlit para analizar los datos
recolectados de la Gasolinera Shell y obtener los parámetros necesarios
para construir el modelo de simulación en Simio.

## Requisitos previos

- Python 3.10 o superior
- Git

## Pasos para correr el aplicativo

### 1. Clonar el repositorio

git clone <url-del-repositorio>
cd gasolinera_sim

### 2. Crear y activar el ambiente virtual

python -m venv venv

En Windows (Git Bash):
source venv/Scripts/activate

En Mac/Linux:
source venv/bin/activate

### 3. Instalar dependencias

pip install -r requirements.txt

### 4. Correr el aplicativo

streamlit run app.py

El aplicativo se abrirá automáticamente en el navegador.

### 5. Usar el aplicativo

1. Hacer clic en "Selecciona el archivo Excel"
2. Cargar el archivo: datos/gasolinera_datos_estandarizados.xlsx
3. Los parámetros para Simio aparecerán automáticamente
4. Hacer clic en "Ver gráficas de distribuciones" para visualizar
   los histogramas con las curvas exponenciales ajustadas

## Archivos del proyecto

- app.py — aplicativo principal
- requirements.txt — dependencias del proyecto
- datos/ — carpeta con el Excel estandarizado