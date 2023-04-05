from .component_classes import *


def create_comp_instance(converted_comp_type, comp_data):
    """Instantiates the appropriate class depending on converted_comp_type."""

    if converted_comp_type == "L":
        return Inductor(converted_comp_type, **comp_data)

    elif converted_comp_type == "L_COUPLED":
        return CoupledInductor(converted_comp_type, **comp_data)

    elif converted_comp_type == "C":
        return Capacitor(converted_comp_type, **comp_data)

    elif converted_comp_type == "R":
        return Resistor(converted_comp_type, **comp_data)

    elif converted_comp_type == "IDEAL_TRANSFORMER":
        return IdealTransformer(converted_comp_type, **comp_data)

    elif converted_comp_type == "YMEMRISTOR":
        if comp_data.get("tse_properties").get("subc_model") == "True":
            return SubcircuitMemristor(converted_comp_type, **comp_data)
        else:
            return Memristor(converted_comp_type, **comp_data)

    elif converted_comp_type == "D_IDEAL":
        return IdealDiode(converted_comp_type, **comp_data)

    elif converted_comp_type == "UNIDIRSWITCH":
        return UnidirectionalSwitch(converted_comp_type, **comp_data)

    elif converted_comp_type == "D":
        if comp_data.get("tse_properties").get("subc_model") == "True":
            return SubcircuitDiode(converted_comp_type, **comp_data)
        else:
            return Diode(converted_comp_type, **comp_data)

    elif converted_comp_type == "M":
        if comp_data.get("tse_properties").get("subc_model") == "True":
            return SubcircuitFet(converted_comp_type, **comp_data)
        else:
            return Fet(converted_comp_type, **comp_data)

    elif converted_comp_type == "J":
        if comp_data.get("tse_properties").get("subc_model") == "True":
            return SubcircuitFet(converted_comp_type, **comp_data)
        else:
            return Fet(converted_comp_type, **comp_data)

    elif converted_comp_type == "Z":
        if comp_data.get("tse_properties").get("subc_model") == "True":
            return SubcircuitFet(converted_comp_type, **comp_data)
        else:
            return Fet(converted_comp_type, **comp_data)

    elif converted_comp_type == "Q":
        if comp_data.get("tse_properties").get("subc_model") == "True":
            return SubcircuitBJT(converted_comp_type, **comp_data)
        else:
            return BJT(converted_comp_type, **comp_data)

    elif converted_comp_type == "S":
        return VoltageControlledSwitch(converted_comp_type, **comp_data)

    elif converted_comp_type == "W":
        return CurrentControlledSwitch(converted_comp_type, **comp_data)

    elif converted_comp_type == "LOGIC_PORT":
        return LogicPort(converted_comp_type, **comp_data)

    elif converted_comp_type == "DELAY":
        return Delay(converted_comp_type, **comp_data)

    elif converted_comp_type == "PWM":
        return PulseWidthModulator(converted_comp_type, **comp_data)

    elif any(converted_comp_type == t for t in ["VDC", "VSIN", "VPULSE", "VEXP", "VTRI", "I_MEAS"]):
        return VoltageSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "I_MEAS_OUT":
        if comp_data.get("tse_properties").get("signal_out") == "True":
            return MeasureWithOutput(converted_comp_type, **comp_data)
        else:
            return VoltageSource(converted_comp_type, **comp_data)

    elif any(converted_comp_type == t for t in ["IDC", "ISIN", "IPULSE", "IEXP", "V_MEAS"]):
        return CurrentSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "V_MEAS_OUT":
        if comp_data.get("tse_properties").get("signal_out") == "True":
            return MeasureWithOutput(converted_comp_type, **comp_data)
        else:
            return CurrentSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "SGN_TO_PWR":
        return SignalToPower(converted_comp_type, **comp_data)

    elif converted_comp_type == "VSMALL":
        return VoltageSmallSignal(converted_comp_type, **comp_data)

    elif converted_comp_type == "ISMALL":
        return CurrentSmallSignal(converted_comp_type, **comp_data)

    elif converted_comp_type == "P_MEAS":
        return PowerMeasurement(converted_comp_type, **comp_data)

    elif converted_comp_type == "VNODE":
        return NodeVoltage(converted_comp_type, **comp_data)

    elif converted_comp_type == "PROBE":
        return Probe(converted_comp_type, **comp_data)

    elif converted_comp_type == "OPAMP":
        return OperationalAmplifier(converted_comp_type, **comp_data)

    elif converted_comp_type == "OPAMP_MODEL":
        return ModelBasedOperationalAmplifier(converted_comp_type, **comp_data)

    elif converted_comp_type == "COMP":
        return Comparator(converted_comp_type, **comp_data)

    elif converted_comp_type == "VCVS":
        return VoltageControlledVoltageSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "VCCS":
        return VoltageControlledCurrentSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "CCCS":
        return CurrentControlledCurrentSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "CCVS":
        return CurrentControlledVoltageSource(converted_comp_type, **comp_data)

    elif converted_comp_type == "T":
        return LosslessTransmissionLine(converted_comp_type, **comp_data)

    elif converted_comp_type == "O":
        return LossyTransmissionLine(converted_comp_type, **comp_data)

    elif converted_comp_type == "YTRANSLINE":
        return LumpedTransmissionLine(converted_comp_type, **comp_data)

    elif converted_comp_type == "DYN_SPICE":
        return DynamicSpiceComponent(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_CONSTANT":
        return Constant(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_SUM":
        return Sum(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_PROD":
        return Product(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_GAIN":
        return Gain(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_ABS":
        return AbsoluteValue(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_SAT":
        return Saturation(converted_comp_type, **comp_data)

    elif converted_comp_type == "MATH_TRIG":
        return TrigonometricFunction(converted_comp_type, **comp_data)

