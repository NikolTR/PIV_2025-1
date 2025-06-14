# Pipeline para el Análisis de Meta Platforms

Este proyecto implementa un pipeline completo de extracción, enriquecimiento, modelamiento y visualización de datos históricos de precios de acciones de Meta Platforms Inc. (META) desde Yahoo Finance. Incluye predicciones con modelos ARIMA y un dashboard interactivo desarrollado en Streamlit.

---

## 🚀 Tecnologías utilizadas

- Python 3.10+
- Web Scraping: BeautifulSoup 4, requests
- Análisis de datos: pandas, numpy
- Machine Learning: scikit-learn, statsmodels (ARIMA)
- Visualización: Streamlit, Plotly, matplotlib, seaborn
- Logging: Sistema de logs personalizado

---

## 🧠 Estructura del proyecto
```
PIV_2025-1/
├── src/
│   └── piv/
│       ├── static/
│       │   └── data/
│       │       ├── meta_history.csv           # Datos históricos crudos
│       │       ├── meta_data_enricher.csv     # Datos enriquecidos con KPIs
│       │       ├── meta_predicciones.csv      # Predicciones del modelo
│       │       └── models/
│       │           └── model.pkl              # Modelo ARIMA entrenado
│       ├── collector.py                       # Extracción de datos desde Yahoo Finance
│       ├── enricher.py                        # Cálculo de KPIs financieros
│       ├── modeller.py                        # Entrenamiento modelo ARIMA
│       ├── dashboard.py                       # Dashboard interactivo Streamlit
│       ├── logger.py                          # Sistema de logging personalizado
│       └── main.py                            # Orquestador principal del pipeline
├── logs/                                      # Directorio de archivos de log
├── setup.py                                   # Configuración de dependencias
└── README.md

```
---

## ⚙️ Instalación y ejecución

1. Clona el repositorio:
git clone https://github.com/tu_usuario/PIV_2025-1.git

cd PIV_2025-1

2. Crea y activa el entorno virtual:

python -m venv venv

### Windows
venv\Scripts\activate

### Linux/Mac
source venv/bin/activate

3. Instala las dependencias:

pip install -e .

---

## 🔄 Ejecución del pipeline

python src/piv/main.py

Este comando ejecuta secuencialmente:

✅ Extracción de datos desde Yahoo Finance

✅ Limpieza y estandarización de columnas

✅ Enriquecimiento con KPIs financieros

✅ Entrenamiento del modelo ARIMA

✅ Generación de predicciones

✅ Almacenamiento de todos los datasets

---

## Dashboard interactivo

streamlit run src/piv/dashboard.py

---

📊 Funcionalidades del proyecto

🔍 Extracción de datos (collector.py)

 - Web scraping desde finance.yahoo.com
 - Manejo automático de headers y HTML
 - Limpieza de separadores y casting de tipos
 - Soporte para estructuras cambiantes

📈 Enriquecimiento (enricher.py)
Cálculo automático de KPIs:

- Retorno diario
- Tasa apertura-cierre
- Retorno acumulado
- Media móvil 5 días
- Volatilidad móvil
-Clasificación temporal (día, mes, año)

🤖 Modelamiento predictivo (modeller.py)
Modelo ARIMA(1,1,1)

Métricas:
- MAE, RMSE, R², MAPE
- Predicciones configurables (hasta 30 días)
- Persistencia en .pkl

📊 Dashboard interactivo (dashboard.py)
Resumen ejecutivo

- Análisis multivariado (precios, volumen, KPIs)
- Gráficos interactivos con Plotly
- Matriz de correlación
- Predicciones ARIMA visuales
- Filtros y selectores dinámicos

---

## 🧹 Transformaciones realizadas

- Conversión de nombres de columnas a español estándar:
  - `Date` → `fecha`
  - `Open` → `abrir`, `High` → `max`, `Low` → `min`, etc.
- Limpieza de separadores de miles y decimales
- Corrección de escala decimal en valores sin separador explícito
- Estándar de fecha: `MM/DD/YYYY`
- Exportación en `.csv` con dos decimales y punto como separador decimal

---

📈 Métricas del modelo ARIMA
Métrica	Descripción	Interpretación
MAE	Error Absoluto Medio	Menor es mejor
RMSE	Raíz del Error Cuadrático Medio	Penaliza errores grandes
R²	Coeficiente de Determinación	Entre 0 y 1 - más alto, mejor
MAPE	Error Porcentual Absoluto Medio	% de error - menor es mejor

---

🔧 Configuración avanzada

Parámetros ARIMA:

model = ARIMA(series, order=(1, 1, 1))  # (p,d,q)

Días de predicción:

dias_prediccion = 30

Ventanas técnicas:

media_movil_5d = df['cerrar'].rolling(window=5).mean()
volatilidad = df['cerrar'].rolling(window=5).std()

---

📊 Dashboard - Funcionalidades principales


📊 Análisis Indicadores

🔍 Análisis Multivariado

 - Precios y volumen

 - Indicadores técnicos

 - Matriz de correlación

🤖 Modelo ARIMA

 - Métricas, predicciones, control de forecast

Controles interactivos:

- Filtros por fecha

- Selector de KPIs

- Generación de predicciones dinámicas

---

## 📌 Notas

- Yahoo Finance cambia frecuentemente su estructura; se recomienda validar periódicamente el scraper.
- En caso de usar la versión `es.finance.yahoo.com`, asegúrate de adaptar el procesamiento de separadores regionales.

---

## 👤 Autor

**NIKOL TAMAYO RUA**  
**JULIANA MARIA PEÑA SUAREZ**  
🦍 Proyecto académico para PIV 2025  


---

## 📄 Licencia

MIT License – libre para modificar y compartir.









