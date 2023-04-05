from .base import *
from ...output_functions import *
from ..constants import *
import os


class UnidirectionalSwitch(SubcircuitBased):
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
            "r_on": tse_properties["r_on"],
            "vd_on": tse_properties["vd_on"] if float(tse_properties['vd_on']) >= 0 else "0",
            "vsw_on": tse_properties["vsw_on"] if float(tse_properties['vsw_on']) >= 0 else "0"
        }

        return new_format_properties

    @staticmethod
    def create_component_model(self, tse_properties, tse_component):
        """ Creates a component model instance. Models are shared by different components. """

        model_name = "unidir_switch"

        component_model = None
        for comp in self.circuit.components:
            if comp.type == "COMPONENT_MODEL":
                if comp.name == model_name:
                    component_model = comp
                    break

        if not component_model:
            component_model = ComponentModel(self.circuit, model_name,
                                             file_path=os.path.join(XYCE_INCLUDED_MODELS_PATH, "unidirectional_switch.lib"))
            self.created_instances_list.append(component_model)

        return component_model

    @staticmethod
    def define_nodes(self, tse_properties, tse_component):
        """ Create component node IDs list. """

        nodes = [
            XYCE_NODE_PREFIX + str(tse_component.terminals["drain"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["gate"].node.name),
            XYCE_NODE_PREFIX + str(tse_component.terminals["src"].node.name),
        ]

        for idx, n in enumerate(nodes):
            if n == f"{XYCE_NODE_PREFIX}0":
                nodes[idx] = "0"

        return nodes

    @staticmethod
    def create_measurements(self, circuit, nodes, tse_properties, tse_component):
        """ Create measurement object instances for each selected measurement type. """

        if tse_properties.get("meas_v") == "True":
            node_p = nodes[0]
            node_n = nodes[2]
            v_meas = VoltageMeasurement(circuit, node_p, node_n, self)
            self.created_instances_list.append(v_meas)

        if tse_properties.get("meas_g") == "True":
            node_p = nodes[1]
            node_n = nodes[2]
            v_meas = VoltageMeasurement(circuit, node_p, node_n, self, vgs=True)
            self.created_instances_list.append(v_meas)

        if tse_properties.get("meas_i") == "True":
            i_meas1 = CurrentMeasurement(circuit, self, measured_subsystem_component="V_MEAS_SW")
            self.created_instances_list.append(i_meas1)
            i_meas2 = CurrentMeasurement(circuit, self, measured_subsystem_component="V_MEAS_D")
            self.created_instances_list.append(i_meas2)

        if tse_properties.get("meas_p") == "True":
            p_meas1 = PowerMeasurement(circuit, self, measured_subsystem_component="SW_DIODE")
            self.created_instances_list.append(p_meas1)
            p_meas2 = PowerMeasurement(circuit, self, measured_subsystem_component="SW_UNI")
            self.created_instances_list.append(p_meas2)

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
