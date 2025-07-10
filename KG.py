import networkx as nx
from matplotlib import pyplot as plt
from collections import deque
import serial
import time

class Knowledge_Graph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.serial_connections = {} 

    def Add_Node(self,GUID,c,port = 0,typ = 0):
        self.G.add_node(GUID, **{'C': c,'T': c,'src':{},'port': port, 'type':typ})

    def add_a_house_node(self,GUID,c,port,typ):
        self.Add_Node(GUID, c, port, typ)
        if port != 0:
            if port not in self.serial_connections:
                try:
                    self.serial_connections[port] = serial.Serial(port=f'COM{port}', baudrate=115200, timeout=0.1)
                    time.sleep(2)
                except serial.SerialException as e:
                    print(f"Could not open COM{port}: {e}")
                    return

            arduino = self.serial_connections[port]
            if typ == "A":
                arduino.write(b'A1')
            elif typ == "B":
                arduino.write(b'B1')
            time.sleep(0.1)
            #print(arduino.readline().decode().strip())

    def turn_off(self,port,typ):
        if port != 0:
            if port not in self.serial_connections:
                try:
                    self.serial_connections[port] = serial.Serial(port=f'COM{port}', baudrate=115200, timeout=0.1)
                    time.sleep(2)
                except serial.SerialException as e:
                    print(f"Could not open COM{port}: {e}")
                    return

            arduino = self.serial_connections[port]
            if typ == "A":
                arduino.write(b'A0')
            elif typ == "B":
                arduino.write(b'B0')
            time.sleep(0.1)
            #print(arduino.readline().decode().strip())

    def Add_Relationship(self,a,b):
        if (b,a) not in self.G.edges:
            a_att = self.G.nodes[a] #ATTRIBUTES OF A
            a_att['src'][b] = 0
            self.G.add_edge(b,a)

    def request_rec(self,a,p,res):
        a_att = self.G.nodes[a]
        src = a_att['src']
        if len(src) == 0:
            return p
        for sr in src:
            tot = self.G.nodes[sr]['T']
            if tot == 0:
                continue
            elif tot - p >= 0:
                self.G.nodes[sr]['T'] -= p
                a_att['src'][sr] += p
                a_att['T'] += p
                p = 0
                if self.G.nodes[sr]['port'] != 0:
                    res.append((self.G.nodes[sr]['port'],self.G.nodes[sr]['type']))
                return 0
            else:
                p = p - tot
                a_att['src'][sr] += tot
                a_att['T'] += tot
                self.G.nodes[sr]['T'] = 0
                if self.G.nodes[sr]['port'] != 0:
                    res.append((self.G.nodes[sr]['port'],self.G.nodes[sr]['type']))

        if p > 0 :
            for sr in src:
                print(p)
                self.request_rec(sr,p,res)
                tot = self.G.nodes[sr]['T']
                if tot == 0:
                    continue
                elif tot - p >= 0:
                    self.G.nodes[sr]['T'] -= p
                    a_att['src'][sr] += p
                    a_att['T'] += p
                    p = 0
                    if self.G.nodes[sr]['port'] != 0:
                        res.append((self.G.nodes[sr]['port'],self.G.nodes[sr]['type']))
                    break
                else:
                    p = p - tot
                    a_att['src'][sr] += tot
                    a_att['T'] += tot
                    self.G.nodes[sr]['T'] = 0
                    if self.G.nodes[sr]['port'] != 0:
                        res.append((self.G.nodes[sr]['port'],self.G.nodes[sr]['type']))
        else:
            return
    
    def request(self,a,p):
        res = []
        n = self.request_rec(a,p,res)
        #print('Amount Transferred:',p - n)
        print(res)
        return res


    def delete_node(self,a):
        srcs = self.G.nodes[a]['src']
        for sr in srcs:
            self.G.nodes[sr]['T'] += srcs[sr]

        lst = [a]
        while lst:
            t = lst.pop()
            dec = self.G.successors(t)
            for el in dec:
                srcs = self.G.nodes[el]['src']  
                if srcs[t] == 0:
                    del srcs[t]
                    continue
                self.G.nodes[el]['T'] -= srcs[t] 
                del srcs[t]

        dec = deque(self.G.successors(a))
        while dec:
            el = dec.popleft()
            if self.G.nodes[el]['T'] < 0:
                needed = -self.G.nodes[el]['T']
                dec2 = self.G.successors(el)
                lst = []
                for t in dec2:
                    lst.append((self.G.nodes[t]['src'][el],t))
                print(lst)
                print(self.G.nodes[1]['src'][el])
                elem = max(lst)[1]
                print(elem)
                self.G.nodes[elem]['T'] -= needed
                self.G.nodes[elem]['src'][el] -= needed
                self.G.nodes[el]['T'] += needed
                if self.G.nodes[elem]['T'] < 0:
                    dec.append(elem)

        self.G.remove_node(a)

    def delete_edge(self,a,b):
        lst = [b]
        while lst:
            t = lst.pop()
            dec = self.G.successors(t)
            for el in dec:
                srcs = self.G.nodes[el]['src']  
                if srcs[t] == 0:
                    del srcs[t]
                    continue
                lst.append(el)
                self.G.nodes[el]['T'] -= srcs[t] 
                if t in srcs:
                    del srcs[t]

        self.G.remove_edge(b,a)



KG = Knowledge_Graph()

nodes = [(5,200),(4,100),(3,300),(2,200),(1,50)]

for el in nodes:
    KG.Add_Node(el[0],el[1])



KG.add_a_house_node(6,20,5,"A")
KG.add_a_house_node(8,20,3,"A")
time.sleep(1)
time.sleep(1)
time.sleep(1)
KG.add_a_house_node(9,50,3,"B")
KG.add_a_house_node(7,50,5,"B")




edges = [(3,5),(3,4),(1,2),(1,3),(4,6),(4,7),(5,8),(5,9)]

for a,b in edges:
    KG.Add_Relationship(a,b)

#KG.request(3,250)
#KG.request(1,600)

while True:
    print("1. ADD NODE   2. ADD AN EDGE  3. SHOW KNOWLEDGE GRAPH  4. DELETE A NODE 5. DELETE AN EDGE" \
            "  6. Request power 7. QUIT")
    ent = input(' - ')

    if ent == "7":
        break
    elif ent == "1":
        GUID = int(input('Enter the GUID: '))
        c = int(input("Enter the Capacity of the node: "))
        port = int(input("Enter port (0 if N/A): "))
        typ = input("Enter type (0 if N/A): ")
        KG.Add_Node(GUID,c,port,typ)
        if port != 0:
            arduino = serial.Serial(port=f'COM{port}', baudrate=115200, timeout=0.1)
            time.sleep(2)  # Wait for Arduino to reset
            if typ == "A":
                arduino.write(b'A1')  # Set LED ON
            if typ == "B":
                arduino.write(b'B1')
            time.sleep(0.1)
            print(arduino.readline().decode().strip())

            arduino.close()

    elif ent == '2':
        a = int(input("Enter the GUID of the Top node: "))
        b = int(input("Enter the GUID of the Source node: "))
        KG.Add_Relationship(a,b)

    elif ent == '3':
        pos = nx.spring_layout(KG.G)  # Layout for positioning
        labels = {
            node: "\n".join([f"{k}: {v}" for k, v in attrs.items()])
            for node, attrs in KG.G.nodes(data=True)
        }
        nx.draw(KG.G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10,font_weight = 'bold')
        nx.draw_networkx_labels(KG.G, pos, labels=labels, font_size=8,horizontalalignment= 'left',verticalalignment= 'top',font_weight='bold')

        plt.title("Knowledge Graph")
        plt.show()

    elif ent == '4':
        GUID = int(input('Enter the GUID of the node: '))
        KG.delete_node(GUID)

    elif ent == '5':
        a = int(input('Enter the GUID of the top node: '))
        b = int(input('Enter the GUID of the source node: '))

        KG.delete_edge(a,b)

    elif ent == '6':
        a = int(input('Enter the GUID: '))
        p = int(input('Enter how much power is needed: '))
    
        a_att = KG.G.nodes[a]
        src = a_att['src']
        print(src)

        res = KG.request(a,p)
        a_att = KG.G.nodes[a]
        src = a_att['src']
        print(src)
        if res:
            for por, typ in res:
                KG.turn_off(por,typ)
                time.sleep(1)
                time.sleep(1)

for conn in KG.serial_connections.values():
    conn.close()
