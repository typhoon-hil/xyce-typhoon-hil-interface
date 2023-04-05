XYCE_AC_VSOURCE = "xyce_lib/AC Voltage Source"
XYCE_DC_VSOURCE = "xyce_lib/DC Voltage Source"
XYCE_SS_AC_VSOURCE = "xyce_lib/Small-signal AC Voltage Source"
XYCE_PULSE_VSOURCE = "xyce_lib/Pulse Voltage Source"
XYCE_EXP_VSOURCE = "xyce_lib/Exponent Voltage Source"
XYCE_TRI_VSOURCE = "xyce_lib/Triangular Voltage Source"
XYCE_AC_ISOURCE = "xyce_lib/AC Current Source"
XYCE_SS_AC_ISOURCE = "xyce_lib/Small-signal AC Current Source"
XYCE_DC_ISOURCE = "xyce_lib/DC Current Source"
XYCE_PULSE_ISOURCE = "xyce_lib/Pulse Current Source"
XYCE_EXP_ISOURCE = "xyce_lib/Exponent Current Source"
XYCE_VCVS = "xyce_lib/Voltage-Controlled Voltage Source"
XYCE_VCCS = "xyce_lib/Voltage-Controlled Current Source"
XYCE_CCVS = "xyce_lib/Current-Controlled Voltage Source"
XYCE_CCCS = "xyce_lib/Current-Controlled Current Source"
XYCE_GND = "xyce_lib/Ground"
CORE_GND = "Ground"
XYCE_OPAMP = "xyce_lib/Operational Amplifier"
XYCE_MODEL_OPAMP = "xyce_lib/Model-based OpAmp"
XYCE_IDEAL_COMP = "xyce_lib/Ideal Comparator"
XYCE_PWM = "xyce_lib/Pulse Width Modulator"
XYCE_IMEAS = "xyce_lib/Current Measurement"
CORE_IMEAS = "Current Measurement"
XYCE_VMEAS = "xyce_lib/Voltage Measurement"
CORE_VMEAS = "Voltage Measurement"
XYCE_PMEAS = "xyce_lib/Power Measurement"
XYCE_PROBE = "xyce_lib/Probe"
XYCE_VNODE = "xyce_lib/Node Voltage"
XYCE_SIG2PWR = "xyce_lib/Signal-to-Power"
XYCE_R_IDEAL = "xyce_lib/Ideal Resistor"
XYCE_C_IDEAL = "xyce_lib/Ideal Capacitor"
XYCE_L_IDEAL = "xyce_lib/Ideal Inductor"
XYCE_TRANSFORMER = "xyce_lib/Transformer"
XYCE_L_COUPLED = "xyce_lib/Coupled Inductor"
XYCE_MEMRISTOR = "xyce_lib/Memristor"
XYCE_R_3P = "xyce_lib/3PResistor"
XYCE_D = "xyce_lib/Diode"
XYCE_D_IDEAL = "xyce_lib/Ideal Diode"
XYCE_UNIDIR_SWITCH = "xyce_lib/Unidirectional Switch"
XYCE_MOSFET = "xyce_lib/MOSFET"
XYCE_JFET = "xyce_lib/JFET"
XYCE_BJT = "xyce_lib/BJT"
XYCE_MESFET = "xyce_lib/MESFET"
XYCE_VC_SWITCH = "xyce_lib/Voltage-Controlled Switch"
XYCE_CC_SWITCH = "xyce_lib/Current-Controlled Switch"
XYCE_TL_IDEAL = "xyce_lib/Ideal Transmission Line"
XYCE_TL_LOSSY = "xyce_lib/Lossy Transmission Line"
XYCE_TL_LUMPED = "xyce_lib/Lumped Transmission Line"
XYCE_NOT = "xyce_lib/NOT"
XYCE_BUFFER = "xyce_lib/BUFFER"
XYCE_AND = "xyce_lib/AND"
XYCE_NAND = "xyce_lib/NAND"
XYCE_OR = "xyce_lib/OR"
XYCE_NOR = "xyce_lib/NOR"
XYCE_XOR = "xyce_lib/XOR"
XYCE_XNOR = "xyce_lib/XNOR"
XYCE_DELAY = "xyce_lib/Delay_"
XYCE_DYN_SPICE = "xyce_lib/Dynamic SPICE component"
XYCE_NODE_ID = "xyce_lib/NodeID"
XYCE_SUM = "xyce_lib/Sum"
XYCE_PRODUCT = "xyce_lib/Product_"
XYCE_CONSTANT = "xyce_lib/Constant"
XYCE_TRIG = "xyce_lib/Trig Function"
XYCE_SAT = "xyce_lib/Saturation"
XYCE_GAIN = "xyce_lib/Gain"
XYCE_ABS = "xyce_lib/Absolute Value"

XYCE_NODE_PREFIX = "N_"

import pathlib
import tse_to_xyce
XYCE_INCLUDED_MODELS_PATH = str(pathlib.Path(tse_to_xyce.__file__).parent.joinpath("xyce_component_models"))

