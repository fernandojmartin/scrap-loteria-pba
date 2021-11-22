# Extractor de resultados de Quiniela de la Provincia   

#### ~ Este es un proyecto de hobby ~

Está realizado en Python 3 y lo que hace es:
- Dada una fecha, recolecta todos los resultados para esa fecha con todos los extractos
- Descarga los PDFs
- Extrae los resultados de cada sorteo publicado
- Almacena los datos para luego hacer análisis de datos
- Registra en una base de datos SQlite las URLs y PDFs procesados para evitar procesos repetidos

Esta es una primera versión que requiere invocación manual. En una próxima se podrá automatizar con Apache Airflow.

## Ejecución

Para hacer scraping y descargar los PDFs se debe invocar el scraper de la siguiente manera: 
```bash
$ python daily_crawler.py YYYY/MM/DD 
```
La fecha debe estar en ese formato. Hay que tener en cuenta que no todos los días hay resultados 
y en tal caso se devuelve el error del sitio.

Para ejecutar la extracción de datos, se invoca de la siguiente manera:
```bash
$ python extractor.py
```
Éste buscará todos los PDFs que no se hayan procesado (el estado se almacena en la DB) y los extraerá.
De momento sólo procesa los de tipo "Quiniela Múltiple".
En el futuro se añadirán más formatos.
