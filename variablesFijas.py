import numpy as np
import modelo

class GeneradorDeSecuencias:

    def __init__(self, n_loops = 10_000, n_repeticiones = 3, distribuciones = None):
        self.n_loops = n_loops
        self.n_repeticiones = n_repeticiones
        if distribuciones is None:
            self.distribuciones = modelo.DistribucionesNuevas()
        else:
            self.distribuciones = distribuciones
        self.secuencias = []
        self.generar_variables_aleatorias()

    
    def generar_variables_aleatorias(self):
        self.secuencias = []
        for i in range(self.n_repeticiones):
            self.secuencias.append(self.crear_archivos_distribuciones())

    def crear_archivos_distribuciones(self):

        proximas_llegadas = np.array([self.distribuciones.generar_proxima_llegada() for _ in range(self.n_loops)])
        montos_honorarios = np.array([self.distribuciones.generar_monto_honorarios() for _ in range(self.n_loops)])
        duraciones_consulta = np.array([self.distribuciones.generar_duracion_consulta() for _ in range(self.n_loops)])
        return proximas_llegadas, montos_honorarios, duraciones_consulta

    def nueva_secuencias(self):
        return [Secuencia(self.secuencias[i][0], self.secuencias[i][1], self.secuencias[i][2]) for i in range(self.n_repeticiones)]

class Secuencia:

    def __init__(self, llegadas, montos, duracion):
        self.i_llegadas = 0
        self.i_montos = 0
        self.i_duracion = 0
        self.proximas_llegadas = llegadas
        self.montos_honorarios = montos
        self.duraciones_consulta = duracion
        self.len = len(self.proximas_llegadas)



    def generar_proxima_llegada(self):
        r = self.proximas_llegadas[self.i_llegadas]
        self.i_llegadas += 1
        if self.i_llegadas == self.len:
            self.i_llegadas = 0

        return r
    
    def generar_monto_honorarios(self):
        r = self.montos_honorarios[self.i_llegadas]
        self.i_montos += 1
        if self.i_montos == self.len:
            self.i_montos = 0

        return r
    
    def generar_duracion_consulta(self):
        r = self.duraciones_consulta[self.i_llegadas]
        self.i_duracion += 1
        if self.i_duracion == self.len:
            self.i_duracion = 0

        return r
    
    

    




