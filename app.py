import streamlit as st
import numpy as np
import pandas as pd

st.title("Cluster Routing Visualiser")

# --- Sidebar controls ---
st.sidebar.header("Parameters")

wC = st.sidebar.number_input("wC (cost weight)", value=5.0, step=0.1)
wU = st.sidebar.number_input("wU (utilisation weight)", value=1.0, step=0.1)
L = st.sidebar.number_input("L (mixing parameter)", value=0.5, min_value=0.0, max_value=1.0, step=0.05)
ULimit = st.sidebar.number_input("ULimit (utilisation cap)", value=1000, min_value=2, step=1)

st.sidebar.subheader("Enable/Disable Clusters")

enabled = []
for i in range(4):
    enabled.append(st.sidebar.checkbox(f"Cluster {i} enabled", value=True))

st.sidebar.subheader("Cost per EMR Unit")

C = []
for i in range(4):
    c_val = st.sidebar.slider(f"C[{i}] (cost per EMR unit)", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    C.append(c_val)

st.sidebar.subheader("Utilisation")

U = []
for i in range(4):
    u_val = st.sidebar.slider(f"U[{i}] (utilisation)", min_value=0, max_value=int(ULimit) - 1, value=500, step=1)
    U.append(u_val)

# --- Computation ---
C = np.array(C)
U = np.array(U)

active = [i for i in range(4) if enabled[i]]
N_active = len(active)

if N_active == 0:
    routing = np.zeros(4)
    raw_score = np.zeros(4)
    final_score = np.zeros(4)
else:
    C_active = C[active]
    U_active = U[active]
    raw_active = -wC * C_active - wU * (U_active / (ULimit - U_active))
    exp_active = np.exp(raw_active - np.max(raw_active))
    final_active = exp_active / exp_active.sum()
    routing_active = (1 - L) * (1 / N_active) + L * final_active

    raw_score = np.zeros(4)
    final_score = np.zeros(4)
    routing = np.zeros(4)
    for idx, i in enumerate(active):
        raw_score[i] = raw_active[idx]
        final_score[i] = final_active[idx]
        routing[i] = routing_active[idx]

# --- Visualisation ---
st.subheader("Percentage Routing")

routing_pct = routing * 100
chart_data = pd.DataFrame(
    {"Routing (%)": routing_pct},
    index=[f"Cluster {i}" for i in range(4)],
)
st.bar_chart(chart_data)

st.subheader("Summary Table")

summary = pd.DataFrame({
    "Cluster": [f"Cluster {i}" for i in range(4)],
    "Enabled": enabled,
    "C[i]": C,
    "U[i]": U.astype(int),
    "cluster_score[i]": raw_score,
    "final_cluster_score[i]": final_score,
    "routing[i]": routing,
    "routing (%)": routing_pct,
})
summary = summary.set_index("Cluster")
st.dataframe(summary.style.format({
    "C[i]": "{:.1f}",
    "U[i]": "{:d}",
    "cluster_score[i]": "{:.4f}",
    "final_cluster_score[i]": "{:.4f}",
    "routing[i]": "{:.4f}",
    "routing (%)": "{:.2f}%",
}))

st.caption(f"Routing sum: {routing.sum():.6f} (should be 1.0 when at least one cluster is active)")
