from schematic_converter.libfqn_dict import determine_elem
from schematic_converter.elements import *

import time
import json

# Converts jsonfile to a Xyce compatible syntax
def tse2xyce(jsonfile, sim_params_dict):
    t0 = time.time()
    analysis_type = sim_params_dict["analysis_type"]

    with open(jsonfile) as f:
        data = json.load(f)

    # List of elements present in the JSON
    elem_list = data["dev_partitions"][0]["components"]
    # List of subsystems present in the JSON
    subsys_list = data["dev_partitions"][0]["parent_components"]
    # List of nodes present in the JSON
    node_data = data["dev_partitions"][0]["nodes"]
    # Initialization of Xyce text
    lines = models = subcircuits = includes = ""
    # List of measurements and their aliases (for better readability in the GUI)
    measurements = []
    meas_aliases = []
    groundnodes = []
    unsupported_components = []
    node_merges = {}
    node_ids = {}
    coupled_L_lines = ""

    def get_elem_data(elem_json):
        ''' Returns the pertinent data of an element in the JSON file. '''
        # Cannot have spaces in the name
        elem_name = elem_json["name"]
        # Determine the element type by searching for the libfqn entry in a dict
        # using libfqn_dict.py
        elem_type = determine_elem(elem_json["lib_fqn"])
        # Create a proper preceding string if the component is located inside subsystem(s)
        subsys_id = elem_json["parent_comp_id"]
        prefix_subs = ""
        while subsys_id:
            for subsystem in subsys_list:
                if subsystem["id"] == subsys_id:
                    prefix_subs = subsystem["name"] + "." + prefix_subs
                    subsys_id = subsystem["parent_comp_id"]
        elem_name = prefix_subs + elem_name
        elem_name = elem_name.replace(" ", "_")
        # Initialization of the data to be returned
        elem_data = {}

        def elem_get_nodes():
            # elem_json is a name in the scope of the parent function
            nonlocal elem_json
            nodes_dict = {}
            for term in elem_json["terminals"]:
                # Check every circuit node for the presence of the terminal id.
                for n in node_data:
                    # If terminal is contained in this node's terminals list
                    if term["id"] in n["terminals"]:
                        # Entry example: "p_node":"123456789"
                        nodes_dict.update({term["name"]:str(n["id"])})
            return nodes_dict

        ########## Measurements are standard TSE components ######
        # Current measurement
        if elem_type == "I_meas":
            # Relevant data for instantiation
            meas_nodes = elem_get_nodes()
            if len(meas_nodes) == 3:
                elem_type = "I_meas_out"
                name = elem_name
            else:
                name = "_I_meas__" + elem_name
            elem_data = {"name":name,
                        "nodes":meas_nodes,
                        "init_data":{"voltage":"0","analysis_type":analysis_type}}
            if len(meas_nodes) == 2:
                # If no output port, add the name to the list of aliases
                if analysis_type == "AC small-signal":
                    meas_aliases.extend([f"mag({elem_name})", f"phase({elem_name})"])
                else:
                    meas_aliases.append(elem_name)

        # Voltage measurement
        elif elem_type == "V_meas":
            # Relevant data for instantiation
            meas_nodes = elem_get_nodes()
            if len(meas_nodes) == 3:
                elem_type = "V_meas_out"
                name = elem_name
            else:
                name = "_V_meas__" + elem_name
            elem_data = {"name":name,
                        "nodes":meas_nodes,
                        "init_data":{"current":"0", "analysis_type":analysis_type}}

            if len(meas_nodes) == 2:
                # If no output port, add the name to the list of aliases
                if analysis_type == "AC small-signal":
                    meas_aliases.extend([f"mag({elem_name})", f"phase({elem_name})"])
                else:
                    meas_aliases.append(elem_name)

        elif elem_type in ["Probe", "Vnode"]:
            # Relevant data for instantiation
            elem_data = {"name":elem_name,
                        "nodes":elem_get_nodes(),
                        "init_data":{"analysis_type":analysis_type}}
            # if analysis_type == "AC small-signal":
            #     meas_aliases.extend([f"mag({elem_name})", f"phase({elem_name})"])
            # else:
            #     meas_aliases.append(elem_name)

        ##########################################################

        #### In the case of every other element contained in the new library
        elif elem_json["masks"] and not elem_type in ["V_meas","I_meas"]:
            prop_list = elem_json["masks"][0]["properties"]
            # Return the dict based on the element properties
            init_dict = {prop["name"]:str(prop["value"]) for prop in prop_list}
            init_dict.update({"analysis_type":analysis_type})
            # Relevant data for instantiation
            elem_data = {
                        "name":elem_name, "nodes":elem_get_nodes(),
                        "init_data":init_dict
                        }


        return (elem_type, elem_data)

    for elem in elem_list:
        # Get the element type and the relevant data
        elem_type, elem_data = get_elem_data(elem)
        # Use the type and data to instantiate the correct class
        this_element = Element.pick_correct_subclass(elem_type, elem_data)
        # If a proper class is available
        if this_element != None:
            # Include the library that contains the element model
            try: # Error for some elements that don't have the opt to add model
                if this_element.model_path:
                    if this_element.model_path not in includes:
                        includes += f'.INCLUDE "{this_element.model_path}"\n'
            except AttributeError: pass
            # Model lines. Used by controlled switches, for example.
            try: # Error for elements without the model_lines method
                models += this_element.model_lines()
            except AttributeError: pass
            # Append the element's Xyce line to the lines list
            lines += this_element.xyce_line()
            # If the element is of composite type
            if this_element.type == "X":
                # Append the needed subcircuit syntax to the list of subcircuits
                subcircuits += this_element.xyce_subc()
            # Construct the coupled inductor networks
            if isinstance(this_element, CoupledInductor):
                # Append the needed subcircuit syntax to the list of subcircuits
                coupled_L_lines += "".join((CoupledInductor.lines))
            # Measurement
            enabled_measurements = []
            if sim_params_dict["analysis_type"] == "AC small-signal":
                # Debug unsupported components
                if elem_type in ["COMP","PWM","D","IdealD","UnidirSwitch","M","J","Q","Z","S","W","T","O","U"]:
                    unsupported_components.append(this_element.name)
            if elem_type in ["V_meas", "I_meas"]: # Zero value sources
                # Append the resulting string to the list of measurements
                measurements.append(this_element.as_measurement(sim_params_dict["analysis_type"]))
            elif elem_type == "P_meas":
                if sim_params_dict["analysis_type"] == "Transient":
                    meas_string, meas_alias = this_element.measurements(sim_params_dict["analysis_type"], ["P"])
                    measurements.append(meas_string)
                    meas_aliases.extend([meas_alias])
            elif this_element.type == "NodeV":
                meas_string, meas_alias = this_element.measurements(sim_params_dict["analysis_type"], ["V"])
                measurements.append(meas_string)
                meas_aliases.extend([meas_alias])
            elif this_element.type == "Probe":
                if sim_params_dict["analysis_type"] == "Transient":
                    meas_string, meas_alias = this_element.measurements(sim_params_dict["analysis_type"], ["V"])
                    measurements.append(meas_string)
                    meas_aliases.extend([meas_alias])
            elif this_element.init_data.get("model_name") == "v_meas_out":
                meas_string, meas_alias = this_element.measurements(sim_params_dict["analysis_type"], ["V"])
                measurements.append(meas_string)
                meas_aliases.extend([meas_alias])
            elif this_element.init_data.get("model_name") == "i_meas_out":
                meas_string, meas_alias = this_element.measurements(sim_params_dict["analysis_type"], ["I"])
                measurements.append(meas_string)
                meas_aliases.extend([meas_alias])
            else:
                init_data = elem_data.get("init_data")
                if init_data.get("meas_v") == "True":
                    enabled_measurements.append("V")
                if init_data.get("meas_i") == "True":
                    enabled_measurements.append("I")
                if init_data.get("meas_p") == "True" and sim_params_dict["analysis_type"] == "Transient":
                    enabled_measurements.append("P")
                if init_data.get("meas_g") == "True" and sim_params_dict["analysis_type"] == "Transient":
                    enabled_measurements.append("G")

                meas_string, meas_alias = this_element.measurements(sim_params_dict["analysis_type"], enabled_measurements)

                if enabled_measurements:
                    if not meas_string == "":
                        measurements.append(meas_string)
                        meas_aliases.extend([meas_alias])

        # Search for the ground node. It has to be named "0" in Xyce.
        if elem_type == "GND":
            # For each node in the circuit
            for n in node_data:
                if elem["terminals"][0]["id"] in n["terminals"]:
                    groundnodes.append(str(n["id"]))

        # Replace node numbers based on node_id field.
        elif elem_type == "NodeID":
            identifier = elem_data["init_data"]["node_id"]
            term = elem["terminals"][0]["id"]
            # For each node in the circuit
            for n in node_data:
                if term in n["terminals"]:
                    node_ids.update({str(n["id"]):identifier})

        # Merge signal-to-power nodes
        elif elem_type == "sgn_to_pwr":
            term1 = elem["terminals"][0]["id"]
            term2 = elem["terminals"][1]["id"]
            for n in node_data:
                if term1 in n["terminals"]:
                    n_term1 = str(n['id'])
                if term2 in n["terminals"]:
                    n_term2 = str(n['id'])
            node_merges.update({n_term1:n_term2})

    if len(unsupported_components) > 0:
        uns_string = "<br>".join([comp for comp in unsupported_components])
        return [False, f"The following components are not supported for AC-analysis:<br>"+uns_string]

    if len(measurements) == 0:
        return [False, "There are no measurements."]

    if len(groundnodes) == 0:
        return [False, "Please add at least one Ground component."]

    # Convert the lists to proper strings
    measurements = " ".join(measurements)
    meas_aliases = ",".join(meas_aliases)

    # Replace the ground node name with "0" in the lines and measurements
    for g in groundnodes:
        lines = lines.replace("n_" + g, "0")
        measurements = measurements.replace("n_" + g, "0")

    for node in node_merges:
        lines = lines.replace("n_" + node, "n_" + node_merges[node])
        measurements = measurements.replace("n_" + node, "n_" + node_merges[node])

    for node in node_ids:
        lines = lines.replace("n_" + node, "n_" + node_ids[node])
        measurements = measurements.replace("n_" + node, "n_" + node_ids[node])

    # Analysis type
    analysis_type = sim_params_dict["analysis_type"]
    if analysis_type == "Transient":
        sim_time = sim_params_dict['sim_time']
        max_ts = sim_params_dict['max_ts']
        nonlinear_solver = sim_params_dict['nonlinear_solver']
        nonlinear_maxstep = sim_params_dict['nonlinear_maxstep']
        nonlinear_abstol = sim_params_dict['nonlinear_abstol']
        nonlinear_reltol = sim_params_dict['nonlinear_reltol']
        analysis_lines = f'.TRAN {max_ts} {sim_time} 0 {max_ts} NOOP\n'\
        f'.OPTIONS NONLIN-TRAN NLSTRATEGY={nonlinear_solver} ABSTOL={nonlinear_abstol} RELTOL={nonlinear_reltol} MAXSTEP={nonlinear_maxstep}\n'\
        f'.OPTIONS OUTPUT INITIAL_INTERVAL=decimation {sim_time}\n'\
        f'.GLOBAL_PARAM GLOBAL_TS = {max_ts} GLOBAL_RON = 1e-4 GLOBAL_ROFF = 1e5\n'\
        f'.PRINT TRAN WIDTH=4 FORMAT=csv FILE=xyce_out.csv {measurements}\n'

    elif analysis_type == "AC small-signal":
        num_points = sim_params_dict["num_points"]
        start_f = sim_params_dict["start_f"]
        end_f = sim_params_dict["end_f"]
        analysis_lines = f'.AC LIN {num_points} {start_f} {end_f}\n'\
        f'.GLOBAL_PARAM GLOBAL_RON = 1e-4 GLOBAL_ROFF = 1e5\n'\
        f'.PRINT AC WIDTH=4 FORMAT=csv FILE=xyce_f_out.csv {measurements}\n'


    timeint_abstol = sim_params_dict['timeint_abstol']
    timeint_reltol = sim_params_dict['timeint_reltol']
    timeint_method = sim_params_dict['timeint_method']
    #  Final syntax output
    output =    (
                f'Automatically generated by https://github.com/typhoon-hil/xyce-typhoon-hil-interface\n'\
                f'{analysis_lines}'
                f'.OPTIONS TIMEINT METHOD={timeint_method} ABSTOL={timeint_abstol} RELTOL={timeint_reltol} newlte=2 \n'\
                '\n'\
                f'{lines}\n{models}\n'\
                f'{coupled_L_lines}'\
                f'{subcircuits}'\
                f'{includes}\n'\
                '.END\n'\
                f'*TIME,{meas_aliases}'
                )

    # Write a .cir file with the same name as the JSON, and in the same folder
    with open(os.path.splitext(jsonfile)[0]+".cir","w+") as f:
        f.write(output)

    # Program speed test
    print(f"Total conversion time: {time.time()-t0} seconds")

    # Prepare for another conversion
    # Reset the instance counter for coupled inductors
    CoupledInductor.instance_counter = 0

    return [True, "The conversion to Xyce syntax was successful."]

if __name__ == "__main__":
    # sim_params = {'analysis_type':'Transient','max_ts':'1e-6','sim_time':'1ms'}
    sim_params = {'analysis_type':'AC small-signal','start_f':'10','end_f':'100000', 'num_points':'1000'}
    tse2xyce(r"path_to.json", sim_params)
