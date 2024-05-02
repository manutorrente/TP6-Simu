import pickle
import modelo

class DistribucionesFijas:

    ### guardar la secuencia de valores aleatorios en un archivo para poder reproducir la simulación
    def __init__(self):
        with open("proximas_llegadas.pkl", "rb") as f:
            self.proximas_llegadas = pickle.load(f)
        with open("montos_honorarios.pkl", "rb") as f:
            self.montos_honorarios = pickle.load(f)
        with open("duracion_consulta.pkl", "rb") as f:
            self.duraciones_consulta = pickle.load(f)
        self.i_llegadas = 0
        self.i_montos = 0
        self.i_duracion = 0
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

    proximas_llegadas = [distribuciones.generar_proxima_llegada() for _ in range(len)]
    montos_honorarios = [distribuciones.generar_monto_honorarios() for _ in range(len)]
    duraciones_consulta = [distribuciones.generar_duracion_consulta() for _ in range(len)]

    with open("proximas_llegadas.pkl", "wb") as f:
        pickle.dump(proximas_llegadas, f)
    with open("montos_honorarios.pkl", "wb") as f:
        pickle.dump(montos_honorarios, f)
    with open("duracion_consulta.pkl", "wb") as f:
        pickle.dump(duraciones_consulta, f)