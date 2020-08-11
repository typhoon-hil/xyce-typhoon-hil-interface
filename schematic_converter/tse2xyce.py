from libfqn_dict import determine_elem
from elements import *

import time
import json

# Simple file verification (checks the first three JSON entries)
def test_tse_file(jsonfile):
    with open(jsonfile) as f:
        data = json.load(f)
    return ["ver","_cls","name"] == list(data.keys())[0:3]

# Converts jsonfile to a Xyce compatible syntax
def tse2xyce(jsonfile):
    t0 = time.time()

    with open(jsonfile) as f:
        data = json.load(f)

    # List of elements present in the JSON
    elem_list = data["dev_partitions"][0]["components"]
    # List of nodes present in the JSON
    node_data = data["dev_partitions"][0]["nodes"]
    # Initialization of Xyce text
    lines = models = subcircuits = includes = ""
    # List of measurements and their aliases (for better readability in the GUI)
    measurements = []
    meas_aliases = []
    groundnodes = []
    node_ids = {}
    coupled_L_lines = ""

    def get_elem_data(elem_json):
        ''' Returns the pertinent data of an element in the JSON file. '''
        # Cannot have spaces in the name
        elem_name = elem_json["name"].replace(" ","_")
        # Determine the element type by searching for the libfqn entry in a dict
        # using libfqn_dict.py
        elem_type = determine_elem(elem_json["lib_fqn"])
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
        if elem_type is "I_meas":
            # Relevant data for instantiation
            elem_data = {"name":"_I_meas__" + elem_name,
                        "nodes":elem_get_nodes(),
                        "init_data":{"voltage":"0"}}
            # Add the name to the list of aliases
            meas_aliases.append(elem_name)

        # Voltage measurement
        elif elem_type is "V_meas":
            # Relevant data for instantiation
            elem_data = {"name":"_V_meas__" + elem_name,
                        "nodes":elem_get_nodes(),
                        "init_data":{"current":"0"}}
            # Add the name to the list of aliases
            meas_aliases.append(elem_name)
        ##########################################################

        #### In the case of every element contained in the new library
        elif elem_json["masks"] and not elem_type in ["V_meas","I_meas"]:
            prop_list = elem_json["masks"][0]["properties"]
            # Return the dict based on the element properties
            init_dict = {prop["name"]:str(prop["value"]) for prop in prop_list}
            # Relevant data for instantiation
            elem_data = {
                        "name":elem_name, "nodes":elem_get_nodes(),
                        "init_data":init_dict
                        }

        return (elem_type, elem_data)

    for elem in elem_list:
        # Get the element type and the relevant data
        elem_type, elem_data = get_elem_data(elem)
        # Treat coupled inductors
        # if elem_type == "L_coupled":
        #     # Do this once. Every coupled ind contains all the information.
        #     try: coupled_dict
        #     except:
        #         coupled_dict = elem["masks"][0]["vars"]["coupled_dict"]
        #     elem_data.update({"coupled_dict":coupled_dict})
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
            if this_element.type is "X":
                # Append the needed subcircuit syntax to the list of subcircuits
                subcircuits += this_element.xyce_subc()
            # Construct the coupled inductor networks
            if isinstance(this_element, CoupledInductor):
                # Append the needed subcircuit syntax to the list of subcircuits
                coupled_L_lines += "".join((CoupledInductor.lines))
            # If the element is used for measurement
            if "_meas_" in this_element.name:
                # Append the resulting string to the list of measurements
                measurements.append(this_element.as_measurement())

        # Search for the ground node. It has to be named "0" in Xyce.
        if elem_type == "GND":
            # For each node in the circuit
            for n in node_data:
                if elem["terminals"][0]["id"] in n["terminals"]:
                    groundnodes.append(str(n["id"]))

        # Replace node numbers based on node_id field.
        if elem_type == "NodeID":
            identificator = elem_data["init_data"]["node_id"]
            term = elem["terminals"][0]["id"]
            # For each node in the circuit
            for n in node_data:
                if term in n["terminals"]:
                    node_ids.update({str(n["id"]):identificator})

    # Convert the lists to proper strings
    measurements = " ".join(measurements)
    meas_aliases = ",".join(meas_aliases)

    # Replace the ground node name with "0" in the lines and measurements
    for g in groundnodes:
        lines = lines.replace("n_" + g,"0") #.replace("  "," ") use to get rid of double spaces
        measurements = measurements.replace("n_" + g,"0")

    for node in node_ids:
        lines = lines.replace("n_" + node, "n_" + node_ids[node])
        measurements = measurements.replace("n_" + node, "n_" + node_ids[node])



    # Final syntax output
    output =    (
                f'Automatically generated by https://github.com/typhoon-hil/xyce-typhoon-hil-interface\n'\
                f'.TRAN t_step total_time 0 t_step NOOP\n'\
                f'.OPTIONS NONLIN-TRAN ABSTOL=1e-6 RELTOL=1e-3 MAXSTEP=20\n'\
                '.OPTIONS OUTPUT INITIAL_INTERVAL=decimation total_time\n'\
                #f'.OPTIONS TIMEINT ABSTOL=1e-5 RELTOL=1e-2 ERROPTION=1 NLMIN=2 NLMAX=7\n'\
                f'.OPTIONS TIMEINT ABSTOL=1e-6 RELTOL=1e-3 newlte=2 \n'\
                '.GLOBAL_PARAM GLOBAL_TS = t_step GLOBAL_RON = 1e-4 GLOBAL_ROFF = 1e5\n'\
                f'.PRINT TRAN WIDTH=4 FORMAT=csv FILE=xyce_out.csv {measurements}\n\n'\
                f'{lines}\n{models}\n'\
                f'{coupled_L_lines}'\
                f'{subcircuits}'\
                f'{includes}\n'\
                '.END\n'\
                f'*TIME,{meas_aliases}'
                )

    # Write a .cir file with the same name as the JSON, and in the same folder
    with open("".join(jsonfile.split(".")[0:-1])+".cir","w+") as f:
        f.write(output)

    # Program speed test
    print(f"Total conversion time: {time.time()-t0} seconds")

    # Prepare for another conversion
    # Reset the instance counter for coupled inductors
    CoupledInductor.instance_counter = 0

if __name__ == "__main__":
    tse2xyce(r"path_to.json")
