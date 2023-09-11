import json 

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
                print(f"{last+2}) CANCELAR")

                input_ = input("Seleccione el nodo actual: ")

                if input_ in [ str(x + 1) for x in range(len(nodes))]:
                    # return nodes[int(input_) - 1]
                    return jsonR["config"][nodes[int(input_) - 1]]
                
                elif input_ == str(len(nodes) + 1):
                    return None
                
                else: 
                    print("\n[[Opción inválida, pruebe nuevamente]]")

        except:
            print("[[Error, ocurrió un error]]")
            return None


def main_menu():
    while(True):
        print("\n1) Iniciar sesión")
        print("\n2) Crear una cuenta")
        print("\n3) Salir\n")

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
        print("\nIngrese el número de la opción que desea realizar: ")
        print("\n1) Mostrar todos los contactos y su estado")
        print("\n2) Enviar un mensaje")
        print("\n3) Consultar tabla de enrutamiento")
        print("\n4) SALIR")

        input_ = input("No. de opción: ")

        poss = [str(x + 1) for x in range(4)] # [1, 4]

        if input_ in poss:
            return int(input_)
        
        else: 
            print("\n[[Opción inválida, pruebe nuevamente]]")
        






