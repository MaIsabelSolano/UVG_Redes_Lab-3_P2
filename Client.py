import slixmpp
import asyncio
import time
from slixmpp.xmlstream.stanzabase import ET
from view import *
from RT import *

class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, neighbors, currentNode):
        super().__init__(jid, password)

        self.name = jid.split('@')[0]
        self.host = jid.split('@')[1]
        self.status = ""
        self.status_message = ""      

         # Obtained from slixmpp examples
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Group chat

        # Event handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.listen)

        # routing table
        self.RT = RoutingTable()
        self.RT.addNeighbor(currentNode, 0, currentNode)
        for n in neighbors:
            self.RT.addNeighbor(n, 1, n)
              


###################################################################
# Necesary functionality method definitions
###################################################################

    async def start(self, event):
        print("start")

        # presence
        self.send_presence()
        await self.get_roster()

        asyncio.create_task(self.user_menu())
        # while(True):
        #     print("kdjf")
        #     time.sleep(4)
        """Initializes de program by sending the presence, getting the roster and creating the user menu
        """

    async def createJSON():
        0


    async def listen():
        print("mensaje")
        0


###################################################################
# User methods
###################################################################

    async def user_menu(self):

        await self.get_roster()

        print("menu")
        # user menu
        while(self.is_connected):

            option_2 = functions()

            if option_2 == 1:
                # Mostrar todos los contactos y su estado
                pass 

            elif option_2 == 2:
                # Enviar mensaje
                algorithm = choose_algorithm()
                if (algorithm == 1):
                    print("Flooding")
                    # TODO

                elif (algorithm == 2):
                    print("Link State routing")
                    # TODO

                elif (algorithm == 3):
                    print("Distance vector routing")
                    # TODO

            elif option_2 == 3:
                # Consulstar tabla de enrutamiento
                print(self.RT)

            elif option_2 == 4:
                # Quit
                print("Cerrando sesión...")
                self.disconnect()
                self.is_connected = False


            