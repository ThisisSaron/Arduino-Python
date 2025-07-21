import networkx as nx
from matplotlib import pyplot as plt
from collections import deque
import socket
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import random


def random_guid(exclude, lower=0, upper=100):
    while True:
        r = random.randint(lower, upper)
        if r not in exclude:
            return r

def send_command(cmd, ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # optional: avoid hanging forever
            s.connect((ip, 8888))
            s.sendall((cmd + '\n').encode())
            response = s.recv(1024).decode()
            print("ESP32 says:", response)
    except socket.timeout:
        print("⚠️ Connection timed out — is the ESP32 running and reachable?")
    except ConnectionRefusedError:
        print("❌ Connection refused — check if the ESP32 is running a TCP server.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

class Knowledge_Graph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.serial_connections = {} 

    def Add_Node(self,GUID,c,ip = 0,typ = 0):
        self.G.add_node(GUID, **{'C': c,'T': c,'src':{},"ip": ip, 'type':typ})

    def add_a_house_node(self,GUID,c,ip):
        KG.Add_Node(GUID,c,ip,0)
        a = random_guid(list(self.G.nodes),1,100)
        KG.Add_Node(a, 20, ip, "A")
        b = random_guid(list(self.G.nodes),1,100)
        KG.Add_Node(b, 50, ip, "B")
        KG.Add_Relationship(GUID,a)
        KG.Add_Relationship(GUID,b)
        if ip != 0:
            send_command("A1",ip)
            time.sleep(1)
            time.sleep(1)
            send_command("B1",ip)
            time.sleep(0.1)


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
                if self.G.nodes[sr]['ip'] != 0:
                    res.append((self.G.nodes[sr]['ip'],self.G.nodes[sr]['type']))
                return 0
            else:
                p = p - tot
                a_att['src'][sr] += tot
                a_att['T'] += tot
                self.G.nodes[sr]['T'] = 0
                if self.G.nodes[sr]['ip'] != 0:
                    res.append((self.G.nodes[sr]['ip'],self.G.nodes[sr]['type']))

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
                    if self.G.nodes[sr]['ip'] != 0:
                        res.append((self.G.nodes[sr]['ip'],self.G.nodes[sr]['type']))
                    break
                else:
                    p = p - tot
                    a_att['src'][sr] += tot
                    a_att['T'] += tot
                    self.G.nodes[sr]['T'] = 0
                    if self.G.nodes[sr]['ip'] != 0:
                        res.append((self.G.nodes[sr]['ip'],self.G.nodes[sr]['type']))
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

nodes = [(1,50)]

for el in nodes:
    KG.Add_Node(el[0],el[1])


KG.add_a_house_node(2,0,"149.84.81.192")
KG.add_a_house_node(3,0,"149.84.81.163")



edges = [(1,2),(1,3)]

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
            if guid in list(KG.G.nodes):
                raise RuntimeError("GUID already exists")
            capacity = int(simpledialog.askstring("Add Node", "Enter Capacity:"))
            ip = simpledialog.askstring("Add Node", "Enter ip (0 if Not a house):")
            #typ = simpledialog.askstring("Add Node", "Enter type (0 if N/A):")
            if ip == 0:
                KG.Add_Node(guid, capacity, ip, 0)
            else:
                KG.add_a_house_node(guid,capacity,ip)

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
                for ip, typ in res:
                    if typ == "A":
                        send_command("A0",ip)
                    elif typ == "B":
                        send_command("B0",ip)

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
