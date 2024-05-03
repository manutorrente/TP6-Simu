import modelo
import variablesFijas
from importlib import reload
reload(variablesFijas)
reload(modelo)
import multiprocessing as mp
import numpy as np

class Maximizacion:
        
        def __init__(self, distribuciones = None, n_loops = 1000, n_repeticiones = 3, resultado_a_optimizar = 0, multiprocesamiento = True):
            if distribuciones is None:
                self.distribuciones = modelo.DistribucionesAleatorias()
            else :
                self.distribuciones = distribuciones
            self.n_loops = n_loops
            self.generar_variables_aleatorias(n_repeticiones)
            self.modelo = modelo.Modelo
            self.resultado_a_optimizar = resultado_a_optimizar
            self.n_repeticiones = n_repeticiones
            self.h_x = 1
            self.h_y = 0.01
            self.tracking = []
            self.multiprocesamiento = multiprocesamiento


        def generar_punto_de_partida(self, x = None, y = None):
            if x is None:
                self.x = np.random.randint(0, 40)
            else:
                self.x = x
            if y is None:
                self.y = np.random.random()*3
            else:
                self.y = y
            return x, y


        def generar_variables_aleatorias(self, cantidad):
            self.secuencias = []
            for i in range(cantidad):
                self.secuencias.append(variablesFijas.crear_archivos_distribuciones(self.n_loops, self.distribuciones))


        def nueva_secuencia(self, i):
            return variablesFijas.DistribucionesFijas(self.secuencias[i][0], self.secuencias[i][1], self.secuencias[i][2])
        
        def calcular_modelo(self, x, y, queue = None, key = None):
            distribuciones = [self.nueva_secuencia(i) for i in range(self.n_repeticiones)]
            resultados = []
            for distribucion in distribuciones:
                model = modelo.Modelo(x, y, loops=self.n_loops, aleatoriedad = distribucion, crit="log")
                resultados.append(model.simular()[self.resultado_a_optimizar])
            resultado = sum(resultados)/self.n_repeticiones
            if queue is not None:
                queue.put({key: resultado})
            else:
                return resultado
        
        def calcular_gradiente(self, x, y, h_x, h_y):
            x0y0 = self.calcular_modelo(x, y)
            xhy0 = self.calcular_modelo(x+h_x, y)
            x0yh = self.calcular_modelo(x, y+h_y)
            dx_dz = (xhy0 - x0y0)/h_x
            dy_dz = (x0yh - x0y0)/h_y
            return x0y0, dx_dz, dy_dz
        
        def calcular_gradiente_multiprocesamiento(self, x, y, h_x, h_y):
            queue = mp.Queue()
            processes = [
                mp.Process(target = self.calcular_modelo, args = (x, y, queue, "base")),
                mp.Process(target = self.calcular_modelo, args = (x+h_x, y, queue, "x")),
                mp.Process(target = self.calcular_modelo, args = (x, y+h_y, queue, "y"))
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            results = {}
            while not queue.empty():
                results.update(queue.get())
            x0y0 = results["base"]
            xhy0 = results["x"]
            x0yh = results["y"]
            dx_dz = (xhy0 - x0y0)/h_x
            dy_dz = (x0yh - x0y0)/h_y
            return x0y0, dx_dz, dy_dz



        def optimizar(self, n_iteraciones = 100, alpha_x = 0.02, alpha_y = 0.0001):
            x = self.x
            y = self.y
            for i in range(n_iteraciones):
                if self.multiprocesamiento:
                    z, dx_dz, dy_dz = self.calcular_gradiente_multiprocesamiento(x, y, self.h_x, self.h_y)
                else:
                    z, dx_dz, dy_dz = self.calcular_gradiente(x, y, self.h_x, self.h_y)
                self.tracking.append((x,y,z))
                mov_x = alpha_x*dx_dz
                mov_y = alpha_y*dy_dz
                print("Iteración", i, "x:", x, "y:", y, "z:", z, "\n", "desplzaiento x:", mov_x, "desplazamiento y:", mov_y)
                x += mov_x
                y += mov_y
            self.x = x
            self.y = y
            return x, y

