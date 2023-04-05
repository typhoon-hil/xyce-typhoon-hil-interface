from .base import *
from ...output_functions import *
from ..constants import *
import os

class SignalToPower(SubcircuitBased):
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

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = "sgn_to_pwr"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"signal_to_power.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["p_node"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["n_node"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["In"].node.name)
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

        pass

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()
