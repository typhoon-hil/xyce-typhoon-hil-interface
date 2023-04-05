from .base import *
from ...output_functions import *
from ..constants import *
import os
import ast


class Inductor(TwoTerminal):
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
            "L": tse_properties["L"],
            "IC": tse_properties["IC"]
        }

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        return None

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

        super().create_measurements(circuit, nodes, tse_properties, tse_component)

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        pass

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        analysis_type = self.circuit.simulation_parameters["analysis_type"]
        ic = f' IC={self.new_format_properties.get("IC")}' if not analysis_type == "AC small-signal" else ""
        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {self.new_format_properties.get("L")}{ic}'


class CoupledInductor(TwoTerminal):
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
            "L": tse_properties["L"],
            "IC": tse_properties["IC"]
        }

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        return None

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

        super().create_measurements(circuit, nodes, tse_properties, tse_component)

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        self.type = "L"
        xyce_couplings_dict = ast.literal_eval(tse_properties.get("xyce_couplings_dict"))

        inductances = xyce_couplings_dict.get(self.name)
        inductances.pop(self.name)

        mutual_inductances = inductances  # Popped self inductance

        for coupled_inductor in mutual_inductances:
            coupling_not_found = True
            for component in self.circuit.components:
                if isinstance(component, InductorCoupling):
                    coupling_inductors = component.coupled_inductors
                    if self.name in coupling_inductors and coupled_inductor in coupling_inductors:
                        coupling_not_found = False
                        break
            if coupling_not_found:
                coupling_properties = {
                    "coef": mutual_inductances.get(coupled_inductor),
                    "coupled_to_ind_name": coupled_inductor,
                    "ind_name": self.name
                }
                # If the coupling between these inductors has not been added yet
                coupling_name = f"{self.name}_{coupled_inductor}"
                new_coupling = InductorCoupling(coupling_name,
                                                self.circuit,
                                                coupling_properties,
                                                self.tse_component)
                self.created_instances_list.append(new_coupling)


    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

    def output_line(self):
        """ Overrides parent output_line method. """

        analysis_type = self.circuit.simulation_parameters["analysis_type"]
        ic = f' IC={self.new_format_properties.get("IC")}' if not analysis_type == "AC small-signal" else ""
        return f'{self.identifier()} {" ".join(self.new_format_nodes)} {self.new_format_properties.get("L")}{ic}'

