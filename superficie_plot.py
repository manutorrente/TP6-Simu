import modelo
import matplotlib.pyplot as plt
import variablesFijas
import multiprocessing as mp
import os
import numpy as np
from importlib import reload
reload(variablesFijas)

class SuperficiePlot:
    def __init__(self, crit, n_loops = 10_000, resultado_a_optimizar = 0, generadorSecuencias = None):
        self.n_loops = n_loops
        self.points = []
        self.criteria = crit
        self.secuencias = []
        self.resultado_a_optimizar = resultado_a_optimizar
        if generadorSecuencias is None:
            self.generadorSecuencias = variablesFijas.GeneradorDeSecuencias(n_loops = n_loops)
        else:
            self.generadorSecuencias = generadorSecuencias



    def calcular_modelo(self, lbx, ubx, lby, uby, granularidad_x, granularidad_y):
        num_processes = os.cpu_count() - 1
        queue = mp.Queue()
        # Partition the area between the cpus
        x_points = np.arange(lbx, ubx, granularidad_x)
        y_points = np.arange(lby, uby, granularidad_y)
        total_points = len(x_points) * len(y_points)
        limits = [x_points[i:i + len(x_points)//num_processes] for i in range(0, len(x_points), max(len(x_points)//num_processes, 1))]
        processes = []
        for limit in limits:
            p = mp.Process(target=self.calcular_puntos, args=(limit[0], limit[-1], lby, uby, granularidad_x, granularidad_y, queue))
            processes.append(p)
            p.start()
            print(f"Started process for {limit[0]} < x < {limit[-1]}")
        
        # Main process continuously gets items from the queue
        points_count = 0
        while points_count < total_points:
            while not queue.empty():
                c = queue.get()
                self.points.extend(c)
                points_count += len(c)
                print(f"Received {len(c)} points. Total points: {points_count}/{total_points}")
        
        # Wait for all processes to finish
        for process in processes:
            process.join()
        print("All processes finished")

    def calcular_puntos(self, lbx, ubx, lby, uby, granularidad_x, granularidad_y, queue):
        puntos = []
        for x in np.arange(lbx, ubx + granularidad_x, granularidad_x):
            for y in np.arange(lby, uby, granularidad_y):
                resultado = self.calcular_punto(x, y)
                puntos.append((x, y, resultado))
            print(f"Calculado para x = {x}")
            queue.put(puntos)  # Put results into the queue after each loop iteration
            puntos = []

    def calcular_punto(self, x, y):
        distribuciones = self.generadorSecuencias.nueva_secuencias()
        resultados = []
        for distribucion in distribuciones:
            model = modelo.Modelo(x, y, loops=self.n_loops, aleatoriedad = distribucion, crit = self.criteria)
            resultados.append(model.simular()[self.resultado_a_optimizar])
        resultado = sum(resultados)/len(distribuciones)
        return resultado


    def plot(self):
        x, y, z = zip(*self.points)
        fig = plt.figure(figsize=(12, 9))
        maxz = max(self.points, key=lambda x: x[2])

        fig.suptitle(f"Superficie de ganancia semanal en función de B y M con criterio {self.criteria} \nMáximo: B = {maxz[0]}, M = {maxz[1]}, Ganancia semanal: {maxz[2]}", fontsize=16)

        for i, angle in enumerate([45, 135, 225, 315]):  # Angles for the four plots
            ax = fig.add_subplot(2, 2, i+1, projection='3d')
            
            # Plotting the surface
            ax.plot_trisurf(x, y, z, cmap='viridis', edgecolor='none')
            
            # Adding labels
            ax.set_xlabel('B')
            ax.set_ylabel('M')
            ax.set_zlabel('Ganancia semanal')
            
            # Setting the viewing angle
            ax.view_init(azim=angle)
            
            ax.set_title(f"Viewing angle: {angle} degrees")

        # Adjust layout and show plot
        plt.tight_layout()
        plt.show()


    def plot_max(self):


        max_tuple = max(self.points, key=lambda x: x[2])
        b_max, m_max, z_max = max_tuple

        # Define the function b + m * log(x+1)
        if self.criteria == 'log':
            def function(x, b, m):
                return b + m * np.log(x + 1)
        elif self.criteria == 'lineal':
            def function(x, b, m):
                return b + m * x

        f = lambda x: function(x, b_max, m_max)

        # Generate x values
        x_values = np.linspace(0, 40, 1000)

        # Generate y values using the function with the maximum b and m
        y_values = function(x_values, b_max, m_max)

        # Plot the function
        plt.plot(x_values, y_values, label=f'{b_max} + {m_max} {"* log(x + 1)" if self.criteria == "log" else "* x"}')

        # Shade the area above the curve
        plt.fill_between(x_values, y_values, max(y_values), color='green', alpha=0.3, where=(x_values >0)&(x_values<40))

        # Shade the area below the curve
        plt.fill_between(x_values, y_values, min(y_values), color='red', alpha=0.3, where=(x_values >0)&(x_values<40))

        # Label the areas
        plt.text(10, max(y_values) -1.5, 'ACEPTA', horizontalalignment='center', fontsize=12, color='green')
        plt.text(20, min(y_values)+1, 'NO ACEPTA', horizontalalignment='center', fontsize=12, color='red')

        # Add legend
        plt.legend()

        # Add labels and title
        plt.xlabel('Horas Ocupadas')
        plt.ylabel('Monto')
        plt.title('Criterio de aceptación')

        # Show plot
        plt.grid(True)
        plt.show()


