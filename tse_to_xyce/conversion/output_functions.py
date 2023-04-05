from ..tse2tpt_base_converter import tse_functions as tse_fns
import json

# Use default mapping
from .default_mapping import map
from .default_mapping import constants

def verify_duplicate_names(tse_model):
    """ Xyce is not case sensitive while TSE is. Avoid duplicates. """

    converted_components = []
    all_components = tse_model.components
    for component in all_components:
        if map.ignore_component(component.comp_type):
            converted_components.append(component)
        elif map.map_component(component.comp_type):
            converted_components.append(component)

    all_fqns_lower = [n.fqn.lower() for n in converted_components]
    duplicates = []
    for idx, name in enumerate(all_fqns_lower):
        if all_fqns_lower.count(name) > 1:
            duplicates.append(converted_components[idx].name)

    if len(duplicates) > 0:
        raise Exception(f"Xyce is case insensitive. "
                        f"Please change the name of the following conflicting components: {duplicates}")


def merge_terminals(tse_component):
    """ Merge the terminals of ignored components """

    merge_dict = map.ignore_component(tse_component.comp_type)

    # Get the merge information from merge_dict
    for merge_to_terminal, other_terms_list in merge_dict.items():
        # Find the terminal (dict key) other terminals are being merged to
        for t_name, t_instance in tse_component.terminals.items():
            if t_name == merge_to_terminal:
                # Get the node of the terminal
                merge_to_node = t_instance.node
                # Loop again through all the terminals to find the other terminal instances
                for other_term_name in other_terms_list:
                    for other_t_name, other_t_instance in tse_component.terminals.items():
                        if other_term_name == other_t_name:
                            # Get all terminals from all components connected to this terminal node
                            all_terminals = other_t_instance.node.terminals
                            for t in all_terminals:
                                # Connect this terminal to the merge_to_node
                                t.node = merge_to_node
                                merge_to_node.add_terminal(t)
                            # Remove the merged terminals from the node
                            merge_to_node.remove_terminal(t_instance)
                            merge_to_node.remove_terminal(other_t_instance)


def create_measurement_json(output_circuit, xyce_data_path):

    import json, os
    from .default_mapping.component_classes.base import VoltageMeasurement
    from .default_mapping.component_classes.base import CurrentMeasurement
    from .default_mapping.component_classes.base import PowerMeasurement

    old_names = []
    new_names = []
    for comp in output_circuit.components:
        if output_circuit.simulation_parameters["analysis_type"] == "AC small-signal":
            if isinstance(comp, VoltageMeasurement):
                mag_str = comp.measurement_string()[0]
                phase_str = comp.measurement_string()[1]
                old_names.append(mag_str.upper())
                new_names.append(f"VM({comp.measured_component.name})")
                old_names.append(phase_str.upper())
                new_names.append(f"VP({comp.measured_component.name})")
            if isinstance(comp, CurrentMeasurement):
                mag_str = comp.measurement_string()[0]
                phase_str = comp.measurement_string()[1]
                if comp.measured_subsystem_component:
                    old_names.append(mag_str.upper())
                    new_names.append(f"IM({comp.measured_component.name}:{comp.measured_subsystem_component})")
                    old_names.append(phase_str.upper())
                    new_names.append(f"IP({comp.measured_component.name}:{comp.measured_subsystem_component})")
                else:
                    old_names.append(mag_str.upper())
                    new_names.append(f"IM({comp.measured_component.name})")
                    old_names.append(phase_str.upper())
                    new_names.append(f"IP({comp.measured_component.name})")
            if isinstance(comp, PowerMeasurement):
                p_str = comp.measurement_string()[0]
                if comp.measured_subsystem_component:
                    old_names.append(p_str.upper())
                    new_names.append(f"P({comp.measured_component.name}:{comp.measured_subsystem_component})")
                else:
                    old_names.append(p_str.upper())
                    new_names.append(f"P({comp.measured_component.name})")
        else:
            if isinstance(comp, VoltageMeasurement):
                for m_str in comp.measurement_string():
                    old_names.append(m_str.upper())
                    if comp.vgs:
                        new_names.append(f"V({comp.measured_component.name}_gs)")
                    else:
                        new_names.append(f"V({comp.measured_component.name})")
            if isinstance(comp, CurrentMeasurement):
                for m_str in comp.measurement_string():
                    if comp.measured_subsystem_component:
                        old_names.append(m_str.upper())
                        new_names.append(f"I({comp.measured_component.name}:{comp.measured_subsystem_component})")
                    else:
                        old_names.append(m_str.upper())
                        new_names.append(f"I({comp.measured_component.name})")
            if isinstance(comp, PowerMeasurement):
                for m_str in comp.measurement_string():
                    if comp.measured_subsystem_component:
                        old_names.append(m_str.upper())
                        new_names.append(f"P({comp.measured_component.name}:{comp.measured_subsystem_component})")
                    else:
                        old_names.append(m_str.upper())
                        new_names.append(f"P({comp.measured_component.name})")

    meas_dict = {"new_names": new_names, "old_names": old_names}
    with open(f"{os.path.join(xyce_data_path, 'measurement_names.json')}", 'w') as f:
        f.write(json.dumps(meas_dict, indent=4))
