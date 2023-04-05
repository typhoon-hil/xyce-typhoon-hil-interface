class Circuit:

    def __init__(self, name, simulation_parameters):
        self.name = name
        self.components = []
        self.simulation_parameters = simulation_parameters

class VoltageMeasurement:
    """ Defines a measurement the input component. """

    def __init__(self, circuit, node_p, node_n, measured_component, vgs=False):
        self.type = "MEASUREMENT"
        self.circuit = circuit
        self.node_p = node_p
        self.node_n = node_n
        self.measured_component = measured_component
        self.vgs = vgs

    def measurement_string(self):
        """ String to be added to the XYCE model to perform the measurement. """

        if self.circuit.simulation_parameters["analysis_type"] == "Transient":
            return [f"V({self.node_p},{self.node_n})"]
        elif self.circuit.simulation_parameters["analysis_type"] == "AC small-signal":
            return [f"VM({self.node_p},{self.node_n})", f"VP({self.node_p},{self.node_n})"]


class CurrentMeasurement:
    """ Defines a measurement the input component. """

    def __init__(self, circuit, measured_component, measured_subsystem_component=None):
        self.type = "MEASUREMENT"
        self.circuit = circuit
        self.measured_component = measured_component
        self.measured_subsystem_component = measured_subsystem_component

    def measurement_string(self):
        """ String to be added to the XYCE model to perform the measurement. """

        if self.measured_subsystem_component:
            meas_target = self.measured_component.identifier() + f":{self.measured_subsystem_component}"
        else:
            meas_target = self.measured_component.identifier()
        if self.circuit.simulation_parameters["analysis_type"] == "Transient":
            return [f"I({meas_target})"]
        elif self.circuit.simulation_parameters["analysis_type"] == "AC small-signal":
            return [f"IM({meas_target})", f"IP({meas_target})"]

class PowerMeasurement:
    """ Defines a measurement the input component. """

    def __init__(self, circuit, measured_component, measured_subsystem_component=None):
        self.type = "MEASUREMENT"
        self.circuit = circuit
        self.measured_component = measured_component
        self.measured_subsystem_component = measured_subsystem_component

    def measurement_string(self):
        """ String to be added to the XYCE model to perform the measurement. """

        if self.measured_subsystem_component:
            meas_target = self.measured_component.identifier() + f":{self.measured_subsystem_component}"
        else:
            meas_target = self.measured_component.identifier()

        return [f"P({meas_target})"]


class ComponentModel:
    """ Component models may be shared by Xyce components. """

    def __init__(self, circuit, name, file_path=None, model_string=""):
        self.type = "COMPONENT_MODEL"
        self.name = name
        self.circuit = circuit
        self.model_string = model_string
        self.file_path = file_path

        # Avoid repeating include lines
        self.include_line = f'.include "{self.file_path}"\n'
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL" and not comp == self:
                if comp.include_line == self.include_line:
                    self.include_line = ""

    def output_line(self):
        if self.file_path:
            return self.include_line
        else:
            return self.model_string


class Component:
    """ Circuit components base class. """

    def __init__(self, name, circuit):
        self.name = name
        self.circuit = circuit

    def identifier(self):
        # Xyce example: R_R1
        return f'{self.type.upper()}_{self.name.replace(" ", "_")}'

    def output_line(self):
        return ""


class SubcircuitBased(Component):

    def __init__(self, converted_comp_type, name, circuit, model, new_format_properties, tse_component):
        self.type = "X"
        self.name = name
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties
        self.model = model

    def output_line(self):

        component_properties = [f"{k}={v}" for k, v in self.new_format_properties.items()]

        return f'{self.identifier()} {" ".join(self.new_format_nodes)}' \
               f' {self.model.name} PARAMS: {" ".join(component_properties).upper()}\n'


class ModelBased(Component):

    def __init__(self, converted_comp_type, name, circuit, model, new_format_properties, tse_component):
        self.name = name
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties
        self.model = model

    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        if tse_properties.get("meas_v") == "True":
            node_p = nodes[0]
            node_n = nodes[1]
            v_meas = VoltageMeasurement(circuit, node_p, node_n, self)
            self.created_instances_list.append(v_meas)

        if tse_properties.get("meas_g") == "True":
            node_p = nodes[1]
            node_n = nodes[2]
            g_meas = VoltageMeasurement(circuit, node_p, node_n, self, vgs=True)
            self.created_instances_list.append(g_meas)

        if tse_properties.get("meas_i") == "True":
            i_meas = CurrentMeasurement(circuit, self)
            self.created_instances_list.append(i_meas)

        sim_mode = self.circuit.simulation_parameters["analysis_type"]
        if tse_properties.get("meas_p") == "True" and not sim_mode == "AC small-signal":
            p_meas = PowerMeasurement(circuit, self)
            self.created_instances_list.append(p_meas)

    def output_line(self):

        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {self.model.name}'

class TwoTerminal(Component):

    def __init__(self, converted_comp_type, name, circuit, model, new_format_properties, tse_component):
        self.name = name
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties
        self.model = model

    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        if tse_properties.get("meas_v") == "True":
            node_p = nodes[0]
            node_n = nodes[1]
            v_meas = VoltageMeasurement(circuit, node_p, node_n, self)
            self.created_instances_list.append(v_meas)

        if tse_properties.get("meas_i") == "True":
            i_meas = CurrentMeasurement(circuit, self)
            self.created_instances_list.append(i_meas)

        sim_mode = self.circuit.simulation_parameters["analysis_type"]
        if tse_properties.get("meas_p") == "True" and not sim_mode == "AC small-signal":
            p_meas = PowerMeasurement(circuit, self)
            self.created_instances_list.append(p_meas)

    def output_line(self):

        return f''

class CurrentControlled(Component):

    def __init__(self, converted_comp_type, name, circuit, model, new_format_properties, tse_component):
        self.name = name
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties
        self.model = model

    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        if tse_properties.get("meas_v") == "True":
            node_p = nodes[0]
            node_n = nodes[1]
            v_meas = VoltageMeasurement(circuit, node_p, node_n, self)
            self.created_instances_list.append(v_meas)

        if tse_properties.get("meas_i") == "True":
            i_meas = CurrentMeasurement(circuit, self)
            self.created_instances_list.append(i_meas)

        sim_mode = self.circuit.simulation_parameters["analysis_type"]
        if tse_properties.get("meas_p") == "True" and not sim_mode == "AC small-signal":
            p_meas = PowerMeasurement(circuit, self)
            self.created_instances_list.append(p_meas)

    def output_line(self):
        gain = self.new_format_properties.get("gain")
        transr = self.new_format_properties.get("transr")
        return f'{self.identifier()} {" ".join(self.new_format_nodes)}' \
               f' V_{self.new_format_properties["ctrl_name"]} {self.model.name if self.model else gain if gain else transr}\n'

class VoltageControlled(Component):

    def __init__(self, converted_comp_type, name, circuit, model, new_format_properties, tse_component):
        self.name = name
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties
        self.model = model

    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        if tse_properties.get("meas_v") == "True":
            node_p = nodes[0]
            node_n = nodes[1]
            v_meas = VoltageMeasurement(circuit, node_p, node_n, self)
            self.created_instances_list.append(v_meas)

        if tse_properties.get("meas_i") == "True":
            i_meas = CurrentMeasurement(circuit, self)
            self.created_instances_list.append(i_meas)

        sim_mode = self.circuit.simulation_parameters["analysis_type"]
        if tse_properties.get("meas_p") == "True" and not sim_mode == "AC small-signal":
            p_meas = PowerMeasurement(circuit, self)
            self.created_instances_list.append(p_meas)

    def output_line(self):
        gain = self.new_format_properties.get("gain")
        transc = self.new_format_properties.get("transc")
        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {self.model.name if self.model else gain if gain else transc}\n'


class BehavioralDigitalDevice(Component):

    def __init__(self, converted_comp_type, name, circuit, model, new_format_properties, tse_component):
        self.name = name
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties
        self.model = model
        self.type = "U"
        self.created_vsource = self.create_digital_voltage_source()

    def create_digital_voltage_source(self):
        """ The output voltage level of the behavioral digital devices is defined by this voltage source. """

        from .vsource import VoltageSource

        # Digital Ground Node is the system ground (0)
        output_voltage = float(self.new_format_properties["output_voltage"])

        vsource_props = {
                            "voltage": output_voltage,
                            "meas_v": "False",
                            "meas_i": "False",
                            "meas_p": "False"
        }

        v_digital = VoltageSource("VDC", "DIG_PWR_" + self.name, self.circuit, vsource_props, tse_component=None)
        v_digital.new_format_nodes = [f"N_DIGPWR_{self.name}", "0"]

        self.created_instances_list.append(v_digital)

        return v_digital


    def output_line(self):
        """
        U<name> <type>(<num inputs>) [digital power node]
        + [digital ground node] <input node>* <output node>*
        + <model name> [device parameters]
        """

        in_nodes = self.new_format_nodes[:-1]
        out_node = self.new_format_nodes[-1]

        device_type = self.new_format_properties['type']
        num_inputs = len(in_nodes)

        vsource_nodes = self.created_vsource.new_format_nodes

        return f'{self.identifier()} {device_type}({num_inputs}) {vsource_nodes[0]} {vsource_nodes[1]} ' \
               f'{" ".join(in_nodes)} {out_node} {self.model.name} IC1=FALSE\n'


class InductorCoupling(Component):

    def __init__(self, name, circuit, new_format_properties, tse_component):
        self.name = name
        self.type = "K"
        self.tse_component = tse_component
        self.circuit = circuit
        self.new_format_properties = new_format_properties

        # List with the inductors coupled by this InductorCoupling
        self.inductor1 = tse_component.name
        self.inductor2 = self.new_format_properties.get("coupled_to_ind_name")
        self.coupled_inductors = [self.inductor1, self.inductor2]

    def output_line(self):

        return f'k{self.name}' \
             f'{" L_" + self.inductor1.replace(" ", "_")} ' \
             f'{"L_" + self.inductor2.replace(" ", "_")}' \
             f' {self.new_format_properties.get("coef")}\n'







