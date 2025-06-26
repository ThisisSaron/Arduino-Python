import networkx as nx
from matplotlib import pyplot as plt
from collections import deque

class Knowledge_Graph:
    def __init__(self):
        self.G = nx.DiGraph()

    def Add_Node(self,GUID,n):
        self.G.add_node(GUID, **{'N': n,'T': n,'src':{}})

    def Add_Relationship(self,a,b):
        if (b,a) not in self.G.edges:
            a_att = self.G.nodes[a] #ATTRIBUTES OF A
            a_att['src'][b] = 0
            self.G.add_edge(b,a)

    def request(self,a,p):
        a_att = self.G.nodes[a]
        src = a_att['src']
        og = p
        for sr in src:
            tot = self.G.nodes[sr]['T']
            if tot == 0:
                continue
            elif tot - p >= 0:
                self.G.nodes[sr]['T'] -= p
                a_att['src'][sr] += p
                a_att['T'] += p
                p = 0
                break
            else:
                p = p - tot
                a_att['src'][sr] += tot
                a_att['T'] += tot
                self.G.nodes[sr]['T'] = 0
        print('Amount Transferred:',og-p)


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

edges = [(3,5),(3,4),(1,2),(1,3)]

for a,b in edges:
    KG.Add_Relationship(a,b)

KG.request(3,250)
KG.request(1,600)

while True:
    print("1. ADD NODE   2. ADD AN EDGE  3. SHOW KNOWLEDGE GRAPH  4. DELETE A NODE 5. DELETE AN EDGE" \
            "  6. Request power 7. QUIT")
    ent = input(' - ')

    if ent == "7":
        break
    elif ent == "1":
        GUID = int(input('Enter the GUID: '))
        c = int(input("Enter the Capacity of the node: "))
        KG.Add_Node(GUID,c)

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
        KG.request(a,p)
        a_att = KG.G.nodes[a]
        src = a_att['src']
        print(src)
