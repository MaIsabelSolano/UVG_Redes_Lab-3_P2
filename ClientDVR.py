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

         # Obtenido de ejemplos de slixmpp
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Group chat


        # Event handlers
        self.add_event_handler("session_start", self.start)


        async def start(self, event):
            print("start")

            # presence
            # self.send_presence()
            # await self.get_roster()

            asyncio.create_task(self.user_menu())
            """Initializes de program by sending the presence, getting the roster and creating the user menu
            """


            async def user_menu(self):

                await self.get_roster()

                print("menu")
                # user menu
                while(self.is_connected):

                    option_2 = functions()