# EE 347 - Substation Transformer Loading Calculator

This repository contains a Python script developed for the **EE 347 (Power Systems I) Term Project**. 

As outlined in **Deliverable 3.2.8** of the project specifications, this script calculates the loading on the substation transformer for any combination of loading from the resistor bank, capacitor bank, and motor. It determines whether the combined feeder loading exceeds the rated transformer capacity.

## ⚙️ System Parameters
The script models the following LabVolt substation equipment:
*   **Transformer:** Three-phase 208 V / 208 V Delta-Delta bank (3x 250 VA single-phase transformers = **750 VA total**)
*   **Feeder 1:** Wye-connected resistive load bank & Delta-connected capacitive load bank
*   **Feeder 2:** GS13N-20P2 VFD, Four-pole squirrel-cage induction motor, and Four-quadrant dynamometer

## ✨ Features
*   **Interactive CLI:** Guides the user through switchgear status (XMFR, Bus, Feeder 1, Feeder 2) and load inputs.
*   **Component-Level Inputs:** Allows selection of specific resistor/capacitor steps and motor torque/speed parameters.
*   **Dual Assessment Methodology:** Calculates loading using an *Illustrative* method (assumes capacitive reactive power cancels motor reactive power) and a *Conservative Upper Bound* (assumes worst-case additive apparent power).
*   **Safety Warnings:** Alerts the user if mechanical power exceeds motor/dynamometer limits, or if capacitor voltage exceeds ratings.
*   **Capacity Assessment:** Concludes if the system is within the 750 VA capacity, overloaded, or if capacity cannot be verified without actual VFD measurements.

## 🚀 Getting Started

### Prerequisites
*   Python 3.x installed on your machine. (No external libraries are required; the script uses the built-in `math` module).

### Running the Script
1. Clone the repository or download the `.py` file.
2. Open a terminal or command prompt.
3. Navigate to the folder containing the script.
4. Run the script using the following command:
   ```bash
   python "Substation Transformer Loading Calculator.py"
