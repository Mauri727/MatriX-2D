# MatriX v1.0 🏗️
### Sistema Computacional para el Análisis Matricial de Pórticos Planos en 2D
**Universidad Autónoma Juan Misael Saracho (UAJMS)** *Facultad de Ciencias y Tecnología - Carrera de Ingeniería Civil* *Materia: CIV 931 - Análisis de Estructuras III*

---

## 📝 Descripción del Proyecto

**MatriX v1.0** es una aplicación de escritorio nativa desarrollada en Python orientada al análisis lineal de estructuras aporticadas en el plano mediante el **Método Matricial de la Rigidez Directo**. 

Este software surge como una alternativa automatizada, robusta e interactiva a las tradicionales hojas de cálculo de MathCAD, permitiendo a estudiantes e ingenieros modelar topologías complejas, introducir estados de carga mixtos y obtener de forma instantánea tanto la respuesta numérica (desplazamientos y reacciones) como la representación gráfica de las solicitaciones internas.

---

## 🎯 Objetivos del Sistema

* **Automatización Absoluta:** Eliminar el ensamblaje manual de matrices elásticas y la manipulación manual de vectores de carga, reduciendo el error humano a cero.
* **Fidelidad Académica:** Generar memorias de cálculo impresas (`.txt`) que sigan estrictamente el formato tabular y el paso a paso algebraico exigido por la cátedra de Análisis Estructural III de la UAJMS.
* **Interactividad Científica:** Proveer herramientas visuales para la interpretación física inmediata del comportamiento estructural bajo cargas de servicio.

---

## ✨ Características Principales y Capacidades Técnicas

MatriX v1.0 incorpora algoritmos de nivel comercial adaptados a las necesidades de la materia:

1. **Modelado Geométrico Flexible:** Introducción ilimitada de nudos y barras en coordenadas globales (X, Y).
2. **Cosenos Directores Automáticos:** El programa calcula la longitud (L) y el ángulo de inclinación (theta) de elementos esviajados o inclinados a partir de sus coordenadas nodales, construyendo la matriz de transformación [T] de 6 x 6 automáticamente.
3. **Soporte para Estructuras Mixtas (Condensación Estática):** Permite la liberación de momentos flectores (*Moment Releases*) en los extremos de las barras (*Rótula en Nodo i / j*), reduciendo la matriz elástica local mediante condensación para modelar vigas articuladas o cerchas puras.
4. **Motor de Cargas Avanzado:** Procesamiento de cargas puntuales en nudos y cargas distribuidas (uniformes y variables/triangulares) aplicadas en sistemas de coordenadas tanto locales como globales (ideal para la proyección del viento en cubiertas inclinadas).
5. **Dibujo Dinámico de Apoyos (Rotación Unificada):** Renderización precisa de 6 tipologías de apoyo (Empotramiento perfecto, apoyo fijo, apoyos móviles horizontales/verticales y empotramientos guiados o deslizantes) con rotación angular interactiva respecto al centro del nudo.
6. **Inspector Analítico Exacto:** Evaluación de esfuerzos (Axial, Corte, Momento) y desplazamientos en cualquier sección infinitesimal (x) de la barra utilizando los **Polinomios Cúbicos de Hermite** (funciones de forma exactas de Euler-Bernoulli).

---

## 🛠️ Arquitectura del Software

El código fuente está estructurado bajo un paradigma modular enfocado en la separación de responsabilidades:

* `motor_calculo.py` (Backend): Contiene las abstracciones físicas (`Nodo`, `Elemento`, `Estructura`) y las operaciones de álgebra lineal (inversión de matrices mediante eliminación gaussiana con la librería `NumPy`).
* `memoria_calculo.py` (Módulo de Reportes): Se encarga de procesar los tensores de resultados a través de `Pandas`, tabulando las matrices locales 6 x 6, globales y estructurales en formato de notación científica.
* `main.py` (Frontend e Interfaz): Administra la interfaz de usuario moderna construida con `CustomTkinter` y controla el lienzo gráfico interactivo embebido con `Matplotlib`.

---

## 🚀 Requisitos e Instalación

Para ejecutar MatriX v1.0 desde el código fuente, asegúrese de contar con **Python 3.10 o superior** instalado en su sistema operativo.

1. Clonar el Repositorio
```bash   
git clone [https://github.com/TU-USUARIO/MatriX-2D.git](https://github.com/TU-USUARIO/MatriX-2D.git)
cd MatriX-2D

2. Instalar Dependencias
Instale las librerías científicas y de interfaz necesarias ejecutando el gestor de paquetes de Python (pip):
pip install -r requirements.txt

3. Ejecutar la AplicaciónInicie el entorno gráfico del programa ejecutando el archivo principal:
python main.py
Nota: Si se desea compilar el software en un archivo ejecutable único de Windows (.exe), ejecute en la terminal:
pip install pyinstaller
pyinstaller --onefile --windowed main.py

📖 Manual Breve de Usuario
1. Definir Nodos: Ingrese a la opción 1. Definir Nodos, coloque las coordenadas y configure las restricciones de soporte marcando las casillas (Tx, Ty, Rz). Si el nudo es una articulación completa, active Rótula / Armadura.
2. Trazar Barras: En la opción 2. Trazar Elementos, conecte los nudos indicando el nodo inicial (i) y final (j). Defina las propiedades de sección (E, A, I).
3. Aplicar Cargas: Utilice las pestañas correspondientes para añadir fuerzas nodales puntuales o presiones distribuidas sobre los elementos.
4. Calcular: Presione el botón verde ▶ CALCULAR. El panel inferior expondrá las reacciones de inmediato.
5. Visualización y Reportes: Cambie el menú desplegable superior para examinar las gráficas de Momento, Cortante o la Deformada. Haga clic en Ver Memoria o Exportar Documento para extraer el reporte auditable en formato .txt.

👥 Créditos y Cátedra
Materia: Análisis de Estructuras III (CIV 931) - Grupo 1
Docente: MSc. Ing. Ernesto Alvarez Gozalvez
Institución: Universidad Autónoma Juan Misael Saracho - Tarija, Bolivia
