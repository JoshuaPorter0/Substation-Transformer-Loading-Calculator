# EE 347 - Substation Transformer Loading Heatmap & Overload Analyzer

This repository contains a Python script developed for the **EE 347 (Power Systems I) Term Project**.

As outlined in **Task 3.2.7** of the project specifications, this script models theoretical 208 V substation transformer-bank loading across all 64 possible Feeder 1 resistor/capacitor bank combinations over a continuous dynamometer torque sweep[cite: 1]. Rather than requiring manual interactive inputs, it automatically evaluates the operating space and exports a high-resolution gradient heatmap along with a CSV report of all overload intervals[cite: 1].

## ⚙️ System Parameters & Modeling Assumptions
The script models the LabVolt substation setup using the following baseline parameters (configurable at the top of the script)[cite: 1]:
* **Transformer Bank:** Three-phase 208 V / 208 V Delta-Delta bank (`3 × 250 VA` single-phase transformers = **750 VA** total; **2.082 A** rated line current)[cite: 1]
* **Source Frequency:** 60 Hz[cite: 1]
* **Feeder 1 (Static Loads):**
  * **Resistive Load Bank (Wye-connected):** 1200 Ω, 600 Ω, and 300 Ω per-phase steps (8 combinations)[cite: 1]
  * **Capacitive Load Bank (Delta-connected):** 2.2 µF, 4.4 µF, and 8.8 µF per-branch steps (8 combinations)[cite: 1]
* **Feeder 2 (Motor & Drive):**
  * **Motor/Dynamometer Operating Point:** Sweeps dynamometer torque from **0.0 to 1.25 N·m** (301 samples) at a fixed shaft speed of **1,770 RPM**[cite: 1]
  * **Ratings & Assumptions:** 175 W rated motor shaft output (~0.944 N·m at 1,770 RPM), 350 W dynamometer rating, idealized 100% motor and VFD efficiencies, and an assumed **0.95 lagging input power factor** at the VFD[cite: 1]

## ✨ Features & Outputs
* **Full Combinatorial & Torque Sweep:** Evaluates all **64** Feeder 1 R/C load-bank permutations across 301 torque points by algebraically summing active ($P$) and reactive ($Q$) power at the source-side bus[cite: 1].
* **Gradient Heatmap (`EE347_Transformer_Gradient_Heatmap.png`):**
  * Color-codes transformer loading (% of 750 VA) from green (safe) to yellow/orange (approaching 98–100%) to red (>100% overload)[cite: 1, 2].
  * Plots **98%** (dashed) and **100%** (solid) loading contours alongside a vertical marker for the **175 W rated motor shaft limit**[cite: 1, 2].
* **Overload Interval CSV (`EE347_Heatmap_Overloads_Only.csv`):** Filters out safe operating regions and logs contiguous overload intervals, recording exact threshold torque, motor shaft power, peak loading percentage, maximum apparent power (VA), and maximum line current (A)[cite: 1].
* **Console Summary:** Prints file export paths, rated transformer current, overall sweep maximum loading, count of overloaded configurations, and the motor's rated torque limit[cite: 1].

> **Modeling Note:** `PF = 0.95` is a theoretical lagging input power-factor assumption (not derived from a manufacturer's reported 4.7% VFD relative loss). Real-world VFD operation introduces current harmonics, standby draw, and efficiency losses not captured in this idealized sweep[cite: 1].

## 🚀 Getting Started

### Prerequisites
* **Python 3.x**
* **External Libraries:** `numpy` and `matplotlib` (included by default in standard Spyder/Anaconda installations)[cite: 1]

### Running the Script
1. Clone the repository or download `EE347_Transformer_Gradient_Heatmap.py`[cite: 1].
2. Open a terminal, command prompt, or Spyder IDE and navigate to the script's directory[cite: 1].
3. Run the script:
   ```bash
   python EE347_Transformer_Gradient_Heatmap.py
