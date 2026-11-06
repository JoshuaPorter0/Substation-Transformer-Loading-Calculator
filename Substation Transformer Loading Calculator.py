"""
EE 347 - Power Systems I
Task 3: Substation Transformer Loading Calculator

System:
    Three-phase 208 V / 208 V Delta-Delta transformer bank
    Three single-phase transformers, 250 VA each
    Total three-phase transformer rating: 750 VA

    Feeder 1:
        Wye-connected resistive load bank
        Delta-connected capacitive load bank

    Feeder 2:
        GS13N-20P2 Variable Frequency Drive
        Four-pole squirrel-cage induction motor
        Four-quadrant dynamometer

Purpose:
    Calculate transformer loading for any combination of
    resistive, capacitive, and motor loading.

    Determine whether the combined feeder loading exceeds
    the rated transformer capacity (750 VA).

Note:
    Motor/VFD electrical loading is estimated unless actual
    VFD input measurements are provided.
"""

import math


# ============================================================
# 1. SYSTEM CONSTANTS
# ============================================================

V_LL = 208.0                  # Line-to-line voltage (V)
FREQUENCY = 60.0              # System frequency (Hz)

TRANSFORMER_COUNT = 3
TRANSFORMER_VA_EACH = 250.0

TRANSFORMER_RATED_VA = (
    TRANSFORMER_COUNT * TRANSFORMER_VA_EACH
)

TRANSFORMER_RATED_CURRENT = (
    TRANSFORMER_RATED_VA /
    (math.sqrt(3) * V_LL)
)

# Resistive load bank (Ohms per phase)
RESISTOR_STEPS = {
    1: 1200.0,
    2: 600.0,
    3: 300.0
}

# Capacitive load bank (microfarads per delta branch)
CAPACITOR_STEPS = {
    1: 2.2,
    2: 4.4,
    3: 8.8
}

# Capacitor nameplate
CAP_RATED_VAR = 252.0
CAP_RATED_VOLTAGE = 120.0
CAP_MAX_VOLTAGE = 230.0

# Motor nameplate
MOTOR_RATED_POWER = 175.0     # Mechanical output (W)
MOTOR_RATED_RPM = 1670.0
MOTOR_RATED_CURRENT = 1.2
MOTOR_RATED_VOLTAGE = 208.0

# Dynamometer limits
DYNAMOMETER_MAX_TORQUE = 3.0  # N*m
DYNAMOMETER_MAX_RPM = 2500.0
DYNAMOMETER_MAX_POWER = 350.0 # W

# Assumed efficiencies
DEFAULT_MOTOR_EFF = 0.75
DEFAULT_VFD_EFF = 0.90

# Assumed VFD input displacement power factor
DEFAULT_VFD_PF = 0.95


# ============================================================
# 2. INPUT FUNCTIONS
# ============================================================

def yes_no(prompt):

    while True:

        response = input(prompt + " [y/n]: ").strip().lower()

        if response in ("y", "yes"):
            return True

        elif response in ("n", "no"):
            return False

        else:
            print("Please enter y or n.")


def get_float(prompt, default=None, minimum=None, maximum=None):

    while True:

        if default is not None:
            response = input(
                f"{prompt} [{default}]: "
            ).strip()
        else:
            response = input(
                f"{prompt}: "
            ).strip()

        if response == "" and default is not None:
            value = default

        else:
            try:
                value = float(response)

            except ValueError:
                print("Please enter a valid number.")
                continue

        if not math.isfinite(value):
            print("Please enter a finite number.")
            continue

        if minimum is not None and value < minimum:
            print(f"Value must be at least {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"Value must not exceed {maximum}.")
            continue

        return value


def select_steps(name, steps, unit):

    print(f"\n{name}")

    for number, value in steps.items():
        print(f"  {number}: {value} {unit}")

    print("Enter step numbers separated by commas.")
    print("Example: 1,3")
    print("Press Enter for no load.")

    while True:

        response = input("Selected steps: ").strip()

        if response == "":
            return []

        try:

            selected = [
                int(item.strip())
                for item in response.split(",")
            ]

            if len(selected) != len(set(selected)):
                print("Do not enter duplicate steps.")
                continue

            if all(step in steps for step in selected):
                return selected

            print("Invalid step selection.")

        except ValueError:
            print("Enter numbers separated by commas.")


# ============================================================
# 3. SWITCHGEAR STATUS
# ============================================================

def get_switchgear_status():

    print("\n" + "=" * 60)
    print("SWITCHGEAR STATUS")
    print("=" * 60)

    xmfr = yes_no("XMFR switchgear closed?")

    if not xmfr:

        print("\nXMFR is OPEN.")
        print("All downstream loads are disconnected.")

        return False, False, False, False

    bus = yes_no("Bus switchgear closed?")

    if not bus:

        print("\nBus is OPEN.")
        print("Both feeders are disconnected.")

        return True, False, False, False

    feeder1 = yes_no("Feeder 1 closed?")
    feeder2 = yes_no("Feeder 2 closed?")

    return xmfr, bus, feeder1, feeder2


# ============================================================
# 4. RESISTIVE LOAD CALCULATIONS
# ============================================================

def calculate_resistive_load(selected_steps):

    """
    Wye-connected balanced resistive load.

    V_phase = V_LL / sqrt(3)

    P_3phase = 3 * V_phase^2 / R

    Equivalent:
    P_3phase = V_LL^2 / R

    Each selected step is treated as a balanced
    three-phase resistance connected in parallel.
    """

    total_power = 0.0

    print("\nRESISTIVE LOAD CALCULATIONS")

    for step in selected_steps:

        resistance = RESISTOR_STEPS[step]

        power = V_LL**2 / resistance

        total_power += power

        print(
            f"Step {step}: "
            f"{resistance:.0f} ohm -> "
            f"{power:.2f} W"
        )

    print(f"Total resistive power: {total_power:.2f} W")

    return total_power


# ============================================================
# 5. CAPACITIVE LOAD CALCULATIONS
# ============================================================

def calculate_capacitive_load(selected_steps):

    """
    Delta-connected balanced capacitive load.

    Each delta branch experiences V_LL.

    Q_3phase = -3 * V_LL^2 * omega * C

    Negative reactive power represents
    capacitive reactive power.
    """

    omega = 2 * math.pi * FREQUENCY

    total_reactive_power = 0.0

    print("\nCAPACITIVE LOAD CALCULATIONS")

    for step in selected_steps:

        capacitance_uF = CAPACITOR_STEPS[step]

        capacitance_F = capacitance_uF * 1e-6

        reactive_power = (
            -3 *
            V_LL**2 *
            omega *
            capacitance_F
        )

        total_reactive_power += reactive_power

        print(
            f"Step {step}: "
            f"{capacitance_uF:.1f} uF -> "
            f"{reactive_power:.2f} VAR"
        )

    print(
        f"Total capacitive reactive power: "
        f"{total_reactive_power:.2f} VAR"
    )

    if abs(total_reactive_power) > CAP_RATED_VAR:

        print(
            "NOTICE: Capacitive reactive power exceeds "
            "the nominal 252 VAR nameplate value."
        )

    if V_LL > CAP_MAX_VOLTAGE:

        print(
            "WARNING: Capacitor voltage exceeds "
            "the 230 V maximum rating!"
        )

    return total_reactive_power


# ============================================================
# 6. MOTOR AND DYNAMOMETER CALCULATIONS
# ============================================================

def calculate_motor_load():

    print("\n" + "=" * 60)
    print("MOTOR AND DYNAMOMETER LOADING")
    print("=" * 60)

    motor_running = yes_no("Is the motor running?")

    if not motor_running:

        print("Motor is not running.")

        return 0.0, 0.0, 0.0

    torque = get_float(
        "Dynamometer torque (N*m)",
        default=0.0,
        minimum=0.0,
        maximum=DYNAMOMETER_MAX_TORQUE
    )

    rpm = get_float(
        "Motor speed (RPM)",
        default=MOTOR_RATED_RPM,
        minimum=0.0,
        maximum=DYNAMOMETER_MAX_RPM
    )

    # Mechanical shaft power
    mechanical_power = (
        2 * math.pi * rpm * torque / 60
    )

    print(
        f"\nMechanical shaft power: "
        f"{mechanical_power:.2f} W"
    )

    if mechanical_power > MOTOR_RATED_POWER:

        print(
            "WARNING: Mechanical shaft power exceeds "
            "the motor's rated 175 W output."
        )

    if mechanical_power > DYNAMOMETER_MAX_POWER:

        print(
            "WARNING: Mechanical power exceeds "
            "the dynamometer's 350 W rating."
        )

    print("\nEnter estimated efficiencies.")

    motor_eff = get_float(
        "Motor efficiency",
        default=DEFAULT_MOTOR_EFF,
        minimum=0.01,
        maximum=1.0
    )

    vfd_eff = get_float(
        "VFD efficiency",
        default=DEFAULT_VFD_EFF,
        minimum=0.01,
        maximum=1.0
    )

    vfd_pf = get_float(
        "Estimated VFD input power factor",
        default=DEFAULT_VFD_PF,
        minimum=0.01,
        maximum=1.0
    )

    # Electrical real power at VFD input
    electrical_power = (
        mechanical_power /
        (motor_eff * vfd_eff)
    )

    # Apparent power estimate
    apparent_power = electrical_power / vfd_pf

    # Equivalent nonactive power estimate
    nonactive_power = math.sqrt(
        max(
            apparent_power**2 - electrical_power**2,
            0.0
        )
    )

    print("\nMOTOR/VFD RESULTS")

    print(
        f"Mechanical power: "
        f"{mechanical_power:.2f} W"
    )

    print(
        f"Estimated VFD input real power: "
        f"{electrical_power:.2f} W"
    )

    print(
        f"Estimated VFD input apparent power: "
        f"{apparent_power:.2f} VA"
    )

    print(
        f"Equivalent nonactive power: "
        f"{nonactive_power:.2f} VAR-equivalent"
    )

    return (
        electrical_power,
        apparent_power,
        nonactive_power
    )


# ============================================================
# 7. TRANSFORMER LOADING CALCULATIONS
# ============================================================

def calculate_transformer_loading(
    resistor_power,
    capacitor_reactive_power,
    motor_real_power,
    motor_apparent_power,
    motor_nonactive_power
):

    print("\n" + "=" * 60)
    print("TRANSFORMER LOADING RESULTS")
    print("=" * 60)

    # Total real power
    total_real_power = (
        resistor_power + motor_real_power
    )

    # Illustrative reactive-power combination.
    #
    # This assumes motor/VFD nonactive power behaves
    # as positive fundamental reactive power.
    #
    # Actual VFD harmonic distortion may prevent
    # this assumption from being accurate.

    illustrative_reactive_power = (
        capacitor_reactive_power +
        motor_nonactive_power
    )

    illustrative_apparent_power = math.sqrt(
        total_real_power**2 +
        illustrative_reactive_power**2
    )

    # Conservative upper bound using triangle inequality
    #
    # Does not assume capacitive compensation
    # cancels VFD harmonic/nonactive loading.

    resistor_apparent_power = abs(resistor_power)

    capacitor_apparent_power = abs(
        capacitor_reactive_power
    )

    conservative_upper_bound = (
        resistor_apparent_power +
        capacitor_apparent_power +
        motor_apparent_power
    )

    # Transformer loading percentages
    illustrative_loading_percent = (
        illustrative_apparent_power /
        TRANSFORMER_RATED_VA * 100
    )

    upper_bound_percent = (
        conservative_upper_bound /
        TRANSFORMER_RATED_VA * 100
    )

    # Estimated line current
    illustrative_line_current = (
        illustrative_apparent_power /
        (math.sqrt(3) * V_LL)
    )

    upper_bound_line_current = (
        conservative_upper_bound /
        (math.sqrt(3) * V_LL)
    )

    # Illustrative overall power factor
    if illustrative_apparent_power > 0:

        overall_pf = (
            total_real_power /
            illustrative_apparent_power
        )

    else:
        overall_pf = 1.0

    print("\nINDIVIDUAL LOADS")

    print(
        f"Resistive real power: "
        f"{resistor_power:.2f} W"
    )

    print(
        f"Capacitive reactive power: "
        f"{capacitor_reactive_power:.2f} VAR"
    )

    print(
        f"Motor/VFD real power: "
        f"{motor_real_power:.2f} W"
    )

    print(
        f"Motor/VFD apparent power: "
        f"{motor_apparent_power:.2f} VA"
    )

    print("\nCOMBINED LOAD")

    print(
        f"Total real power: "
        f"{total_real_power:.2f} W"
    )

    print(
        f"Illustrative reactive power: "
        f"{illustrative_reactive_power:.2f} VAR"
    )

    print(
        f"Illustrative apparent power: "
        f"{illustrative_apparent_power:.2f} VA"
    )

    print(
        f"Illustrative power factor: "
        f"{overall_pf:.4f}"
    )

    print(
        f"Illustrative line current: "
        f"{illustrative_line_current:.3f} A"
    )

    print("\nTRANSFORMER CAPACITY")

    print(
        f"Rated transformer capacity: "
        f"{TRANSFORMER_RATED_VA:.2f} VA"
    )

    print(
        f"Rated transformer line current: "
        f"{TRANSFORMER_RATED_CURRENT:.3f} A"
    )

    print(
        f"Illustrative loading: "
        f"{illustrative_loading_percent:.2f}%"
    )

    print(
        f"Conservative apparent-power upper bound: "
        f"{conservative_upper_bound:.2f} VA"
    )

    print(
        f"Conservative loading bound: "
        f"{upper_bound_percent:.2f}%"
    )

    print(
        f"Conservative line-current bound: "
        f"{upper_bound_line_current:.3f} A"
    )

    # ========================================================
    # 8. TRANSFORMER CAPACITY ASSESSMENT
    # ========================================================

    print("\n" + "-" * 60)
    print("TASK 3.2.7 CAPACITY ASSESSMENT")
    print("-" * 60)

    if total_real_power > TRANSFORMER_RATED_VA:

        print("RESULT: TRANSFORMER OVERLOAD")

        print(
            "Real power alone exceeds the transformer's "
            "rated apparent-power capacity."
        )

    elif conservative_upper_bound <= TRANSFORMER_RATED_VA:

        print("RESULT: WITHIN TRANSFORMER CAPACITY")

        print(
            "The conservative apparent-power upper bound "
            "is within the 750 VA transformer rating."
        )

    elif motor_apparent_power == 0:

        if illustrative_apparent_power > TRANSFORMER_RATED_VA:

            print("RESULT: TRANSFORMER OVERLOAD")

            print(
                "Calculated apparent power exceeds "
                "the 750 VA transformer rating."
            )

        else:

            print("RESULT: WITHIN TRANSFORMER CAPACITY")

            print(
                "Calculated apparent power is within "
                "the 750 VA transformer rating."
            )

    else:

        print("RESULT: CAPACITY NOT VERIFIED")

        print(
            "The conservative upper bound exceeds "
            "750 VA, but this does not prove an overload."
        )

        print(
            "Actual VFD input measurements are needed "
            "for a more reliable assessment."
        )

    print("-" * 60)


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("EE 347 - TASK 3")
    print("SUBSTATION TRANSFORMER LOADING CALCULATOR")
    print("=" * 60)

    print("\nSYSTEM INFORMATION")

    print(f"System voltage: {V_LL:.0f} V L-L")
    print(f"Frequency: {FREQUENCY:.0f} Hz")

    print(
        f"Transformer bank rating: "
        f"{TRANSFORMER_RATED_VA:.0f} VA"
    )

    print(
        f"Rated line current: "
        f"{TRANSFORMER_RATED_CURRENT:.3f} A"
    )

    while True:

        # Switchgear status
        xmfr, bus, feeder1, feeder2 = (
            get_switchgear_status()
        )

        resistor_power = 0.0
        capacitor_reactive_power = 0.0

        motor_real_power = 0.0
        motor_apparent_power = 0.0
        motor_nonactive_power = 0.0

        # ====================================================
        # FEEDER 1
        # ====================================================

        if feeder1:

            print("\n" + "=" * 60)
            print("FEEDER 1 - RESISTIVE/CAPACITIVE LOADS")
            print("=" * 60)

            resistor_selection = select_steps(
                "RESISTOR BANK",
                RESISTOR_STEPS,
                "ohm"
            )

            capacitor_selection = select_steps(
                "CAPACITOR BANK",
                CAPACITOR_STEPS,
                "uF"
            )

            resistor_power = calculate_resistive_load(
                resistor_selection
            )

            capacitor_reactive_power = (
                calculate_capacitive_load(
                    capacitor_selection
                )
            )

        else:

            print("\nFeeder 1 is OPEN.")
            print("Resistive and capacitive loads disconnected.")

        # ====================================================
        # FEEDER 2
        # ====================================================

        if feeder2:

            print("\n" + "=" * 60)
            print("FEEDER 2 - MOTOR/VFD")
            print("=" * 60)

            (
                motor_real_power,
                motor_apparent_power,
                motor_nonactive_power
            ) = calculate_motor_load()

        else:

            print("\nFeeder 2 is OPEN.")
            print("Motor load disconnected.")

        # ====================================================
        # TOTAL TRANSFORMER LOADING
        # ====================================================

        calculate_transformer_loading(
            resistor_power,
            capacitor_reactive_power,
            motor_real_power,
            motor_apparent_power,
            motor_nonactive_power
        )

        print("\n")

        again = yes_no(
            "Calculate another loading combination?"
        )

        if not again:

            print("\nProgram finished.")
            break


# ============================================================
# 10. RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()