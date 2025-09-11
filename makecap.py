import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from zipfile import ZipFile
import time
import requests
import urllib3
from urllib.parse import urljoin
from PIL import Image
import re  # Expresiones regulares

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def descargar_pagina_con_firefox(url, carpeta_descarga):
    """
    Descarga la página completa usando Firefox con Selenium, realizando scrolls intermedios.
    """
    try:
        # Configurar Firefox
        geckodriver_path = '/usr/local/bin/geckodriver'  # Cambia si tu geckodriver está en otra ruta
        firefox_options = Options()
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", carpeta_descarga)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/webp")
        firefox_options.add_argument("--headless")

        service = FirefoxService(executable_path=geckodriver_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)

        # Cargar la página
        print(f"Cargando la página: {url}")
        driver.get(url)
        time.sleep(1)

        # Simular scrolls intermedios
        print("Simulando scrolls intermedios para cargar las imágenes...")
        scroll_pause_time = 1
        total_height = driver.execute_script("return document.body.scrollHeight;")
        num_scrolls = 4
        scroll_increment = total_height // num_scrolls
        current_scroll = 0

        for _ in range(num_scrolls):
            current_scroll += scroll_increment
            driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            time.sleep(scroll_pause_time * 2)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time * 2)

        print("Scrolls completados. Esperando carga de imágenes...")
        time.sleep(1)

        # Extraer imágenes .webp válidas
        imagenes_webp = driver.find_elements(
            "xpath",
            "//img[(contains(@src, '.webp') and contains(@src, '/uploads/') and not(contains(@src, '/defaults/loading.gif'))) or "
            "(contains(@data-src, '.webp') and contains(@data-src, '/uploads/') and not(contains(@data-src, '/defaults/loading.gif')))]"
        )

        if not imagenes_webp:
            print("No se encontraron imágenes válidas en la página.")
            driver.quit()
            return []

        # Definir padding dinámico según cantidad total
        total_imagenes = len(imagenes_webp)
        ancho = len(str(total_imagenes))

        rutas_jpg = []
        urls_descargadas = set()
        contador = 1

        for img in imagenes_webp:
            img_url = img.get_attribute('src') or img.get_attribute('data-src')
            if img_url and img_url.endswith('.webp') and '/uploads/' in img_url and '/defaults/loading.gif' not in img_url and img_url not in urls_descargadas:
                if not img_url.startswith('http') and not img_url.startswith('//'):
                    img_url = urljoin(url, img_url)

                # Nombre secuencial con ceros dinámicos
                nombre_jpg = f"{contador:0{ancho}d}.jpg"
                ruta_jpg = os.path.join(carpeta_descarga, nombre_jpg)
                print(f"Descargando y convirtiendo: {img_url} -> {nombre_jpg}")

                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        'Referer': url
                    }
                    response = requests.get(img_url, stream=True, verify=False, timeout=10, headers=headers)
                    response.raise_for_status()
                    with open(f"{ruta_jpg}.webp_temp", 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Convertir .webp a .jpg
                    try:
                        img_pil = Image.open(f"{ruta_jpg}.webp_temp").convert('RGB')
                        img_pil.save(ruta_jpg, 'JPEG')
                        os.remove(f"{ruta_jpg}.webp_temp")
                        rutas_jpg.append(ruta_jpg)
                        urls_descargadas.add(img_url)
                        contador += 1
                    except Exception as e:
                        print(f"Error al convertir {img_url}: {e}")
                        if os.path.exists(f"{ruta_jpg}.webp_temp"):
                            os.remove(f"{ruta_jpg}.webp_temp")

                except requests.exceptions.RequestException as e:
                    print(f"Error al descargar {img_url}: {e}")

        print("Descarga y conversión completadas.")
        driver.quit()
        return rutas_jpg

    except Exception as e:
        print(f"Error al descargar imágenes: {e}")
        return []

def comprimir_a_zip(imagenes, archivo_salida_base):
    """
    Comprime las imágenes en un archivo ZIP con nombre secuencial basado en los CBZ existentes.
    """
    try:
        archivos_cbz = [f for f in os.listdir('.') if f.endswith('.cbz') and f.startswith(archivo_salida_base)]
        numeros_existentes = []
        for archivo in archivos_cbz:
            match = re.search(r'(\d+)', archivo)
            if match:
                numeros_existentes.append(int(match.group(1)))

        siguiente_numero = 1
        if numeros_existentes:
            siguiente_numero = max(numeros_existentes) + 1

        archivo_zip = f"{archivo_salida_base}{siguiente_numero:02d}.zip"

        with ZipFile(archivo_zip, 'w') as zipf:
            if imagenes:
                common_path = os.path.dirname(min(imagenes, key=len))
                for img_path in imagenes:
                    zipf.write(img_path, os.path.relpath(img_path, common_path))
            else:
                print("No hay imágenes para comprimir.")
        print(f"Archivo comprimido creado: {archivo_zip}")
        return archivo_zip
    except Exception as e:
        print(f"Error al comprimir archivos: {e}")
        return None

def cambiar_extension(archivo_original, nueva_extension):
    """
    Cambia la extensión de un archivo.
    """
    try:
        nuevo_archivo = os.path.splitext(archivo_original)[0] + nueva_extension
        os.rename(archivo_original, nuevo_archivo)
        print(f"Extensión cambiada a {nueva_extension}: {nuevo_archivo}")
    except Exception as e:
        print(f"Error al cambiar la extensión: {e}")

def main():
    url = input("Ingrese la URL de la página (ejemplo: https://zonatmo.com/): ").strip()
    carpeta_temporal = "temp_images"
    nombre_base_archivo = "capitulo"

    os.makedirs(carpeta_temporal, exist_ok=True)
    imagenes_jpg = descargar_pagina_con_firefox(url, carpeta_temporal)

    if not imagenes_jpg:
        print("No se descargaron imágenes. El proceso se detendrá aquí.")
        return

    archivo_zip = comprimir_a_zip(imagenes_jpg, nombre_base_archivo)

    if archivo_zip:
        cambiar_extension(archivo_zip, ".cbz")

    if os.path.exists(carpeta_temporal):
        for root, dirs, files in os.walk(carpeta_temporal):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(carpeta_temporal)
    else:
        print("La carpeta temporal no existe, no se realizará limpieza.")

if __name__ == "__main__":
    main()
