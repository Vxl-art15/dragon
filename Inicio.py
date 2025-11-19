import pandas as pd
import streamlit as st
from influxdb_client import InfluxDBClient
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Crecimiento del Dragón",
    page_icon="🐉",
    layout="wide"
)

# Título y descripción
st.title('📊 Crecimiento del Dragón')
st.markdown("""
    Esta aplicación permite analizar y visualizar el crecimiento de un dragón
    monitoreado a través de un sensor en tiempo real.
""")

# Conectar a InfluxDB
client = InfluxDBClient(url="https://us-east-1-1.aws.cloud2.influxdata.com", token="TuToken", org="TuOrganizacion")
query = 'from(bucket: "valdragon123") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "Sensor 1" and r._field == "longituddeldragon")'

# Ejecutar la consulta
result = client.query_api().query(org="TuOrganizacion", query=query)
data = []

# Procesar los resultados de la consulta
for table in result:
    for record in table.records:
        data.append({"time": record.get_time(), "longituddeldragon": record.get_value()})

# Convertir los datos en un DataFrame de Pandas
df = pd.DataFrame(data)

# Mostrar los datos en Streamlit
st.subheader("📈 Longitud del Dragón")
st.write("Aquí puedes ver la longitud del dragón en tiempo real.")

# Mostrar el último valor de la longitud del dragón
ultimo_valor = df["longituddeldragon"].iloc[-1]
st.metric("Longitud del Dragón (cm)", f"{ultimo_valor:.2f} cm")

# Gráfico de la longitud del dragón usando Plotly (Gauge)
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=ultimo_valor,
    title={'text': "Crecimiento del Dragón (cm)"},
    gauge={'axis': {'range': [0, 100]},  # Ajusta el rango según el crecimiento del dragón
           'steps': [{'range': [0, 30], 'color': "blue"},
                     {'range': [30, 70], 'color': "green"},
                     {'range': [70, 100], 'color': "red"}]}
))

st.plotly_chart(fig)

# Estadísticas de la longitud del dragón
st.subheader("📊 Estadísticas de la Longitud del Dragón")

# Mostrar resumen estadístico
stats_df = df["longituddeldragon"].describe()

col1, col2 = st.columns(2)

with col1:
    st.dataframe(stats_df)

with col2:
    st.metric("Valor Promedio", f"{stats_df['mean']:.2f} cm")
    st.metric("Valor Máximo", f"{stats_df['max']:.2f} cm")
    st.metric("Valor Mínimo", f"{stats_df['min']:.2f} cm")
    st.metric("Desviación Estándar", f"{stats_df['std']:.2f} cm")

# Mostrar los datos crudos
st.subheader("📅 Datos Recientes del Dragón")
if st.checkbox('Mostrar datos crudos'):
    st.write(df)

# Filtros de Datos (si quieres filtrar el crecimiento)
st.subheader('🔍 Filtros de Datos')

# Calcular el rango de valores
min_value = df["longituddeldragon"].min()
max_value = df["longituddeldragon"].max()
mean_value = df["longituddeldragon"].mean()

col1, col2 = st.columns(2)

with col1:
    # Filtro de valor mínimo
    min_val = st.slider(
        'Valor mínimo',
        min_value,
        max_value,
        mean_value,
        key="min_val"
    )
    filtrado_df_min = df[df["longituddeldragon"] > min_val]
    st.write(f"Registros con valor superior a {min_val:.2f} cm:")
    st.dataframe(filtrado_df_min)

with col2:
    # Filtro de valor máximo
    max_val = st.slider(
        'Valor máximo',
        min_value,
        max_value,
        mean_value,
        key="max_val"
    )
    filtrado_df_max = df[df["longituddeldragon"] < max_val]
    st.write(f"Registros con valor inferior a {max_val:.2f} cm:")
    st.dataframe(filtrado_df_max)

# Descargar datos filtrados
if st.button('Descargar datos filtrados'):
    csv = filtrado_df_min.to_csv().encode('utf-8')
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name='datos_filtrados.csv',
        mime='text/csv',
    )

# Footer
st.markdown("""
    ---
    Desarrollado para monitoreo del crecimiento de un dragón basado en sensores.
""")
