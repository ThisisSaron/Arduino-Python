import networkx as nx
from matplotlib import pyplot as plt
from collections import deque
import serial
import time
import tkinter as tk
from tkinter import simpledialog, messagebox

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


KG.add_a_house_node(4,20,5,"A")
KG.add_a_house_node(6,20,3,"A")
time.sleep(1)
time.sleep(1)
time.sleep(1)
KG.add_a_house_node(7,50,3,"B")
KG.add_a_house_node(5,50,5,"B")




edges = [(1,3),(1,2),(2,4),(2,5),(3,6),(3,7)]

for a,b in edges:
    KG.Add_Relationship(a,b)

#KG.request(3,250)
#KG.request(1,600)

class KnowledgeGraphApp:
    def __init__(self, master):
        self.master = master
        master.title("Knowledge Graph")

        # Buttons
        tk.Button(master, text="Add Node", command=self.add_node).pack()
        tk.Button(master, text="Add Edge", command=self.add_edge).pack()
        tk.Button(master, text="Delete Node", command=self.delete_node).pack()
        tk.Button(master, text="Delete Edge", command=self.delete_edge).pack()
        tk.Button(master, text="Request Power", command=self.request_power).pack()
        tk.Button(master, text="Show Graph", command=self.show_graph).pack()

    def add_node(self):
        try:
            guid = int(simpledialog.askstring("Add Node", "Enter GUID:"))
            capacity = int(simpledialog.askstring("Add Node", "Enter Capacity:"))
            port = int(simpledialog.askstring("Add Node", "Enter port (0 if N/A):"))
            typ = simpledialog.askstring("Add Node", "Enter type (0 if N/A):")

            KG.Add_Node(guid, capacity, port, typ)

            if port != 0:
                arduino = serial.Serial(port=f'COM{port}', baudrate=115200, timeout=0.1)
                time.sleep(2)  # Wait for Arduino to reset
                if typ == "A":
                    arduino.write(b'A1')  # Set LED ON
                elif typ == "B":
                    arduino.write(b'B1')
                time.sleep(0.1)
                print(arduino.readline().decode().strip())
                arduino.close()

            self.show_graph()

        except Exception as e:
            messagebox.showerror("Invalid input", f"Error: {e}")

    def add_edge(self):
        try:
            top = int(simpledialog.askstring("Add Edge", "Enter Top Node GUID:"))
            source = int(simpledialog.askstring("Add Edge", "Enter Source Node GUID:"))
            KG.Add_Relationship(top, source)
            self.show_graph()
        except Exception:
            messagebox.showerror("Invalid input", "Please enter valid integers.")

    def delete_node(self):
        try:
            guid = int(simpledialog.askstring("Delete Node", "Enter GUID to delete:"))
            KG.delete_node(guid)
            self.show_graph()
        except Exception:
            messagebox.showerror("Invalid input", "Please enter a valid GUID.")

    def delete_edge(self):
        try:
            top = int(simpledialog.askstring("Delete Edge", "Enter Top Node GUID:"))
            source = int(simpledialog.askstring("Delete Edge", "Enter Source Node GUID:"))
            KG.delete_edge(top, source)
            self.show_graph()
        except Exception:
            messagebox.showerror("Invalid input", "Please enter valid GUIDs.")

    def request_power(self):
        try:
            a = int(simpledialog.askstring("Request Power", "Enter GUID:"))
            p = int(simpledialog.askstring("Request Power", "Enter Power Needed:"))
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
                self.show_graph()
        except Exception:
            messagebox.showerror("Invalid input", "Please enter valid values.")

    def show_graph(self):
        plt.clf()

        pos = nx.spring_layout(KG.G, seed=42)

        # Draw nodes and GUID labels
        nx.draw(KG.G, pos, with_labels=True, node_color='lightblue',
                node_size=2000, font_size=10, font_weight='bold', arrows=True)

        # Draw metadata just below the node label (slightly offset)
        for node, (x, y) in pos.items():
            attrs = KG.G.nodes[node]
            info = "\n".join([f"{k}: {v}" for k, v in attrs.items()])
            plt.text(x, y - 0.08, info, fontsize=8, ha='center', va='top')

        plt.title("Knowledge Graph")
        plt.tight_layout()
        plt.margins(y=0.2) # add extra margin at bottom to avoid cutoff
        plt.show()


# Main setup
if __name__ == "__main__":
    root = tk.Tk()
    app = KnowledgeGraphApp(root)
    root.mainloop()
