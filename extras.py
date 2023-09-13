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


class Node:
    def __init__(self, name):
        self.name = name.upper()
        self.neighbors = {}

    def add_neighbors(self, neighbors):
        for node, dir in neighbors.items():
            self.neighbors[Node(node)] = dir

    def get_neighbors(self):
        return list(self.neighbors.keys())
    
    def get_directions(self):
        return list(self.neighbors.values())

    def __repr__(self):
        return f"Nodo: {self.name}{(' | Vecinos: '+str(self.neighbors)) if len(self.neighbors)>0 else ''}"
        
    def __str__(self):
        return f"Nodo: {self.name}{(' | Vecinos: '+str(self.neighbors)) if len(self.neighbors)>0 else ''}"