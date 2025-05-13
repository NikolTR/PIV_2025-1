Este proyecto realiza la extracción, limpieza y almacenamiento de datos históricos de precios de acciones de la empresa **Meta Platforms Inc. (META)** desde Yahoo Finance. El flujo incluye la recolección desde HTML, transformación, estandarización de columnas, y almacenamiento local en formato CSV.

---

## 🚀 Tecnologías utilizadas

- Python 3.10+
- BeautifulSoup 4
- pandas
- requests
- logging personalizado

---

## 🧠 Estructura del proyecto

```
src/
├── edu_piv/
│   ├── collector.py         # Clase que recolecta y limpia los datos
│   ├── logger.py            # Logger personalizado con estructura enriquecida
│   ├── main.py              # Script principal para ejecutar el flujo
│   └── static/
│       └── data/
│           └── meta_history.csv   # Archivo de salida con los datos
```

---

## ⚙️ Instalación y ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```

2. Instala las dependencias:
   ```bash
   pip install e.

3. Activa el entorno virtual:
   ```bash
   venv\Scripts\activate
   ```

4. Ejecuta el script principal:
   ```bash
   python src/edu_piv/main.py
   ```

5. Revisa el archivo generado:
   ```
   src/edu_piv/static/data/meta_history.csv
   ```

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

## 📝 Ejemplo de salida (CSV)

```csv
fecha,abrir,max,min,cerrar,cierre_ajustado,volumen
05/10/2025,602.34,610.50,598.01,604.72,604.72,10234900
05/09/2025,603.72,606.97,591.71,592.49,592.49,10408400
...
```

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









