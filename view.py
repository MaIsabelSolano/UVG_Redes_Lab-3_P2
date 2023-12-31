import json 
from prettytable import PrettyTable
from RT import *

def get_node():

    nodes = []
    filepath = 'names-g4.txt'
    with open(filepath, 'r') as file:
        try: 
            jsonR = json.load(file)
            for x in jsonR["config"]:
                nodes.append(x)
        
            while(True):
                print("")
                last = 0
                for i, node in enumerate(nodes):
                    print(f"{i+1}) {node}")
                    last = i
                print(f"{last+2}) CANCELAR\n")

                input_ = input("Seleccione el nodo actual: ")

                if input_ in [ str(x + 1) for x in range(len(nodes))]:
                    # return nodes[int(input_) - 1]
                    return nodes[int(input_) - 1], jsonR["config"][nodes[int(input_) - 1]]
                
                elif input_ == str(len(nodes) + 1):
                    return None
                
                else: 
                    print("\n[[Opción inválida, pruebe nuevamente]]")

        except:
            print("[[Error, ocurrió un error]]")
            return None


def main_menu():
    while(True):
        print("1) Iniciar sesión")
        print("2) Crear una cuenta")
        print("3) Salir\n")

        op = input("No. de opción: ")

        if (op == '1'or op == '2' or op == '3'):
            return op 
        else:
            print("\n[[Opción inválida, pruebe nuevamente]]")


def functions():
    valid_options = range(1, 3) # [1, 2]

    stop = False
    while(not stop):
        print("\n__________________________")
        print("Ingrese el número de la opción que desea realizar: ")
        print("1) Mostrar todos los contactos y su estado")
        print("2) Enviar un mensaje")
        print("3) Consultar tabla de enrutamiento")
        print("4) SALIR\n")

        input_ = input("No. de opción: ")

        poss = [str(x + 1) for x in range(4)] # [1, 4]

        if input_ in poss:
            return int(input_)
        
        else: 
            print("\n[[Opción inválida, pruebe nuevamente]]")

def print_contacts(contacts):
    """
    Given a list of contacts, this function creates a table to display them

    Args:
        contacts (str): contact list
    """
    x = PrettyTable()
    x.field_names = ["Contacto", "Estado"]
    for c in contacts:
        x.add_row([c[0], c[1]])

    print(x)

def choose_algorithm():

    while(True):
        print("\nEscoja el algoritmo a utilizar")
        print("1) Flooding")
        print("2) Link State Routing")
        print("3) Distance vector routing")
        print("4) CANCELAR")
        
        input_ = input("\nNo. del algoritmo: ")

        ops = [str(x) for x in range(1, 5)]

        if input_ not in ops:
            print("\n[[Opción inválida, pruebe nuevamente]]")

        else:
            return int(input_)
        

def message_Info(nodo_actual, nodes_list, rt:RoutingTable):

    while(True):

        print("\nIngrese los datos que se le piden a continuación")
        node = input("Nodo: ")
        payload = input("Mensaje: ")

        if (payload is None) or (node is None):
            return None

        if (node not in nodes_list):
            print(f"[[Error: {nodo_actual} no tiene relación con {node}]]")
            print("Pruebe nuevamente")

        else:
            hop = ""
            try: 
                # get direction
                with open('names-g4.txt', 'r') as file:
                    jsonNames = json.load(file)
                    hop = jsonNames["config"][rt.get_info(node)[1]] # where to hop

            except:
                print(f"[[Error al leer el archivo]]")
                print("Pruebe nuevamente")
                
            return (node, payload, hop)

def create_message():
    while(True):
        print("\nIngrese los datos que se le piden a continuación")
        node = input("Nodo destino: ")
        payload = input("Mensaje: ")

        if (payload is None) or (node is None):
            return None

        dest = ""
        try: 
            # get direction
            with open('names-g4.txt', 'r') as file:
                jsonNames = json.load(file)
                dest = jsonNames["config"][node]

        except:
            print(f"[[Error al leer el archivo]]")
            print("Pruebe nuevamente")
            
        return (node, payload, dest)

