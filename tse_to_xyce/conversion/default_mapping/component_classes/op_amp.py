from .base import *
from ...output_functions import *
from ..constants import *
import os


class OperationalAmplifier(SubcircuitBased):
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
            "GAIN": tse_properties["gain"],
            "RES_FILTER": tse_properties["Rf"],
            "CAP_FILTER": tse_properties["Cf"]
        }

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        if self.circuit.simulation_parameters["analysis_type"] == "AC small-signal":
            model_name = "op_amp_3"
        else:
            if tse_properties["model_type"] == "Ideal":
                model_name = "op_amp_1"
            elif tse_properties["model_type"] == "Low-pass filter":
                model_name = "op_amp_2"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name, file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, "op-amp.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["non_inv"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["inv"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name)
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


##
class ModelBasedOperationalAmplifier(SubcircuitBased):
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

        model_name = tse_properties["model_name"]
        model_path = tse_properties["model_path"]

        component_model = ComponentModel(self.circuit, model_name, model_path)
        self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["n_node"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["p_node"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["vcc+"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["vcc-"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["out"].node.name)
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

