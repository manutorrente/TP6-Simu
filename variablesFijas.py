import numpy as np

class DistribucionesFijas:

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


def crear_archivos_distribuciones(len, distribuciones):

    proximas_llegadas = np.array([distribuciones.generar_proxima_llegada() for _ in range(len)])
    montos_honorarios = np.array([distribuciones.generar_monto_honorarios() for _ in range(len)])
    duraciones_consulta = np.array([distribuciones.generar_duracion_consulta() for _ in range(len)])
    return proximas_llegadas, montos_honorarios, duraciones_consulta
