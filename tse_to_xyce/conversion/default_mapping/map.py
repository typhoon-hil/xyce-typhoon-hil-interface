from .constants import *

def map_component(comp_type):
    """ Translate from TSE comp_type to corresponding component(s) in the output format """

    mappings = {
        XYCE_AC_VSOURCE: ["VSIN"],
        XYCE_DC_VSOURCE: ["VDC"],
        XYCE_SS_AC_VSOURCE: ["VSMALL"],
        XYCE_PULSE_VSOURCE: ["VPULSE"],
        XYCE_EXP_VSOURCE: ["VEXP"],
        XYCE_TRI_VSOURCE: ["VTRI"],
        XYCE_AC_ISOURCE: ["ISIN"],
        XYCE_SS_AC_ISOURCE: ["ISMALL"],
        XYCE_DC_ISOURCE: ["IDC"],
        XYCE_PULSE_ISOURCE: ["IPULSE"],
        XYCE_EXP_ISOURCE: ["IEXP"],
        XYCE_VCVS: ["VCVS"],
        XYCE_VCCS: ["VCCS"],
        XYCE_CCVS: ["CCVS"],
        XYCE_CCCS: ["CCCS"],
        XYCE_GND: ["GND"],
        CORE_GND: ["GND"],
        XYCE_OPAMP: ["OPAMP"],
        XYCE_MODEL_OPAMP: ["OPAMP_MODEL"],
        XYCE_IDEAL_COMP: ["COMP"],
        XYCE_PWM: ["PWM"],
        XYCE_IMEAS: ["I_MEAS_OUT"],
        XYCE_VMEAS: ["V_MEAS_OUT"],
        CORE_IMEAS: ["I_MEAS"],
        CORE_VMEAS: ["V_MEAS"],
        XYCE_PMEAS: ["P_MEAS"],
        XYCE_PROBE: ["PROBE"],
        XYCE_VNODE: ["VNODE"],
        XYCE_SIG2PWR: ["SGN_TO_PWR"],
        XYCE_R_IDEAL: ["R"],
        XYCE_C_IDEAL: ["C"],
        XYCE_L_IDEAL: ["L"],
        XYCE_TRANSFORMER: ["IDEAL_TRANSFORMER"],
        XYCE_L_COUPLED: ["L_COUPLED"],
        XYCE_MEMRISTOR: ["YMEMRISTOR"],
        XYCE_D: ["D"],
        XYCE_D_IDEAL: ["D_IDEAL"],
        XYCE_UNIDIR_SWITCH: ["UNIDIRSWITCH"],
        XYCE_MOSFET: ["M"],
        XYCE_JFET: ["J"],
        XYCE_BJT: ["Q"],
        XYCE_MESFET: ["Z"],
        XYCE_VC_SWITCH: ["S"],
        XYCE_CC_SWITCH: ["W"],
        XYCE_TL_IDEAL: ["T"],
        XYCE_TL_LOSSY: ["O"],
        XYCE_TL_LUMPED: ["YTRANSLINE"],
        XYCE_NOT: ["LOGIC_PORT"],
        XYCE_BUFFER: ["LOGIC_PORT"],
        XYCE_AND: ["LOGIC_PORT"],
        XYCE_NAND: ["LOGIC_PORT"],
        XYCE_OR: ["LOGIC_PORT"],
        XYCE_NOR: ["LOGIC_PORT"],
        XYCE_XOR: ["LOGIC_PORT"],
        XYCE_XNOR: ["LOGIC_PORT"],
        XYCE_DELAY: ["LOGIC_PORT"],
        XYCE_DYN_SPICE: ["DYN_SPICE"],
        XYCE_NODE_ID: ["NODE_ID"],
        XYCE_SUM: ["MATH_SUM"],
        XYCE_PRODUCT: ["MATH_PROD"],
        XYCE_CONSTANT: ["MATH_CONSTANT"],
        XYCE_TRIG: ["MATH_TRIG"],
        XYCE_SAT: ["MATH_SAT"],
        XYCE_GAIN: ["MATH_GAIN"],
        XYCE_ABS: ["MATH_ABS"],
    }

    if comp_type in mappings.keys():
        return mappings.get(comp_type)


def ignore_component(comp_type):
    """ Merge terminals of supported ignored components
        Dictionary key is a terminal and the value is the list of terminals that are being merged to it.
    """

    merge_dict = {}

    return merge_dict.get(comp_type)
