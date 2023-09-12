import slixmpp
from slixmpp import Presence
import asyncio
from view import *
from RT import *

class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, neighbors, currentNode):
        super().__init__(jid, password)

        self.name = jid.split('@')[0]
        self.host = jid.split('@')[1]
        self.status = ""

        self.neighbors = neighbors
        self.currentNode = currentNode

        # routing table
        self.RT = RoutingTable()
        self.RT.addNeighbor(currentNode, 0, currentNode)

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


###################################################################
# Necesary functionality method definitions
###################################################################

    async def start(self, event):
        print("start")

        # presence
        self.send_presence(pshow="available")
        await self.get_roster()
        # print("status: ", self.status)

        await self.add_Neighbors()

        # generate matrix
        self.matrix = [[999 for __ in range(9)] for _ in range(9)]
        self.positions = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8}
        self.positionsR = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

        # Update matrix accordin to routing table
        for n in self.RT.TABLE:
            self.matrix[self.positions[self.currentNode]][self.positions[n[0]]] = n[1]

        # for _ in self.matrix:
        #     print(_)

        # share initial routing table to connected 
        await self.shareRT()

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
                # print(message_Recieved)

                if message_Recieved["headers"]["algorithm"] == "flooding":
                    0

                if message_Recieved["headers"]["algorithm"] == "LST":
                    0

                if message_Recieved["headers"]["algorithm"] == "DVR":
                    # print("DVR")
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
                                    # print(f"reenvio por {hop_dir}\n", jsonEnv)

                                    # Send message
                                    self.send_message(mto=hop_dir, 
                                                    mbody=jsonEnv, 
                                                    mtype='chat')

                    if message_Recieved["type"] == "info":
                        # print("info!!!")
                        # Got a routing tabl

                        currentmat = [] # create copy to compare later
                        for n in self.matrix:
                            temp = []
                            for w in n:
                                temp.append(w)
                            currentmat.append(temp)

                        from_ = message_Recieved["headers"]["from"]
                        mat = message_Recieved["payload"]

                        # update whole matrix
                        for x in range(len(mat)):
                            for y in range(len(mat[x])):
                                if self.matrix[x][y] > mat[x][y]:
                                    # update weight
                                    self.matrix[x][y] = mat[x][y]

                        # gen recievend routing table
                        list_ = mat[self.positions[from_]]
                        # print(list_)
                        for i in range(len(list_)):
                            if list_[i] != 999:

                                if self.RT.contains(self.positionsR[i]):
                                    # update
                                    wAcc = self.RT.get_info(self.positionsR[i])[0]
                                    weight = self.RT.get_info(from_)[0] + list_[i]
                                    # print(f"{weight} < {wAcc}? {self.actual_node}, {rt[i][0]}, {from_} ")

                                    if weight < wAcc:
                                        # Actualizar si es menor
                                        self.RT.update_info(self.positionsR[i], weight, from_)
                                        # print("actualiza", rt[i][0], weight, from_)

                                else: 
                                    # add
                                    weight = self.RT.get_info(from_)[0] + list_[i]
                                    self.RT.addNeighbor(self.positionsR[i], weight, from_)


                        #update matrix
                        for n in self.RT.TABLE:
                            self.matrix[self.positions[self.currentNode]][self.positions[n[0]]] = n[1]


                        # for i in range(len(rt)):
                        #     if (self.RT.contains(rt[i][0])):
                        #         # update si es menor
                        #         wAcc = self.RT.get_info(rt[i][0])[0]
                        #         weight = self.RT.get_info(from_)[0] + rt[i][1]
                        #         # print(f"{weight} < {wAcc}? {self.actual_node}, {rt[i][0]}, {from_} ")

                        #         if weight < wAcc:
                        #             # Actualizar si es menor
                        #             self.RT.update_info(rt[i][0], weight, from_)
                        #             # print("actualiza", rt[i][0], weight, from_)

                        #     else:
                        #         # agregar
                        #         weight = self.RT.get_info(from_)[0] + rt[i][1]
                        #         self.RT.addNeighbor(rt[i][0], weight, from_)

                        # share routing table only if it changed
                        # print(currentmat)
                        # print()
                        # print(self.matrix)
                        # if currentmat != self.matrix:
                        #     await self.shareRT()

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

            # print("")
            jsonEnv = json.dumps(message, indent=4)
            # print(jsonEnv)

            # Send message
            self.send_message(mto=res[2], 
                          mbody=jsonEnv, 
                          mtype='chat')
            

    async def shareRT(self):
        # print("Sharing Routing Table")
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

            # print("cn: ", connectedNeighbors)

            payload = self.matrix

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
                # print(jsonRes)

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

        # print("menu")
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
                    # TODO

                elif (algorithm == 3):
                    print("Distance vector routing")
                    await self.DVRmessage()

            elif option_2 == 3:
                # Consulstar tabla de enrutamiento
                print(self.RT)

                for m in self.matrix:
                    print(m)

            elif option_2 == 4:
                # Quit
                print("Cerrando sesión...")
                self.send_presence(pshow="unavailable", pstatus="unavailable" )
                # await asyncio.sleep(5)
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
