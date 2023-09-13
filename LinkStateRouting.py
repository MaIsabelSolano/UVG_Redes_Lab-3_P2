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


class NodeLSR:
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
        node = NodeLSR(name, address)
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

        previous_nodes = {node: None for node in self.nodes}
        queue = PriorityQueue()
        queue.put((0, start))

        while not queue.empty():
            _, current = queue.get()
            for neighbor in self.nodes[current].neighbors:
                distance = D[current] + 1
                if distance < D[neighbor.name]:
                    D[neighbor.name] = distance
                    previous_nodes[neighbor.name] = current
                    queue.put((distance, neighbor.name))

        path = []
        while end is not None:
            path.insert(0, end)
            end = previous_nodes[end]
        return path