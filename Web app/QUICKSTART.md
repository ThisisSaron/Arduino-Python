# Quick Start Guide - Local Testing

Run the Knowledge Graph web application locally before deploying to PythonAnywhere.

## Prerequisites

- Python 3.8+ installed
- `pip` package manager

## Setup (First Time)

1. **Navigate to project directory:**
   ```bash
   cd ~/Projects/Arduino-Python
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Socket.IO server started
```

## Access the Web Interface

Open your browser and go to:
```
http://localhost:5000
```

You should see the Knowledge Graph dashboard with:
- Interactive graph visualization
- Node management controls
- Edge (connection) controls
- Power request system
- Scenario loading buttons

## Features to Test

### 1. Load a Scenario
- Click **Scenario A** to populate the graph with sample nodes and edges
- Watch the graph render in real-time

### 2. Add a Node
- Enter Node ID: `10`
- Enter Capacity: `25`
- IP: `0` (not a house node)
- Click **Add Node**
- See the new node appear in the graph

### 3. Add an Edge
- Click **Scenario A** first to have nodes
- From Node ID: `1`
- To Node ID: `2`
- Click **Add Edge**
- See the connection appear in the graph

### 4. Request Power
- With Scenario A loaded:
- Node ID: `2`
- Power Needed: `10`
- Click **Request Power**
- Watch the power transfer through the graph

### 5. Delete a Node
- Node ID to Delete: `4`
- Click **Delete Node**
- Node disappears from the graph and relationships are recalculated

### 6. Scenario E (ESP32 Integration)
- Requires actual ESP32 devices running on the IPs specified
- You can modify the IPs in the code to test with your devices
- Commands A0, B0 will be sent to your ESP32s

## Keyboard & Mouse Shortcuts

- **Scroll:** Zoom in/out of the graph
- **Drag nodes:** Reposition them for better visibility
- **Click node:** View detailed information
- **Double-click:** Focus on a node

## Troubleshooting Local Issues

### Module not found errors
```bash
pip install -r requirements.txt
```

### Port already in use
Change port in `app.py` line (last line):
```python
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### WebSocket connection fails
- Ensure no firewall is blocking port 5000
- Try using localhost instead of 0.0.0.0 for binding

### Graph visualization doesn't show
- Check browser console (F12) for JavaScript errors
- Ensure internet connection (loads vis.js from CDN)
- Clear browser cache

## Stopping the Application

Press `Ctrl+C` in your terminal

## Project Structure

```
Arduino-Python/
├── app.py                 # Flask application (runs locally on port 5000)
├── KG_wifi.py            # Original knowledge graph code
├── KG.py                 # Alternative serial version
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── QUICKSTART.md         # This file
├── DEPLOYMENT.md         # PythonAnywhere setup guide
└── README.md             # Project overview
```

## Notes

- The web version preserves all the core knowledge graph logic from `KG_wifi.py`
- Local testing uses in-memory graph (data lost when you stop the app)
- For persistent data, consider adding a database

---

**Happy coding!** 🚀
