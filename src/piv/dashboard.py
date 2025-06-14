import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import os
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from modeller import Modeller
from logger import Logger
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# =================== CONFIGURACIÓN DE LA PÁGINA ===================
st.set_page_config(
    page_title="Meta Platforms Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1877f2;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1877f2;
        margin: 0.5rem 0;
    }
    
    .section-header {
        color: #1877f2;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1877f2;
    }
    
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =================== CONFIGURACIÓN DE RUTAS ===================
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "static" / "data" / "meta_data_enricher.csv"
HISTORY_PATH = BASE_DIR / "static" / "data" / "meta_history.csv"
PREDICTIONS_PATH = BASE_DIR / "static" / "data" / "meta_predicciones.csv"
MODEL_PATH = BASE_DIR / "static" / "data" / "models" / "model.pkl"

# =================== FUNCIONES DE CARGA DE DATOS ===================
@st.cache_data
def load_data():
    """Carga los datos enriquecidos"""
    try:
        df = pd.read_csv(DATA_PATH)
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except Exception as e:
        st.error(f"Error al cargar datos enriquecidos: {e}")
        return pd.DataFrame()

@st.cache_data
def load_predictions():
    """Carga las predicciones si existen"""
    try:
        if PREDICTIONS_PATH.exists():
            df_pred = pd.read_csv(PREDICTIONS_PATH)
            df_pred['fecha'] = pd.to_datetime(df_pred['fecha'])
            return df_pred
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar predicciones: {e}")
        return pd.DataFrame()

@st.cache_data
def load_model_metrics():
    """Calcula las métricas del modelo si existe"""
    try:
        if not MODEL_PATH.exists():
            return None
        
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        
        df = load_data()
        if df.empty:
            return None
            
        df_model = df.dropna(subset=["cierre_ajustado"]).copy()
        serie_real = df_model["cierre_ajustado"]
        pred = model.fittedvalues
        
        # Alinear series para comparación
        y_valid = serie_real[-len(pred):]
        
        # Calcular métricas
        mae = mean_absolute_error(y_valid, pred)
        rmse = np.sqrt(mean_squared_error(y_valid, pred))
        r2 = r2_score(y_valid, pred)
        mape = np.mean(np.abs((y_valid - pred) / y_valid)) * 100
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'model': model,
            'serie_real': serie_real,
            'pred': pred
        }
    except Exception as e:
        st.error(f"Error al cargar métricas del modelo: {e}")
        return None

# =================== HEADER PRINCIPAL ===================
st.markdown('<div class="main-header">📊 Meta Platforms Analytics Dashboard</div>', unsafe_allow_html=True)

# =================== SIDEBAR ===================
st.sidebar.title("🔧 Configuraciones")
st.sidebar.markdown("---")

# Cargar datos
df = load_data()
df_predictions = load_predictions()
model_metrics = load_model_metrics()

if df.empty:
    st.error("⚠️ No se pudieron cargar los datos. Ejecuta `main.py` primero.")
    st.stop()

# Configuración de fechas en sidebar
fecha_min = df['fecha'].min()
fecha_max = df['fecha'].max()

st.sidebar.subheader("📅 Filtros de Fecha")
fecha_inicio = st.sidebar.date_input(
    "Fecha de inicio",
    value=fecha_min,
    min_value=fecha_min,
    max_value=fecha_max
)
fecha_fin = st.sidebar.date_input(
    "Fecha de fin",
    value=fecha_max,
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtrar datos por fecha
df_filtered = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) & 
                 (df['fecha'] <= pd.to_datetime(fecha_fin))]

# =================== MÉTRICAS PRINCIPALES ===================
st.markdown('<div class="section-header">📈 Resumen Ejecutivo</div>', unsafe_allow_html=True)

if not df_filtered.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        ultimo_precio = df_filtered['cerrar'].iloc[-1]
        st.metric(
            "💰 Último Precio",
            f"${ultimo_precio:.2f}",
            delta=f"{df_filtered['retorno_diario'].iloc[-1]:.2%}" if not df_filtered['retorno_diario'].iloc[-1] == 0 else None
        )
    
    with col2:
        retorno_total = df_filtered['retorno_acumulado'].iloc[-1]
        st.metric(
            "📊 Retorno Total",
            f"{retorno_total:.2%}",
            delta=f"{retorno_total:.2%}"
        )
    
    with col3:
        volatilidad_promedio = df_filtered['volatilidad'].mean()
        st.metric(
            "📉 Volatilidad Promedio",
            f"{volatilidad_promedio:.2f}",
            delta=f"{df_filtered['volatilidad'].iloc[-1] - volatilidad_promedio:.2f}"
        )
    
    with col4:
        volumen_promedio = df_filtered['volumen'].mean()
        st.metric(
            "📊 Volumen Promedio",
            f"{volumen_promedio:,.0f}",
            delta=f"{df_filtered['volumen'].iloc[-1] - volumen_promedio:,.0f}"
        )
    
    with col5:
        media_movil = df_filtered['media_movil_5d'].iloc[-1]
        precio_actual = df_filtered['cerrar'].iloc[-1]
        diferencia_mm = ((precio_actual - media_movil) / media_movil) * 100
        st.metric(
            "📈 vs Media Móvil 5D",
            f"{diferencia_mm:.1f}%",
            delta=f"{diferencia_mm:.1f}%"
        )

# =================== GRÁFICOS DE INDICADORES FINANCIEROS ===================
st.markdown('<div class="section-header">📊 Análisis de Indicadores Financieros</div>', unsafe_allow_html=True)

# Configuración de indicadores
kpi_options = {
    'retorno_diario': 'Retorno Diario (%)',
    'tasa_variacion_ac': 'Tasa de Variación Apertura-Cierre (%)',
    'retorno_acumulado': 'Retorno Acumulado (%)',
    'media_movil_5d': 'Media Móvil 5 Días ($)',
    'volatilidad': 'Volatilidad (Rolling 5D)'
}

# Selector de KPI
selected_kpi = st.selectbox(
    "🎯 Selecciona un indicador para análisis detallado:",
    options=list(kpi_options.keys()),
    format_func=lambda x: kpi_options[x]
)

# Crear gráfico interactivo
fig = go.Figure()

# Configurar formato según el tipo de indicador
if selected_kpi in ['retorno_diario', 'tasa_variacion_ac', 'retorno_acumulado']:
    y_values = df_filtered[selected_kpi] * 100  # Convertir a porcentaje
    y_format = '.2%'
    y_title = kpi_options[selected_kpi]
else:
    y_values = df_filtered[selected_kpi]
    y_format = '.2f'
    y_title = kpi_options[selected_kpi]

fig.add_trace(go.Scatter(
    x=df_filtered['fecha'],
    y=y_values,
    mode='lines',
    name=kpi_options[selected_kpi],
    line=dict(color='#1877f2', width=2),
    hovertemplate='<b>Fecha:</b> %{x}<br><b>Valor:</b> %{y}<extra></extra>'
))

fig.update_layout(
    title=f'📈 {kpi_options[selected_kpi]} - Evolución Temporal',
    xaxis_title='Fecha',
    yaxis_title=y_title,
    template='plotly_white',
    hovermode='x unified',
    showlegend=False,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# =================== ANÁLISIS MULTIVARIADO ===================
st.markdown('<div class="section-header">🔍 Análisis Multivariado</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Precios y Volumen", "📈 Indicadores Técnicos", "🎯 Correlaciones"])

with tab1:
    # Gráfico de precios con volumen
    fig_multi = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Precio de Cierre y Media Móvil', 'Volumen'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Precio de cierre
    fig_multi.add_trace(
        go.Scatter(x=df_filtered['fecha'], y=df_filtered['cerrar'],
                  name='Precio de Cierre', line=dict(color='#1877f2')),
        row=1, col=1
    )
    
    # Media móvil
    fig_multi.add_trace(
        go.Scatter(x=df_filtered['fecha'], y=df_filtered['media_movil_5d'],
                  name='Media Móvil 5D', line=dict(color='#ff6b6b', dash='dash')),
        row=1, col=1
    )
    
    # Volumen
    fig_multi.add_trace(
        go.Bar(x=df_filtered['fecha'], y=df_filtered['volumen'],
               name='Volumen', marker_color='#95a5a6'),
        row=2, col=1
    )
    
    fig_multi.update_layout(height=600, template='plotly_white')
    fig_multi.update_xaxes(title_text="Fecha", row=2, col=1)
    fig_multi.update_yaxes(title_text="Precio ($)", row=1, col=1)
    fig_multi.update_yaxes(title_text="Volumen", row=2, col=1)
    
    st.plotly_chart(fig_multi, use_container_width=True)

with tab2:
    # Indicadores técnicos
    col1, col2 = st.columns(2)
    
    with col1:
        # Retorno diario
        fig_ret = px.histogram(df_filtered, x='retorno_diario', nbins=30,
                              title='Distribución del Retorno Diario')
        fig_ret.update_layout(template='plotly_white')
        st.plotly_chart(fig_ret, use_container_width=True)
    
    with col2:
        # Volatilidad
        fig_vol = px.line(df_filtered, x='fecha', y='volatilidad',
                         title='Evolución de la Volatilidad')
        fig_vol.update_layout(template='plotly_white')
        st.plotly_chart(fig_vol, use_container_width=True)

with tab3:
    # Matriz de correlación
    numeric_cols = ['apertura', 'alto', 'bajo', 'cerrar', 'volumen', 
                   'retorno_diario', 'volatilidad', 'media_movil_5d']
    corr_matrix = df_filtered[numeric_cols].corr()
    
    fig_corr = px.imshow(corr_matrix, 
                        title='Matriz de Correlación de Indicadores Financieros',
                        color_continuous_scale='RdBu_r',
                        aspect='auto')
    fig_corr.update_layout(template='plotly_white', height=500)
    st.plotly_chart(fig_corr, use_container_width=True)

# =================== MODELO ARIMA Y PREDICCIONES ===================
st.markdown('<div class="section-header">🤖 Modelo ARIMA y Predicciones</div>', unsafe_allow_html=True)

if model_metrics:
    # Métricas del modelo
    st.markdown("#### 📊 Métricas de Evaluación del Modelo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #1877f2; margin: 0;">MAE</h3>
            <h2 style="margin: 0.5rem 0;">{model_metrics['mae']:.2f}</h2>
            <small>Error Absoluto Medio</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #1877f2; margin: 0;">RMSE</h3>
            <h2 style="margin: 0.5rem 0;">{model_metrics['rmse']:.2f}</h2>
            <small>Raíz del Error Cuadrático Medio</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #1877f2; margin: 0;">R²</h3>
            <h2 style="margin: 0.5rem 0;">{model_metrics['r2']:.3f}</h2>
            <small>Coeficiente de Determinación</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #1877f2; margin: 0;">MAPE</h3>
            <h2 style="margin: 0.5rem 0;">{model_metrics['mape']:.2f}%</h2>
            <small>Error Porcentual Absoluto Medio</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Información sobre las métricas
    st.markdown("""
    <div class="info-box">
        <h4>📋 Interpretación de Métricas:</h4>
        <ul>
            <li><strong>MAE:</strong> Error promedio en términos absolutos. Valores más bajos indican mejor precisión.</li>
            <li><strong>RMSE:</strong> Penaliza más los errores grandes. Útil para detectar outliers en las predicciones.</li>
            <li><strong>R²:</strong> Proporción de variabilidad explicada por el modelo (0-1, donde 1 es perfecto).</li>
            <li><strong>MAPE:</strong> Error relativo expresado en porcentaje. Más fácil de interpretar.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico de ajuste del modelo
    st.markdown("#### 📈 Comparación: Valores Reales vs Modelo ARIMA")
    
    fig_model = go.Figure()
    
    # Serie real
    fig_model.add_trace(go.Scatter(
        x=model_metrics['serie_real'].index,
        y=model_metrics['serie_real'].values,
        mode='lines',
        name='Valores Reales',
        line=dict(color='#1877f2', width=2)
    ))
    
    # Predicciones del modelo
    fig_model.add_trace(go.Scatter(
        x=model_metrics['pred'].index,
        y=model_metrics['pred'].values,
        mode='lines',
        name='ARIMA Ajustado',
        line=dict(color='#ff6b6b', dash='dash', width=2)
    ))
    
    fig_model.update_layout(
        title='Serie de Tiempo: Comparación Modelo vs Realidad',
        xaxis_title='Período',
        yaxis_title='Precio de Cierre Ajustado ($)',
        template='plotly_white',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig_model, use_container_width=True)
    
    # Predicción futura interactiva
    st.markdown("#### 🔮 Predicción Futura")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        steps = st.slider("Días a predecir:", min_value=1, max_value=30, value=7)
        
        if st.button("🚀 Generar Predicción"):
            try:
                logger = Logger()
                modeller = Modeller(logger)
                forecast = modeller.predecir(df, steps=steps)
                
                st.success(f"✅ Predicción generada para {steps} días")
                
                # Mostrar predicciones en formato tabla
                fecha_inicio_pred = df['fecha'].max() + timedelta(days=1)
                fechas_pred = pd.date_range(start=fecha_inicio_pred, periods=steps, freq='D')
                
                df_forecast = pd.DataFrame({
                    'Fecha': fechas_pred,
                    'Precio Predicho': forecast
                })
                
                st.dataframe(df_forecast, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error al generar predicción: {e}")
    
    with col2:
        # Mostrar predicciones existentes si están disponibles
        if not df_predictions.empty:
            st.markdown("##### 📊 Predicciones Precalculadas")
            
            fig_pred = go.Figure()
            
            # Datos históricos (últimos 30 días)
            df_recent = df.tail(30)
            fig_pred.add_trace(go.Scatter(
                x=df_recent['fecha'],
                y=df_recent['cerrar'],
                mode='lines',
                name='Histórico',
                line=dict(color='#1877f2', width=2)
            ))
            
            # Predicciones
            fig_pred.add_trace(go.Scatter(
                x=df_predictions['fecha'],
                y=df_predictions['cerrar'],
                mode='lines',
                name='Predicciones',
                line=dict(color='#28a745', width=2, dash='dash')
            ))
            
            fig_pred.update_layout(
                title='Predicciones vs Datos Históricos',
                xaxis_title='Fecha',
                yaxis_title='Precio ($)',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig_pred, use_container_width=True)

else:
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Modelo no disponible</h4>
        <p>No se encontró el modelo ARIMA entrenado. Para generar predicciones y métricas:</p>
        <ol>
            <li>Ejecuta <code>main.py</code> para entrenar el modelo</li>
            <li>Asegúrate de que el archivo <code>model.pkl</code> se haya generado correctamente</li>
            <li>Recarga esta página</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# =================== FOOTER CON INFORMACIÓN ADICIONAL ===================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>
        📊 Dashboard generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | 
        📈 Datos de {df['fecha'].min().strftime('%d/%m/%Y') if not df.empty else 'N/A'} a {df['fecha'].max().strftime('%d/%m/%Y') if not df.empty else 'N/A'} | 
        🔄 Total de registros: {len(df)}
    </small>
</div>
""", unsafe_allow_html=True)

