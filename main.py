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

import asyncio
import pyfiglet
import xmpp
from Client import *
from view import *

# Avoids Exception ignored from cffi callback <function _sock_state_cb at 0x000002C1CE3BF940>: error
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def main():

    titulo = pyfiglet.figlet_format("Lab3 p2")
    print("\n"+titulo)  


    programRunning = True
    while(programRunning):

        option = main_menu()

        if (option == '1'):
            res = get_node()
            if res is not None:
                nodoAc, jid = res
                print(nodoAc)

                # get neighours
                neighbors = []
                with open('topo-g4.txt', 'r') as file:
                    topology = json.load(file)
                    neighbors = topology["config"][nodoAc]

                # default password
                passw = "redes2023"

                # connection
                client = Client(jid, passw, neighbors, nodoAc)
                client.connect(disable_starttls=True, use_ssl=False)
                client.process(forever=False)


        elif (option == '2'):

            print("Todas las cuentas han sido creadas...")
            continue

            # get desired user from topology
            nodoAc, jid = get_node()
            if nodoAc is not None:
                print(nodoAc)

            # create user 
            # jid = nodoAc
            passw = "redes2023"

            try:
                # register                
                newUser = xmpp.JID(jid)

                newUser_ = xmpp.Client(newUser.getDomain(), debug=[])
                newUser_.connect()
                
                res = bool(
                    xmpp.features.register(
                    newUser_, 
                    newUser.getDomain(), 
                    {
                        'username': newUser.getNode(),
                        'password': passw
                    })
                )

                if res:
                    print("\nCuenta creada con éxito")
                else:
                    print("\nOcurrió un error al momento de crear la cuenta")

                print("Por favor seleccione el la primera opción para ingresar con sus nuevos datos")

            except:
                print("\n[[Ocurrió un error, pruebe más tarde]]\n")

        elif (option == '3'):
            # exit
            programRunning = False

if __name__ == '__main__':
    main()

