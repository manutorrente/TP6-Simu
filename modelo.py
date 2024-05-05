import numpy as np
from scipy.stats import binom, norm, lognorm, truncnorm, exponpow, mielke, genhyperbolic
import math

class Modelo:

    def __init__(self, b, m, loops, horas_semanales = 40, aleatoriedad = None, crit = "lineal"):
        self.b = b
        self.m = m
        self.horas_semanales = horas_semanales
        self.loops = loops
        self.tiempo_actual = 0
        self.sumatoria_ganancias = 0
        self.pacientes_actuales = np.zeros(horas_semanales)
        self.honorarios_pacientes = np.zeros(horas_semanales)
        self.sumatoria_horas_ocupadas = 0
        self.contador_personas_rechazadas_cupo = 0
        self.contador_personas_rechazdas_monto = 0
        self.contador_llegadas_totales = 0
        if aleatoriedad:
            self.aleatorias = aleatoriedad
        else:
            self.aleatorias = DistribucionesAleatorias()
        self.crit = crit

    def init_random(self):
        self.pacientes_actuales = np.random.randint(0, 40, self.horas_semanales)
        self.honorarios_pacientes = np.random.randint(0, 25, self.horas_semanales)

    def horas_ocupadas(self):
        return np.count_nonzero(self.pacientes_actuales)
    
    def generar_proxima_llegada(self):
        return self.aleatorias.generar_proxima_llegada()
    
    def generar_monto_honorarios(self):
        return self.aleatorias.generar_monto_honorarios()

    def generar_duracion_consulta(self):
        return self.aleatorias.generar_duracion_consulta()
        
    def encontrar_posicion_libre(self):
            horas_libres = np.where(self.pacientes_actuales == 0)[0]
            if len(horas_libres) > 0:
                return horas_libres[0]
            else:
                return None
            
        
    def evaluar_monto(self, monto):
        if self.crit == "log":
            return self.evaluar_monto_log(monto)
        elif self.crit == "lineal":
            return self.evaluar_monto_lineal(monto)
    
    def evaluar_monto_log(self, monto):
        return monto > self.b + self.m*math.log(self.horas_ocupadas() + 1)
    
    def evaluar_monto_lineal(self, monto):
        return monto > self.b + self.m*self.horas_ocupadas()

    def loop(self):
        dt = self.generar_proxima_llegada()
        self.contador_llegadas_totales += 1
        self.tiempo_actual += dt
        self.sumatoria_ganancias += np.dot(np.minimum(self.pacientes_actuales, dt), self.honorarios_pacientes)
        self.pacientes_actuales = np.maximum(self.pacientes_actuales - dt, 0)
        horas_ocupadas = self.horas_ocupadas()
        self.sumatoria_horas_ocupadas += horas_ocupadas * dt
        monto = self.generar_monto_honorarios()
        
        if horas_ocupadas == self.horas_semanales:
            self.contador_personas_rechazadas_cupo += 1
        
        elif not self.evaluar_monto(monto):
            self.contador_personas_rechazdas_monto += 1

        else:
            duracion = self.generar_duracion_consulta()
            i = self.encontrar_posicion_libre()
            self.pacientes_actuales[i] = duracion
            self.honorarios_pacientes[i] = monto


    def simular(self):
        for i in range(self.loops):
            self.loop()
        return self.calcular_resultados()


    def calcular_resultados(self):
        ganancia_semanal = self.sumatoria_ganancias / self.tiempo_actual
        promedio_ocupacion = self.sumatoria_horas_ocupadas / (self.tiempo_actual*self.horas_semanales)
        promedio_rechazo_cupo = (self.contador_personas_rechazadas_cupo / self.contador_llegadas_totales) * 100
        promedio_rechazo_monto = (self.contador_personas_rechazdas_monto / (self.contador_llegadas_totales)) * 100
        print(f"Ganancia semanal: {ganancia_semanal}")
        print(f"Promedio ocupación: {promedio_ocupacion}")
        print(f"Promedio rechazo cupo: {promedio_rechazo_cupo}")
        print(f"Promedio rechazo monto: {promedio_rechazo_monto}")
        return ganancia_semanal, promedio_ocupacion, promedio_rechazo_cupo, promedio_rechazo_monto
    
    def reset(self):
        self.tiempo_actual = 0
        self.sumatoria_ganancias = 0
        self.pacientes_actuales = np.zeros(self.horas_semanales)
        self.honorarios_pacientes = np.zeros(self.horas_semanales)
        self.sumatoria_horas_ocupadas = 0
        self.contador_personas_rechazadas_cupo = 0
        self.contador_personas_rechazdas_monto = 0
        self.contador_llegadas_totales = 0





class DistribucionesAleatorias:
    def generar_proxima_llegada(self):
        mean_stay = 0.5  # Mean stay in weeks
        std_stay = 0.2  # Standard deviation of stay in weeks
        norm_dist = norm(mean_stay, std_stay)
        
        while True:
            r = norm_dist.rvs()
            if r > 0:
                return r
    
    def generar_monto_honorarios(self):
        # Define the bounds
        lower_bound = 8

        # Adjust parameters to achieve the desired CDF at 20
        mu = np.log(10)  # Mean of the underlying normal distribution (to achieve CDF(20) = 50%)
        sigma = 0.5  # Standard deviation of the underlying normal distribution

        # Calculate parameters of the lognormal distribution
        s = sigma
        scale = np.exp(mu)

        # Generate random values from lognormal distribution
        return int(lognorm.rvs(s=s, scale=scale, loc=lower_bound))

    def generar_duracion_consulta(self):
        # Parameters for binomial distribution
        n = 25  # Number of weeks
        p = 0.3  # Probability of leaving within 25 weeks
        binom_dist = binom(n, p)

        # Parameters for normal distribution (long-term stay)
        mean_stay = 208  # Mean stay in weeks
        std_stay = 100
        lower_bound = 0
        upper_bound = float("inf")  # Standard deviation of stay in weeks
        norm_dist = truncnorm(loc = mean_stay, scale = std_stay, a=(lower_bound - mean_stay) / std_stay, b=(upper_bound - mean_stay) / std_stay)

        if np.random.random() > 0.3:
            return int(norm_dist.rvs())
        else:
            return int(binom_dist.rvs())
        


class DistribucionesNuevas:

    def generar_proxima_llegada(self):
        params = {'b': 0.2530355326169663, 'loc': 1.9999999999999998, 'scale': 2.220442218350816}
        return exponpow.rvs(b=params['b'], loc=params['loc'], scale=params['scale'])

    def generar_monto_honorarios(self):
        params = {'k': 98.9292288769887, 's': 2.0254220214519876, 'loc': 14.861378634704273, 'scale': 0.02783457664798305}
        return mielke.rvs(k=params['k'], s=params['s'], loc=params['loc'], scale=params['scale'])
    
    def generar_duracion_consulta(self):
        params = {'p': 0.24829868410300127, 'a': 0.9027799441751452, 'b': 0.9027799436159013, 'loc': 1.9999999434593596, 'scale': 7.062554221953598e-08}
        return genhyperbolic.rvs(p=params['p'], a=params['a'], b=params['b'], loc=params['loc'], scale=params['scale'])