from .base import *
from ...output_functions import *
from ..constants import *
import os


class Constant(TwoTerminal):
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

        pass

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:
            nodes = [
                XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name),
                XYCE_NODE_PREFIX + "0"
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

        self.type = "V"
        # Create parallel resistor
        from .resistor import Resistor
        r_properties = {"R": "1e7"}
        new_r = Resistor("R", f"PARALLEL_{self.identifier()}", self.circuit, r_properties, tse_component=None)
        new_r.new_format_nodes = {" ".join(self.new_format_nodes)}
        self.created_instances_list.append(new_r)

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {self.new_format_properties["value"]}\n'


class Saturation(SubcircuitBased):
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
            "max": tse_properties["max"],
            "min": tse_properties["min"]
        }

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = "saturation"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"math_other.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:
            nodes = [
                XYCE_NODE_PREFIX + str(tse_component.terminals["In"].node.name),
                XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name),
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


class AbsoluteValue(SubcircuitBased):
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

        model_name = "abs"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"math_other.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:
            nodes = [
                XYCE_NODE_PREFIX + str(tse_component.terminals["In"].node.name),
                XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name),
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


class Gain(SubcircuitBased):
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

        new_format_properties = {"gain": tse_properties["gain"]}

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = "gain"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"math_other.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:
            nodes = [
                XYCE_NODE_PREFIX + str(tse_component.terminals["In"].node.name),
                XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name),
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


class TrigonometricFunction(SubcircuitBased):
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

        model_name = tse_properties["trig_fcn"]

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"math_trig.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:
            nodes = [
                XYCE_NODE_PREFIX + str(tse_component.terminals["In"].node.name),
                XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name),
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


class Sum(SubcircuitBased):
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

        sgn_dict = {"+": "1",
                    "-": "-1"}

        signs = tse_properties["signs"]

        new_format_properties = {f"S{idx + 1}": f"{sgn_dict.get(signs[idx])}" for idx in range(len(signs))}

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = "math_sum"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"math_sum.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:

            signs = tse_properties["signs"]
            sign_numbers = range(1, len(signs) + 1)
            nodes = [XYCE_NODE_PREFIX + str(tse_component.terminals[f"In{n}"].node.name) for n in sign_numbers]
            while len(nodes) < 5:
                nodes.append("0")  # Connect unused inputs to ground
            nodes.append(XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name))

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


class Product(SubcircuitBased):
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

        sgn_dict = {"*": "1",
                    "/": "-1"}

        operations = tse_properties["operations"]

        new_format_properties = {f"S{idx + 1}": f"{sgn_dict.get(operations[idx])}" for idx in range(len(operations))}

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = "math_prod"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, f"math_prod.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        if tse_component:

            operations = tse_properties["operations"]
            operation_numbers = range(1, len(operations) + 1)
            nodes = [XYCE_NODE_PREFIX + str(tse_component.terminals[f"In{n}"].node.name) for n in operation_numbers]
            while len(nodes) < 5:
                nodes.append("0")  # Connect unused inputs to ground
            nodes.append(XYCE_NODE_PREFIX + str(tse_component.terminals["Out"].node.name))

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
