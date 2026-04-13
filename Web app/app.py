import networkx as nx
from collections import deque
import socket
import time
import random
from flask import Flask, render_template, jsonify, request
import json

# ========== Knowledge Graph Core Logic ==========
def random_guid(exclude, lower=0, upper=100):
    while True:
        r = random.randint(lower, upper)
        if r not in exclude:
            return r

def send_command(cmd, ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, 8888))
            s.sendall((cmd + '\n').encode())
            response = s.recv(1024).decode()
            print(f"✓ ESP32 {ip} says: {response}")
            return response
    except socket.timeout:
        print(f"⚠️ Connection timed out — is the ESP32 {ip} running and reachable?")
        return None
    except ConnectionRefusedError:
        print(f"❌ Connection refused — check if the ESP32 {ip} is running a TCP server.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

class Knowledge_Graph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.serial_connections = {} 

    def Add_Node(self, GUID, c, ip=0, typ=0):
        self.G.add_node(GUID, **{'C': c, 'T': c, 'src': {}, "ip": ip, 'type': typ})

    def add_a_house_node(self, GUID, c, ip):
        self.Add_Node(GUID, c, ip, 0)
        # fan or light ?
        a = random_guid(list(self.G.nodes), 1, 100)
        self.Add_Node(a, 20, ip, "A")
        # fan or light ?
        b = random_guid(list(self.G.nodes), 1, 100)
        self.Add_Node(b, 50, ip, "B")
        # solar panel
        c = random_guid(list(self.G.nodes), 1, 100)
        self.Add_Node(b, 50, ip, "C")
        self.Add_Relationship(GUID, a)
        self.Add_Relationship(GUID, b)
        self.Add_Relationship(GUID, c)
        if ip != 0:
            send_command("A1", ip)
            time.sleep(1)
            send_command("B1", ip)
            time.sleep(0.1)
            send_command("C1", ip)
            time.sleep(0.1)

    def Add_Relationship(self, a, b):
        if (a, b) not in self.G.edges:
            b_att = self.G.nodes[b]
            b_att['src'][a] = 0
            self.G.add_edge(a, b)

    def request_rec(self, a, p, res):
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
                    res.append((self.G.nodes[sr]['ip'], self.G.nodes[sr]['type']))
                return 0
            else:
                p = p - tot
                a_att['src'][sr] += tot
                a_att['T'] += tot
                self.G.nodes[sr]['T'] = 0
                if self.G.nodes[sr]['ip'] != 0:
                    res.append((self.G.nodes[sr]['ip'], self.G.nodes[sr]['type']))

        if p > 0:
            for sr in src:
                self.request_rec(sr, p, res)
                tot = self.G.nodes[sr]['T']
                if tot == 0:
                    continue
                elif tot - p >= 0:
                    self.G.nodes[sr]['T'] -= p
                    a_att['src'][sr] += p
                    a_att['T'] += p
                    p = 0
                    if self.G.nodes[sr]['ip'] != 0:
                        res.append((self.G.nodes[sr]['ip'], self.G.nodes[sr]['type']))
                    break
                else:
                    p = p - tot
                    a_att['src'][sr] += tot
                    a_att['T'] += tot
                    self.G.nodes[sr]['T'] = 0
                    if self.G.nodes[sr]['ip'] != 0:
                        res.append((self.G.nodes[sr]['ip'], self.G.nodes[sr]['type']))
        else:
            return

    def request(self, a, p):
        res = []
        n = self.request_rec(a, p, res)
        return res

    def delete_node(self, a):
        """
        Delete a node and its edges. When a node is deleted (modeling an outage):
        - Direct children of the deleted node become new top nodes of independent grids
        - They can no longer receive power from above (no parent to pass power up to)
        - They maintain their current resources and power everything below them
        - The deleted node's parents must reallocate power to other children
        """
        # Get node attributes before deletion
        node_sources = self.G.nodes[a]['src']  # Parents of this node
        children = list(self.G.successors(a))  # Direct children of this node
        
        # Step 1: Children become independent top nodes
        # Remove the deleted node from their source dictionaries
        for child in children:
            if a in self.G.nodes[child]['src']:
                # Remove power tracking from this parent
                power_lost = self.G.nodes[child]['src'][a]
                del self.G.nodes[child]['src'][a]
                # Child now operates independently with remaining power
                # No need to adjust T - they keep what they have
        
        # Step 2: Return power to the deleted node's parents
        # Since the child nodes are now independent, power from parents
        # that was allocated to children through this node gets returned
        for parent in node_sources:
            power_to_return = node_sources[parent]
            if parent in self.G.nodes:
                self.G.nodes[parent]['T'] += power_to_return
        
        # Step 3: Remove all edges involving this node
        # Remove parents' sources
        for parent in list(node_sources.keys()):
            self.G.remove_edge(parent, a)
        
        # Remove child edges
        for child in children:
            self.G.remove_edge(a, child)
        
        # Step 4: Remove the node from the graph
        self.G.remove_node(a)

    def delete_edge(self, a, b):
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

        self.G.remove_edge(a, b)

    def get_graph_data(self):
        """Convert graph to JSON-serializable format"""
        nodes = []
        edges = []
        
        for node_id in self.G.nodes():
            attrs = self.G.nodes[node_id]
            nodes.append({
                'id': str(node_id),
                'label': f"Node {node_id}",
                'title': f"ID: {node_id}<br>Capacity: {attrs['C']}<br>Current: {attrs['T']}<br>Type: {attrs.get('type', 'N/A')}<br>IP: {attrs.get('ip', '0')}",
                'capacity': attrs['C'],
                'current': attrs['T'],
                'ip': attrs.get('ip', '0'),
                'type': str(attrs.get('type', '0'))
            })
        
        for src, dst in self.G.edges():
            edges.append({
                'from': str(src),
                'to': str(dst)
            })
        
        return {'nodes': nodes, 'edges': edges}

# ========== Flask App Setup ==========
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Remove SocketIO for PythonAnywhere compatibility (free tier doesn't support WebSockets)
# socketio = SocketIO(app, cors_allowed_origins="*")

# Add CORS headers manually for PythonAnywhere
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Global knowledge graph instance
KG = Knowledge_Graph()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/graph', methods=['GET'])
def get_graph():
    return jsonify(KG.get_graph_data())

@app.route('/api/nodes', methods=['POST'])
def add_node():
    data = request.json
    try:
        guid = int(data['guid'])
        capacity = int(data['capacity'])
        ip = data.get('ip', '0')
        
        if guid in list(KG.G.nodes):
            return jsonify({'error': 'GUID already exists'}), 400
        
        if ip == '0' or ip == 0:
            KG.Add_Node(guid, capacity, 0, 0)
        else:
            KG.add_a_house_node(guid, capacity, ip)
        
        # Remove socketio.emit - will use polling instead
        # socketio.emit('graph_updated', KG.get_graph_data(), broadcast=True)
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/edges', methods=['POST'])
def add_edge():
    data = request.json
    try:
        a = int(data['from'])
        b = int(data['to'])
        
        if a not in KG.G.nodes or b not in KG.G.nodes:
            return jsonify({'error': 'One or both nodes do not exist'}), 400
        
        KG.Add_Relationship(a, b)
        # Remove socketio.emit - will use polling instead
        # socketio.emit('graph_updated', KG.get_graph_data(), broadcast=True)
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/nodes/<int:guid>', methods=['DELETE'])
def delete_node(guid):
    try:
        if guid not in KG.G.nodes:
            return jsonify({'error': 'Node does not exist'}), 404
        
        KG.delete_node(guid)
        # Remove socketio.emit - will use polling instead
        # socketio.emit('graph_updated', KG.get_graph_data(), broadcast=True)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/edges', methods=['DELETE'])
def delete_edge():
    data = request.json
    try:
        a = int(data['from'])
        b = int(data['to'])
        
        if (a, b) not in KG.G.edges:
            return jsonify({'error': 'Edge does not exist'}), 404
        
        KG.delete_edge(a, b)
        # Remove socketio.emit - will use polling instead
        # socketio.emit('graph_updated', KG.get_graph_data(), broadcast=True)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/request-power', methods=['POST'])
def request_power():
    data = request.json
    try:
        a = int(data['node_id'])
        p = int(data['power'])
        
        if a not in KG.G.nodes:
            return jsonify({'error': 'Node does not exist'}), 404
        
        res = KG.request(a, p)
        
        # Send commands to ESP32 devices
        commands_sent = []
        for ip, typ in res:
            if typ == "A":
                result = send_command("A0", ip)
                commands_sent.append({'ip': ip, 'command': 'A0', 'result': result})
            elif typ == "B":
                result = send_command("B0", ip)
                commands_sent.append({'ip': ip, 'command': 'B0', 'result': result})
            elif typ == "C":
                result = send_command("C0", ip)
                commands_sent.append({'ip': ip, 'command': 'C0', 'result': result})
        
        # Remove socketio.emit - will use polling instead
        # socketio.emit('graph_updated', KG.get_graph_data(), broadcast=True)
        return jsonify({'status': 'success', 'power_transferred': p, 'commands_sent': commands_sent}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/scenarios/<scenario>', methods=['POST'])
def load_scenario(scenario):
    try:
        # Clear current graph
        KG.G.clear()
        
        if scenario.upper() == 'A':
            nodes = [(1, 20), (2, 20), (3, 20), (4, 20)]
            for node in nodes:
                KG.Add_Node(node[0], node[1])
            edges = [(1, 2), (1, 3), (1, 4)]
            for a, b in edges:
                KG.Add_Relationship(a, b)
        
        elif scenario.upper() == 'B':
            nodes = [(1, 20), (2, 20), (3, 20), (4, 20)]
            for node in nodes:
                KG.Add_Node(node[0], node[1])
            edges = [(1, 2), (1, 3), (3, 4)]
            for a, b in edges:
                KG.Add_Relationship(a, b)
        
        elif scenario.upper() == 'C':
            nodes = [(1, 20), (2, 20), (3, 20), (4, 20)]
            for node in nodes:
                KG.Add_Node(node[0], node[1])
            edges = [(1, 2), (2, 3), (2, 4)]
            for a, b in edges:
                KG.Add_Relationship(a, b)
        
        elif scenario.upper() == 'D':
            nodes = [(1, 20), (2, 20), (3, 20), (4, 20)]
            for node in nodes:
                KG.Add_Node(node[0], node[1])
            edges = [(1, 2), (2, 3), (3, 4)]
            for a, b in edges:
                KG.Add_Relationship(a, b)
        
        elif scenario.upper() == 'E':
            nodes = [(1, 50)]
            for el in nodes:
                KG.Add_Node(el[0], el[1])
            # Note: Update these IPs to your actual ESP32 addresses
            KG.add_a_house_node(2, 0, "149.84.81.192")
            KG.add_a_house_node(3, 0, "149.84.81.163")
            edges = [(1, 2), (1, 3)]
            for a, b in edges:
                KG.Add_Relationship(a, b)
        
        else:
            return jsonify({'error': 'Unknown scenario'}), 400
        
        # Remove socketio.emit - will use polling instead
        # socketio.emit('graph_updated', KG.get_graph_data(), broadcast=True)
        return jsonify({'status': 'success', 'scenario': scenario}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Remove SocketIO event handlers - using polling instead
# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     emit('graph_updated', KG.get_graph_data())

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

if __name__ == '__main__':
    # Remove socketio.run - using regular Flask for PythonAnywhere compatibility
    app.run(host='0.0.0.0', port=5000, debug=False)
