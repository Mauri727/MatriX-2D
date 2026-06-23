import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import json 

from motor_calculo import Nodo, Elemento, Estructura
from memoria_calculo import GeneradorMemoria

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MatrixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MatriX - Análisis Estructural")
        self.geometry("1200x800")
        
        self.modelo = Estructura()
        self.K_global = None 
        self.archivo_actual = None 
        
        # --- SISTEMA DE UNIDADES DINÁMICO ---
        self.sistema_unidades = "kN-m"
        self.u_len = "m"; self.u_area = "m²"; self.u_iner = "m^4"
        self.u_force = "kN"; self.u_mom = "kNm"; self.u_q = "kN/m"; self.u_E = "kPa"
        self.f_E = 1.0; self.f_A = 1.0; self.f_I = 1.0
        self.uf, self.ul, self.um = "kN", "m", "kNm" 

        self.crear_menu_superior()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- FRAME LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MatriX", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        ctk.CTkButton(self.sidebar_frame, text="1. Definir Nodos", command=self.abrir_formulario_nodos).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="2. Trazar Elementos", command=self.abrir_formulario_elementos).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="3. Aplicar Cargas", command=self.abrir_formulario_cargas).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="4. Editar / Eliminar", command=self.abrir_formulario_eliminar, fg_color="#8E44AD", hover_color="#9B59B6").grid(row=4, column=0, padx=20, pady=10)
        
        ctk.CTkButton(self.sidebar_frame, text="▶ CALCULAR", fg_color="#27AE60", hover_color="#2ECC71", command=self.ejecutar_calculo).grid(row=5, column=0, padx=20, pady=30)

        # --- FRAME CENTRAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2b2b2b")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.frame_top = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_top.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(self.frame_top, text="Ver Diagrama:").pack(side="left", padx=(10, 5))
        self.combo_vista = ctk.CTkOptionMenu(self.frame_top, values=["Modelo Básico", "Axial", "Cortante", "Momento", "Deformada"], command=self.cambiar_vista)
        self.combo_vista.pack(side="left")

        self.switch_reacciones = ctk.CTkSwitch(self.frame_top, text="Mostrar Reacciones", command=self.dibujar_estructura)
        self.switch_reacciones.pack(side="left", padx=(20, 0))
        self.switch_reacciones.select() 
        
        self.btn_exportar = ctk.CTkButton(self.frame_top, text="💾 Exportar Documento", command=self.exportar_memoria, fg_color="#D35400", hover_color="#E67E22")
        self.btn_exportar.pack(side="right", padx=5)
        
        self.btn_inspector = ctk.CTkButton(self.frame_top, text="🔍 Inspector Manual", command=self.abrir_inspector_valores, fg_color="#8E44AD", hover_color="#9B59B6")
        self.btn_inspector.pack(side="right", padx=5)
        
        ctk.CTkButton(self.frame_top, text="📄 Ver Memoria", command=self.mostrar_memoria_completa).pack(side="right", padx=10)

        self.frame_grafico = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.caja_resultados = ctk.CTkTextbox(self.main_frame, height=150, font=ctk.CTkFont(family="Consolas", size=12))
        self.caja_resultados.pack(fill="x", padx=10, pady=(0, 10))
        self.caja_resultados.insert("0.0", "Comienza modelando la estructura.\n")
        
        # Aplicamos las unidades predeterminadas y dibujamos
        self.cambiar_unidades("kN-m")

    # =========================================================
    # MENÚ Y SISTEMA DE UNIDADES
    # =========================================================
    def crear_menu_superior(self):
        menubar = tk.Menu(self)
        
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Nuevo Proyecto", command=self.nuevo_proyecto)
        filemenu.add_separator()
        filemenu.add_command(label="Abrir Proyecto (.json)", command=self.abrir_archivo)
        filemenu.add_command(label="Guardar", command=self.guardar_archivo)
        filemenu.add_command(label="Guardar Como...", command=self.guardar_como)
        menubar.add_cascade(label="Archivo", menu=filemenu)
        
        optmenu = tk.Menu(menubar, tearoff=0)
        optmenu.add_command(label="Unidades: SI [ m, mm², MPa ]", command=lambda: self.cambiar_unidades("SI"))
        optmenu.add_command(label="Unidades: kN-m [ m, m², kPa ]", command=lambda: self.cambiar_unidades("kN-m"))
        optmenu.add_command(label="Unidades: US [ ft, in², ksi ]", command=lambda: self.cambiar_unidades("US"))
        menubar.add_cascade(label="Opciones", menu=optmenu)
        
        self.config(menu=menubar)

    def nuevo_proyecto(self):
        if messagebox.askyesno("Nuevo Proyecto", "¿Estás seguro de crear un nuevo proyecto? Se perderán los datos no guardados."):
            self.modelo = Estructura()
            self.K_global = None
            self.archivo_actual = None
            
            # [CORRECCIÓN]: Forzar la interfaz a regresar al Modelo Básico
            self.combo_vista.set("Modelo Básico") 
            
            self.caja_resultados.delete("0.0", "end")
            self.caja_resultados.insert("0.0", "Nuevo proyecto iniciado.\n")
            self.dibujar_estructura()
            
    def cambiar_unidades(self, sist):
        self.sistema_unidades = sist
        # Lógica de formato y conversión interna para igualar a Ftool
        if sist == "SI":
            self.u_len = "m"; self.u_area = "mm²"; self.u_iner = "mm^4"
            self.u_force = "kN"; self.u_mom = "kNm"; self.u_q = "kN/m"; self.u_E = "MPa"
            self.f_E = 1000.0; self.f_A = 1e-6; self.f_I = 1e-12
        elif sist == "kN-m":
            self.u_len = "m"; self.u_area = "m²"; self.u_iner = "m^4"
            self.u_force = "kN"; self.u_mom = "kNm"; self.u_q = "kN/m"; self.u_E = "kPa"
            self.f_E = 1.0; self.f_A = 1.0; self.f_I = 1.0
        else: # US
            self.u_len = "ft"; self.u_area = "in²"; self.u_iner = "in^4"
            self.u_force = "kip"; self.u_mom = "ft-kip"; self.u_q = "kip/ft"; self.u_E = "ksi"
            self.f_E = 144.0; self.f_A = 1/144.0; self.f_I = 1/20736.0
            
        self.uf, self.ul, self.um = self.u_force, self.u_len, self.u_mom
        self.caja_resultados.insert(ctk.END, f"\n[INFO] Unidades cambiadas al Sistema {sist}.\n")
        self.dibujar_estructura()

    def guardar_archivo(self):
        if self.archivo_actual:
            with open(self.archivo_actual, 'w', encoding='utf-8') as f: json.dump(self.modelo.to_dict(), f, indent=4)
            self.caja_resultados.insert(ctk.END, "[GUARDADO] Proyecto actualizado.\n")
        else: self.guardar_como()

    def guardar_como(self):
        arch = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivos JSON", "*.json")])
        if arch:
            self.archivo_actual = arch
            with open(arch, 'w', encoding='utf-8') as f: json.dump(self.modelo.to_dict(), f, indent=4)
            self.caja_resultados.insert(ctk.END, f"[GUARDADO] Proyecto guardado.\n")
            return True
        return False

    def abrir_archivo(self):
        arch = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if arch:
            try:
                with open(arch, 'r', encoding='utf-8') as f: data = json.load(f)
                self.modelo = Estructura.from_dict(data)
                self.archivo_actual = arch
                self.K_global = None 
                
                # [CORRECCIÓN]: Al abrir un archivo, mostramos su geometría primero
                self.combo_vista.set("Modelo Básico") 
                
                self.caja_resultados.insert(ctk.END, f"[ABIERTO] Proyecto cargado con éxito.\n")
                self.dibujar_estructura()
            except Exception as e: 
                self.caja_resultados.insert(ctk.END, f"[ERROR] Archivo corrupto.\n")

    def exportar_memoria(self):
        # [DEFENSA]: Prevención de errores. Verificamos que la matriz exista antes de exportar.
        if self.K_global is None: 
            messagebox.showwarning("Atención", "¡Debes modelar y presionar 'CALCULAR' antes de exportar la memoria!")
            return
            
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Doc Texto", "*.txt")])
        if archivo:
            try:
                with open(archivo, 'w', encoding='utf-8') as f: 
                    f.write(GeneradorMemoria(self.modelo).generar_texto_completo(self.K_global))
                self.caja_resultados.insert(ctk.END, f"[EXPORTADO] Memoria guardada exitosamente.\n")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def mostrar_memoria_completa(self):
        # [DEFENSA]: Si el usuario pide la memoria sin calcular, le avisamos en lugar de ignorarlo.
        if self.K_global is None: 
            messagebox.showwarning("Atención", "¡Debes modelar y presionar 'CALCULAR' para ver la memoria!")
            return
            
        v = ctk.CTkToplevel(self)
        v.title("Memoria Completa")
        self.centrar_ventana(v, 800, 600)
        v.attributes('-topmost', True)
        
        txt = ctk.CTkTextbox(v, font=ctk.CTkFont(family="Consolas", size=13))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("0.0", GeneradorMemoria(self.modelo).generar_texto_completo(self.K_global))

    def centrar_ventana(self, ventana, ancho, alto):
        x = int((self.winfo_screenwidth()/2) - (ancho/2))
        y = int((self.winfo_screenheight()/2) - (alto/2))
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    # =========================================================
    # FORMULARIOS
    # =========================================================
    def abrir_formulario_nodos(self):
        v = ctk.CTkToplevel(self); v.title("Definir Nodo"); self.centrar_ventana(v, 550, 580); v.attributes('-topmost', True); v.grab_set()
        ctk.CTkLabel(v, text="Nuevo Nodo", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        f = ctk.CTkFrame(v, fg_color="transparent"); f.pack(expand=True)
        
        ctk.CTkLabel(f, text="ID:").grid(row=0, column=0, pady=5, sticky="e", padx=10); e_id = ctk.CTkEntry(f, width=120); e_id.grid(row=0, column=1, columnspan=2, sticky="w")
        ctk.CTkLabel(f, text=f"Coordenada X [{self.u_len}]:").grid(row=1, column=0, pady=5, sticky="e", padx=10); e_x = ctk.CTkEntry(f, width=120); e_x.grid(row=1, column=1, columnspan=2, sticky="w")
        ctk.CTkLabel(f, text=f"Coordenada Y [{self.u_len}]:").grid(row=2, column=0, pady=5, sticky="e", padx=10); e_y = ctk.CTkEntry(f, width=120); e_y.grid(row=2, column=1, columnspan=2, sticky="w")
        
        ctk.CTkLabel(f, text="Condiciones de Apoyo y Desplazamientos Iniciales:", font=ctk.CTkFont(weight="bold"), text_color="#3498DB").grid(row=3, column=0, columnspan=3, pady=(15, 5))
        s_rx = ctk.CTkSwitch(f, text="Restringir X"); s_rx.grid(row=4, column=0, pady=5, padx=10, sticky="w")
        ctk.CTkLabel(f, text=f"Desplaz. Δx [{self.u_len}]:").grid(row=4, column=1, pady=5, sticky="e", padx=5); e_dx = ctk.CTkEntry(f, width=80); e_dx.grid(row=4, column=2, sticky="w")
        s_ry = ctk.CTkSwitch(f, text="Restringir Y"); s_ry.grid(row=5, column=0, pady=5, padx=10, sticky="w")
        ctk.CTkLabel(f, text=f"Desplaz. Δy [{self.u_len}]:").grid(row=5, column=1, pady=5, sticky="e", padx=5); e_dy = ctk.CTkEntry(f, width=80); e_dy.grid(row=5, column=2, sticky="w")
        s_rz = ctk.CTkSwitch(f, text="Restringir Rz"); s_rz.grid(row=6, column=0, pady=5, padx=10, sticky="w")
        ctk.CTkLabel(f, text="Giro Δz [rad]:").grid(row=6, column=1, pady=5, sticky="e", padx=5); e_dr = ctk.CTkEntry(f, width=80); e_dr.grid(row=6, column=2, sticky="w")
        s_art = ctk.CTkSwitch(f, text="Rótula / Armadura", button_color="#F1C40F"); s_art.grid(row=7, column=0, columnspan=3, pady=15)
        ctk.CTkLabel(f, text="Ángulo Apoyo [°]:").grid(row=8, column=0, pady=5, sticky="e", padx=10); e_ang = ctk.CTkEntry(f, width=80); e_ang.insert(0, "0.0"); e_ang.grid(row=8, column=1, sticky="w")
        ctk.CTkLabel(f, text="↺ (+)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2ECC71").grid(row=8, column=2, sticky="w")

        def guardar():
            # [DEFENSA]: Validación Estricta - Evita nodos duplicados
            try: nuevo_id = int(e_id.get())
            except ValueError: return messagebox.showerror("Error", "El ID debe ser un número entero.")
            if any(n.id == nuevo_id for n in self.modelo.nodos):
                return messagebox.showerror("Error de ID", f"¡El Nodo con ID {nuevo_id} ya existe!\nPor favor, asigna un ID diferente.")

            val_dx = float(e_dx.get()) if e_dx.get().strip() else 0.0
            val_dy = float(e_dy.get()) if e_dy.get().strip() else 0.0
            val_dr = float(e_dr.get()) if e_dr.get().strip() else 0.0
            n = Nodo(nuevo_id, float(e_x.get()), float(e_y.get()))
            rz_val = 1 if s_rz.get() or s_art.get() else 0
            n.fijar_apoyo(1 if s_rx.get() else 0, 1 if s_ry.get() else 0, rz_val, float(e_ang.get()), val_dx, val_dy, val_dr)
            n.articulado = bool(s_art.get())
            self.modelo.agregar_nodo(n); self.dibujar_estructura()
            for e in [e_id, e_x, e_y, e_dx, e_dy, e_dr, e_ang]: e.delete(0, 'end')
            e_ang.insert(0, "0.0")
        ctk.CTkButton(v, text="Guardar", command=guardar).pack(pady=15)

    def abrir_formulario_elementos(self):
        v = ctk.CTkToplevel(self); v.title("Definir Barra"); self.centrar_ventana(v, 450, 580); v.attributes('-topmost', True); v.grab_set()
        ctk.CTkLabel(v, text="Nueva Barra", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        f = ctk.CTkFrame(v, fg_color="transparent"); f.pack(expand=True)
        ctk.CTkLabel(f, text="ID Elemento:").grid(row=0, column=0, pady=5, sticky="e", padx=10); e_id = ctk.CTkEntry(f, width=120); e_id.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(f, text="Nodo (i):").grid(row=1, column=0, pady=5, sticky="e", padx=10); e_ni = ctk.CTkEntry(f, width=120); e_ni.grid(row=1, column=1, sticky="w")
        ctk.CTkLabel(f, text="Nodo (j):").grid(row=2, column=0, pady=5, sticky="e", padx=10); e_nj = ctk.CTkEntry(f, width=120); e_nj.grid(row=2, column=1, sticky="w")
        def cambiar_mat(choice):
            e_E.delete(0, 'end')
            if choice == "Hormigón": e_E.insert(0, "21300" if self.sistema_unidades == "SI" else "21300000" if self.sistema_unidades == "kN-m" else "3089")
            elif choice == "Acero": e_E.insert(0, "200000" if self.sistema_unidades == "SI" else "200000000" if self.sistema_unidades == "kN-m" else "29000")
            elif choice == "Madera": e_E.insert(0, "10000" if self.sistema_unidades == "SI" else "10000000" if self.sistema_unidades == "kN-m" else "1450")
        ctk.CTkLabel(f, text="Material:").grid(row=3, column=0, pady=5, sticky="e", padx=10); ctk.CTkOptionMenu(f, values=["Personalizado", "Hormigón", "Acero", "Madera"], command=cambiar_mat).grid(row=3, column=1, pady=5, sticky="w")
        ctk.CTkLabel(f, text=f"E [{self.u_E}]:").grid(row=4, column=0, pady=5, sticky="e", padx=10); e_E = ctk.CTkEntry(f, width=120); e_E.grid(row=4, column=1, sticky="w")
        ctk.CTkLabel(f, text=f"A [{self.u_area}]:").grid(row=5, column=0, pady=5, sticky="e", padx=10); e_A = ctk.CTkEntry(f, width=120); e_A.grid(row=5, column=1, sticky="w")
        ctk.CTkLabel(f, text=f"I [{self.u_iner}]:").grid(row=6, column=0, pady=5, sticky="e", padx=10); e_I = ctk.CTkEntry(f, width=120); e_I.grid(row=6, column=1, sticky="w")
        if self.sistema_unidades == "SI": e_E.insert(0, "200000"); e_A.insert(0, "160000"); e_I.insert(0, "2130000000")
        elif self.sistema_unidades == "kN-m": e_E.insert(0, "200000000"); e_A.insert(0, "0.16"); e_I.insert(0, "0.00213")
        else: e_E.insert(0, "29000"); e_A.insert(0, "248"); e_I.insert(0, "5120")
        s_rot_i = ctk.CTkSwitch(f, text="Rótula en Nodo i"); s_rot_i.grid(row=7, column=0, pady=(15, 5), padx=10, sticky="e")
        s_rot_j = ctk.CTkSwitch(f, text="Rótula en Nodo j"); s_rot_j.grid(row=7, column=1, pady=(15, 5), padx=10, sticky="w")
        ctk.CTkLabel(f, text="*Nota: Uso exclusivo para liberar momento en Vigas/Pórticos.\nPara modelar Cerchas, utilice la opción en Definir Nodos.", font=ctk.CTkFont(size=11, slant="italic"), text_color="#BDC3C7").grid(row=8, column=0, columnspan=2, pady=(0, 10))

        def guardar():
            # [DEFENSA]: Validación Estricta - Evita barras duplicadas
            try: nuevo_id = int(e_id.get())
            except ValueError: return messagebox.showerror("Error", "El ID debe ser un número entero.")
            if any(e.id == nuevo_id for e in self.modelo.elementos):
                return messagebox.showerror("Error de ID", f"¡La Barra con ID {nuevo_id} ya existe!\nPor favor, asigna un ID diferente.")

            n_i = next((n for n in self.modelo.nodos if n.id == int(e_ni.get())), None)
            n_j = next((n for n in self.modelo.nodos if n.id == int(e_nj.get())), None)
            if n_i and n_j:
                val_E, val_A, val_I = float(e_E.get()) * self.f_E, float(e_A.get()) * self.f_A, float(e_I.get()) * self.f_I
                self.modelo.agregar_elemento(Elemento(nuevo_id, n_i, n_j, val_E, val_A, val_I, bool(s_rot_i.get()), bool(s_rot_j.get())))
                self.dibujar_estructura()
                for e in [e_id, e_ni, e_nj]: e.delete(0, 'end')
        ctk.CTkButton(v, text="Trazar", command=guardar).pack(pady=10)

    def abrir_formulario_cargas(self):
        v = ctk.CTkToplevel(self); v.title("Cargas"); self.centrar_ventana(v, 450, 550); v.attributes('-topmost', True); v.grab_set()
        tabview = ctk.CTkTabview(v, width=400); tabview.pack(padx=20, pady=20, fill="both", expand=True)
        tabview.add("Nodal"); tabview.add("Distrib. Uniforme"); tabview.add("Distrib. Variable")
        
        # --- NODAL ---
        tab1 = tabview.tab("Nodal")
        f1 = ctk.CTkFrame(tab1, fg_color="transparent"); f1.pack(expand=True)
        ctk.CTkLabel(f1, text="ID Nodo:").grid(row=0, column=0, pady=10, sticky="e", padx=10); e_id = ctk.CTkEntry(f1, width=100); e_id.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(f1, text=f"Fuerza X [{self.u_force}]:").grid(row=1, column=0, pady=10, sticky="e", padx=10); e_fx = ctk.CTkEntry(f1, width=100); e_fx.insert(0, "0.0"); e_fx.grid(row=1, column=1, sticky="w")
        ctk.CTkLabel(f1, text=f"Fuerza Y [{self.u_force}]:").grid(row=2, column=0, pady=10, sticky="e", padx=10); e_fy = ctk.CTkEntry(f1, width=100); e_fy.insert(0, "0.0"); e_fy.grid(row=2, column=1, sticky="w")
        ctk.CTkLabel(f1, text=f"Momento Z [{self.u_mom}]:").grid(row=3, column=0, pady=10, sticky="e", padx=10); e_mz = ctk.CTkEntry(f1, width=100); e_mz.insert(0, "0.0"); e_mz.grid(row=3, column=1, sticky="w")
        def guardar_nodal():
            nodo = next((n for n in self.modelo.nodos if n.id == int(e_id.get())), None)
            if nodo: nodo.aplicar_fuerza(float(e_fx.get()), float(e_fy.get()), float(e_mz.get())); self.dibujar_estructura()
        ctk.CTkButton(f1, text="Aplicar al Nodo", command=guardar_nodal).grid(row=4, column=0, columnspan=2, pady=20)

        # --- UNIFORME ---
        tab2 = tabview.tab("Distrib. Uniforme")
        f2 = ctk.CTkFrame(tab2, fg_color="transparent"); f2.pack(expand=True)
        ctk.CTkLabel(f2, text="ID Barra:").grid(row=0, column=0, pady=10, sticky="e", padx=10); e_b1 = ctk.CTkEntry(f2, width=100); e_b1.grid(row=0, column=1, sticky="w")
        
        dir_var1 = ctk.StringVar(value="Global")
        ctk.CTkRadioButton(f2, text="Global", variable=dir_var1, value="Global").grid(row=1, column=0, pady=10, padx=10)
        ctk.CTkRadioButton(f2, text="Local", variable=dir_var1, value="Local").grid(row=1, column=1, pady=10, sticky="w")
        
        ctk.CTkLabel(f2, text=f"qX [{self.u_q}]:").grid(row=2, column=0, pady=10, sticky="e", padx=10); e_q1x = ctk.CTkEntry(f2, width=100); e_q1x.insert(0, "0.0"); e_q1x.grid(row=2, column=1, sticky="w")
        ctk.CTkLabel(f2, text=f"qY [{self.u_q}]:").grid(row=3, column=0, pady=10, sticky="e", padx=10); e_q1y = ctk.CTkEntry(f2, width=100); e_q1y.insert(0, "-10.0"); e_q1y.grid(row=3, column=1, sticky="w")
        
        def guardar_rect():
            elem = next((e for e in self.modelo.elementos if e.id == int(e_b1.get())), None)
            if elem: 
                qx, qy = float(e_q1x.get()), float(e_q1y.get())
                elem.cargas_distribuidas.append((dir_var1.get(), qx, qy, qx, qy))
                self.dibujar_estructura()
        ctk.CTkButton(f2, text="Aplicar Uniforme", command=guardar_rect).grid(row=4, column=0, columnspan=2, pady=20)

        # --- TRIANGULAR/VARIABLE ---
        tab3 = tabview.tab("Distrib. Variable")
        f3 = ctk.CTkFrame(tab3, fg_color="transparent"); f3.pack(expand=True)
        ctk.CTkLabel(f3, text="ID Barra:").grid(row=0, column=0, pady=5, sticky="e", padx=10); e_b2 = ctk.CTkEntry(f3, width=100); e_b2.grid(row=0, column=1, sticky="w")
        
        dir_var2 = ctk.StringVar(value="Global")
        ctk.CTkRadioButton(f3, text="Global", variable=dir_var2, value="Global").grid(row=1, column=0, pady=5, padx=10)
        ctk.CTkRadioButton(f3, text="Local", variable=dir_var2, value="Local").grid(row=1, column=1, pady=5, sticky="w")
        
        ctk.CTkLabel(f3, text=f"qX Inicio [{self.u_q}]:").grid(row=2, column=0, pady=5, sticky="e", padx=10); e_qix = ctk.CTkEntry(f3, width=100); e_qix.insert(0, "0.0"); e_qix.grid(row=2, column=1, sticky="w")
        ctk.CTkLabel(f3, text=f"qY Inicio [{self.u_q}]:").grid(row=3, column=0, pady=5, sticky="e", padx=10); e_qiy = ctk.CTkEntry(f3, width=100); e_qiy.insert(0, "-10.0"); e_qiy.grid(row=3, column=1, sticky="w")
        
        ctk.CTkLabel(f3, text=f"qX Final [{self.u_q}]:").grid(row=4, column=0, pady=5, sticky="e", padx=10); e_qjx = ctk.CTkEntry(f3, width=100); e_qjx.insert(0, "0.0"); e_qjx.grid(row=4, column=1, sticky="w")
        ctk.CTkLabel(f3, text=f"qY Final [{self.u_q}]:").grid(row=5, column=0, pady=5, sticky="e", padx=10); e_qjy = ctk.CTkEntry(f3, width=100); e_qjy.insert(0, "0.0"); e_qjy.grid(row=5, column=1, sticky="w")
        
        def guardar_tria():
            elem = next((e for e in self.modelo.elementos if e.id == int(e_b2.get())), None)
            if elem: 
                elem.cargas_distribuidas.append((dir_var2.get(), float(e_qix.get()), float(e_qiy.get()), float(e_qjx.get()), float(e_qjy.get())))
                self.dibujar_estructura()
        ctk.CTkButton(f3, text="Aplicar Variable", command=guardar_tria).grid(row=6, column=0, columnspan=2, pady=15)

    def abrir_formulario_eliminar(self):
        v = ctk.CTkToplevel(self); v.title("Editar Estructura"); self.centrar_ventana(v, 300, 350); v.attributes('-topmost', True); v.grab_set()
        ctk.CTkLabel(v, text="Eliminar Componente", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        f = ctk.CTkFrame(v, fg_color="transparent"); f.pack(expand=True)
        ctk.CTkLabel(f, text="ID:").grid(row=0, column=0, pady=10, sticky="e", padx=10); e_id = ctk.CTkEntry(f, width=100); e_id.grid(row=0, column=1, pady=10, sticky="w")
        
        def del_nodo(): self.modelo.eliminar_nodo(int(e_id.get())); self.dibujar_estructura()
        def del_elem(): self.modelo.eliminar_elemento(int(e_id.get())); self.dibujar_estructura()
        def del_carga(): self.modelo.limpiar_cargas_nodo(int(e_id.get())); self.dibujar_estructura()
        ctk.CTkButton(f, text="Eliminar Nodo", command=del_nodo, fg_color="#E74C3C", hover_color="#C0392B").grid(row=1, column=0, columnspan=2, pady=5)
        ctk.CTkButton(f, text="Eliminar Barra", command=del_elem, fg_color="#E74C3C", hover_color="#C0392B").grid(row=2, column=0, columnspan=2, pady=5)
        ctk.CTkButton(f, text="Limpiar Cargas de Nodo", command=del_carga, fg_color="#E67E22", hover_color="#D35400").grid(row=3, column=0, columnspan=2, pady=5)
        
    def ejecutar_calculo(self):
        if not self.modelo.elementos: return
        if not self.archivo_actual:
            if messagebox.askyesno("Guardar", "¿Deseas guardar el proyecto antes de realizar el cálculo?"):
                if not self.guardar_como(): return 

        self.caja_resultados.insert(ctk.END, "\nCalculando matrices...\n")
        self.update() 

        try:
            desplazamientos, self.K_global = self.modelo.resolver_sistema()
            mem = GeneradorMemoria(self.modelo)
            self.caja_resultados.insert(ctk.END, mem.tabla_reacciones().to_string(index=False) + "\n\n")
            self.dibujar_estructura()
        except np.linalg.LinAlgError:
            self.caja_resultados.insert(ctk.END, "\n[ERROR MATEMÁTICO] MATRIZ SINGULAR.\n")
            self.caja_resultados.insert(ctk.END, "La estructura es inestable. Causas comunes:\n")
            self.caja_resultados.insert(ctk.END, "1. Faltan apoyos o no activaste la 'Rótula (Armadura)' en nodos libres de una cercha.\n\n")
        except Exception as e:
            self.caja_resultados.insert(ctk.END, f"\n[ERROR] {e}\n\n")

    def cambiar_vista(self, valor):
        # [DEFENSA]: Validación de UX. Evita que el usuario vea diagramas vacíos si olvidó calcular.
        if valor in ["Axial", "Cortante", "Momento", "Deformada"] and self.K_global is None:
            messagebox.showwarning("Atención", "¡Debes presionar 'CALCULAR' primero para ver los resultados!")
            self.combo_vista.set("Modelo Básico")
            self.dibujar_estructura()
            return
        self.dibujar_estructura()

    def abrir_inspector_valores(self):
        if self.K_global is None:
            messagebox.showwarning("Atención", "¡Debes calcular la estructura primero!")
            return

        v = ctk.CTkToplevel(self)
        v.title("Inspector Analítico Exacto")
        v.geometry("450x500")
        v.attributes('-topmost', True)

        ctk.CTkLabel(v, text="Buscador de Esfuerzos y Deformaciones", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        f = ctk.CTkFrame(v, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=20)

        ctk.CTkLabel(f, text="Elemento:").grid(row=0, column=0, pady=10, sticky="e", padx=10)
        combo_barra = ctk.CTkOptionMenu(f, values=[f"Barra {e.id}" for e in self.modelo.elementos])
        combo_barra.grid(row=0, column=1, pady=10, sticky="w")

        ctk.CTkLabel(f, text="Análisis:").grid(row=1, column=0, pady=10, sticky="e", padx=10)
        combo_esfuerzo = ctk.CTkOptionMenu(f, values=["Momento", "Cortante", "Axial", "Desplazamiento X", "Desplazamiento Y"])
        combo_esfuerzo.grid(row=1, column=1, pady=10, sticky="w")

        ctk.CTkFrame(f, height=2, fg_color="#555555").grid(row=2, column=0, columnspan=2, pady=15, sticky="ew")

        ctk.CTkLabel(f, text="➤ Dada la Distancia (x), hallar Valor:", font=ctk.CTkFont(weight="bold", size=14), text_color="#3498DB").grid(row=3, column=0, columnspan=2, pady=5, sticky="w")
        ctk.CTkLabel(f, text="Distancia x [m]:").grid(row=4, column=0, pady=5, sticky="e", padx=10)
        e_x = ctk.CTkEntry(f, width=120)
        e_x.grid(row=4, column=1, sticky="w")
        lbl_res_x = ctk.CTkLabel(f, text="Resultado: ---", text_color="#F1C40F", font=ctk.CTkFont(weight="bold", size=14))
        lbl_res_x.grid(row=5, column=1, sticky="w", pady=5)

        ctk.CTkFrame(f, height=2, fg_color="#555555").grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

        ctk.CTkLabel(f, text="➤ Dado el Valor, hallar Distancia (x):", font=ctk.CTkFont(weight="bold", size=14), text_color="#2ECC71").grid(row=7, column=0, columnspan=2, pady=5, sticky="w")
        ctk.CTkLabel(f, text="Valor Deseado:").grid(row=8, column=0, pady=5, sticky="e", padx=10)
        e_val = ctk.CTkEntry(f, width=120)
        e_val.grid(row=8, column=1, sticky="w")
        lbl_res_val = ctk.CTkLabel(f, text="Posición x: ---", text_color="#2ECC71", font=ctk.CTkFont(weight="bold", size=14))
        lbl_res_val.grid(row=9, column=1, sticky="w", pady=5)

        def calcular_exacto():
            try:
                b_id = int(combo_barra.get().split()[1])
                elem = next((e for e in self.modelo.elementos if e.id == b_id), None)
                if not elem: return
                L = elem.longitud(); esf = combo_esfuerzo.get(); F = elem.fuerzas_internas
                
                # [DEFENSA]: Resolución matemática pura de la ecuación de esfuerzo con múltiples cargas
                def get_f_at(x):
                    sum_qxi, sum_qyi, sum_qxj, sum_qyj = 0, 0, 0, 0
                    c, s = elem.cosenos_directores()
                    for c_data in elem.cargas_distribuidas:
                        if len(c_data) == 2: sum_qyi += c_data[0]; sum_qyj += c_data[1]
                        else:
                            t_dir, v1x, v1y, v2x, v2y = c_data
                            if t_dir == "Global":
                                sum_qxi += v1x * c + v1y * s; sum_qyi += -v1x * s + v1y * c
                                sum_qxj += v2x * c + v2y * s; sum_qyj += -v2x * s + v2y * c
                            else:
                                sum_qxi += v1x; sum_qyi += v1y; sum_qxj += v2x; sum_qyj += v2y
                    
                    if esf == "Axial": return -F[0] - (sum_qxi * x + (sum_qxj - sum_qxi) * x**2 / (2 * L))
                    elif esf == "Cortante": return F[1] + (sum_qyi * x + (sum_qyj - sum_qyi) * x**2 / (2 * L))
                    elif esf == "Momento": return -F[2] + F[1] * x + sum_qyi * x**2 / 2 + (sum_qyj - sum_qyi) * x**3 / (6 * L)
                    elif esf in ["Desplazamiento X", "Desplazamiento Y"]:
                        D_global = np.array([
                            elem.ni.desplazamientos[0], elem.ni.desplazamientos[1], elem.ni.desplazamientos[2],
                            elem.nj.desplazamientos[0], elem.nj.desplazamientos[1], elem.nj.desplazamientos[2]
                        ])
                        u1, v1, th1, u2, v2, th2 = elem.matriz_transformacion() @ D_global
                        xi_l = x / L
                        v_x = (1 - 3*xi_l**2 + 2*xi_l**3)*v1 + (x*(1 - 2*xi_l + xi_l**2))*th1 + (3*xi_l**2 - 2*xi_l**3)*v2 + (x*(xi_l**2 - xi_l))*th2
                        u_x = (1 - xi_l)*u1 + xi_l*u2
                        if esf == "Desplazamiento X": return (u_x*c - v_x*s)
                        else: return (u_x*s + v_x*c)
                    else: raise ValueError("Análisis inválido")

                str_x = e_x.get().strip()
                if str_x:
                    x_target = float(str_x)
                    if 0 <= x_target <= L:
                        v_target = get_f_at(x_target)
                        if esf in ["Desplazamiento X", "Desplazamiento Y"]:
                            unid = self.u_len
                            formato = f"{v_target:.6e}" if abs(v_target) < 1e-4 and v_target != 0 else f"{v_target:.6f}"
                        else:
                            unid = self.u_force if esf != "Momento" else self.u_mom
                            formato = f"{v_target:.3f}"
                        lbl_res_x.configure(text=f"Resultado: {formato} {unid}")
                    else: lbl_res_x.configure(text=f"Fuera de rango (0 a {L:.2f}m)")

                str_val = e_val.get().strip()
                if str_val:
                    v_search = float(str_val)
                    x_dense = np.linspace(0, L, 5000)
                    y_dense = np.array([get_f_at(xd) for xd in x_dense]) - v_search
                    
                    crossings = np.where(np.diff(np.sign(y_dense)))[0]
                    res_dist = []
                    for idx in crossings:
                        x1, x2 = x_dense[idx], x_dense[idx+1]; y1, y2 = y_dense[idx], y_dense[idx+1]
                        x_exact = x1 - y1 * ((x2 - x1) / (y2 - y1))
                        res_dist.append(f"{x_exact:.3f}m")

                    if abs(y_dense[0]) < 1e-4 and "0.000m" not in res_dist: res_dist.append("0.000m")
                    if abs(y_dense[-1]) < 1e-4 and f"{L:.3f}m" not in res_dist: res_dist.append(f"{L:.3f}m")

                    lbl_res_val.configure(text=f"x = {', '.join(res_dist)}" if res_dist else "No se alcanza este valor")
            except Exception: messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

        ctk.CTkButton(v, text="⚡ Ejecutar Cálculo Analítico", command=calcular_exacto, fg_color="#E67E22", hover_color="#D35400").pack(pady=20)

        
    # =========================================================
    # DIBUJO AVANZADO Y RENDERIZADO (VERSIÓN COMERCIAL DEFINITIVA)
    # =========================================================
    def dibujar_estructura(self):
        for widget in self.frame_grafico.winfo_children(): widget.destroy()
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#2b2b2b')
        ax.set_facecolor('#2b2b2b'); ax.tick_params(colors='white'); [s.set_color('white') for s in ax.spines.values()]
        
        vista = self.combo_vista.get()
        col_pos = '#3498DB'; col_neg = '#E74C3C'
        fondo_texto = dict(boxstyle="round,pad=0.2", facecolor="#2b2b2b", edgecolor="none", alpha=0.85)

        if vista == "Deformada": ax.set_title(f"Diagrama de Deformaciones [{self.u_len}]", color='#F1C40F', fontweight='bold', pad=35)
        elif vista == "Modelo Básico": ax.set_title(f"Modelo Estructural [{self.u_len}, {self.u_force}]", color='white', fontweight='bold', pad=35)
        else: ax.set_title(f"Diagrama de {vista}", color='#3498DB', fontweight='bold', pad=35)

        x_coords = [n.x for n in self.modelo.nodos]; y_coords = [n.y for n in self.modelo.nodos]
        dim_global = max(max(x_coords)-min(x_coords), max(y_coords)-min(y_coords)) if x_coords else 5
        dim_global = dim_global if dim_global > 0 else 5

        escala_d = dim_global * 0.08 
        tam = escala_d * 0.7 
        escala_def = 1.0; escala_fuerza = 1.0

        if vista == "Deformada" and self.K_global is not None:
            max_disp = 1e-6
            for n in self.modelo.nodos:
                if hasattr(n, 'desplazamientos'):
                    d = np.sqrt(n.desplazamientos[0]**2 + n.desplazamientos[1]**2)
                    if d > max_disp: max_disp = d
            escala_def = (dim_global * 0.1) / max_disp 
            
        elif vista in ["Axial", "Cortante", "Momento"] and self.K_global is not None:
            max_val_global = 1e-6
            for elem in self.modelo.elementos:
                if hasattr(elem, 'fuerzas_internas'):
                    L = elem.longitud(); x_pts = np.linspace(0, L, 50)
                    sum_qxi, sum_qyi, sum_qxj, sum_qyj = 0, 0, 0, 0
                    c, s = elem.cosenos_directores()
                    for c_data in elem.cargas_distribuidas:
                        if len(c_data) == 2: sum_qyi += c_data[0]; sum_qyj += c_data[1]
                        else:
                            t_dir, v1x, v1y, v2x, v2y = c_data
                            if t_dir == "Global":
                                sum_qxi += v1x * c + v1y * s; sum_qyi += -v1x * s + v1y * c
                                sum_qxj += v2x * c + v2y * s; sum_qyj += -v2x * s + v2y * c
                            else:
                                sum_qxi += v1x; sum_qyi += v1y; sum_qxj += v2x; sum_qyj += v2y
                    
                    F = elem.fuerzas_internas
                    if vista == "Axial": val_pts = -F[0] - (sum_qxi * x_pts + (sum_qxj - sum_qxi) * x_pts**2 / (2 * L))
                    elif vista == "Cortante": val_pts = F[1] + (sum_qyi * x_pts + (sum_qyj - sum_qyi) * x_pts**2 / (2 * L))
                    elif vista == "Momento": val_pts = -F[2] + F[1] * x_pts + sum_qyi * x_pts**2 / 2 + (sum_qyj - sum_qyi) * x_pts**3 / (6 * L)
                    
                    val = max(abs(np.max(val_pts)), abs(np.min(val_pts)))
                    if val > max_val_global: max_val_global = val
            escala_fuerza = (dim_global * 0.15) / max_val_global

        for elem in self.modelo.elementos:
            xi, yi, xj, yj = elem.ni.x, elem.ni.y, elem.nj.x, elem.nj.y
            L = elem.longitud(); c, s = elem.cosenos_directores()
            rot_ang = np.degrees(np.arctan2(s, c))
            rot_text = rot_ang if -90 <= rot_ang <= 90 else rot_ang - 180 if rot_ang > 90 else rot_ang + 180
            off_t = dim_global * 0.035 
            
            if vista == "Deformada":
                ax.plot([xi, xj], [yi, yj], color='#555555', linestyle='--', zorder=1) 
                if hasattr(elem.ni, 'desplazamientos') and self.K_global is not None:
                    D_global = np.array([
                        elem.ni.desplazamientos[0], elem.ni.desplazamientos[1], elem.ni.desplazamientos[2],
                        elem.nj.desplazamientos[0], elem.nj.desplazamientos[1], elem.nj.desplazamientos[2]
                    ])
                    u1, v1, th1, u2, v2, th2 = elem.matriz_transformacion() @ D_global
                    x_pts = np.linspace(0, L, 20); x_def, y_def = [], []
                    for x in x_pts:
                        xi_l = x / L
                        v_x = (1 - 3*xi_l**2 + 2*xi_l**3)*v1 + (x*(1 - 2*xi_l + xi_l**2))*th1 + (3*xi_l**2 - 2*xi_l**3)*v2 + (x*(xi_l**2 - xi_l))*th2
                        u_x = (1 - xi_l)*u1 + xi_l*u2
                        x_def.append((xi + x*c) + (u_x*c - v_x*s)*escala_def); y_def.append((yi + x*s) + (u_x*s + v_x*c)*escala_def)
                    ax.plot(x_def, y_def, color='#F1C40F', lw=2.5, zorder=3)
            
            else:
                ax.plot([xi, xj], [yi, yj], color='#3498DB' if vista == "Modelo Básico" else '#555555', linewidth=4, zorder=1)
                
                if vista == "Modelo Básico":
                    ax.text((xi+xj)/2, (yi+yj)/2 - tam*1.2, f"B{elem.id}", color='#85C1E9', fontweight='bold', fontsize=10, rotation=rot_text, ha='center', va='center', zorder=6, bbox=fondo_texto)

                if hasattr(elem, 'rotula_i') and elem.rotula_i: ax.plot(xi, yi, marker='o', markersize=6, color='white', markerfacecolor='#2b2b2b', zorder=5)
                if hasattr(elem, 'rotula_j') and elem.rotula_j: ax.plot(xj, yj, marker='o', markersize=6, color='white', markerfacecolor='#2b2b2b', zorder=5)

                # [DEFENSA]: Dibujo generalizado para todo tipo de diagrama
                if vista in ["Axial", "Cortante", "Momento"] and hasattr(elem, 'fuerzas_internas') and self.K_global is not None:
                    F = elem.fuerzas_internas
                    x_pts = np.linspace(0, L, 50)
                    sum_qxi, sum_qyi, sum_qxj, sum_qyj = 0, 0, 0, 0
                    for c_data in elem.cargas_distribuidas:
                        if len(c_data) == 2: sum_qyi += c_data[0]; sum_qyj += c_data[1]
                        else:
                            t_dir, v1x, v1y, v2x, v2y = c_data
                            if t_dir == "Global":
                                sum_qxi += v1x * c + v1y * s; sum_qyi += -v1x * s + v1y * c
                                sum_qxj += v2x * c + v2y * s; sum_qyj += -v2x * s + v2y * c
                            else:
                                sum_qxi += v1x; sum_qyi += v1y; sum_qxj += v2x; sum_qyj += v2y
                    
                    val_pts = np.zeros_like(x_pts)
                    if vista == "Axial":
                        val_pts = -F[0] - (sum_qxi * x_pts + (sum_qxj - sum_qxi) * x_pts**2 / (2 * L))
                    elif vista == "Cortante":
                        val_pts = F[1] + (sum_qyi * x_pts + (sum_qyj - sum_qyi) * x_pts**2 / (2 * L))
                    elif vista == "Momento":
                        val_pts = -F[2] + F[1] * x_pts + sum_qyi * x_pts**2 / 2 + (sum_qyj - sum_qyi) * x_pts**3 / (6 * L)

                    max_val_elem = max(abs(np.max(val_pts)), abs(np.min(val_pts)))
                    if max_val_elem < 1e-4: 
                        ax.plot([xi, xj], [yi, yj], color='#2ECC71', lw=2, zorder=3)
                        continue

                    escala = escala_fuerza
                    yl_pts = -val_pts * escala if vista == "Momento" else val_pts * escala
                    xg_pts = xi + x_pts * c - yl_pts * s
                    yg_pts = yi + x_pts * s + yl_pts * c
                    
                    # Rellenado estético usando franjas divididas para colorear bien el cambio de signo
                    for i in range(len(x_pts)-1):
                        v_mid = (val_pts[i] + val_pts[i+1]) / 2
                        col = '#9B59B6' if vista == "Momento" else (col_pos if v_mid >= 0 else col_neg)
                        poly_x = [xi + x_pts[i]*c, xg_pts[i], xg_pts[i+1], xi + x_pts[i+1]*c]
                        poly_y = [yi + x_pts[i]*s, yg_pts[i], yg_pts[i+1], yi + x_pts[i+1]*s]
                        ax.fill(poly_x, poly_y, color=col, alpha=0.5, zorder=2)
                    
                    line_col = '#8E44AD' if vista == "Momento" else '#2980B9'
                    ax.plot(xg_pts, yg_pts, color=line_col, lw=2, zorder=3)

                    def imprimir_texto(v_val, x_val):
                        if abs(v_val) < 1e-2: return
                        push_loc = -v_val * escala + (-off_t*0.5 if v_val > 0 else off_t*0.5) if vista == "Momento" else v_val * escala + (off_t*0.5 if v_val >= 0 else -off_t*0.5)
                        v_align = 'top' if (vista == "Momento" and v_val > 0) or (vista != "Momento" and v_val < 0) else 'bottom'
                        x_draw = x_val
                        if x_val < 0.15 * L: x_draw = 0.15 * L
                        elif x_val > 0.85 * L: x_draw = 0.85 * L
                        xm_g = xi + x_draw*c - push_loc*s; ym_g = yi + x_draw*s + push_loc*c
                        signo = "+" if v_val > 0 else ""
                        txt_esf = f"{signo}{v_val:.2f}\n(x={x_val:.2f}m)" if vista == "Momento" else f"{v_val:.1f}"
                        ax.text(xm_g, ym_g, txt_esf, color='white', fontsize=8 if vista=="Momento" else 9, ha='center', va=v_align if vista=="Momento" else 'center', rotation=rot_text, fontweight='bold', zorder=6, bbox=fondo_texto)

                    v_max, v_min = np.max(val_pts), np.min(val_pts)
                    x_max, x_min = x_pts[np.argmax(val_pts)], x_pts[np.argmin(val_pts)]
                    if vista == "Momento":
                        imprimir_texto(v_max, x_max); imprimir_texto(v_min, x_min)
                    else:
                        imprimir_texto(val_pts[0], 0); imprimir_texto(val_pts[-1], L)

        if vista in ["Modelo Básico", "Deformada"]:
            for n in self.modelo.nodos:
                rx, ry, rz = n.restricciones; articulado = hasattr(n, 'articulado') and n.articulado
                
                # Un apoyo real siempre restringe al menos X o Y.
                if rx == 1 or ry == 1:
                    ang = np.radians(n.angulo_apoyo)
                    ca, sa = np.cos(ang), np.sin(ang)
                    def rot_trans(px, py): return n.x + px*tam*ca - py*tam*sa, n.y + px*tam*sa + py*tam*ca
                    
                    if rx==1 and ry==1 and rz==1 and not articulado:
                        # 1. Empotramiento Perfecto (Base horizontal)
                        ax.plot(*rot_trans(np.array([-1, 1]), np.array([0, 0])), color='#E74C3C', lw=5, zorder=3)
                        for i in np.linspace(-0.8, 0.8, 5): 
                            ax.plot(*rot_trans(np.array([i, i-0.4]), np.array([0, -0.4])), color='#E74C3C', lw=2, zorder=3)
                            
                    elif rx==1 and ry==1:
                        # 2. Apoyo Fijo / Articulado (Base horizontal)
                        ax.fill(*rot_trans(np.array([0, -0.8, 0.8, 0]), np.array([0, -1.2, -1.2, 0])), color='#E74C3C', zorder=3)
                        ax.plot(*rot_trans(np.array([-1, 1]), np.array([-1.2, -1.2])), color='#E74C3C', lw=3, zorder=3)
                        
                    elif rz==1 and (rx==0 or ry==0):
                        # 3. Empotramientos Guiados (Base horizontal unificada, vista arriba)
                        ax.plot(*rot_trans(np.array([-0.8, 0.8]), np.array([0, 0])), color='#E74C3C', lw=4, zorder=3)
                        ax.plot(*rot_trans(np.array([-1.2, 1.2]), np.array([-0.4, -0.4])), color='#E74C3C', lw=4, zorder=3)
                        for i in np.linspace(-1.0, 1.0, 5):
                            ax.plot(*rot_trans(np.array([i, i-0.3]), np.array([-0.4, -0.8])), color='#E74C3C', lw=2, zorder=3)
                            
                    else:
                        # 4. Apoyos Móviles / Rodillos (Base horizontal unificada, vista arriba)
                        ax.fill(*rot_trans(np.array([0, -0.8, 0.8, 0]), np.array([0, -1.2, -1.2, 0])), color='#E74C3C', zorder=3)
                        ax.plot(*rot_trans(np.array([-1, 1]), np.array([-1.6, -1.6])), color='#E74C3C', lw=3, zorder=3)
                        ax.plot(*rot_trans(np.array([-0.4, 0.4]), np.array([-1.4, -1.4])), marker='o', markersize=5, color='#E74C3C', ls='', zorder=3)
                        
                else: 
                    # Nudos libres en el aire
                    ax.scatter(n.x, n.y, color='white', s=60, zorder=4)

                if articulado:
                    # Dibuja el círculo interno de la rótula
                    ax.scatter(n.x, n.y, color='white', s=50, zorder=4)
                    ax.scatter(n.x, n.y, color='#2b2b2b', s=20, zorder=5)
                                              
                if vista == "Deformada" and self.K_global is not None:
                    dx, dy = n.desplazamientos[0], n.desplazamientos[1]
                    ax.scatter(n.x + dx*escala_def, n.y + dy*escala_def, color='#F1C40F', s=50, zorder=4)
                    if abs(dx) > 1e-6 or abs(dy) > 1e-6:
                        ax.text(n.x + dx*escala_def, (n.y + dy*escala_def) + tam*0.5, f"Δx: {dx:.4f}\nΔy: {dy:.4f}", color='#F1C40F', fontsize=8, fontweight='bold', ha='center', zorder=6, bbox=fondo_texto)
                else:
                    ax.text(n.x - tam*0.8, n.y - tam*0.8, f"N{n.id}", color='white', fontweight='bold', fontsize=11, zorder=8, bbox=fondo_texto)
                    
                if vista == "Modelo Básico":
                    if hasattr(n, 'historial_cargas') and len(n.historial_cargas) > 0:
                        for idx, carga in enumerate(n.historial_cargas):
                            fx, fy, mz = carga
                            if fx != 0:
                                d_x = np.sign(fx) * tam * 2.5; off_x = np.sign(fx) * tam * 0.5
                                ax.annotate("", xy=(n.x - off_x, n.y), xytext=(n.x - d_x, n.y), arrowprops=dict(arrowstyle="-|>", color='#F1C40F', lw=2.5, mutation_scale=15), zorder=9)
                                ax.text(n.x - d_x - np.sign(fx)*tam*0.3, n.y, f"{fx} {self.uf}", color='#F1C40F', fontsize=10, fontweight='bold', ha='right' if fx>0 else 'left', va='center', zorder=9, bbox=fondo_texto)
                            if fy != 0:
                                d_y = np.sign(fy) * tam * 2.5; off_y = np.sign(fy) * tam * 0.5
                                ax.annotate("", xy=(n.x, n.y - off_y), xytext=(n.x, n.y - d_y), arrowprops=dict(arrowstyle="-|>", color='#F1C40F', lw=2.5, mutation_scale=15), zorder=9)
                                ax.text(n.x, n.y - d_y - np.sign(fy)*tam*0.3, f"{fy} {self.uf}", color='#F1C40F', fontsize=10, fontweight='bold', ha='center', va='bottom' if fy<0 else 'top', zorder=9, bbox=fondo_texto)
                            if mz != 0: 
                                ax.text(n.x + tam*1.5, n.y + tam*1.5, f"↺ {mz} {self.um}", color='#F1C40F', fontsize=12, ha='left', va='bottom', zorder=9, bbox=fondo_texto)

                    if hasattr(n, 'reacciones') and self.K_global is not None and self.switch_reacciones.get():
                        frx, fry, frm = n.reacciones
                        if abs(frx) > 0.01:
                            d_x = np.sign(frx) * tam * 3.0; off_x = np.sign(frx) * tam * 1.2
                            ax.annotate("", xy=(n.x - off_x, n.y - tam*0.5), xytext=(n.x - d_x, n.y - tam*0.5), arrowprops=dict(arrowstyle="-|>", color='#2ECC71', lw=3, mutation_scale=20), zorder=8)
                            ax.text(n.x - d_x - np.sign(frx)*tam*0.3, n.y - tam*0.5, f"{abs(frx):.2f} {self.uf}", color='#2ECC71', fontweight='bold', ha='right' if frx>0 else 'left', va='center', zorder=8, bbox=fondo_texto)
                        if abs(fry) > 0.01:
                            d_y = np.sign(fry) * tam * 3.0; off_y = np.sign(fry) * tam * 1.5
                            ax.annotate("", xy=(n.x, n.y - off_y), xytext=(n.x, n.y - d_y), arrowprops=dict(arrowstyle="-|>", color='#2ECC71', lw=3, mutation_scale=20), zorder=8)
                            ax.text(n.x, n.y - d_y - np.sign(fry)*tam*0.3, f"{abs(fry):.2f} {self.uf}", color='#2ECC71', fontweight='bold', ha='center', va='top' if fry>0 else 'bottom', zorder=8, bbox=fondo_texto)
                        if abs(frm) > 0.01:
                            ax.text(n.x, n.y + tam*2.0, f"↺ {abs(frm):.2f} {self.um}", color='#2ECC71', fontweight='bold', fontsize=11, ha='center', va='bottom', zorder=8, bbox=fondo_texto)

            # --- DIBUJO DE CARGAS DISTRIBUIDAS (NUEVO MOTOR VISUAL) ---
            if vista == "Modelo Básico":
                for elem in self.modelo.elementos:
                    if len(elem.cargas_distribuidas) > 0:
                        xi, yi, xj, yj = elem.ni.x, elem.ni.y, elem.nj.x, elem.nj.y
                        L = elem.longitud(); c, s = elem.cosenos_directores()
                        for c_data in elem.cargas_distribuidas:
                            if len(c_data) == 2:
                                tipo_dir = "Local"; qxi, qyi, qxj, qyj = 0, c_data[0], 0, c_data[1]
                            else:
                                tipo_dir, qxi, qyi, qxj, qyj = c_data
                            
                            q_max = max(abs(qxi), abs(qyi), abs(qxj), abs(qyj))
                            if q_max == 0: continue
                            scale = (tam * 2.5) / q_max 
                            
                            def dibujar_carga(vi, vj, es_x, es_global):
                                if abs(vi) < 1e-4 and abs(vj) < 1e-4: return
                                x_pts = np.linspace(0, L, 6); q_pts = np.linspace(vi, vj, 6)
                                heads_x = xi + x_pts * c; heads_y = yi + x_pts * s
                                
                                # Anclaje exacto de las flechas según Global o Local
                                if es_global:
                                    if es_x: tails_x = heads_x - q_pts * scale; tails_y = heads_y
                                    else:    tails_x = heads_x; tails_y = heads_y - q_pts * scale
                                else:
                                    if es_x: tails_x = heads_x - q_pts * scale * c; tails_y = heads_y - q_pts * scale * s
                                    else:    tails_x = heads_x + q_pts * scale * s; tails_y = heads_y - q_pts * scale * c
                                
                                ax.plot([tails_x[0], tails_x[-1]], [tails_y[0], tails_y[-1]], color='#E67E22', lw=2, zorder=4)
                                for hx, hy, tx, ty, q_val in zip(heads_x, heads_y, tails_x, tails_y, q_pts):
                                    if abs(q_val) > 1e-4: ax.annotate("", xy=(hx, hy), xytext=(tx, ty), arrowprops=dict(arrowstyle="-|>", color='#E67E22', lw=1.5, mutation_scale=10), zorder=4)
                                        
                                rot_txt = 0 if es_global else np.degrees(np.arctan2(s, c))
                                if abs(vi - vj) < 1e-4:
                                    ax.text(tails_x[2], tails_y[2], f"{vi} {self.u_q}", color='#E67E22', ha='center', va='center', fontsize=10, fontweight='bold', rotation=rot_txt, zorder=7, bbox=fondo_texto)
                                else:
                                    if abs(vi) > 0.01: ax.text(tails_x[1], tails_y[1], f"{vi} {self.u_q}", color='#E67E22', ha='center', va='center', fontsize=10, fontweight='bold', rotation=rot_txt, zorder=7, bbox=fondo_texto)
                                    if abs(vj) > 0.01: ax.text(tails_x[-2], tails_y[-2], f"{vj} {self.u_q}", color='#E67E22', ha='center', va='center', fontsize=10, fontweight='bold', rotation=rot_txt, zorder=7, bbox=fondo_texto)

                            dibujar_carga(qxi, qxj, es_x=True, es_global=(tipo_dir=="Global"))
                            dibujar_carga(qyi, qyj, es_x=False, es_global=(tipo_dir=="Global"))

        if vista in ["Modelo Básico", "Deformada"]:
            ax.set_aspect('equal', adjustable='datalim')
            if x_coords and y_coords:
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)
                width = max_x - min_x if max_x > min_x else 5
                height = max_y - min_y
                if height < width / 1.5:
                    target_height = width / 1.5
                    center_y = (max_y + min_y) / 2
                    ax.set_ylim(center_y - target_height/2, center_y + target_height/2)
                elif width < height * 1.5:
                    target_width = height * 1.5
                    center_x = (max_x + min_x) / 2
                    ax.set_xlim(center_x - target_width/2, center_x + target_width/2)
            else:
                ax.set_xlim(-1, 10); ax.set_ylim(-5, 5)
                
            ax.margins(x=0.25, y=0.35) 
        else:
            ax.set_aspect('auto') 
            ax.margins(x=0.20, y=0.35)
            
        ax.grid(True, linestyle='--', alpha=0.3)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MatrixApp()
    app.mainloop()