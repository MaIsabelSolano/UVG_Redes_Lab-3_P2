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

class Node:
    def __init__(self, name):
        self.name = name
        self.neighbors = []

    def add_neighbor(self, node):
        self.neighbors.append(node)

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name):
        node = Node(name)
        self.nodes[name] = node

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

def main():
    g = Graph()
    with open('./topologia_.json') as f:
        data_dict = json.load(f)

    for name in data_dict['config']:
        g.add_node(name)

    for name, neighbors in data_dict['config'].items():
        for neighbor in neighbors:
            g.add_edge(name, neighbor)

    print(g.dijkstra('A', 'D'))

if __name__ == "__main__":
    main()
