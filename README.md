# Smart House Knowledge Graph Network

## Overview
This project is a real‑world demonstration of a **smart house network** built using a **knowledge graph–based control system** integrated with **Arduino hardware**. The system models different components of a smart house (e.g., power‑consuming devices and connections between houses) as nodes in a knowledge graph and uses that model to dynamically control hardware behavior based on power requirements and network relationships.

The project was designed to demonstrate how **network grids**, **IoT systems**, and **software abstractions** can work together to manage distributed physical systems.

---

## Key Features
- Knowledge graph representation of smart house components and their relationships
- Dynamic power‑based decision making using graph relationships
- Real‑time communication between a Python control system and Arduino hardware
- Demonstration of interconnected houses forming a network grid

---

## Architecture
**High-level flow:**
1. Smart house components (e.g., lights, fans) and connections are modeled as nodes and edges in a Python-based knowledge graph
2. The knowledge graph evaluates power requirements and network relationships
3. Control signals are sent from Python to Arduino boards via **serial or network communication**
4. Arduino hardware activates or deactivates components based on received commands

```
[ Knowledge Graph (Python) ]  <-->  [ Arduino Controller ]  -->  [ Smart House Components ]
```

---

## Technologies Used
- **Python** – knowledge graph implementation and control logic
- **Arduino (C/C++)** – hardware control and sensor/actuator management
- **Serial / Network Communication** – configurable communication between software and hardware (serial or network-based)
- **Tkinter** – visualization of the network grid and component states

---


## How It Works (Simplified)
- Each smart house component is represented as a node in the knowledge graph
- Relationships encode power usage, dependencies, and network connections
- When power conditions or network states change, the graph is evaluated
- Control commands are generated and transmitted to Arduino boards
- Arduino devices actuate hardware components accordingly

---

## Demo Use Case
- Multiple smart houses connected as a network grid
- Components such as **lights and fans** are selectively enabled or disabled
- System demonstrates distributed decision-making using software abstractions rather than hard-coded rules

---

## What This Project Demonstrates
- Knowledge graphs applied to real‑world systems
- Software‑hardware integration
- IoT communication patterns
- Modeling complex systems using graph abstractions
- Practical networking and systems thinking

---

## License
This project was developed for an academic demonstration. Please contact the author before reuse or modification.

