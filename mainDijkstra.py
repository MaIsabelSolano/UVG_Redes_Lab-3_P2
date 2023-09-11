"""
Universidad del Valle de Guatemala
Facultad de Ingeniería
Departamento de Ciencias de la Computación
CC3067 - Redes

Laboratorio 3 - Segunda Parte 
Algoritmos de Enrutamiento

Integrantes:
- Christopher García (20541)
- José Rodrigo Barrera (20807)
- Ma. Isabel Solano (20504)
"""

import json
import sys
from queue import PriorityQueue
import slixmpp

class Node:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.neighbors = []

    def add_neighbor(self, node):
        self.neighbors.append(node)

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, address):
        node = Node(name, address)
        self.nodes[name] = node
    
    def print_addresses(self):
        for node in self.nodes.values():
            print(f'Dirección XMPP: {node.address}')

    def add_edge(self, name1, name2):
        self.nodes[name1].add_neighbor(self.nodes[name2])
        self.nodes[name2].add_neighbor(self.nodes[name1])

    def dijkstra(self, start, end):
        D = {node: float('infinity') for node in self.nodes}
        D[start] = 0

        queue = PriorityQueue()
        queue.put((0, start))

        while not queue.empty():
            _, current = queue.get()
            for neighbor in self.nodes[current].neighbors:
                distance = D[current] + 1
                if distance < D[neighbor.name]:
                    D[neighbor.name] = distance
                    queue.put((distance, neighbor.name))

        return D[end]

    def main_menu():
        while True:
            print("Menú principal:")
            print("1. Iniciar sesión")
            print("2. Registrar")
            print("3. Salir")

            option = input("Seleccione una opción: ")

            if option == "1":
                print("Iniciar sesión")
            elif option == "2":
                 print("Registrar")
            elif option == "3":
                print("¡Hasta luego!")
                break
            else:
                print("Opción inválida. Por favor, seleccione una opción válida.")

    def login_menu():
        while True:
            print("Menú de inicio de sesión:")
            print("1. Enviar mensaje")
            print("2. Escuchar mensaje")
            print("3. Salir")

            option = input("Seleccione una opción: ")

            if option == "1":
                 print("Enviar mensaje")
            elif option == "2":
                print("Escuchar mensaje")
            elif option == "3":
                print("¡Hasta luego!")
                break
            else:
                print("Opción inválida. Por favor, seleccione una opción válida.")

def main():
    g = Graph()

    # Cargar la topología de la red
    with open('./topologia_.json') as f:
        topology = json.load(f)

    # Cargar las direcciones de XMPP de cada nodo
    with open('./adress.json') as f:
        addresses = json.load(f)

    for name in topology['config']:
        g.add_node(name, addresses['config'][name])

    for name, neighbors in topology['config'].items():
        for neighbor in neighbors:
            g.add_edge(name, neighbor)

    print(g.dijkstra('A', 'D'))
    g.print_addresses()

if __name__ == "__main__":
    main()
