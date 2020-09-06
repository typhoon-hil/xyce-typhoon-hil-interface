import re, os
from math import sqrt
import ast

included_models_path = os.getcwd() + "/libs/component_models/included/"

class Element:
    ''' Element is the main class. Circuit elements inherit from this class and
    must have string-type method arguments. '''
    def __init__(self,name):
        self.name = name
        self.value = self.params = self.model = ""

    def xyce_element(self):
        # Part of the Xyce syntax line construction of most elements.
        # Return example: "R_R1"
        return self.type + "_" + self.name

    def measurements(self, analysis_type, enabled_measurements=None):
        self.meas_string = ""
        self.meas_alias = []
        if "V" in enabled_measurements:
            self.meas_string += self.v_measurement_line()
            self.meas_alias.append(self.v_measurement_alias())
        if "I" in enabled_measurements:
            self.meas_string += self.i_measurement_line()
            self.meas_alias.append(self.i_measurement_alias())
        if "P" in enabled_measurements:
            self.meas_string += self.p_measurement_line()
            self.meas_alias.append(self.p_measurement_alias())
        if "G" in enabled_measurements:
            self.meas_string += self.g_measurement_line()
            self.meas_alias.append(self.g_measurement_alias())

        return [self.meas_string, ",".join(self.meas_alias)]

    @staticmethod
    def pick_correct_subclass(elem_type, elem_data):
        # Instantiates the appropriate class depending on elem_type.
        if elem_type == "L":
            return Inductor(elem_type, **elem_data)
        if elem_type == "L_coupled":
            return CoupledInductor(elem_type, **elem_data)
        if elem_type == "C":
            return Capacitor(elem_type, **elem_data)
        if elem_type == "R":
            return Resistor(elem_type, **elem_data)
        if elem_type == "Transf":
            return IdealTransformer2W(elem_type, **elem_data)
        if elem_type == "ymemristor":
            return Memristor(elem_type, **elem_data)
        if elem_type == "D":
            return Diode(elem_type, **elem_data)
        if elem_type == "IdealD":
            return IdealDiode(elem_type, **elem_data)
        if elem_type == "UnidirSwitch":
            return UnidirectionalSwitch(elem_type, **elem_data)
        if elem_type == "M":
            return Mosfet(elem_type, **elem_data)
        if elem_type == "J":
            return Jfet(elem_type, **elem_data)
        if elem_type == "Z":
            return Mesfet(elem_type, **elem_data)
        if elem_type == "Q":
            return Bjt(elem_type, **elem_data)
        if elem_type == "S":
            return VoltageControlledSwitch(elem_type, **elem_data)
        if elem_type == "W":
            return CurrentControlledSwitch(elem_type, **elem_data)
        # if elem_type == "X":
        #     return SubcircuitBased(elem_type, **elem_data)
        if elem_type == "U":
            return BehavioralDigitalDevice(elem_type, **elem_data)
        if elem_type == "DELAY":
            return Delay(elem_type, **elem_data)
        if elem_type == "PWM":
            return PWM(elem_type, **elem_data)
        if any(elem_type == t for t in ["Vdc", "Vsin", "Vpulse", "Vexp", "Vtri", "I_meas"]):
            return VoltageSource(elem_type,**elem_data)
        if any(elem_type == t for t in ["Idc", "Iac", "Ipulse", "Iexp", "V_meas"]):
            return CurrentSource(elem_type, **elem_data)
        if elem_type == "OPAMP":
            return OperationalAmplifier(elem_type, **elem_data)
        if elem_type == "OPAMP_MODEL":
            return ModelBasedOperationalAmplifier(elem_type, **elem_data)
        if elem_type == "COMP":
            return Comparator(elem_type, **elem_data)
        if elem_type == "VCVS":
            return VoltageControlledVoltageSource(elem_type, **elem_data)
        if elem_type == "VCCS":
            return VoltageControlledCurrentSource(elem_type, **elem_data)
        if elem_type == "CCCS":
            return CurrentControlledCurrentSource(elem_type, **elem_data)
        if elem_type == "CCVS":
            return CurrentControlledVoltageSource(elem_type, **elem_data)
        if elem_type == "T":
            return LosslessTransmissionLine(elem_type, **elem_data)
        if elem_type == "O":
            return LossyTransmissionLine(elem_type, **elem_data)
        if elem_type == "ytransline":
            return LumpedTransmissionLine(elem_type, **elem_data)
        if elem_type == "Smart":
            return DynamicSpiceComponent(elem_type, **elem_data)
        if elem_type == "3PVoltageSource":
            return ThreePhaseVoltageSource(elem_type, **elem_data)
################################################################################

### Two-terminal elements ######################################################
class TwoTerminal(Element):
    def __init__(self,name,nodes):
        super().__init__(name)
        self.node_p = nodes["p_node"]
        self.node_n = nodes["n_node"]

    def xyce_line(self):
        return  (Element.xyce_element(self) + " n_" +
                self.node_p + " n_" + self.node_n + " " +
                self.model + " " + self.value + " " + self.params + "\n")

    def v_measurement_line(self):
        return f"V(n_{self.node_p}, n_{self.node_n}) "

    def v_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"V({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"VM({self.name}),VP({self.name})"

    def i_measurement_line(self):
        return f"I({self.xyce_element()}) "

    def i_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"I({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"IM({self.name}),IP({self.name})"

    def p_measurement_line(self):
        return f"P({self.xyce_element()}) "

    def p_measurement_alias(self):
        return f"P({self.name})"

    def lib_file(self):
        return self.model_path
################################################################################

### Linear elements ############################################################
class Capacitor(TwoTerminal):
    type = "C"
    # C<name> <+ node> <- node> [model name] <value> [IC=<initial value>]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        self.value = init_data.get("C")
        analysis_type = init_data.get("analysis_type")
        if analysis_type == "Transient":
            # Don't set the value to zero for AC analysis
            self.params = "IC="+init_data["IC"]
        self.model = init_data.get("model","")

class Inductor(TwoTerminal):
    type = "L"
    # L<name> <+ node> <- node> [model name] <value> [IC=<initial value>]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.value = init_data.get("L")
        self.init_data = init_data
        analysis_type = init_data.get("analysis_type")
        if analysis_type == "Transient":
            # Don't set the value to zero for AC analysis
            self.params = "IC="+init_data["IC"]
        self.model = init_data.get("model","")

class CoupledInductor(TwoTerminal):
    type = "L"
    instance_counter = 0
    # L<name> <+ node> <- node> [model name] <value> [IC=<initial value>]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        analysis_type = init_data.get("analysis_type")
        if analysis_type == "Transient":
            # Don't set the value to zero for AC analysis
            self.params = "IC="+init_data["IC"]
        self.value = init_data.get("L")
        self.xyce_couplings_dict = ast.literal_eval(init_data.get("xyce_couplings_dict"))
        CoupledInductor.lines = []
        CoupledInductor.instance_counter += 1

        # xyce_couplings_dict is the same for every inductor
        # The first instance creates the mutual inductor (K) lines
        if CoupledInductor.instance_counter == 1:
            # Get the list of coupled inductors
            for ind_name in self.xyce_couplings_dict:
                # Get the list of inductors coupled to the current inductor
                this_ind_couplings = self.xyce_couplings_dict.get(ind_name)
                for coupled_to_ind_name, value in this_ind_couplings.items():
                    if not coupled_to_ind_name == ind_name:
                        coef = init_data.get("coupling_coefficient")
                        # Invalid coefficient values
                        if float(coef) > 1:
                            coef = "1"
                        elif float(coef) < -1:
                            coef = "-1"
                        # Define mutual inductor lines
                        mutual_name = (ind_name + coupled_to_ind_name)
                        mutual_name_reversed = (coupled_to_ind_name + ind_name)
                        mutual_name = mutual_name.replace(" ","")
                        mutual_name_reversed = mutual_name_reversed.replace(" ","")

                        equivalent_line = False
                        for line in CoupledInductor.lines:
                            if "k"+mutual_name_reversed in line:
                                equivalent_line = True

                        if not equivalent_line:
                            CoupledInductor.lines.append(f'k{mutual_name}'\
                            f'{" L_"+coupled_to_ind_name.replace(" ","_")} '\
                            f'{"L_"+ind_name.replace(" ","_")}'\
                            f' {coef}\n')

class Resistor(TwoTerminal):
    type = "R"
    # R<name> <+ node> <- node> [model name] <value> [L=<length>] [W=<width>]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        self.value = init_data.get("R")
        self.params = init_data.get("PLACEHOLDER","")
        self.model = init_data.get("model","")

class VoltageSource(TwoTerminal):
    type = "V"
    # V<name> <(+) node> <(-) node> [ [DC] <value> ]
    # + [AC [magnitude value [phase value] ] ] [transient specification]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        tr_spec = []

        def vtri_spec():
            V0 = init_data["vmin"]
            V1 = init_data["vmax"]
            T1 = float(init_data["trise"])
            T2 = float(init_data["tfall"])
            return f"PWL 0S {V0} {str(T1)} {str(V1)} {str(T1+T2)} {V0} R=0"

        for k in init_data.keys():
            if not k in ["analysis_type", "meas_v", "meas_i", "meas_p"]:
                tr_spec.append(f"{k}={init_data[k]}")

        tr_spec_dict = {"Vdc":init_data["voltage"] if elem_type == "Vdc" else "",
                        "I_meas": init_data["voltage"] if elem_type == "I_meas" else "",
                        "Vsin":"SIN " + " ".join(tr_spec) if elem_type == "Vsin" else "",
                        "Vpulse":"PULSE " + " ".join(tr_spec) if elem_type == "Vpulse" else "",
                        "Vexp": "EXP " + " ".join(tr_spec) if elem_type == "Vexp" else "",
                        "Vtri":vtri_spec() if elem_type == "Vtri" else ""
                        }

        ac_spec_dict = {"Vdc":"AC " + init_data["voltage"] if elem_type == "Vdc" else "",
                        "I_meas": init_data["voltage"] if elem_type == "I_meas" else "",
                        "Vsin":"AC " + init_data["VA"]  + " " + init_data["PHASE"] if elem_type == "Vsin" else "",
                        "Vpulse":"AC" + init_data["V1"] if elem_type == "Vpulse" else "",
                        "Vexp": "AC" + init_data["V1"] if elem_type == "Vexp" else "",
                        "Vtri":"AC" + init_data["vmax"] if elem_type == "Vtri" else ""
                        }

        if init_data["analysis_type"] == "AC small-signal":
            self.source_spec = ac_spec_dict[elem_type]
        else:
            self.source_spec = tr_spec_dict[elem_type]

    # Needs special xyce_line method
    def xyce_line(self):
        return  (Element.xyce_element(self) + " n_" +
                self.node_p + " n_" + self.node_n + " " +
                self.source_spec  + "\n")

    def as_measurement(self, analysis_type):
        # Used when the voltage source is a current measurement. Called on
        # tse2xyce, based on the element name.
        if analysis_type == "Transient":
            return  f"I(V_{self.name})"
        elif analysis_type == "AC small-signal":
            return  f"IM(V_{self.name}) IP(V_{self.name})"

class CurrentSource(TwoTerminal):
    type = "I"
    # I<name> <(+) node> <(-) node> [ [DC] <value> ]
    # + [AC [magnitude value [phase value] ] ] [transient specification]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        tr_spec = []
        self.elem_type = elem_type
        self.init_data = init_data

        for k in init_data.keys():
            if not k == "analysis_type":
                tr_spec.append(f"{k}={init_data[k]}")

        tr_spec_dict = {"Idc":init_data["current"] if elem_type == "Idc" else "",
                        "V_meas": init_data["current"] if elem_type == "V_meas" else "",
                        "Isin":"SIN " + " ".join(tr_spec) if elem_type == "Isin" else "",
                        "Ipulse":"PULSE " + " ".join(tr_spec) if elem_type == "Ipulse" else "",
                        "Iexp": "EXP " + " ".join(tr_spec) if elem_type == "Iexp" else "",
                        }

        ac_spec_dict = {"Idc":"AC " + init_data["current"] if elem_type == "Idc" else "",
                        "V_meas": init_data["current"] if elem_type == "V_meas" else "",
                        "Isin":"AC " + init_data["VA"]  + " " + init_data["PHASE"] if elem_type == "Isin" else "",
                        "Ipulse":"AC" + init_data["V0"] if elem_type == "Ipulse" else "",
                        "Iexp": "AC" + init_data["V0"] if elem_type == "Iexp" else "",
                        }

        if init_data["analysis_type"] == "AC small-signal":
            self.source_spec = ac_spec_dict[elem_type]
        else:
            self.source_spec = tr_spec_dict[elem_type]

    # Needs special xyce_line method
    def xyce_line(self):
        if self.elem_type == "V_meas":
            return ""
        else:
            return  (Element.xyce_element(self) + " n_" +
                    self.node_p + " n_" + self.node_n + " " +
                    self.source_spec  + "\n")

    def as_measurement(self, analysis_type):
        if analysis_type == "Transient":
            return  f"V(n_{self.node_p},n_{self.node_n})"
        elif analysis_type == "AC small-signal":
            return  f"VM(n_{self.node_p},n_{self.node_n}) VP(n_{self.node_p},n_{self.node_n})"
################################################################################

### General Non-Linear Devices #################################################
class Memristor(TwoTerminal):
    type = "ymemristor"
    # ymemristor <name> <(+) node> <(-) node> <model>
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        self.model = init_data["model_name"]
        self.model_path = init_data["model_path"]
        # Some component models are subcircuit-based
        if init_data["subc_model"] == "True":
            self.type = "X"
    # No subcircuit lines should be added when a subc-based model is used
    def xyce_subc(self):
        return ""



################################################################################


### Semiconductors #############################################################

class Diode(TwoTerminal):
    type = "D"
    # D<name> <(+) node> <(-) node> <model name> [area value]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        self.model = init_data["model_name"]
        self.model_path = init_data["model_path"]
        # Some component models are subcircuit-based
        if init_data["subc_model"] == "True":
            self.type = "X"
    # No subcircuit lines should be added when a subc-based model is used
    def xyce_subc(self):
        return ""

class Fet(Element):
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name)
        self.init_data = init_data
        self.model = init_data["model_name"]
        self.nodeinfo = "n_" + " n_".join([nodes["drain"],
                nodes["gate"], nodes["src"], nodes["src"]])
        self.model_path = init_data["model_path"]
        # Some component models are subcircuit-based
        if init_data["subc_model"] == "True":
            self.type = "X"
            # May have to check for the number of subcircuit nodes in the future
            self.nodeinfo = "n_" + " n_".join([nodes["drain"],
                    nodes["gate"], nodes["src"]])
    # No subcircuit lines should be added when a subc-based model is used
    def xyce_subc(self):
        return ""

    def xyce_line(self):
        return  f'{Element.xyce_element(self)} {self.nodeinfo}'\
                    f' {self.model} \n'

    def v_measurement_nodes(self):
        return ["n_"+self.node_p, "n_"+self.node_n]

    def i_measurement_element(self):
        return self.xyce_element()

    def p_measurement_element(self):
        return self.name

class Mosfet(Fet):
    type = "M"
        # M<name> <drain node> <gate node> <source node>
        # + <bulk/substrate node> <model name>
        # + [PARAMS]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(elem_type, name, nodes, init_data)
        self.init_data = init_data
    # FUTURE:
    # Check special BSIMSOI and MVS forms

class Jfet(Fet):
    type = "J"
    # J<name> <drain node> <gate node> <source node> <model name> + [area
    # value] [device parameters]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(elem_type, name, nodes, init_data)
        self.init_data = init_data

class Mesfet(Fet):
    type = "Z"
    # Z<name> < drain node> <gate node> <source node> <model name>
    # + [area value] [device parameters]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(elem_type, name, nodes, init_data)
        self.init_data = init_data
        self.nodeinfo = "n_" + " n_".join([nodes["drain"],
                nodes["gate"], nodes["src"]])

# Not a Fet, but shares much of the syntax
class Bjt(Fet):
    type = "Q"
        # Q<name> <collector node> <base node> <emitter node>
        # + [substrate node] <model name> [area value]
    def __init__(self, elem_type, name, nodes, init_data):
        # nodes dict keys are different from what the Fet class demands
        fake_nodes = {"drain":"0","gate":"0","src":"0"}
        super().__init__(elem_type, name, fake_nodes, init_data)
        self.init_data = init_data
        self.nodeinfo = "n_" + " n_".join([nodes["col"],
                nodes["base"], nodes["emit"]])
################################################################################


### Voltage controlled elements ################################################
class VoltageControlled(Element):
    def __init__(self, name, nodes, init_data):
        super().__init__(name)
        self.init_data = init_data
        self.node_p = nodes["p_node"]
        self.node_n = nodes["n_node"]
        self.ctrl_p = nodes["p_ctrl"]
        self.ctrl_n = nodes["n_ctrl"]

    def xyce_line(self):
        return  (Element.xyce_element(self) + " n_" +
                self.node_p + " n_" + self.node_n + " " + " n_" +
                self.ctrl_p + " n_" + self.ctrl_n + " " +
                self.model + "\n")

class VoltageControlledSwitch(VoltageControlled):
    type = "S"
    instance_counter = 0
    # S<name> <(+) switch node> <(-) switch node>
    # + <(+) control node> <(-) control node>
    # + <model name> [ON] [OFF]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes, init_data)
        VoltageControlledSwitch.instance_counter += 1
        self.model = f"VoltCtrldSwitch{self.instance_counter}"

    def model_lines(self):
        if self.init_data["logic"] == "Active Low":
            logic_on = "0"
            logic_off = "1"
        elif self.init_data["logic"] == "Active High":
            logic_on = "1"
            logic_off = "0"
        return  f'.MODEL {self.model} VSWITCH '\
                f'RON={self.init_data["r_on"]} ROFF={self.init_data["r_off"]} '\
                f'ON={logic_on} OFF={logic_off}\n'

class VoltageControlledVoltageSource(VoltageControlled):
    type = "E"
    # E<name> <(+) node> <(-) node> <(+) controlling node>
    # + <(-) controlling node> <gain>
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes, init_data)
        # No model used, only the gain
        self.model = init_data["gain"]

    # FUTURE:
    # E<name> <(+) node> <(-) node> VALUE = <expression>
    # + [device parameters]
    # E<name> <(+) node> <(-) node> TABLE <expression> =
    # + < <input value>,<output value> >*
    # E<name> <(+) node> <(-) node> POLY(<value>)
    # + [<+ control node> <- control node>]*
    # + [<polynomial coefficient value>]*

class VoltageControlledCurrentSource(VoltageControlled):
    type = "G"
    # G<name> <(+) node> <(-) node> <(+) controlling node>
    # + <(-) controlling node> <transconductance>
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes, init_data)
        # No model used, only the gain
        self.init_data = init_data
        self.model = init_data["transc"]

    # FUTURE:
    # G<name> <(+) <node> <(-) node> VALUE = <expression>
    # G<name> <(+) <node> <(-) node> TABLE <expression> =
    # + < <input value>,<output value> >*
    # G<name> <(+) <node> <(-) node> POLY(<value>)
    # + [<+ controlling node> <- controlling node>]*
    # + [<polynomial coefficient>]*

################################################################################


### Currrent controlled elements ###############################################

class CurrentControlled(TwoTerminal):
    def __init__(self, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        self.ctrl_name = "V__I_meas__" + init_data["ctrl_name"]

    def xyce_line(self):
        ''' Xyce line construction - Current controlled element. '''
        return  (Element.xyce_element(self) + " n_" +
                self.node_p + " n_" + self.node_n + " " +
                self.ctrl_name + " " + self.model + "\n")

class CurrentControlledSwitch(CurrentControlled):
    type = "W"
    instance_counter = 0
    # W<name> <(+) switch node> <(-) switch node>
    # + <control node voltage source>
    # + <model name> [ON] [OFF]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes, init_data)
        CurrentControlledSwitch.instance_counter += 1
        self.model = f"CurCtrldSwitch{self.instance_counter}"

    def model_lines(self):
        if self.init_data["logic"] == "Active Low":
            logic_on = "0"
            logic_off = "1"
        elif self.init_data["logic"] == "Active High":
            logic_on = "1"
            logic_off = "0"
        return  f'.MODEL {self.model} ISWITCH '\
                f'RON={self.init_data["r_on"]} ROFF={self.init_data["r_off"]} '\
                f'ON={logic_on} OFF={logic_off}\n'

class CurrentControlledCurrentSource(CurrentControlled):
    type = "F"
    # F<name> <(+) node> <(-) node>
    # + <controlling V device name> <gain>
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes, init_data)
        # No model used, only the gain
        self.model = init_data["gain"]
        self.init_data = init_data
    # FUTURE
    # F<name> <(+) node> <(-) node> POLY(<value>)
    # + <controlling V device name>*
    # + < <polynomial coefficient value> >*

class CurrentControlledVoltageSource(CurrentControlled):
    type = "H"
    # H<name> <(+) node> <(-) node>
    # + <controlling V device name> <transresistance>
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes, init_data)
        # No model used, only the gain
        self.model = init_data["transr"]
        self.init_data = init_data
    # FUTURE
    # H<name> <(+) node> <(-) node> POLY(<value>)
    # + <controlling V device name>*
    # + < <polynomial coefficient value> >*
################################################################################

### Transmission Lines #########################################################

class TransmissionLine(Element):
    def __init__(self, name, nodes):
        super().__init__(name)
        self.init_data = init_data
        self.ports = "n_" + " n_".join( [nodes["P1_p"],nodes["P1_n"],
                                        nodes["P2_p"],nodes["P2_n"]])

    def xyce_line(self):
        return  f'{Element.xyce_element(self)} {self.ports} {self.model}\n'

class LosslessTransmissionLine(TransmissionLine):
    type = "T"
    # T<name> <port 1 (+) node> <port 1 (-) node>
    # + <port 2 (+) node> <port 2 (-) node>
    # + Z0=<value> [TD=<value>] [F=<value> [NL=<value>]]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        self.init_data = init_data
        self.model = f'Z0={init_data["Z0"]} TD={init_data["TD"]}'

class LossyTransmissionLine(TransmissionLine):
    type = "O"
    instance_counter = 0
    # O<name> <A port (+) node> <A port (-) node>
    # + <B port (+) node> <B port (-) node> [model name]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name, nodes)
        LossyTransmissionLine.instance_counter += 1
        self.model = f"LossyTRA{self.instance_counter}"
        self.init_data = init_data

    def model_lines(self):
        # Pops "interp" for it is not a Xyce parameter
        interp_type = self.init_data.pop("interp")
        # List of valid parameters
        modparams = [f"{k}={self.init_data[k]}" for k in self.init_data.keys()]
        if interp_type == "Mixed":
            modparams.append("MIXEDINTERP=1")
        if interp_type == "Linear":
            modparams.append("LININTERP=1")
        modparams = " ".join(modparams).replace("True","1").replace("False","0")

        return f'.MODEL {self.model} LTRA {modparams}\n'

class LumpedTransmissionLine(TransmissionLine):
    type = "ytransline"
    instance_counter = 0
    # ytransline <name> <Input port> <Output port> testLine
    # + len=<value> lumps=<value>
    def __init__(self, elem_type, name, nodes, init_data):
        # LumpedTL is a two-port device. TransmissionLine class demands four.
        nodes.update({"P1_n":"0", "P2_n":"0"})
        super().__init__(name, nodes)
        self.init_data = init_data
        LumpedTransmissionLine.instance_counter += 1
        self.ports = "n_" + " n_".join( [nodes["P1_p"], nodes["P2_p"]])
        self.model = f"testLine{self.instance_counter}"

    def xyce_line(self):
        return  f'ytransline {self.name} {self.ports} {self.model} '\
        f'LEN={self.init_data["LEN"]} LUMPS={self.init_data["LUMPS"]}\n'

    def model_lines(self):
        data = self.init_data
        modparams = f'R={data["R"]} L={data["L"]} C={data["C"]}'
        return f'.MODEL {self.model} transline {modparams}\n'

################################################################################

### Behavioral Digital Devices #################################################
class BehavioralDigitalDevice(Element):
    type = "U"
    # U<name> <type>(<num inputs>) [digital power node]
    # + [digital ground node] <input node>* <output node>*
    # + <model name> [device parameters]
    def __init__(self, elem_type, name, nodes, init_data):
        super().__init__(name)
        self.init_data = init_data
        self.nodes = nodes
        self.device_type = init_data["type"]

    def xyce_line(self):
        # Digital Ground Node is the system ground (0)
        # Digital Power Node is a new voltage source defined by "output"
        ouput_voltage = self.init_data["output_voltage"]
        # Fixing inputs in 2 for now
        num_inputs = len(self.nodes)-1
        in_nodes = ["n_" + self.nodes[k] for k in list(self.nodes.keys()) if k != "out"]
        out_node = self.nodes["out"]
        model_name = f"BD{self.name}"

        return f'''V_PN_{self.name} PWRNODE{self.name} 0 {float(ouput_voltage)}
U_{self.name} {self.device_type}({num_inputs}) PWRNODE{self.name} 0 \
{" ".join(in_nodes)} n_{out_node} {model_name} IC1=FALSE\n'''

    def model_lines(self):
        clo = self.init_data["CLO"]
        chi = self.init_data["CHI"]
        s1tsw = self.init_data["S1TSW"]
        s0tsw = self.init_data["S0TSW"]
        s0vlo = self.init_data["S0VLO"]
        s0vhi = self.init_data["S0VHI"]
        s1vlo = self.init_data["S1VLO"]
        s1vhi = self.init_data["S1VHI"]
        s0rlo = self.init_data["S0RLO"]
        s0rhi = self.init_data["S0RHI"]
        s1rlo = self.init_data["S1RLO"]
        s1rhi = self.init_data["S1RHI"]
        rload = self.init_data["RLOAD"]
        cload = self.init_data["CLOAD"]
        delay = self.init_data["DELAY"]
        # Calculation of the resistances
        # Voltage reference is 1.1*output_voltage
        modparams = f'''+ CLO={clo} CHI={chi}
+ S0RLO={s0rlo} S0RHI={s0rhi} S0TSW={s0tsw}
+ S0VLO={s0vlo} S0VHI={s0vhi}
+ S1RLO={s1rlo} S1RHI={s1rhi} S1TSW={s1tsw}
+ S1VLO={s1vlo} S1VHI={s1vhi}
+ RLOAD={rload}
+ CLOAD={cload}
+ DELAY={delay}'''

        return f'''.MODEL BD{self.name} DIG (
{modparams})\n
'''


################################################################################


#### TESTING COMPOSITE CLASSES


### Subcircuit-syntax-dependent elements (composite) ###########################
class SubcircuitBased(Element):
    def __init__(self, elem_type, name, nodes, init_data, params):
        super().__init__(name)
        self.init_data = init_data
        self.model = init_data["model_name"]
        self.model_path = init_data["model_path"]
        self.nodeinfo = "n_" + " n_".join([node for node in nodes])
        self.type = "X"
        self.params = params

    # No subcircuit lines should be added when a subc-based model is used
    def xyce_subc(self):
        return ""

    def xyce_line(self):
        return  f'{Element.xyce_element(self)} {self.nodeinfo}'\
                    f' {self.model} {self.params}\n'

class IdealDiode(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        init_data["model_name"] = "id_diode"
        init_data["model_path"] = included_models_path + "id_diode.lib"
        self.nodes = [nodes["p_node"], nodes["n_node"]]
        r_on = init_data['r_on']
        vd_on = init_data['vd_on']
        if float(vd_on) < 0:
            vd_on = "0"
        params = f"R_ON={r_on} VD_ON={vd_on}"
        super().__init__(elem_type, name, self.nodes, init_data, params)

    def v_measurement_line(self):
        return f"V(n_{self.nodes[0]}, n_{self.nodes[1]}) "

    def v_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"V({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"VM({self.name}) VP({self.name})"

    def i_measurement_line(self):
        return f"I({self.xyce_element()}:V_MEAS) "

    def i_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"I({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"IM({self.name}) IP({self.name})"

    def p_measurement_line(self):
        return f"P({self.xyce_element()}:SW_DIODE) "

    def p_measurement_alias(self):
        return f"P({self.name})"

class UnidirectionalSwitch(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        init_data["model_name"] = "unidir_switch"
        init_data["model_path"] = included_models_path + "unidirectional_switch.lib"
        self.nodes = [nodes["drain"], nodes["gate"], nodes["src"]]
        r_on = init_data['r_on']
        vd_on = init_data['vd_on']
        if float(vd_on) < 0:
            vd_on = "0"
        vsw_on = init_data['vsw_on']
        if float(vsw_on) < 0:
            vsw_on = "0"
        params = f"R_ON={r_on} VD_ON={vd_on} VSW_ON={vsw_on}"
        super().__init__(elem_type, name, self.nodes, init_data, params)

    def v_measurement_line(self):
        return f"V(n_{self.nodes[0]}, n_{self.nodes[2]}) "

    def v_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"V({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"VM({self.name}),VP({self.name})"

    def i_measurement_line(self):
        return f"I({self.xyce_element()}:V_MEAS_SW) I({self.xyce_element()}:V_MEAS_D) "

    def i_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"Isw({self.name}),Id({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"IswM({self.name}),IswP({self.name}),IdM({self.name}),IdP({self.name})"

    def p_measurement_line(self):
        return f"I({self.xyce_element()}+:SW_DIODE) "

    def p_measurement_alias(self):
        return f"P({self.name})"

    def g_measurement_line(self):
        return f"V(n_{self.nodes[1]}, 0) "

    def g_measurement_alias(self):
        if self.init_data["analysis_type"]=="Transient":
            return f"Vg({self.name})"
        elif self.init_data["analysis_type"]=="AC small-signal":
            return f"VgM({self.name}),VgP({self.name})"

class IdealTransformer2W(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        init_data["model_name"] = "id_transformer2w"
        init_data["model_path"] = included_models_path + "id_transformer2w.lib"
        self.nodes = [nodes["prm_1"], nodes["prm_2"], nodes["sec_1"], nodes["sec_2"]]
        n1 = init_data['n1']
        n2 = init_data['n2']
        params = f"N1={n1} N2={n2}"
        super().__init__(elem_type, name, self.nodes, init_data, params)

class OperationalAmplifier(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        if init_data["analysis_type"]=="AC small-signal":
            init_data["model_name"] = "op_amp_3"
        else:
            if init_data["model_type"]=="Ideal":
                init_data["model_name"] = "op_amp_1"
            elif init_data["model_type"]=="Low-pass filter":
                init_data["model_name"] = "op_amp_2"
        init_data["model_path"] = included_models_path + "op-amp.lib"
        self.nodes = [nodes["non_inv"], nodes["inv"], nodes["Out"]]
        rf = init_data['Rf']
        cf = init_data['Cf']
        gain = init_data['gain']
        params = f'PARAMS: GAIN={gain} RES_FILTER={rf} CAP_FILTER={cf}'
        super().__init__(elem_type, name, self.nodes, init_data, params)

class ModelBasedOperationalAmplifier(SubcircuitBased):
        def __init__(self, elem_type, name, nodes, init_data):
            params = ""
            super().__init__(elem_type, name, nodes, init_data, params)

class Comparator(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        init_data["model_name"] = "comparator"
        init_data["model_path"] = included_models_path + "comparator.lib"
        self.nodes = [nodes["non_inv"], nodes["inv"], nodes["Out"]]
        params = f"PARAMS: VOUT={init_data['output_voltage']}"
        super().__init__(elem_type, name, self.nodes, init_data, params)

class PWM(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        init_data["model_name"] = "pwm"
        init_data["model_path"] = included_models_path + "pwm.lib"
        self.nodes = [nodes["duty"], nodes["Comp Out"], nodes["Out"]]
        params = f"PARAMS: VMAX={init_data['vmax']} TS={1/float(init_data['freq'])} DT={0.01*float(init_data['deadtime'])}"
        super().__init__(elem_type, name, self.nodes, init_data, params)

class DynamicSpiceComponent(SubcircuitBased):
    def __init__(self, elem_type, name, nodes, init_data):
        print(init_data)
        self.nodes = [nodes[n] for n in init_data["pin_order"].split(",")]
        params  = ""
        super().__init__(elem_type, name, self.nodes, init_data, params)

################################################################################

# Will not be directly implemented per initial considerations. May be used
# for constructing higher level components.

# class GenericSwitch
    # SW<name> <(+) switch node> <(-) switch node> <model name> [ON] [OFF]
    # <control = expression >

# class NonlinearDependentVoltageSource
    # B<name> <(+) node> <(-) node> V=ABM expression [device parameters]
    # B<name> <(+) node> <(-) node> I=ABM expression

# class BehavioralDigitalDevice
    # U<name> <type>(<num inputs>) [digital power node]
    # + [digital ground node] <input node>* <output node>*
    # + <model name> [device parameters]

# class AcceleratedMass
    # YACC <name> <acceleration node> <velocity node> <position node>
    # + [v0=<initial velocity>] [x0=<initial position>]

# class TCAD
    # YPDE <name> <node> [node] [model name]
    # + [device parameters]
    # YPDE <name> <node> <node> [node][node] [model name]|
    # + [device parameters]

# class PowerGrid
    # Y<type> <name> <input node1> <output node1>
    # + <input node2> <output node2> [device parameters]
