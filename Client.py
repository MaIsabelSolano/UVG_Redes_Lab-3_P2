import slixmpp
import asyncio
from view import *
from RT import *
from LinkStateRouting import *

class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, neighbors, currentNode):
        super().__init__(jid, password)

        self.name = jid.split('@')[0]
        self.host = jid.split('@')[1]
        
        self.graph = Graph()
        # Cargar la topología de la red
        with open('./topo-g4.txt') as f:
            topology = json.load(f)
        # Cargar las direcciones de XMPP de cada nodo
        with open('./names-g4.txt') as f:
            addresses = json.load(f)

        for name in topology['config']:
            self.graph.add_node(name, addresses['config'][name])

        for name, neighbors in topology['config'].items():
            for neighbor in neighbors:
                self.graph.add_edge(name, neighbor)
                
        self.status = ""

        self.neighbors = neighbors
        self.currentNode = currentNode

        # Obtained from slixmpp examples
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Group chat

        # Event handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('presence', self.presence_handler)
        self.add_event_handler("subscribe", self.handle_subscription)
        self.add_event_handler("message", self.listen)

        # routing table
        self.RT = RoutingTable()
        self.RT.addNeighbor(currentNode, 0, currentNode)
        #New rt LSR
        self.newRT = RoutingTable()
        self.newRT.addNeighbor(currentNode, 0, currentNode)


###################################################################
# Necesary functionality method definitions
###################################################################

    async def start(self, event):
        print("start")

        # presence
        self.send_presence(pshow="available")
        await self.get_roster()
        print("status: ", self.status)

        await self.add_Neighbors()

        # share initial routing table to connected 
        await self.shareRT()
        await self.shareRT_LST()

        asyncio.create_task(self.user_menu())
        # asyncio.create_task(self.messages())

        """Initializes de program by sending the presence, getting the roster and creating the user menu
        """

    async def presence_handler(self, presence):

        if presence['type'] == 'subscribe':
            try:
                self.send_presence_subscription(pto=presence['from'], ptype='subscribe')
                await self.get_roster()
            except:
                print("Hubo un error en el presence handler")

        """
        Handles how the presence is dealt with. It sends the currente presence to the accounts the user is subscribed to
        """

    async def handle_subscription(self, presence):
        if presence["type"] == "subscribe":
            self.send_presence(pto=presence["from"], ptype=["subscribed"])

        """
        Handles subscriptions requests
        """

    async def listen(self, message):
        await self.get_roster()        
        if message['type'] in ('chat', 'normal'):
            try:
                message_Recieved = json.loads(message["body"])
                print(message_Recieved)

                if message_Recieved["headers"]["algorithm"] == "flooding":
                    0

                if message_Recieved["headers"]["algorithm"] == "Link State Routing":
                    if message_Recieved["type"] == "message":
                        if message_Recieved["headers"]["to"] == self.currentNode:
                            # The message has reached it's intended node
                            from_ = message_Recieved["headers"]["from"]
                            payload = message_Recieved["payload"]
                            print("\n=======================================")
                            print(f"Nuevo mensaje de {from_}!\n{payload}")
                            print("=======================================\n")

                        else:
                            # Re-semd
                            to_ = message_Recieved["headers"]["to"]
                            if self.newRT.contains(to_):
                                # find the direction
                                with open('names-g4.txt', 'r') as file:
                                    namesJSON = json.load(file)

                                    # from routing table get where to hop
                                    hop = self.newRT.get_info(to_)[1]
                                    hop_dir = namesJSON["config"][hop]
    
                                    jsonEnv = json.dumps(message_Recieved, indent=4)
                                    print(f"reenvio por {hop_dir}\n", jsonEnv)

                                    # Send message
                                    self.send_message(mto=hop_dir, 
                                                    mbody=jsonEnv, 
                                                    mtype='chat')
                    if message_Recieved["type"] == "info":
                        print("info!!!")
                        # Got a routing table
                        currentRT = self.RT.TABLE # used to compare later

                        from_ = message_Recieved["headers"]["from"]
                        rt = message_Recieved["payload"]

                        for i in range(len(rt)):
                            if (self.newRT.contains(rt[i][0])):
                                # update si es menor
                                wAcc = self.RT.get_info(rt[i][0])[0]
                                weight = self.RT.get_info(from_)[0] + rt[i][1]
                                # print(f"{weight} < {wAcc}? {self.actual_node}, {rt[i][0]}, {from_} ")

                                if weight < wAcc:
                                    # Actualizar si es menor
                                    self.newRT.update_info(rt[i][0], weight, from_)
                                    # print("actualiza", rt[i][0], weight, from_)

                            else:
                                # agregar
                                weight = self.newRT.get_info(from_)[0] + rt[i][1]
                                self.newRT.addNeighbor(rt[i][0], weight, from_)

                        # share routing table only if it changed
                        if currentRT != self.RT.TABLE:
                            await self.shareRT_LST()

                if message_Recieved["headers"]["algorithm"] == "DVR":
                    print("DVR")
                    if message_Recieved["type"] == "message":
                        if message_Recieved["headers"]["to"] == self.currentNode:
                            # The message has reached it's intended node
                            from_ = message_Recieved["headers"]["from"]
                            payload = message_Recieved["payload"]
                            print("\n=======================================")
                            print(f"Nuevo mensaje de {from_}!\n{payload}")
                            print("=======================================\n")

                        else:
                            # Re-semd
                            to_ = message_Recieved["headers"]["to"]
                            if self.RT.contains(to_):
                                # find the direction
                                with open('names-g4.txt', 'r') as file:
                                    namesJSON = json.load(file)

                                    # from routing table get where to hop
                                    hop = self.RT.get_info(to_)[1]
                                    hop_dir = namesJSON["config"][hop]
    
                                    jsonEnv = json.dumps(message_Recieved, indent=4)
                                    print(f"reenvio por {hop_dir}\n", jsonEnv)

                                    # Send message
                                    self.send_message(mto=hop_dir, 
                                                    mbody=jsonEnv, 
                                                    mtype='chat')

                    if message_Recieved["type"] == "info":
                        print("info!!!")
                        # Got a routing table
                        currentRT = self.RT.TABLE # used to compare later

                        from_ = message_Recieved["headers"]["from"]
                        rt = message_Recieved["payload"]

                        for i in range(len(rt)):
                            if (self.RT.contains(rt[i][0])):
                                # update si es menor
                                wAcc = self.RT.get_info(rt[i][0])[0]
                                weight = self.RT.get_info(from_)[0] + rt[i][1]
                                # print(f"{weight} < {wAcc}? {self.actual_node}, {rt[i][0]}, {from_} ")

                                if weight < wAcc:
                                    # Actualizar si es menor
                                    self.RT.update_info(rt[i][0], weight, from_)
                                    # print("actualiza", rt[i][0], weight, from_)

                            else:
                                # agregar
                                weight = self.RT.get_info(from_)[0] + rt[i][1]
                                self.RT.addNeighbor(rt[i][0], weight, from_)

                        # share routing table only if it changed
                        if currentRT != self.RT.TABLE:
                            await self.shareRT()


            except:
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
                "hop": " ", # self.RT.get_info(res[0])[1],
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

    async def LSTMessage(self):
        await self.get_roster()

        # get info for messge
        nodos = [n[0] for n in self.RT.TABLE]
        res = message_Info(self.currentNode, nodos, self.RT)

        # Generate json
        if res is not None: 
            headers = {
                "from": self.currentNode,
                "to": res[0], 
                "hop": " ",
                "algorithm": "Link State Routing"
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
            

    async def shareRT(self):
        print("Sharing Routing Table")
        
        
        await self.get_roster()
        
        connectedNeighbors = []
        try:
            with open('names-g4.txt', 'r') as file:
                namesJson = json.load(file)
                for n in self.neighbors:
                    # get direction
                    nDir = namesJson["config"][n]

                    # check connection
                    # TODO at the moment it is not handling presence
                    connectedNeighbors.append((n, nDir))

            print("cn: ", connectedNeighbors)

            payload = self.RT.TABLE

            for n, nDir in connectedNeighbors:
                headers = {
                    "from": self.currentNode,
                    "to": n, 
                    "algorithm": "DVR"                    
                }

                message = {
                    "type": "info",
                    "headers": headers,
                    "payload": payload
                }

                jsonRes = json.dumps(message, indent=4)
                print(jsonRes)

                # Send message
                self.send_message(mto=nDir, 
                            mbody=jsonRes, 
                            mtype='chat')
                
        except:
            print("[[Error: Ocurrió un problema]]")
            
    async def shareRT_LST(self):
        print("Sharing Routing Table")
        await self.get_roster()
        
        #Realizamos dijkstra para obtener el camino más corto
        #Para ello lo hacemos calculando y utilizando ya todos los nodos de la tabla RT que ya se tiene
        #Y así poder obtener el camino más corto
        
        #Obtenemos la tabla de enrutamiento
        rt = self.RT.TABLE
        #Obtenemos los nodos de la tabla de enrutamiento
        nodos = [n[0] for n in rt]
        #Obtenemos el nodo actual
        nodo_actual = self.currentNode
        #Obtenemos el nodo destino
        nodo_destino = nodos[0]
        #Obtenemos el camino más corto
        camino_corto = self.graph.dijkstra(nodo_actual, nodo_destino)
        #Una vez se obtiene el camino más corto, se arma una nueva tabla de enrutamiento, la cual se va a utilizar
        #para así poder enviar los mensajes
        #utiliza lo mismo que una RT
        #Se agrega el nodo actual a la nueva tabla de enrutamiento
        self.newRT.addNeighbor(nodo_actual, 0, nodo_actual)
        #Se agrega el nodo destino a la nueva tabla de enrutamiento
        self.newRT.addNeighbor(nodo_destino, camino_corto, nodo_actual)

        
        connectedNeighbors = []
        try:
            with open('names-g4.txt', 'r') as file:
                namesJson = json.load(file)
                for n in self.neighbors:
                    # get direction
                    nDir = namesJson["config"][n]

                    # check connection
                    # TODO at the moment it is not handling presence
                    connectedNeighbors.append((n, nDir))

            print("cn: ", connectedNeighbors)

            payload = newRT.TABLE

            for n, nDir in connectedNeighbors:
                headers = {
                    "from": self.currentNode,
                    "to": n, 
                    "algorithm": "Link State Routing"                    
                }

                message = {
                    "type": "info",
                    "headers": headers,
                    "payload": payload
                }

                jsonRes = json.dumps(message, indent=4)
                print(jsonRes)

                # Send message
                self.send_message(mto=nDir, 
                            mbody=jsonRes, 
                            mtype='chat')
                
        except:
            print("[[Error: Ocurrió un problema]]")

            

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
                    # TODO

                elif (algorithm == 2):
                    print("Link State routing")
                    await self.LSTMessage()

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

                sh = ''
                st = ''

                # info del contacto
                info = conts.presence(contact)

                for answ, pres in info.items():
                    if pres['show']:
                        sh = pres['show']
                    if pres['status']:
                        st = pres['status']

                contactsFullInfo.append([contact, sh])

            print_contacts(contactsFullInfo)
                

        else:
            print("No se han encontrado contactos")

        """
        Gets all the user's contacts and stores their information to display it
        """
