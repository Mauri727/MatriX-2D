# MatriX v1.0 🏗️

### Sistema Computacional para el Análisis Matricial de Pórticos Planos en 2D

**Universidad Autónoma Juan Misael Saracho (UAJMS)** | *Facultad de Ciencias y Tecnología - Carrera de Ingeniería Civil* | *Materia: CIV 931 - Análisis de Estructuras III*

<img width="2093" height="1412" alt="image" src="https://github.com/user-attachments/assets/5509cd8a-5abd-4d18-aa21-d23765a6182d" />

---

## 📝 Descripción del Proyecto

**MatriX v1.0** es una aplicación de escritorio nativa desarrollada en Python orientada al análisis lineal de estructuras aporticadas en el plano mediante el **Método Matricial de la Rigidez Directo**.

Este software surge como una alternativa automatizada, robusta e interactiva a las tradicionales hojas de cálculo de MathCAD, permitiendo a estudiantes e ingenieros modelar topologías complejas, introducir estados de carga mixtos y obtener de forma instantánea tanto la respuesta numérica (desplazamientos y reacciones) como la representación gráfica de las solicitaciones internas.

## 🎯 Objetivos del Sistema

* **Automatización Absoluta:** Eliminar el ensamblaje manual de matrices elásticas y la manipulación manual de vectores de carga, reduciendo el error humano a cero.
* **Fidelidad Académica:** Generar memorias de cálculo impresas (`.txt`) que sigan estrictamente el formato tabular y el paso a paso algebraico exigido por la cátedra de Análisis Estructural III de la UAJMS.
* **Interactividad Científica:** Proveer herramientas visuales para la interpretación física inmediata del comportamiento estructural bajo cargas de servicio.

## ✨ Características Principales y Capacidades Técnicas

MatriX v1.0 incorpora algoritmos de nivel comercial adaptados a las necesidades de la materia:

* **Modelado Geométrico Flexible:** Introducción ilimitada de nudos y barras en coordenadas globales (X, Y).
* **Cosenos Directores Automáticos:** El programa calcula la longitud (L) y el ángulo de inclinación (θ) de elementos esviajados o inclinados a partir de sus coordenadas nodales, construyendo la matriz de transformación [T] de 6 x 6 automáticamente.
* **Soporte para Estructuras Mixtas (Condensación Estática):** Permite la liberación de momentos flectores (*Moment Releases*) en los extremos de las barras (Rótula en Nodo i / j), reduciendo la matriz elástica local mediante condensación para modelar vigas articuladas o cerchas puras.
* **Motor de Cargas Avanzado:** Procesamiento de cargas puntuales en nudos y cargas distribuidas (uniformes y variables/triangulares) aplicadas en sistemas de coordenadas tanto locales como globales (ideal para la proyección del viento en cubiertas inclinadas).
* **Dibujo Dinámico de Apoyos (Rotación Unificada):** Renderización precisa de 6 tipologías de apoyo (Empotramiento perfecto, apoyo fijo, apoyos móviles horizontales/verticales y empotramientos guiados o deslizantes) con rotación angular interactiva respecto al centro del nudo.
* **Inspector Analítico Exacto:** Evaluación de esfuerzos (Axial, Corte, Momento) y desplazamientos en cualquier sección infinitesimal (x) de la barra utilizando los Polinomios Cúbicos de Hermite (funciones de forma exactas de Euler-Bernoulli).

## 🛠️ Arquitectura del Software

El código fuente está estructurado bajo un paradigma modular enfocado en la separación de responsabilidades:

1. `motor_calculo.py` **(Backend):** Contiene las abstracciones físicas (Nodo, Elemento, Estructura) y las operaciones de álgebra lineal (inversión de matrices mediante eliminación gaussiana con la librería NumPy).
2. `memoria_calculo.py` **(Módulo de Reportes):** Se encarga de procesar los tensores de resultados a través de Pandas, tabulando las matrices locales 6 x 6, globales y estructurales en formato de notación científica.
3. `main.py` **(Frontend e Interfaz):** Administra la interfaz de usuario moderna construida con CustomTkinter y controla el lienzo gráfico interactivo embebido con Matplotlib.

## 🚀 Requisitos e Instalación

Para ejecutar MatriX v1.0 desde el código fuente, asegúrese de contar con **Python 3.10 o superior** instalado en su computadora (Recuerde marcar la casilla *"Add Python to PATH"* durante la instalación).

**1. Descargar el Código Fuente**
* Haga clic en el botón verde **`<> Code`** en la parte superior derecha de esta página y seleccione **`Download ZIP`**.
* Descomprima el archivo descargado en su computadora (ej. en su Escritorio).
<img width="1583" height="610" alt="Screenshot 2026-06-22 224916" src="https://github.com/user-attachments/assets/4713dc64-31c6-4fd8-a92c-c38b75fa0911" />

<img width="897" height="736" alt="Screenshot 2026-06-22 225013" src="https://github.com/user-attachments/assets/f6829946-67bd-4d97-89f9-817ef8a481e1" />

**2. Abrir la Consola de Comandos**
* Entre a la carpeta que acaba de descomprimir.
* Haga clic en la barra de direcciones de la carpeta (donde dice la ruta), borre el texto, escriba `cmd` y presione **Enter**. Se abrirá una pantalla negra de terminal.

<img width="1813" height="320" alt="Screenshot 2026-06-22 225212" src="https://github.com/user-attachments/assets/d73a7db6-fa4d-4224-9182-c16067ac2594" />

<img width="1428" height="451" alt="Screenshot 2026-06-22 225252" src="https://github.com/user-attachments/assets/d2f8e83b-c9bd-48d3-aeed-abd935c15de7" />

<img width="1678" height="502" alt="Screenshot 2026-06-22 225332" src="https://github.com/user-attachments/assets/412f9d2d-e302-4cd6-ac42-fe37011eb8a4" />

**3. Instalar Dependencias**
Instale las librerías científicas y de interfaz necesarias pegando el siguiente comando y presionando Enter:
```bash
pip install -r requirements.txt
```
<img width="1359" height="717" alt="Screenshot 2026-06-22 225426" src="https://github.com/user-attachments/assets/a65bf77c-9d5b-4dce-8030-3e00f531dee8" />

**4. Ejecutar la Aplicación**
Inicie el entorno gráfico del programa ejecutando el archivo principal:

```Bash
python main.py
```
<img width="1324" height="722" alt="Screenshot 2026-06-22 225520" src="https://github.com/user-attachments/assets/9fad2e60-2626-4a4f-b37b-43c72cf47698" />

Nota: Si se desea compilar el software en un archivo ejecutable único de Windows (.exe), ejecute en la terminal:

```Bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```
<img width="1662" height="563" alt="Screenshot 2026-06-22 225722" src="https://github.com/user-attachments/assets/7bd0d4a2-a00a-47aa-980d-d0a653ebf9d3" />

**📖 Manual Breve de Usuario**
Definir Nodos: Ingrese a la opción 1. Definir Nodos, coloque las coordenadas y configure las restricciones de soporte marcando las casillas (Tx, Ty, Rz). Si el nudo es una articulación completa, active Rótula / Armadura.
<img width="1746" height="981" alt="image" src="https://github.com/user-attachments/assets/c4f9f409-4e06-4a5a-ad71-0c98e0b95a51" />

<img width="943" height="1048" alt="Screenshot 2026-06-22 230331" src="https://github.com/user-attachments/assets/9326661e-ae71-45ee-b695-f465f887c655" />


Trazar Barras: En la opción 2. Trazar Elementos, conecte los nudos indicando el nodo inicial (i) y final (j). Defina las propiedades de sección (E, A, I).
<img width="943" height="1048" alt="Screenshot 2026-06-22 230331" src="https://github.com/user-attachments/assets/1ed816d5-5d0e-4a69-a808-c9e0ad397aa2" />

<img width="780" height="1067" alt="Screenshot 2026-06-22 230434" src="https://github.com/user-attachments/assets/2908529d-1fce-402d-a5e5-e9e365fb6896" />

Aplicar Cargas: Utilice las pestañas correspondientes para añadir fuerzas nodales puntuales o presiones distribuidas sobre los elementos.

<img width="1144" height="777" alt="Screenshot 2026-06-22 230401" src="https://github.com/user-attachments/assets/bbc5b41d-e4bc-4229-8ac7-d24724d016e5" />
<img width="775" height="985" alt="Screenshot 2026-06-22 230443" src="https://github.com/user-attachments/assets/47f1d419-1ce5-4ee7-a153-df77adacad9b" />
<img width="775" height="985" alt="Screenshot 2026-06-22 230443" src="https://github.com/user-attachments/assets/48090230-c028-4347-a533-c9d52a19afe5" />
<img width="773" height="1004" alt="Screenshot 2026-06-22 230457" src="https://github.com/user-attachments/assets/bf04209b-4220-4b4f-9b37-323bf62a4757" />



Calcular: Presione el botón verde ▶ CALCULAR. El panel inferior expondrá las reacciones de inmediato.
<img width="1174" height="775" alt="image" src="https://github.com/user-attachments/assets/3bd3dcd1-0dfc-4ab8-b2d9-95f3ce03faa2" />



Visualización y Reportes: Cambie el menú desplegable superior para examinar las gráficas de Momento, Cortante o la Deformada.
<img width="1279" height="731" alt="Screenshot 2026-06-22 230552" src="https://github.com/user-attachments/assets/73ed48cb-dfa1-4e5a-a1c3-21f2d93e4918" />

Haga clic en Ver Memoria o Exportar Documento para extraer el reporte auditable en formato .txt.
<img width="1170" height="791" alt="image" src="https://github.com/user-attachments/assets/9ce8c9fa-4430-441d-816c-0551b2150f95" />
<img width="1174" height="768" alt="image" src="https://github.com/user-attachments/assets/45c8244e-6e16-41a5-8bb8-9f953c48a5ab" />


**👥 Créditos y Cátedra**

Materia: Análisis de Estructuras III (CIV 931) - Grupo 1

Docente: MSc. Ing. Ernesto Alvarez Gozalvez

Institución: Universidad Autónoma Juan Misael Saracho - Tarija, Bolivia
