import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Industrial IoT Camera Sensor Simulator", page_icon="📡", layout="wide")

st.title("📡 Energy-Efficient Wireless Camera Sensor Networks")
st.caption("Industrial IoT • Educational software simulation • No physical camera hardware required")

with st.sidebar:
    st.header("Simulation settings")
    n_nodes = st.slider("Number of camera sensor nodes", 10, 150, 40, 5)
    rounds = st.slider("Simulation rounds", 10, 300, 100, 10)
    area = st.selectbox("Deployment area (m × m)", [100, 250, 500], index=1)
    initial_energy = st.select_slider("Initial energy per node (J)", options=[0.25, 0.5, 1.0, 2.0], value=0.5)
    packet_bits = st.select_slider("Packet size (bits)", options=[2000, 4000, 8000, 16000], value=4000)
    cluster_percent = st.slider("Cluster-head percentage", 5, 25, 10, 1)
    seed = st.number_input("Random seed", min_value=0, max_value=99999, value=42, step=1)
    run = st.button("▶ Run simulation", type="primary", use_container_width=True)

st.markdown("""
This prototype places camera sensor nodes in a simulated industrial area, assigns cluster heads,
and estimates energy use as nodes send image-metadata packets toward a sink/gateway. It compares
a **cluster-based strategy** with a **direct-transmission baseline**.
""")

def simulate(n, rounds, area, e0, packet_bits, cluster_percent, seed):
    rng = np.random.default_rng(int(seed))
    xy = rng.uniform(0, area, size=(n, 2))
    sink = np.array([area / 2, area + 0.08 * area])
    energy_cluster = np.full(n, e0, dtype=float)
    energy_direct = np.full(n, e0, dtype=float)
    alive_cluster, alive_direct = [], []
    residual_cluster, residual_direct = [], []
    delivered_cluster, delivered_direct = [], []

    # Simplified radio-energy model (illustrative, not hardware-calibrated).
    E_ELEC = 50e-9       # J/bit
    E_AMP = 100e-12      # J/bit/m^2
    E_DA = 5e-9          # J/bit
    ch_count = max(1, int(round(n * cluster_percent / 100)))

    for r in range(rounds):
        # Rotate cluster heads among nodes with remaining energy.
        alive_idx = np.flatnonzero(energy_cluster > 0)
        if len(alive_idx):
            ch_count_now = min(ch_count, len(alive_idx))
            # Prefer high residual energy; random jitter prevents permanent ties.
            jitter = rng.random(len(alive_idx)) * 0.03 * e0
            ch_idx = alive_idx[np.argsort(energy_cluster[alive_idx] + jitter)[-ch_count_now:]]
            for i in alive_idx:
                if energy_cluster[i] <= 0:
                    continue
                if i in ch_idx:
                    members = [j for j in alive_idx if j != i and j not in ch_idx]
                    assigned = [j for j in members if np.argmin(np.linalg.norm(xy[j] - xy[ch_idx], axis=1)) == np.where(ch_idx == i)[0][0]]
                    # CH receives packets from assigned members and sends aggregate packet to sink.
                    rx_cost = len(assigned) * packet_bits * E_ELEC
                    tx_cost = packet_bits * (E_ELEC + E_AMP * np.sum((xy[i] - sink) ** 2))
                    aggregate_cost = max(1, len(assigned)) * packet_bits * E_DA
                    energy_cluster[i] -= rx_cost + tx_cost + aggregate_cost
                else:
                    nearest_ch = ch_idx[np.argmin(np.linalg.norm(xy[ch_idx] - xy[i], axis=1))]
                    d2 = float(np.sum((xy[i] - xy[nearest_ch]) ** 2))
                    energy_cluster[i] -= packet_bits * (E_ELEC + E_AMP * d2)
            energy_cluster = np.maximum(energy_cluster, 0)

        alive_idx_d = np.flatnonzero(energy_direct > 0)
        for i in alive_idx_d:
            d2 = float(np.sum((xy[i] - sink) ** 2))
            energy_direct[i] -= packet_bits * (E_ELEC + E_AMP * d2)
        energy_direct = np.maximum(energy_direct, 0)

        alive_cluster.append(int(np.sum(energy_cluster > 0)))
        alive_direct.append(int(np.sum(energy_direct > 0)))
        residual_cluster.append(float(np.sum(energy_cluster)))
        residual_direct.append(float(np.sum(energy_direct)))
        delivered_cluster.append(int(np.sum(energy_cluster > 0) * (r + 1)))
        delivered_direct.append(int(np.sum(energy_direct > 0) * (r + 1)))

    nodes = pd.DataFrame({
        "Node ID": np.arange(1, n + 1),
        "X (m)": xy[:, 0].round(2),
        "Y (m)": xy[:, 1].round(2),
        "Initial energy (J)": e0,
        "Final energy: cluster (J)": energy_cluster.round(5),
        "Final energy: direct (J)": energy_direct.round(5),
        "Cluster strategy alive": energy_cluster > 0,
        "Direct strategy alive": energy_direct > 0,
    })
    history = pd.DataFrame({
        "Round": np.arange(1, rounds + 1),
        "Alive nodes — cluster": alive_cluster,
        "Alive nodes — direct": alive_direct,
        "Residual energy — cluster (J)": residual_cluster,
        "Residual energy — direct (J)": residual_direct,
    })
    return xy, sink, nodes, history

if run or "sim_data" not in st.session_state:
    st.session_state.sim_data = simulate(n_nodes, rounds, area, initial_energy, packet_bits, cluster_percent, seed)

xy, sink, nodes, history = st.session_state.sim_data

alive_c = int(history["Alive nodes — cluster"].iloc[-1])
alive_d = int(history["Alive nodes — direct"].iloc[-1])
energy_c = float(history["Residual energy — cluster (J)"].iloc[-1])
energy_d = float(history["Residual energy — direct (J)"].iloc[-1])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Camera nodes", n_nodes)
m2.metric("Alive after final round", f"{alive_c} / {n_nodes}", delta=f"{alive_c-alive_d} vs direct")
m3.metric("Residual energy (cluster)", f"{energy_c:.3f} J")
m4.metric("Residual energy (direct)", f"{energy_d:.3f} J")

left, right = st.columns(2)
with left:
    st.subheader("Simulated industrial deployment")
    fig, ax = plt.subplots()
    ax.scatter(xy[:, 0], xy[:, 1], marker="o", label="Camera sensor nodes")
    ax.scatter([sink[0]], [sink[1]], marker="*", s=220, label="Sink / gateway")
    for idx, (x, y) in enumerate(xy):
        ax.annotate(str(idx + 1), (x, y), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set(xlim=(0, area), ylim=(0, area * 1.18), xlabel="X position (m)", ylabel="Y position (m)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Alive nodes over time")
    fig, ax = plt.subplots()
    ax.plot(history["Round"], history["Alive nodes — cluster"], label="Cluster-based")
    ax.plot(history["Round"], history["Alive nodes — direct"], label="Direct baseline")
    ax.set_xlabel("Simulation round")
    ax.set_ylabel("Alive nodes")
    ax.grid(True, alpha=0.25)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Residual network energy")
fig, ax = plt.subplots()
ax.plot(history["Round"], history["Residual energy — cluster (J)"], label="Cluster-based")
ax.plot(history["Round"], history["Residual energy — direct (J)"], label="Direct baseline")
ax.set_xlabel("Simulation round")
ax.set_ylabel("Total residual energy (J)")
ax.grid(True, alpha=0.25)
ax.legend()
st.pyplot(fig)
plt.close(fig)

st.subheader("Node details")
st.dataframe(nodes, use_container_width=True, hide_index=True)
st.download_button("Download node results (CSV)", nodes.to_csv(index=False).encode("utf-8"),
                   file_name="camera_sensor_node_results.csv", mime="text/csv")
st.download_button("Download round-by-round results (CSV)", history.to_csv(index=False).encode("utf-8"),
                   file_name="simulation_history.csv", mime="text/csv")

with st.expander("How to interpret this prototype"):
    st.write("""
    - Each dot represents a camera sensor node; the star is the sink/gateway.
    - The cluster-based method sends node packets to a nearby cluster head, which forwards aggregated data.
    - The direct baseline sends every node's packet directly to the sink.
    - Alive-node and residual-energy charts show how the two simplified strategies behave across rounds.
    - This is an educational simulation. The radio-energy coefficients are illustrative, not measured for a particular camera or wireless protocol.
    - It does not yet simulate real image files, packet loss, bandwidth, latency, or the full GA/PSO/ABC method from a research paper.
    """)
st.info("For a fair experiment, keep the same random seed and settings when comparing strategies. Try changing node count, packet size, and cluster-head percentage.")
