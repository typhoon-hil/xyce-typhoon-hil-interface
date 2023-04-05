from .base import *
from ...output_functions import *
from ..constants import *
from .resistor import Resistor
import os


class LogicPort(BehavioralDigitalDevice):
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

        new_format_properties = dict(tse_properties)

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = f"BD_{tse_component.name}"

        clo = tse_properties["CLO"]
        chi = tse_properties["CHI"]
        s1tsw = tse_properties["S1TSW"]
        s0tsw = tse_properties["S0TSW"]
        s0vlo = tse_properties["S0VLO"]
        s0vhi = tse_properties["S0VHI"]
        s1vlo = tse_properties["S1VLO"]
        s1vhi = tse_properties["S1VHI"]
        s0rlo = tse_properties["S0RLO"]
        s0rhi = tse_properties["S0RHI"]
        s1rlo = tse_properties["S1RLO"]
        s1rhi = tse_properties["S1RHI"]
        rload = tse_properties["RLOAD"]
        cload = tse_properties["CLOAD"]
        delay = tse_properties["DELAY"]

        model_string = f'''.MODEL {model_name} DIG (
        + CLO={clo} CHI={chi}
        + S0RLO={s0rlo} S0RHI={s0rhi} S0TSW={s0tsw}
        + S0VLO={s0vlo} S0VHI={s0vhi}
        + S1RLO={s1rlo} S1RHI={s1rhi} S1TSW={s1tsw}
        + S1VLO={s1vlo} S1VHI={s1vhi}
        + RLOAD={rload}
        + CLOAD={cload}
        + DELAY={delay})\n'''

        component_model = ComponentModel(self.circuit, model_name, model_string=model_string)
        self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        all_comp_terminals_ordered = list(t for t in tse_component.terminals if t != "out")
        all_comp_terminals_ordered.sort()
        all_comp_terminals_ordered.extend(t for t in tse_component.terminals if t == "out")

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals[t].node.name) for t in all_comp_terminals_ordered
        ]

        for idx, n in enumerate(nodes):
            if n == f"{XYCE_NODE_PREFIX}0":
                nodes[idx] = "0"

        return nodes

    @staticmethod
    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        pass

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        # Create a resistance to ground at the output

        props = {
            "R": "1e8"
        }

        out_node = self.new_format_nodes[-1]

        r_gnd = Resistor("R", f"{self.name}_{out_node}_gnd", self.circuit, props, tse_component=None)

        nodes = [out_node, "0"]

        r_gnd.new_format_nodes = nodes

        self.created_instances_list.append(r_gnd)

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()