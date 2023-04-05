from .base import *
from ...output_functions import *
from ..constants import *
import os


class LosslessTransmissionLine(ModelBased):
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

        new_format_properties["Z0"] = tse_properties["Z0"]
        new_format_properties["TD"] = tse_properties["TD"]

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        pass

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["P1_p"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P1_n"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P2_p"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P2_n"].node.name),
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

        self.type = "T"

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        properties_str = [f"{p}={v}" for p, v in self.new_format_properties.items()]

        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {" ".join(properties_str)}\n'


class LossyTransmissionLine(ModelBased):
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

        interp_type = new_format_properties.pop("interp")

        if interp_type == "Mixed":
            new_format_properties["MIXEDINTERP"] = "1"
        elif interp_type == "Linear":
            new_format_properties["LININTERP"] = "1"

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = f"LossyTL_{tse_component.name}"
        properties_str = [f"{p}={v}" for p, v in self.new_format_properties.items()]

        model_string = f'.MODEL {model_name} LTRA {" ".join(properties_str)}\n'

        component_model = ComponentModel(self.circuit, model_name, model_string=model_string)
        self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["P1_p"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P1_n"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P2_p"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P2_n"].node.name),
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

        self.type = "O"

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {self.component_model.name}\n'



class LumpedTransmissionLine(ModelBased):
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

        new_format_properties["LEN"] = tse_properties["LEN"]
        new_format_properties["LUMPS"] = tse_properties["LUMPS"]

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = f"TRANSLINE_{tse_component.name}"
        properties_str = f'R={tse_properties["R"]} L={tse_properties["L"]} C={tse_properties["C"]}'

        model_string = f'.MODEL {model_name} TRANSLINE {properties_str}\n'

        component_model = ComponentModel(self.circuit, model_name, model_string=model_string)
        self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["P1_p"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["P2_p"].node.name),
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

        self.type = "YTRANSLINE"

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        properties_str = [f"{p}={v}" for p, v in self.new_format_properties.items()]

        return f'YTRANSLINE {self.name} {" ".join(self.new_format_nodes)} {self.component_model.name} ' \
               f'{" ".join(properties_str)}\n'
