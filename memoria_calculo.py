import pandas as pd
import numpy as np

class GeneradorMemoria:
    def __init__(self, estructura_resuelta):
        self.estructura = estructura_resuelta

    def tabla_propiedades_geometricas(self):
        datos = []
        for elem in self.estructura.elementos:
            L = elem.longitud()
            c, s = elem.cosenos_directores()
            datos.append({
                "Elem": elem.id,
                "N.i": elem.ni.id,
                "N.j": elem.nj.id,
                "L [m]": round(L, 3),
                "Área": elem.A,
                "Inercia": elem.I,
                "Ángulo": round(np.degrees(np.arccos(c)), 2)
            })
        return pd.DataFrame(datos)

    def tabla_cosenos_directores(self):
        datos = []
        for elem in self.estructura.elementos:
            c, s = elem.cosenos_directores()
            datos.append({
                "Elem": elem.id,
                "cos(\u03B8)": round(c, 3),
                "sen(\u03B8)": round(s, 3),
                "c\u00B2": round(c**2, 3),
                "s\u00B2": round(s**2, 3),
                "c*s": round(c*s, 3)
            })
        return pd.DataFrame(datos)

    def tabla_desplazamientos(self):
        datos = []
        for nodo in self.estructura.nodos:
            datos.append({
                "Nodo": nodo.id,
                "Dx [m]": format(nodo.desplazamientos[0], '.5E'),
                "Dy [m]": format(nodo.desplazamientos[1], '.5E'),
                "Rz [rad]": format(nodo.desplazamientos[2], '.5E')
            })
        return pd.DataFrame(datos)
        
    def tabla_reacciones(self):
        datos = []
        for nodo in self.estructura.nodos:
            if sum(nodo.restricciones) > 0:
                datos.append({
                    "Apoyo (N)": nodo.id,
                    "FRx [kN]": round(nodo.reacciones[0], 4),
                    "FRy [kN]": round(nodo.reacciones[1], 4),
                    "MRz [kNm]": round(nodo.reacciones[2], 4)
                })
        return pd.DataFrame(datos) if datos else pd.DataFrame([{"Apoyo": "-", "FRx": 0, "FRy": 0, "MRz": 0}])

    def tabla_fuerzas_internas(self):
        datos = []
        for elem in self.estructura.elementos:
            f = elem.fuerzas_internas
            datos.append({
                "Elem": elem.id,
                "N (i)": round(f[0], 4), "V (i)": round(f[1], 4), "M (i)": round(f[2], 4),
                "N (j)": round(f[3], 4), "V (j)": round(f[4], 4), "M (j)": round(f[5], 4)
            })
        return pd.DataFrame(datos)

    def generar_datos_entrada(self):
        txt = "="*85 + "\n"
        txt += "                           DATOS DE ENTRADA\n"
        txt += "="*85 + "\n\n"
        
        # 1. PARAMETROS GENERALES
        txt += "PARAMETROS GENERALES\n"
        txt += "-" * 50 + "\n"
        txt += f"{'Número de Nodos':<25} N = {len(self.estructura.nodos)}\n"
        txt += f"{'Número de Elementos':<25} M = {len(self.estructura.elementos)}\n"
        E_val = self.estructura.elementos[0].E if self.estructura.elementos else 0
        txt += f"{'Módulo de Elasticidad':<25} E = {E_val:.2e}\n"
        txt += "-" * 50 + "\n\n"

        # 2. COORDENADAS GLOBALES
        txt += "COORDENADAS GLOBALES\n"
        txt += "-" * 50 + "\n"
        txt += f"{'NODO':<10} | {'X-X':<15} | {'Y-Y':<15}\n"
        txt += "-" * 50 + "\n"
        for n in self.estructura.nodos:
            txt += f"{n.id:<10} | {n.x:<15.3f} | {n.y:<15.3f}\n"
        txt += "\n"

        # 3. DATOS DE ELEMENTOS
        txt += "DATOS INICIALES CADA ELEMENTO\n"
        txt += "-" * 85 + "\n"
        txt += f"{'ELEM':<6} | {'N. INI':<8} | {'N. FIN':<8} | {'AREA':<12} | {'INERCIA':<12} | {'ELASTICIDAD (E)':<15}\n"
        txt += "-" * 85 + "\n"
        for elem in self.estructura.elementos:
            txt += f"{elem.id:<6} | {elem.ni.id:<8} | {elem.nj.id:<8} | {elem.A:<12.5f} | {elem.I:<12.6f} | {elem.E:<15.2e}\n"
        txt += "\n"

        # 4. RESTRICCIONES DE APOYO
        txt += "CONDICIONES DE APOYO (1=FIJO, 0=LIBRE)\n"
        txt += "-" * 50 + "\n"
        txt += f"{'NODO':<10} | {'Tx':<10} | {'Ty':<10} | {'Rz':<10}\n"
        txt += "-" * 50 + "\n"
        for n in self.estructura.nodos:
            rx, ry, rz = n.restricciones
            if rx==1 or ry==1 or rz==1:
                txt += f"{n.id:<10} | {rx:<10} | {ry:<10} | {rz:<10}\n"
        txt += "\n"
        
        return txt
    
    def generar_texto_completo(self, K_global):
        texto = "="*80 + "\n MEMORIA DE CÁLCULO DETALLADA - MATRÍX \n" + "="*80 + "\n\n"
        texto = self.generar_datos_entrada()
        texto += "--- PASO 1: PROPIEDADES GEOMÉTRICAS DE LA ESTRUCTURA ---\n"
        texto += "Fórmula Longitud: L = \u221A[(Xj - Xi)\u00B2 + (Yj - Yi)\u00B2]\n"
        texto += self.tabla_propiedades_geometricas().to_string(index=False) + "\n\n"

        texto += "--- PASO 1.1: COSENOS DIRECTORES ---\n"
        texto += "Fórmulas: c = cos(\u03B8) = (Xj - Xi) / L  |  s = sen(\u03B8) = (Yj - Yi) / L\n"
        texto += self.tabla_cosenos_directores().to_string(index=False) + "\n\n"

        texto += "--- PASO 1.2: MATRICES DE RIGIDEZ POR ELEMENTO [K_elem] ---\n"
        texto += ">> Fórmula de Rotación: [K_global] = [T]^T * [k_local] * [T]\n"
        texto += ">> Nota: Los números en los bordes de la matriz indican el Grado de Libertad (GDL).\n\n"
        for elem in self.estructura.elementos:
            k_elem = elem.matriz_rigidez_global()
            # Calcular los GDL correspondientes a esta barra (1-based index)
            idx_i = self.estructura.nodos.index(elem.ni)
            idx_j = self.estructura.nodos.index(elem.nj)
            dofs = [idx_i*3+1, idx_i*3+2, idx_i*3+3, idx_j*3+1, idx_j*3+2, idx_j*3+3]
            
            df_k = pd.DataFrame(np.round(k_elem, 2), columns=dofs, index=dofs)
            texto += f"Elemento {elem.id} (Nodos {elem.ni.id} -> {elem.nj.id}):\n"
            texto += df_k.to_string() + "\n\n"

        texto += "--- PASO 2: MATRIZ DE RIGIDEZ GLOBAL ENSAMBLADA [K] ---\n"
        texto += ">> Fórmula Ensamblaje: [K] = \u03A3 [K_global_i]\n"
        texto += ">> Procedimiento: Superposición de coeficientes en los GDL comunes de los nudos.\n\n"
        num_dofs = len(self.estructura.nodos) * 3
        dofs_g = [i+1 for i in range(num_dofs)]
        df_Kg = pd.DataFrame(np.round(K_global, 3), columns=dofs_g, index=dofs_g)
        texto += df_Kg.to_string() + "\n\n"

        gle, glr = self.estructura.clasificar_grados_libertad()
        K_ee = K_global[np.ix_(gle, gle)]
        
        texto += "--- PASO 3: DESPLAZAMIENTOS NODALES (Efectivos) ---\n"
        texto += ">> Ecuación de Equilibrio: {F_e} = [K_ee] * {D_e}\n"
        texto += ">> Despejando Desplazamientos: {D_e} = [K_ee]^(-1) * {F_e}\n\n"
        
        if len(gle) > 0:
            gle_1based = [i+1 for i in gle]
            texto += "Matriz Reducida [K_ee]:\n"
            df_Kee = pd.DataFrame(np.round(K_ee, 3), columns=gle_1based, index=gle_1based)
            texto += df_Kee.to_string() + "\n\n"
            
            # Reconstruyendo el vector D_e y F_e para mostrarlos paso a paso
            D_global = np.zeros(num_dofs)
            for i, n in enumerate(self.estructura.nodos):
                D_global[i*3:i*3+3] = n.desplazamientos
            D_e = D_global[gle]
            F_e = K_ee @ D_e

            df_sistema = pd.DataFrame({
                "GDL": gle_1based,
                "F_efectiva": np.round(F_e, 4),
                " ": ["=" for _ in gle],
                "Desplazamiento {D_e}": [format(val, '.4E') for val in D_e]
            }).set_index("GDL")
            
            texto += "Sustituyendo valores y resolviendo el sistema para {D_e}:\n"
            texto += df_sistema.to_string() + "\n\n"
        else:
            texto += "La estructura está completamente restringida (No hay desplazamientos).\n\n"
            
        texto += "RESUMEN TABULAR DE DESPLAZAMIENTOS:\n"
        texto += self.tabla_desplazamientos().to_string(index=False) + "\n\n"
        
        texto += "--- PASO 4: REACCIONES EN LOS APOYOS ---\n"
        texto += ">> Fórmula de Reacciones: {R_r} = [K_re] * {D_e} + [K_rr] * {D_r} + {FEP_r} - {F_nodal_r}\n"
        texto += ">> Procedimiento: Se extraen las fuerzas resultantes de los GDL que tienen restricciones físicas.\n\n"
        if len(glr) > 0:
            R_r = []
            for i, n in enumerate(self.estructura.nodos):
                if n.restricciones[0]: R_r.append(n.reacciones[0])
                if n.restricciones[1]: R_r.append(n.reacciones[1])
                if n.restricciones[2]: R_r.append(n.reacciones[2])
            glr_1based = [i+1 for i in glr]
            df_reacc = pd.DataFrame({
                "GDL Restringido": glr_1based,
                "Reacción Obtenida {R}": np.round(R_r, 4)
            }).set_index("GDL Restringido")
            texto += df_reacc.to_string() + "\n\n"
            
        texto += "RESUMEN TABULAR DE REACCIONES:\n"
        texto += self.tabla_reacciones().to_string(index=False) + "\n\n"
        
        texto += "--- PASO 5: FUERZAS INTERNAS EN CADA ELEMENTO ---\n"
        texto += ">> Fórmula Fuerzas Internas: {f} = [k_local] * [T] * {D_elem_global} + {FEP_local}\n"
        texto += ">> Procedimiento: Se extraen los desplazamientos del sistema global, se rotan a ejes locales y se multiplican por la rigidez de la barra.\n\n"

        for elem in self.estructura.elementos:
            idx_i, idx_j = self.estructura.nodos.index(elem.ni), self.estructura.nodos.index(elem.nj)
            dofs_elem = [idx_i*3+1, idx_i*3+2, idx_i*3+3, idx_j*3+1, idx_j*3+2, idx_j*3+3]
            D_elem_g = np.array([
                self.estructura.nodos[idx_i].desplazamientos[0], self.estructura.nodos[idx_i].desplazamientos[1], self.estructura.nodos[idx_i].desplazamientos[2],
                self.estructura.nodos[idx_j].desplazamientos[0], self.estructura.nodos[idx_j].desplazamientos[1], self.estructura.nodos[idx_j].desplazamientos[2]
            ])

            texto += f"Elemento {elem.id} (Sustitución de Valores):\n"
            df_dg = pd.DataFrame({"D_global": [format(val, '.4E') for val in D_elem_g]}, index=dofs_elem)
            texto += "1) Vector de desplazamientos globales de la barra:\n"
            texto += df_dg.to_string() + "\n\n"

            f_int = elem.fuerzas_internas
            etiquetas = ["N_i (Axial)", "V_i (Cortante)", "M_i (Momento)", "N_j (Axial)", "V_j (Cortante)", "M_j (Momento)"]
            df_f = pd.DataFrame({"Fuerza Interna Calculada": np.round(f_int, 4)}, index=etiquetas)
            texto += "2) Vector de fuerzas internas resultantes {f}:\n"
            texto += df_f.to_string() + "\n"
            texto += "-"*40 + "\n\n"

        texto += "RESUMEN TABULAR DE FUERZAS INTERNAS (Puntas i, j):\n"
        texto += self.tabla_fuerzas_internas().to_string(index=False) + "\n\n"
        texto += self.generar_resumen_final()

        return texto
    
    def generar_resumen_final(self):
        txt = "\n" + "="*85 + "\n"
        txt += "                           PRESENTACION DE RESULTADOS FINALES\n"
        txt += "="*85 + "\n\n"

        # 1. DESPLAZAMIENTOS
        txt += "DESPLAZAMIENTO DE LOS NODOS - COORDENADAS GLOBALES\n"
        txt += "-" * 70 + "\n"
        txt += f"{'NODO':<10} | {'Dx-x':<15} | {'Dy-y':<15} | {'Rz-z':<15}\n"
        txt += "-" * 70 + "\n"
        for n in self.estructura.nodos:
            if hasattr(n, 'desplazamientos'):
                dx, dy, rz = n.desplazamientos
                # Usamos notación científica para desplazamientos muy pequeños
                txt += f"{n.id:<10} | {dx:<15.6e} | {dy:<15.6e} | {rz:<15.6e}\n"
        txt += "\n"

        # 2. FUERZAS INTERNAS
        txt += "FUERZAS INTERNAS CADA ELEMENTO - COORDENADAS LOCALES\n"
        txt += "-" * 90 + "\n"
        txt += f"{'ELEM':<6} | {'NODO INICIAL (Axial, Corte, Momento)':<38} | {'NODO FINAL (Axial, Corte, Momento)':<38}\n"
        txt += "-" * 90 + "\n"
        for elem in self.estructura.elementos:
            if hasattr(elem, 'fuerzas_internas'):
                F = elem.fuerzas_internas
                txt += f"{elem.id:<6} | {F[0]:>8.2f}  {F[1]:>8.2f}  {F[2]:>8.2f}        | {F[3]:>8.2f}  {F[4]:>8.2f}  {F[5]:>8.2f}\n"
        txt += "\n"

        # 3. REACCIONES
        txt += "FUERZAS EXTERNAS O DE REACCION - COORDENADAS GLOBALES\n"
        txt += "-" * 60 + "\n"
        txt += f"{'APOYO':<10} | {'FR x-x':<15} | {'FR y-y':<15} | {'MR z-z':<15}\n"
        txt += "-" * 60 + "\n"
        for n in self.estructura.nodos:
            if hasattr(n, 'reacciones'):
                rx, ry, rm = n.reacciones
                # Solo imprime los nodos que realmente tienen reacciones
                if abs(rx)>1e-3 or abs(ry)>1e-3 or abs(rm)>1e-3:
                    txt += f"{n.id:<10} | {rx:<15.3f} | {ry:<15.3f} | {rm:<15.3f}\n"
        txt += "\n"

        return txt