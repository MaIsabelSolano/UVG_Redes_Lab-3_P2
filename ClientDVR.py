import slixmpp
import asyncio
from slixmpp.xmlstream.stanzabase import ET
from view import *

class ClientDVR(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.name = jid.split('@')[0]
        self.host = jid.split('@')[1]
        self.status = ""
        self.status_message = ""
        self.message_history = {}
        self.room = None

         # Obtained from slixmpp examples
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Group chat

        # Event handlers
        self.add_event_handler("session_start", self.start)


        # routing table


###################################################################
# Necesary functionality method definitions
###################################################################

    async def start(self, event):
        print("start")

        # presence
        self.send_presence()
        await self.get_roster()

        asyncio.create_task(self.user_menu())
        """Initializes de program by sending the presence, getting the roster and creating the user menu
        """


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
                pass

            elif option_2 == 3:
                # Consulstar tabla de enrutamiento
                pass 

            elif option_2 == 4:
                # Quit
                print("Cerrando sesión...")
                self.disconnect()
                self.is_connected = False


            