import numpy as np

class Nodo:
    def __init__(self, id_nodo, x, y):
        self.id = id_nodo; self.x = x; self.y = y
        self.restricciones = [0, 0, 0]; self.angulo_apoyo = 0.0
        self.asentamientos = [0.0, 0.0, 0.0]
        self.fuerzas = [0.0, 0.0, 0.0]
        self.historial_cargas = [] 
        self.desplazamientos = [0.0, 0.0, 0.0]; self.reacciones = [0.0, 0.0, 0.0]
        self.articulado = False 

    def fijar_apoyo(self, rx, ry, rz, angulo=0.0, dx=0.0, dy=0.0, dz=0.0):
        self.restricciones = [rx, ry, rz]; self.angulo_apoyo = angulo
        self.asentamientos = [dx, dy, dz]

    def aplicar_fuerza(self, fx, fy, mz):
        self.fuerzas[0] += fx; self.fuerzas[1] += fy; self.fuerzas[2] += mz
        self.historial_cargas.append((fx, fy, mz))

    # --- SERIALIZACIÓN JSON ---
    def to_dict(self):
        return {
            "id": self.id, "x": self.x, "y": self.y,
            "restricciones": self.restricciones, "angulo_apoyo": self.angulo_apoyo,
            "asentamientos": self.asentamientos, "fuerzas": self.fuerzas,
            "historial_cargas": self.historial_cargas, "articulado": getattr(self, 'articulado', False)
        }

    @classmethod
    def from_dict(cls, data):
        n = cls(data["id"], data["x"], data["y"])
        n.restricciones = data.get("restricciones", [0,0,0])
        n.angulo_apoyo = data.get("angulo_apoyo", 0.0)
        n.asentamientos = data.get("asentamientos", [0.0, 0.0, 0.0])
        n.fuerzas = data.get("fuerzas", [0.0, 0.0, 0.0])
        n.historial_cargas = [tuple(c) for c in data.get("historial_cargas", [])]
        n.articulado = data.get("articulado", False)
        return n

class Elemento:
    def __init__(self, id_elemento, nodo_i, nodo_j, E, A, I, rotula_i=False, rotula_j=False):
        self.id = id_elemento; self.ni = nodo_i; self.nj = nodo_j
        self.E = E; self.A = A; self.I = I
        self.rotula_i = rotula_i; self.rotula_j = rotula_j 
        self.fuerzas_internas = np.zeros(6) 
        self.cargas_distribuidas = []

    def longitud(self): return np.sqrt((self.nj.x - self.ni.x)**2 + (self.nj.y - self.ni.y)**2)
    def cosenos_directores(self):
        L = self.longitud()
        return (self.nj.x - self.ni.x) / L, (self.nj.y - self.ni.y) / L

    def matrices_condensadas(self):
        L = self.longitud(); E, A, I = self.E, self.A, self.I
        EA_L = (E * A)/L; EI12_L3 = (12 * E * I)/(L**3); EI6_L2 = (6 * E * I)/(L**2)
        EI4_L = (4 * E * I)/L; EI2_L = (2 * E * I)/L
        k_base = np.array([
            [ EA_L, 0, 0, -EA_L, 0, 0 ], [ 0, EI12_L3, EI6_L2, 0, -EI12_L3, EI6_L2 ],
            [ 0, EI6_L2, EI4_L, 0, -EI6_L2, EI2_L ], [-EA_L, 0, 0, EA_L, 0, 0 ],
            [ 0, -EI12_L3, -EI6_L2, 0, EI12_L3, -EI6_L2 ], [ 0, EI6_L2, EI2_L, 0, -EI6_L2, EI4_L ]
        ])

        fep_base = np.zeros(6)
        c, s = self.cosenos_directores()
        
        # [DEFENSA]: Descomposición de cargas Globales a Locales
        for c_data in self.cargas_distribuidas:
            if len(c_data) == 2: # Compatibilidad con proyectos guardados anteriormente
                qyi, qyj = c_data[0], c_data[1]; qxi, qxj = 0.0, 0.0
            else:
                tipo_dir, vix, viy, vjx, vjy = c_data
                if tipo_dir == "Global":
                    qxi = vix * c + viy * s; qyi = -vix * s + viy * c
                    qxj = vjx * c + vjy * s; qyj = -vjx * s + vjy * c
                else:
                    qxi, qyi, qxj, qyj = vix, viy, vjx, vjy

            qu_y = qyi; dq_y = qyj - qyi
            fep_base[1] += -qu_y * L / 2 - dq_y * L * 3 / 20
            fep_base[2] += -qu_y * L**2 / 12 - dq_y * L**2 / 30
            fep_base[4] += -qu_y * L / 2 - dq_y * L * 7 / 20
            fep_base[5] += qu_y * L**2 / 12 + dq_y * L**2 / 20
            
            qu_x = qxi; dq_x = qxj - qxi
            fep_base[0] += -qu_x * L / 2 - dq_x * L / 6
            fep_base[3] += -qu_x * L / 2 - dq_x * L / 3

        gl_liberar = []
        if self.rotula_i: gl_liberar.append(2) 
        if self.rotula_j: gl_liberar.append(5) 

        if not gl_liberar: return k_base, fep_base

        gl_mantener = [i for i in range(6) if i not in gl_liberar]
        k_cc = k_base[np.ix_(gl_liberar, gl_liberar)]
        k_rc = k_base[np.ix_(gl_mantener, gl_liberar)]
        k_cr = k_base[np.ix_(gl_liberar, gl_mantener)]
        k_rr = k_base[np.ix_(gl_mantener, gl_mantener)]
        
        fep_c = fep_base[gl_liberar]
        fep_r = fep_base[gl_mantener]

        k_cc_inv = np.linalg.inv(k_cc)
        k_cond = k_rr - k_rc @ k_cc_inv @ k_cr
        fep_cond = fep_r - k_rc @ k_cc_inv @ fep_c

        k_final = np.zeros((6, 6)); fep_final = np.zeros(6)
        for idx_r, i in enumerate(gl_mantener):
            fep_final[i] = fep_cond[idx_r]
            for idx_c, j in enumerate(gl_mantener):
                k_final[i, j] = k_cond[idx_r, idx_c]

        return k_final, fep_final
    
    def matriz_rigidez_local(self): return self.matrices_condensadas()[0]
    def vector_fep_local(self): return self.matrices_condensadas()[1]

    def matriz_transformacion(self):
        c, s = self.cosenos_directores()
        return np.array([[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
                         [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]])

    def matriz_rigidez_global(self):
        return self.matriz_transformacion().T @ self.matriz_rigidez_local() @ self.matriz_transformacion()

    # --- SERIALIZACIÓN JSON ---
    def to_dict(self):
        return {
            "id": self.id, "ni_id": self.ni.id, "nj_id": self.nj.id,
            "E": self.E, "A": self.A, "I": self.I,
            "rotula_i": getattr(self, 'rotula_i', False), "rotula_j": getattr(self, 'rotula_j', False),
            "cargas_distribuidas": self.cargas_distribuidas
        }

    @classmethod
    def from_dict(cls, data, nodos_dict):
        e = cls(data["id"], nodos_dict[data["ni_id"]], nodos_dict[data["nj_id"]], data["E"], data["A"], data["I"], data.get("rotula_i", False), data.get("rotula_j", False))
        e.cargas_distribuidas = [tuple(c) for c in data.get("cargas_distribuidas", [])]
        return e

class Estructura:
    def __init__(self): self.nodos = []; self.elementos = []
    def agregar_nodo(self, nodo): self.nodos.append(nodo)
    def agregar_elemento(self, elemento): self.elementos.append(elemento)

    def eliminar_nodo(self, id_nodo):
        self.nodos = [n for n in self.nodos if n.id != id_nodo]
        self.elementos = [e for e in self.elementos if e.ni.id != id_nodo and e.nj.id != id_nodo]
    def eliminar_elemento(self, id_elem):
        self.elementos = [e for e in self.elementos if e.id != id_elem]
    def limpiar_cargas_nodo(self, id_nodo):
        for n in self.nodos:
            if n.id == id_nodo: 
                n.fuerzas = [0.0, 0.0, 0.0]
                n.historial_cargas = []

    def ensamblar_matriz_global(self):
        num_dofs = len(self.nodos) * 3
        K_global = np.zeros((num_dofs, num_dofs))
        for elem in self.elementos:
            k_elem = elem.matriz_rigidez_global()
            idx_i, idx_j = self.nodos.index(elem.ni)*3, self.nodos.index(elem.nj)*3
            dofs = [idx_i, idx_i+1, idx_i+2, idx_j, idx_j+1, idx_j+2]
            for i in range(6):
                for j in range(6): K_global[dofs[i], dofs[j]] += k_elem[i, j]
        return K_global

    def clasificar_grados_libertad(self):
        gle, glr = [], []
        for i, n in enumerate(self.nodos):
            for j in range(3):
                if n.restricciones[j] == 1: glr.append(i*3 + j)
                else: gle.append(i*3 + j)
        return gle, glr

    def resolver_sistema(self):
        K = self.ensamblar_matriz_global()
        gle, glr = self.clasificar_grados_libertad()
        
        D_global = np.zeros(len(self.nodos) * 3)
        for i, n in enumerate(self.nodos):
            if n.restricciones[0]: D_global[i*3] = n.asentamientos[0]
            if n.restricciones[1]: D_global[i*3+1] = n.asentamientos[1]
            if n.restricciones[2]: D_global[i*3+2] = n.asentamientos[2]

        FEP_global = np.zeros(len(self.nodos) * 3); F_nodal = np.zeros(len(self.nodos) * 3)
        for i, n in enumerate(self.nodos): F_nodal[i*3:i*3+3] = n.fuerzas
        for elem in self.elementos:
            fep_g = elem.matriz_transformacion().T @ elem.vector_fep_local()
            idx_i, idx_j = self.nodos.index(elem.ni)*3, self.nodos.index(elem.nj)*3
            FEP_global[idx_i:idx_i+3] += fep_g[0:3]; FEP_global[idx_j:idx_j+3] += fep_g[3:6]
            
        D_r = D_global[glr]
        K_ee = K[np.ix_(gle, gle)]
        K_er = K[np.ix_(gle, glr)]
        
        F_total = F_nodal - FEP_global
        F_e = F_total[gle]
        
        F_e_eff = F_e - K_er @ D_r
        
        D_e = np.linalg.solve(K_ee, F_e_eff)
        D_global[gle] = D_e
        
        R_global = K @ D_global + FEP_global - F_nodal
        for i, nodo in enumerate(self.nodos):
            nodo.desplazamientos = D_global[i*3 : i*3+3]
            nodo.reacciones = [
                R_global[i*3] if nodo.restricciones[0] else 0.0,
                R_global[i*3+1] if nodo.restricciones[1] else 0.0,
                R_global[i*3+2] if nodo.restricciones[2] else 0.0
            ]
            
        for elem in self.elementos:
            idx_i, idx_j = self.nodos.index(elem.ni)*3, self.nodos.index(elem.nj)*3
            D_elem_g = np.array([D_global[idx_i], D_global[idx_i+1], D_global[idx_i+2],
                                 D_global[idx_j], D_global[idx_j+1], D_global[idx_j+2]])
            elem.fuerzas_internas = elem.matriz_rigidez_local() @ (elem.matriz_transformacion() @ D_elem_g) + elem.vector_fep_local()
            
        return D_global, K

    # --- SERIALIZACIÓN JSON ---
    def to_dict(self):
        return {
            "nodos": [n.to_dict() for n in self.nodos],
            "elementos": [e.to_dict() for e in self.elementos]
        }

    @classmethod
    def from_dict(cls, data):
        est = cls()
        nodos_dict = {}
        for n_data in data.get("nodos", []):
            n = Nodo.from_dict(n_data)
            est.agregar_nodo(n)
            nodos_dict[n.id] = n
        for e_data in data.get("elementos", []):
            e = Elemento.from_dict(e_data, nodos_dict)
            est.agregar_elemento(e)
        return est