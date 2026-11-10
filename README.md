# Industrial IoT Camera Sensor Network Simulator

A beginner-friendly Streamlit website prototype for simulating energy use in wireless camera sensor networks.

## 1. Install software on Windows
1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/
2. During installation, tick **Add python.exe to PATH**.
3. Install Visual Studio Code from https://code.visualstudio.com/
4. Open VS Code and install the official **Python** extension by Microsoft.

## 2. Open the project
1. Extract the ZIP file.
2. In VS Code, select **File → Open Folder** and choose `industrial_iot_camera_sensor_simulator`.
3. Open **Terminal → New Terminal**.

## 3. Create an environment and install libraries
Run these commands in the VS Code terminal, one at a time:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt in VS Code and run:
```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

## 4. Start the website
```powershell
python -m streamlit run app.py
```
A local address appears in the terminal, normally `http://localhost:8501`. Open it in your browser.

## 5. Test it
1. Keep the default settings and click **Run simulation**.
2. Check that the deployment map, alive-node chart, and residual-energy chart appear.
3. Change the number of nodes from 40 to 80 and run again.
4. Change the packet size and cluster-head percentage and compare results.
5. Download both CSV files and confirm that they contain node-level and round-level data.
6. Keep the same random seed when you want a reproducible comparison.

## Important limitations
This is a starter simulation, not a hardware-ready network or an exact reproduction of any specific paper. It uses synthetic node positions and an illustrative radio-energy model. Camera image capture, realistic wireless protocols, packet loss, latency, and advanced optimization algorithms can be added as later stages.
