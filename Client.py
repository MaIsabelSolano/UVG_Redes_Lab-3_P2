import slixmpp
import asyncio
from extras import Node
from view import *
from RT import *

class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, neighbors, currentNode):
        super().__init__(jid, password)

        self.name = jid.split('@')[0]
        self.host = jid.split('@')[1]
        self.status = ""

        self.neighbors = neighbors
        self.neighbors_names_dir = {}
        self.currentNode = currentNode
        self.actualNode = Node(currentNode)

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

        # messages
        self.DMS = []
        self.Packages = []


###################################################################
# Necesary functionality method definitions
###################################################################

    async def start(self, event):
        print("start")

        # presence
        self.send_presence()
        await self.get_roster()

        await self.add_Neighbors()
        await self.get_Neighbors_list()

        asyncio.create_task(self.user_menu())
        # asyncio.create_task(self.messages())

        """Initializes de program by sending the presence, getting the roster and creating the user menu
        """

    async def createJSON():
        0


    async def listen(self, message):
        await self.get_roster()     
        if message['type'] in ('chat', 'normal', 'message'):
            try:
                message_Recieved = json.loads(message["body"])

                if message_Recieved["headers"]["algorithm"] == "flooding":
                    await self.process_message_flood(message_Recieved)

                if message_Recieved["headers"]["algorithm"] == "LST":
                    0

                if message_Recieved["headers"]["algorithm"] == "DVR":
                    print("DVR")
            except Exception as e:
                print(e)
                print("[[Se produjo un error]]")

    async def add_Neighbors(self):
        namesFP = 'names-g4.txt'
        with open(namesFP, 'r') as file:
            namesJSON = json.load(file)
            for n in self.neighbors:
                self.RT.addNeighbor(n, 1, n)
                self.send_presence_subscription(pto=namesJSON["config"][n])

    async def DVRmessage(self):
        await self.get_roster()

        # get info for messge
        nodos = [n[0] for n in self.RT.TABLE]
        res = message_Info(self.currentNode, nodos, self.RT)

        # Generate json
        if res is not None: 
            headers = {
                "from": self.currentNode,
                "to": res[0], 
                "hop": self.RT.get_info(res[0])[1],
                "algorithm": "DVR"
            }

            message = {
                "type": "message",
                "headers": headers,
                "payload": res[1]
            }

            print("")
            jsonEnv = json.dumps(message, indent=4)
            print(jsonEnv)

            # Send message
            self.send_message(mto=res[2], 
                          mbody=jsonEnv, 
                          mtype='chat')
        
    async def Floodmessage(self, neighbor, message, destiny):
        await self.get_roster()
        self.send_message(mto=destiny, mbody=message, mtype='chat')
        await self.flood(neighbor, message)
        
    async def initiate_flood(self):
        await self.get_roster()
        message = create_message()
        if message is not None: 
            nodeTo = Node(message[0])
            headers = {
                "algorithm": "flooding",
                "from": self.actualNode.name,
                "to": nodeTo.name,
                "receivers": []
            }
            
            payload = message[1]

            message = {
                "type": "message",
                "headers": headers,
                "payload": payload
            }

            jsonEnv = json.dumps(message, indent=4)
            await self.flood(self.actualNode, jsonEnv)
        
    async def flood(self, source_node, message):
        await self.get_roster()
        message_data = json.loads(message)
        message_type = message_data["type"]
        headers = message_data["headers"]
        
        if(source_node.name not in headers["receivers"]):
            headers["receivers"].append(source_node.name)
        
            for neighbor in source_node.get_neighbors(): 
                if(neighbor.name not in headers["receivers"]):
                    if(neighbor.name != headers["to"]):
                        headers["receivers"].append(neighbor.name)
                    messageT = json.dumps(message_data, indent=4)
                    dest = ""
                    with open('names-g4.txt', 'r') as file:
                        jsonNames = json.load(file)
                        dest = jsonNames["config"][neighbor.name]
                    await self.Floodmessage(neighbor, messageT, dest)
        
    async def get_Neighbors_list(self):
        await self.get_roster()
        namesFP = 'names-g4.txt'
        with open(namesFP, 'r') as file:
            namesJSON = json.load(file)
            for n in self.neighbors:
                self.neighbors_names_dir[n] = namesJSON["config"][n]
                
        self.actualNode.add_neighbors(self.neighbors_names_dir)
                
    async def process_message_flood(self, message_data):
        await self.get_roster()
        message_type = message_data["type"]
        headers = message_data["headers"]

        if(self.actualNode.name == headers['to']):
            if(message_type == "info"):
                print("Mensaje de información recibida:", headers)
                print()
            elif(message_type == "message"):
                print(f"Mensaje entrante de: {headers['from']}")
                print(message_data["payload"], "\n")
        else:
            for neighbor in self.actualNode.get_neighbors():  
                if(neighbor.name not in headers["receivers"]):
                    if(neighbor.name != headers["to"]):
                        headers["receivers"].append(neighbor.name)
                    message = json.dumps(message_data, indent=4)
                    print(f"Mensaje reenviado para {headers['to']} de {headers['from']}")
                    await self.flood(neighbor, message)


###################################################################
# User methods
###################################################################

    async def user_menu(self):

        await self.get_roster()

        print("menu")
        # user menu
        while(self.is_connected):
            await self.get_roster()

            option_2 = functions()

            if option_2 == 1:
                # Mostrar todos los contactos y su estado
                await self.contacts_status()

            elif option_2 == 2:
                # Enviar mensaje
                algorithm = choose_algorithm()
                if (algorithm == 1):
                    print("Flooding")
                    await self.initiate_flood()

                elif (algorithm == 2):
                    print("Link State routing")
                    # TODO

                elif (algorithm == 3):
                    print("Distance vector routing")
                    await self.DVRmessage()

            elif option_2 == 3:
                # Consulstar tabla de enrutamiento
                print(self.RT)

            elif option_2 == 4:
                # Quit
                print("Cerrando sesión...")
                self.send_presence(pshow="unavailable", pstatus="unavailable" )
                await asyncio.sleep(5)
                self.disconnect()
                self.is_connected = False


    async def contacts_status(self):
        # listado de contactos
        await self.get_roster()
        conts = self.client_roster
        contacts = [c for c in conts.keys()]
        contactsFullInfo = []

        if (len(contacts) > 0):
            for contact in contacts:

                sh = 'avaliable'

                # info del contacto
                info = conts.presence(contact)

                for answ, pres in info.items():
                    if pres['show']:
                        sh = pres['show']

                contactsFullInfo.append([contact, sh])

            print_contacts(contactsFullInfo)
                

        else:
            print("No se han encontrado contactos")

        """
        Gets all the user's contacts and stores their information to display it
        """
