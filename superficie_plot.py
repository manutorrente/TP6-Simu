import modelo
import matplotlib.pyplot as plt
import variablesFijas
import multiprocessing as mp
import os
import numpy as np

class SuperficiePlot:
    def __init__(self, crit, distribuciones = None, n_loops = 10_000):
        if distribuciones is None:
            self.distribuciones = modelo.DistribucionesAleatorias()
        else :
            self.distribuciones = distribuciones
        self.n_loops = n_loops
        self.generar_variables_aleatorias()
        self.points = []
        self.criteria = crit

    def generar_variables_aleatorias(self):
        self.secuencias = variablesFijas.crear_archivos_distribuciones(self.n_loops, self.distribuciones)


    def nueva_secuencia(self):
        return variablesFijas.DistribucionesFijas(self.secuencias[0], self.secuencias[1], self.secuencias[2])
    
    def calcular_modelo(self, lbx, ubx, lby, uby, granularidad_x, granularidad_y):
        num_processes = os.cpu_count() - 1
        queue = mp.Queue()
        # Partition the area between the cpus
        x_points = np.arange(lbx, ubx, granularidad_x)
        y_points = np.arange(lby, uby, granularidad_y)
        total_points = len(x_points) * len(y_points)
        limits = [x_points[i:i + len(x_points)//num_processes] for i in range(0, len(x_points), len(x_points)//num_processes)]
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
                model = modelo.Modelo(x, y, loops=self.n_loops, aleatoriedad=self.nueva_secuencia(), crit=self.criteria)
                puntos.append((x, y, model.simular()[0]))
            print(f"Calculado para x = {x}")
            queue.put(puntos)  # Put results into the queue after each loop iteration
            puntos = []

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


