from . import output_functions
import pathlib
import os

# Use default mapping
from .default_mapping import constants
from .default_mapping import class_picker
from .default_mapping import map
from .default_mapping.component_classes.base import Circuit
from ..conversion.default_mapping.component_classes import *


def convert(tse_model, input_json_path, simulation_parameters):
    """
    Main conversion function.

    Args:
        tse_model(ModelPartition): ModelPartition object created by the tse_model_load.load_json function.
        input_json_path(str): Path to the original JSON file.
        simulation_parameters(str): Simulation parameters.

    Returns:
        converted_dict(dict): Dictionary with the new model data.
    """

    # Validate the model
    output_functions.verify_duplicate_names(tse_model)

    # Paths
    xyce_folder_path = pathlib.Path(input_json_path).parent.joinpath('xyce')
    xyce_data_path = xyce_folder_path.joinpath('data')
    simulation_parameters.update(
        {
            "xyce_folder_path": xyce_folder_path,
            "xyce_data_path": xyce_data_path
        }
    )

    # Create new output circuit
    circuit_name = tse_model.parent.name
    output_circuit = Circuit(circuit_name, simulation_parameters)

    components = tse_model.components

    # Merge terminals of ignored components
    remove_list = []
    for component in components:
        if map.ignore_component(component.comp_type):
            output_functions.merge_terminals(component)
            remove_list.append(component)
    for component in remove_list:
        tse_model.remove_component_by_fqn(component.fqn)

    # Rename nodes to a more readable. First check for ground and node_id components.
    node_num = 1
    new_nodes = set()
    for node in tse_model.nodes:
        is_ground = False
        is_named = False
        for t in node.terminals:
            if t.parent.comp_type == constants.XYCE_GND or t.parent.comp_type == constants.CORE_GND:
                is_ground = True
                tse_model.remove_component_by_fqn(t.parent.fqn)
            elif t.parent.comp_type == constants.XYCE_NODE_ID:
                if t.parent in components:  # May have already been removed due to ignored components
                    node_id = t.parent.properties.get("node_id").value
                    is_named = True
                    tse_model.remove_component_by_fqn(t.parent.fqn)
        if is_ground:
            node.name = 0
        elif is_named:
            node.name = node_id
        else:
            node.name = node_num
            node_num += 1
        new_nodes.add(node.name)
    output_circuit.nodes = new_nodes

    # Create the output circuit model
    for component in components:
        comp_data = {}

        # Define name (if the component is inside a subsystem, the parent name is appended)
        name = component.name
        parent = component.parent_comp
        while parent:  # If component is inside a subsystem
            name = parent.name + "." + name
            parent = parent.parent_comp
        component.name = name

        # Create properties dictionary
        properties_dict = {str(k): str(v.value) for k, v in component.properties.items()}

        # Create the component data dictionary
        comp_data.update({"name": name,
                          "circuit": output_circuit,
                          "tse_component": component,
                          "tse_properties": properties_dict}
                         )

        # Create instances of the converted components (may be more than one per TSE component)
        mapped_types = map.map_component(component.comp_type)
        if mapped_types:
            for converted_comp_type in mapped_types:
                converted_comp_handle = class_picker.create_comp_instance(converted_comp_type, comp_data)
                converted_comp_list = converted_comp_handle.created_component_instances()
                for comp in converted_comp_list:
                    output_circuit.components.append(comp)
        else:
            pass

    return output_circuit


def generate_output_files(output_circuit):
    """
        Creates all the output files necessary for the simulation with the 3rd party tool.

        Args:
            output_circuit(Circuit): New circuit model.

        Returns:
            None.
        """

    circuit_name = output_circuit.name
    components = output_circuit.components

    # Master xyce file path. Inside the target_files folder.
    xyce_folder_path = output_circuit.simulation_parameters.get("xyce_folder_path")
    if not xyce_folder_path.is_dir():
        os.makedirs(xyce_folder_path)
    # Data folder inside the xyce folder.
    xyce_data_path = xyce_folder_path.joinpath('data')
    if not xyce_data_path.is_dir():
        os.makedirs(xyce_data_path)

    # Set of component types after conversion
    converted_component_types = set(comp.type for comp in components)
    converted_component_types.remove("MEASUREMENT") if "MEASUREMENT" in converted_component_types else None

    # Write the output lines
    for converted_comp_type in converted_component_types:
        first_of_this_type = True
        for comp in components:
            if comp.type == converted_comp_type:
                # Rewrite the file if the element is the first of the type, otherwise append new lines
                if first_of_this_type:
                    with open(f"{xyce_data_path.joinpath(comp.type.lower() + '.txt')}", 'w') as f:
                        f.write(f"* Automatically generated by the Typhoon HIL TSE to Xyce converter.\n\n")
                        first_of_this_type = False
                with open(f"{xyce_data_path.joinpath(comp.type.lower() + '.txt')}", 'a') as f:
                    if comp.output_line():
                        f.write(comp.output_line() + "\n")

    # Measurements
    measurement_strings = []
    for comp in components:
        if comp.type == "MEASUREMENT":
            for m_str in comp.measurement_string():
                if hasattr(comp, "vgs") and comp.vgs:
                    measurement_strings.append(f"+ {m_str}   ; {comp.measured_component.name}_gs\n")
                else:
                    measurement_strings.append(f"+ {m_str}   ; {comp.measured_component.name}\n")

    # Create a JSON file with new names for the Signal Analyzer
    create_measurement_json(output_circuit, xyce_data_path)

    # Debugging

    # Debug unsupported components
    unsupported_comps = []
    if output_circuit.simulation_parameters.get("analysis_type") == "AC small-signal":
        for comp in components:
            if comp.type in ["COMP", "PWM", "D", "IdealD", "UnidirSwitch", "M", "J", "Q", "Z", "S", "W", "T", "O", "U"]:
                unsupported_comps.append(f"{comp.type}:{comp.name}")
    if len(unsupported_comps) > 0:
        uns_string = "<br>".join([comp for comp in unsupported_comps])
        return [False, f"The following components are not supported for AC-analysis:<br>" + uns_string]

    if len(measurement_strings) == 0:
        return [False, "There are no measurements."]

    gnd_present = False
    for node in output_circuit.nodes:
        if node == 0:
            gnd_present = True
    if not gnd_present:
        return [False, "Please add at least one Ground component."]

    # Redirect lines for each component type
    converted_component_types = [comp.lower() for comp in converted_component_types]
    # Some objects need to be in the correct order
    include_paths = "\n".join([f'.include data/{t.lower()}.txt' for t in converted_component_types])

    # Analysis type
    timeint_abstol = output_circuit.simulation_parameters['timeint_abstol']
    timeint_reltol = output_circuit.simulation_parameters['timeint_reltol']
    timeint_method = output_circuit.simulation_parameters['timeint_method']

    analysis_type = output_circuit.simulation_parameters.get("analysis_type")
    if analysis_type == "Transient":
        sim_time = output_circuit.simulation_parameters.get("sim_time")
        max_ts = output_circuit.simulation_parameters.get("max_ts")
        nonlinear_solver = output_circuit.simulation_parameters.get("nonlinear_solver")
        nonlinear_maxstep = output_circuit.simulation_parameters.get("nonlinear_maxstep")
        nonlinear_abstol = output_circuit.simulation_parameters.get("nonlinear_abstol")
        nonlinear_reltol = output_circuit.simulation_parameters.get("nonlinear_reltol")
        voltage_limiting = output_circuit.simulation_parameters.get("voltage_limiting")
        calculate_operation_point = output_circuit.simulation_parameters.get("calculate_operation_point")
        analysis_lines = f'.TRAN {max_ts} {sim_time} 0 {max_ts}{" " if calculate_operation_point else " NOOP"}\n' \
                         f'.OPTIONS NONLIN-TRAN NLSTRATEGY={nonlinear_solver} ABSTOL={nonlinear_abstol} RELTOL={nonlinear_reltol} MAXSTEP={nonlinear_maxstep}\n' \
                         f'*.OPTIONS OUTPUT INITIAL_INTERVAL={float(max_ts)} {sim_time}\n' \
                         f'.OPTIONS DEVICE VOLTLIM={voltage_limiting}\n' \
                         f'.GLOBAL_PARAM GLOBAL_TS = {max_ts} GLOBAL_RON = 1e-4 GLOBAL_ROFF = 1e5\n\n' \
                         f'.PRINT TRAN WIDTH=4 FORMAT=csv FILE=xyce_out.csv\n{"".join(measurement_strings)}\n'
        timeint_lines = f'.OPTIONS TIMEINT METHOD={timeint_method} ABSTOL={timeint_abstol} RELTOL={timeint_reltol} newlte=2  ERROPTION=1\n'
    elif analysis_type == "AC small-signal":
        num_points = output_circuit.simulation_parameters["num_points"]
        start_f = output_circuit.simulation_parameters["start_f"]
        end_f = output_circuit.simulation_parameters["end_f"]
        analysis_lines = f'.AC DEC {num_points} {start_f} {end_f}\n'\
        f'.GLOBAL_PARAM GLOBAL_RON = 1e-4 GLOBAL_ROFF = 1e5\n\n'\
        f'.PRINT AC WIDTH=4 FORMAT=csv FILE=xyce_f_out.csv\n{"".join(measurement_strings)}\n'
        timeint_lines = f'.OPTIONS TIMEINT ABSTOL={timeint_abstol} RELTOL={timeint_reltol} newlte=2\n'

    #  Final syntax output
    main_xyce_file_text = (
        f'* Automatically generated by https://github.com/typhoon-hil/xyce-typhoon-hil-interface\n' \
        '\n' \
        f'{analysis_lines}'
        f'{timeint_lines}' \
        '\n' \
        f'{include_paths}\n' \
        '.END\n' \
    )

    # Write master file
    with open(f"{xyce_folder_path.joinpath(f'{circuit_name}_master.cir')}", 'w') as f:
        f.write(main_xyce_file_text)

    return [True, "The conversion to Xyce syntax was successful."]
