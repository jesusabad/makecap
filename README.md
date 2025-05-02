# makecap.py

Este script de Python utiliza Selenium para descargar imágenes de una página web, simulando scrolls para cargar contenido dinámico, y luego las convierte a un archivo CBZ.

## Requisitos

* Python 3.x
* Bibliotecas de Python (instalables con `pip install -r requirements.txt`):
    * selenium
    * requests
    * Pillow (PIL)
    * urllib3

* Geckodriver (Firefox driver) instalado y en el PATH del sistema.

## Uso

1.  Clonar este repositorio.
2.  Instalar los requisitos: `pip install -r requirements.txt`
3.  Ejecutar el script: `python3 makecap.py`
4.  Ingresar la URL de la página web cuando se solicite.
5.  El archivo CBZ resultante se guardará en el mismo directorio.

## Notas

* Asegúrate de tener Firefox instalado.
* Es posible que necesites ajustar la ruta a `geckodriver` en el script.
* El script maneja páginas con carga dinámica mediante scrolls.
* Las imágenes se descargan y convierten a JPG antes de crear el CBZ.
* Se limpian los archivos temporales después de la ejecución.

## Advertencias

* Usar este script para descargar contenido de sitios web debe hacerse respetando los términos de servicio y derechos de autor de cada sitio.
* El uso indebido puede resultar en bloqueos o problemas legales.
* El autor no se hace responsable del uso que se le dé a este script.
