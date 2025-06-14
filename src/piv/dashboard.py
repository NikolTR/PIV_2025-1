import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pickle
import os
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Importes locales
from modeller import Modeller
from logger import Logger
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# =================== CONFIGURACIÓN DE PÁGINA ===================
st.set_page_config(
    page_title="Meta Platforms Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .info-box {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =================== HEADER PRINCIPAL ===================
st.markdown("""
<div class="main-header">
    <h1>📊 Dashboard de Análisis Financiero</h1>
    <h2>Meta Platforms Inc. (META)</h2>
    <p>Pipeline completo de extracción, enriquecimiento, modelamiento y visualización</p>
</div>
""", unsafe_allow_html=True)

# =================== CONFIGURACIÓN DE RUTAS ===================
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "static" / "data" / "meta_data_enricher.csv"
RAW_DATA_PATH = BASE_DIR / "static" / "data" / "meta_history.csv"
MODEL_PATH = BASE_DIR / "static" / "data" / "models" / "model.pkl"

# =================== FUNCIONES DE CARGA DE DATOS ===================
@st.cache_data
def load_enriched_data():
    """Carga los datos enriquecidos con KPIs calculados"""
    try:
        df = pd.read_csv(DATA_PATH)
        df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y')
        return df.sort_values('fecha')
    except Exception as e:
        st.error(f"Error al cargar datos enriquecidos: {e}")
        return pd.DataFrame()

@st.cache_data
def load_raw_data():
    """Carga los datos históricos sin procesar"""
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y')
        return df.sort_values('fecha')
    except Exception as e:
        st.error(f"Error al cargar datos históricos: {e}")
        return pd.DataFrame()

# =================== SIDEBAR - CONTROLES ===================
with st.sidebar:
    st.markdown("## 🎛️ Panel de Control")
    
    # Selector de vista
    vista_seleccionada = st.selectbox(
        "Selecciona la vista:",
        ["📈 Análisis de Indicadores", "🤖 Modelo ARIMA", "📊 Dashboard Completo", "📋 Datos Históricos"]
    )
    
    st.markdown("---")
    
    # Filtros de fecha
    st.markdown("### 📅 Filtros de Fecha")
    df_enriched = load_enriched_data()
    
    if not df_enriched.empty:
        fecha_min = df_enriched['fecha'].min().date()
        fecha_max = df_enriched['fecha'].max().date()
        
        fecha_inicio = st.date_input(
            "Fecha de inicio:",
            value=fecha_min,
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        fecha_fin = st.date_input(
            "Fecha de fin:",
            value=fecha_max,
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        # Filtrar datos por fecha
        mask = (df_enriched['fecha'].dt.date >= fecha_inicio) & (df_enriched['fecha'].dt.date <= fecha_fin)
        df_filtered = df_enriched.loc[mask]
    else:
        df_filtered = pd.DataFrame()
        st.error("No se pudieron cargar los datos")

# =================== FUNCIONES DE VISUALIZACIÓN ===================
def create_kpi_chart(df, kpi, title):
    """Crea un gráfico interactivo para un KPI específico"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['fecha'],
        y=df[kpi],
        mode='lines',
        name=title,
        line=dict(width=2, color='#1f77b4'),
        hovertemplate='<b>Fecha:</b> %{x}<br><b>' + title + ':</b> %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{title} - Meta Platforms",
        xaxis_title="Fecha",
        yaxis_title=title,
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_price_chart(df):
    """Crea un gráfico de velas japonesas con volumen"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Precio', 'Volumen'),
        row_width=[0.7, 0.3]
    )
    
    # Gráfico de velas
    fig.add_trace(
        go.Candlestick(
            x=df['fecha'],
            open=df['apertura'],
            high=df['alto'],
            low=df['bajo'],
            close=df['cerrar'],
            name="Precio"
        ),
        row=1, col=1
    )
    
    # Media móvil
    if 'media_movil_5d' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['fecha'],
                y=df['media_movil_5d'],
                mode='lines',
                name='Media Móvil 5D',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
    
    # Volumen
    fig.add_trace(
        go.Bar(
            x=df['fecha'],
            y=df['volumen'],
            name='Volumen',
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Análisis de Precios y Volumen - Meta Platforms",
        xaxis_rangeslider_visible=False,
        height=600,
        template='plotly_white'
    )
    
    return fig

def calculate_model_metrics():
    """Calcula las métricas del modelo ARIMA"""
    try:
        if not os.path.exists(MODEL_PATH):
            return None, "Modelo no encontrado"
        
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        
        # Cargar datos para validación
        df_raw = load_raw_data()
        if df_raw.empty:
            return None, "Datos no disponibles"
        
        serie_real = df_raw["cierre_ajustado"].dropna()
        pred = model.fittedvalues
        y_valid = serie_real[-len(pred):]
        
        # Calcular métricas
        mae = mean_absolute_error(y_valid, pred)
        rmse = np.sqrt(mean_squared_error(y_valid, pred))
        r2 = r2_score(y_valid, pred)
        mape = np.mean(np.abs((y_valid - pred) / y_valid)) * 100
        
        metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'R²': r2,
            'MAPE': mape,
            'pred': pred,
            'y_valid': y_valid,
            'model': model
        }
        
        return metrics, "OK"
        
    except Exception as e:
        return None, f"Error al calcular métricas: {e}"

# =================== VISTA: ANÁLISIS DE INDICADORES ===================
if vista_seleccionada == "📈 Análisis de Indicadores":
    if df_filtered.empty:
        st.error("No hay datos disponibles para el rango de fechas seleccionado")
    else:
        st.markdown("## 📈 Análisis de Indicadores Financieros")
        
        # Estadísticas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            precio_actual = df_filtered['cerrar'].iloc[-1]
            precio_anterior = df_filtered['cerrar'].iloc[-2] if len(df_filtered) > 1 else precio_actual
            cambio = precio_actual - precio_anterior
            st.metric("Precio Actual", f"${precio_actual:.2f}", f"{cambio:+.2f}")
        
        with col2:
            vol_promedio = df_filtered['volatilidad'].mean()
            st.metric("Volatilidad Promedio", f"{vol_promedio:.4f}")
        
        with col3:
            retorno_total = df_filtered['retorno_acumulado'].iloc[-1]
            st.metric("Retorno Acumulado", f"{retorno_total:.2%}")
        
        with col4:
            vol_total = df_filtered['volumen'].sum()
            st.metric("Volumen Total", f"{vol_total:,.0f}")
        
        st.markdown("---")
        
        # Selector de KPI
        kpi_options = {
            'retorno_diario': 'Retorno Diario',
            'tasa_variacion_ac': 'Tasa de Variación (Apertura-Cierre)',
            'retorno_acumulado': 'Retorno Acumulado',
            'media_movil_5d': 'Media Móvil 5 Días',
            'volatilidad': 'Volatilidad (Rolling 5D)'
        }
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_kpi = st.selectbox(
                "Selecciona un indicador para visualizar:",
                options=list(kpi_options.keys()),
                format_func=lambda x: kpi_options[x]
            )
        
        with col2:
            show_stats = st.checkbox("Mostrar estadísticas", value=True)
        
        # Gráfico del KPI seleccionado
        fig_kpi = create_kpi_chart(df_filtered, selected_kpi, kpi_options[selected_kpi])
        st.plotly_chart(fig_kpi, use_container_width=True)
        
        # Estadísticas del KPI
        if show_stats:
            st.markdown(f"### 📊 Estadísticas: {kpi_options[selected_kpi]}")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            stats = df_filtered[selected_kpi].describe()
            
            col1.metric("Media", f"{stats['mean']:.4f}")
            col2.metric("Mediana", f"{stats['50%']:.4f}")
            col3.metric("Desv. Estándar", f"{stats['std']:.4f}")
            col4.metric("Mínimo", f"{stats['min']:.4f}")
            col5.metric("Máximo", f"{stats['max']:.4f}")
        
        # Gráfico de precios con volumen
        st.markdown("### 💹 Análisis de Precios y Volumen")
        fig_price = create_price_chart(df_filtered)
        st.plotly_chart(fig_price, use_container_width=True)

# =================== VISTA: MODELO ARIMA ===================
elif vista_seleccionada == "🤖 Modelo ARIMA":
    st.markdown("## 🤖 Modelo de Predicción ARIMA")
    
    # Calcular métricas del modelo
    metrics, status = calculate_model_metrics()
    
    if metrics is None:
        st.markdown(f"""
        <div class="warning-box">
            <h4>⚠️ Modelo no disponible</h4>
            <p>{status}</p>
            <p>Por favor, ejecuta <code>main.py</code> para entrenar el modelo.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Mostrar métricas
        st.markdown("### 📊 Métricas de Evaluación del Modelo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>MAE</h4>
                <h2>{:.2f}</h2>
                <p>Error Absoluto Medio</p>
            </div>
            """.format(metrics['MAE']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>RMSE</h4>
                <h2>{:.2f}</h2>
                <p>Raíz del Error Cuadrático</p>
            </div>
            """.format(metrics['RMSE']), unsafe_allow_html=True)
        
        with col3:
            color = "green" if metrics['R²'] > 0.5 else "orange"
            st.markdown("""
            <div class="metric-card">
                <h4>R²</h4>
                <h2 style="color: {}">{:.3f}</h2>
                <p>Coeficiente de Determinación</p>
            </div>
            """.format(color, metrics['R²']), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h4>MAPE</h4>
                <h2>{:.2f}%</h2>
                <p>Error Porcentual Absoluto</p>
            </div>
            """.format(metrics['MAPE']), unsafe_allow_html=True)
        
        # Interpretación de métricas
        st.markdown("""
        <div class="info-box">
            <h4>📋 Interpretación de Métricas</h4>
            <ul>
                <li><b>MAE:</b> Promedio de error absoluto en las mismas unidades que los datos</li>
                <li><b>RMSE:</b> Penaliza más los errores grandes, útil para detectar outliers</li>
                <li><b>R²:</b> Proporción de variabilidad explicada (0-1, donde 1 es perfecto)</li>
                <li><b>MAPE:</b> Error relativo expresado como porcentaje</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Gráfico de comparación
        st.markdown("### 📈 Valores Reales vs Predicciones del Modelo")
        
        df_raw = load_raw_data()
        fig_comparison = go.Figure()
        
        # Serie real
        fig_comparison.add_trace(go.Scatter(
            x=df_raw['fecha'][-len(metrics['y_valid']):],
            y=metrics['y_valid'],
            mode='lines',
            name='Valores Reales',
            line=dict(color='blue', width=2)
        ))
        
        # Predicciones
        fig_comparison.add_trace(go.Scatter(
            x=df_raw['fecha'][-len(metrics['pred']):],
            y=metrics['pred'],
            mode='lines',
            name='ARIMA Ajustado',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig_comparison.update_layout(
            title="Comparación: Serie Real vs Modelo ARIMA",
            xaxis_title="Fecha",
            yaxis_title="Precio de Cierre Ajustado",
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Predicción futura
        st.markdown("### 🔮 Predicción Futura")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            steps = st.slider(
                "Días a predecir:",
                min_value=1,
                max_value=30,
                value=5,
                help="Selecciona el número de días futuros a predecir"
            )
        
        if st.button("🚀 Generar Predicción", type="primary"):
            try:
                logger = Logger()
                modeller = Modeller(logger)
                forecast = modeller.predecir(df_raw, steps=steps)
                
                if forecast:
                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ Predicción para los próximos {steps} días:</h4>
                        <ul>
                    """, unsafe_allow_html=True)
                    
                    for i, pred_value in enumerate(forecast, 1):
                        fecha_pred = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
                        st.markdown(f"<li><b>Día {i} ({fecha_pred}):</b> ${pred_value:.2f}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                else:
                    st.error("Error al generar la predicción")
            except Exception as e:
                st.error(f"Error en la predicción: {e}")

# =================== VISTA: DASHBOARD COMPLETO ===================
elif vista_seleccionada == "📊 Dashboard Completo":
    if df_filtered.empty:
        st.error("No hay datos disponibles")
    else:
        st.markdown("## 📊 Dashboard Completo - Meta Platforms")
        
        # Fila 1: Métricas principales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            precio_actual = df_filtered['cerrar'].iloc[-1]
            st.metric("Precio Actual", f"${precio_actual:.2f}")
        
        with col2:
            cambio_pct = df_filtered['tasa_variacion_ac'].iloc[-1]
            st.metric("Cambio Diario", f"{cambio_pct:.2%}")
        
        with col3:
            vol_promedio = df_filtered['volatilidad'].mean()
            st.metric("Volatilidad Media", f"{vol_promedio:.4f}")
        
        with col4:
            retorno_total = df_filtered['retorno_acumulado'].iloc[-1]
            st.metric("Retorno Total", f"{retorno_total:.2%}")
        
        with col5:
            vol_medio = df_filtered['volumen'].mean()
            st.metric("Volumen Medio", f"{vol_medio:,.0f}")
        
        # Fila 2: Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de retorno acumulado
            fig_ret = create_kpi_chart(df_filtered, 'retorno_acumulado', 'Retorno Acumulado')
            st.plotly_chart(fig_ret, use_container_width=True)
        
        with col2:
            # Gráfico de volatilidad
            fig_vol = create_kpi_chart(df_filtered, 'volatilidad', 'Volatilidad')
            st.plotly_chart(fig_vol, use_container_width=True)
        
        # Fila 3: Análisis de precios
        fig_price = create_price_chart(df_filtered)
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Fila 4: Matriz de correlación
        st.markdown("### 🔗 Matriz de Correlación de Indicadores")
        
        numeric_cols = ['apertura', 'alto', 'bajo', 'cerrar', 'volumen', 
                       'retorno_diario', 'tasa_variacion_ac', 'volatilidad']
        
        corr_data = df_filtered[numeric_cols].corr()
        
        fig_corr = px.imshow(
            corr_data,
            text_auto=True,
            aspect="auto",
            title="Matriz de Correlación",
            color_continuous_scale="RdBu_r"
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)

# =================== VISTA: DATOS HISTÓRICOS ===================
elif vista_seleccionada == "📋 Datos Históricos":
    st.markdown("## 📋 Datos Históricos")
    
    tab1, tab2 = st.tabs(["📊 Datos Enriquecidos", "📈 Datos Originales"])
    
    with tab1:
        st.markdown("### Datos con Indicadores Calculados")
        if not df_filtered.empty:
            st.dataframe(
                df_filtered.round(4),
                use_container_width=True,
                height=400
            )
            
            # Botón de descarga
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar datos enriquecidos (CSV)",
                data=csv,
                file_name=f'meta_enriched_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
        else:
            st.warning("No hay datos enriquecidos disponibles")
    
    with tab2:
        st.markdown("### Datos Históricos Originales")
        df_raw = load_raw_data()
        if not df_raw.empty:
            # Filtrar por fechas
            mask_raw = (df_raw['fecha'].dt.date >= fecha_inicio) & (df_raw['fecha'].dt.date <= fecha_fin)
            df_raw_filtered = df_raw.loc[mask_raw]
            
            st.dataframe(
                df_raw_filtered.round(2),
                use_container_width=True,
                height=400
            )
            
            # Botón de descarga
            csv_raw = df_raw_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar datos históricos (CSV)",
                data=csv_raw,
                file_name=f'meta_historical_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
        else:
            st.warning("No hay datos históricos disponibles")

# =================== FOOTER ===================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📊 Dashboard desarrollado para análisis financiero de Meta Platforms Inc.</p>
    <p>Fuente de datos: Yahoo Finance | Modelo: ARIMA | Framework: Streamlit</p>
</div>
""", unsafe_allow_html=True)