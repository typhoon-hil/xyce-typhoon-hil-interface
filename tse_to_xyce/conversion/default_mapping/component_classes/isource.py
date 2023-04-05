from .base import *
from ...output_functions import *
from ..constants import *
import os


class CurrentSource(TwoTerminal):
    """ Converted component class. """

    def __init__(self, converted_comp_type, name, circuit, tse_properties, tse_component):
        self.type = converted_comp_type
        self.name = name
        self.circuit = circuit

        # Some TSE components require more than one instance/class
        self.created_instances_list = [self]

        # Filter unused TSE properties and create new ones
        self.new_format_properties = self.create_new_format_properties_dict(self, tse_properties, tse_component)

        # Define the nodes
        self.new_format_nodes = self.define_nodes(self, tse_properties, tse_component)

        # Create the measurements
        self.create_measurements(self, self.circuit, self.new_format_nodes, tse_properties, tse_component)

        # Create the component model object
        self.component_model = self.create_component_model(self, tse_properties, tse_component)

        # Run parent initialization code
        super().__init__(self.type, self.name, self.circuit,
                         self.component_model, self.new_format_properties, tse_component)

        # Apply extra necessary conversion steps
        self.extra_conversion_steps(self, tse_properties, tse_component)

    @staticmethod
    def create_new_format_properties_dict(self, tse_properties, tse_component):
        """ Filters unused TSE properties and creates new ones. Returns a dictionary with the new properties. """

        new_format_properties = {}

        source_tr_spec_properties = []
        for k in tse_properties.keys():
            if k not in ["meas_v", "meas_i", "meas_p"]:
                source_tr_spec_properties.append(f"{k}={tse_properties[k]}")

        if self.type == "IDC":
            transient_spec = tse_properties["current"]
        elif self.type in ["V_MEAS", "V_MEAS_OUT"]:
            transient_spec = "0"
            new_format_properties["is_measurement"] = True
        elif self.type == "ISIN":
            transient_spec = f"SIN {' '.join(source_tr_spec_properties)}"
        elif self.type == "IPULSE":
            transient_spec = f"PULSE {' '.join(source_tr_spec_properties)}"
        elif self.type == "IEXP":
            transient_spec = f"EXP {' '.join(source_tr_spec_properties)}"

        new_format_properties["transient_spec"] = transient_spec

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        pass

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["p_node"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["n_node"].node.name),
        ]

        for idx, n in enumerate(nodes):
            if n == f"{XYCE_NODE_PREFIX}0":
                nodes[idx] = "0"

        return nodes

    @staticmethod
    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        tse_properties["meas_v"] = "True" if self.type in ["V_MEAS", "V_MEAS_OUT"] else tse_properties["meas_v"]
        tse_properties["meas_i"] = "False" if self.circuit.simulation_parameters[
                                                  "analysis_type"] == "AC small-signal" else None
        super().create_measurements(circuit, nodes, tse_properties, tse_component)

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        self.type = "I"

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        if self.new_format_properties.get("is_measurement"):
            self.created_instances_list.remove(self)

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        return f'{self.identifier()} {" ".join(self.new_format_nodes)}' \
               f' {self.new_format_properties.get("transient_spec")}\n'


class CurrentSmallSignal(TwoTerminal):
    """ Converted component class. """

    def __init__(self, converted_comp_type, name, circuit, tse_properties, tse_component):
        self.type = converted_comp_type
        self.name = name
        self.circuit = circuit

        # Some TSE components require more than one instance/class
        self.created_instances_list = [self]

        # Filter unused TSE properties and create new ones
        self.new_format_properties = self.create_new_format_properties_dict(self, tse_properties, tse_component)

        # Define the nodes
        self.new_format_nodes = self.define_nodes(self, tse_properties, tse_component)

        # Create the measurements
        self.create_measurements(self, self.circuit, self.new_format_nodes, tse_properties, tse_component)

        # Create the component model object
        self.component_model = self.create_component_model(self, tse_properties, tse_component)

        # Run parent initialization code
        super().__init__(self.type, self.name, self.circuit,
                         self.component_model, self.new_format_properties, tse_component)

        # Apply extra necessary conversion steps
        self.extra_conversion_steps(self, tse_properties, tse_component)

    @staticmethod
    def create_new_format_properties_dict(self, tse_properties, tse_component):
        """ Filters unused TSE properties and creates new ones. Returns a dictionary with the new properties. """

        new_format_properties = {
            "VA": tse_properties["VA"],
            "PHASE": tse_properties["PHASE"]
        }

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        pass

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:
            nodes = [
                XYCE_NODE_PREFIX + str(tse_component.terminals["p_node"].node.name),
                XYCE_NODE_PREFIX + str(tse_component.terminals["n_node"].node.name),
            ]

            for idx, n in enumerate(nodes):
                if n == f"{XYCE_NODE_PREFIX}0":
                    nodes[idx] = "0"

            return nodes

    @staticmethod
    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        tse_properties["meas_i"] = "False" if self.circuit.simulation_parameters[
                                                  "analysis_type"] == "AC small-signal" else None
        super().create_measurements(circuit, nodes, tse_properties, tse_component)

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        self.type = "I"

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        return f'{self.identifier()} {" ".join(self.new_format_nodes)}' \
               f' AC {self.new_format_properties["VA"]} {self.new_format_properties["PHASE"]}\n'
