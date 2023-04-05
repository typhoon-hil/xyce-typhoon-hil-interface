from PyQt5.QtWidgets import QWidget, QFileDialog, QDialog, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys, csv, io, re, pathlib
from xyce_thcc_lib.gui_scripts.scope import scope


# Build the list of available measurements
def all_circuit_components(mdl, parent_comp=None):
    component_list = []
    if parent_comp:  # Component inside a subsystem
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name:
                component_list.append(comp)
            else:  # Component is a subsystem
                component_list.extend(all_circuit_components(mdl, comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def initialize_scope(mdl, mask_handle):
    all_components = all_circuit_components(mdl)

    found_xycesim = False
    for comp in all_components:
        if mdl.get_component_type_name(comp) == "XyceSim":
            found_xycesim = True
            sim_type_prop = mdl.prop(comp, "sim_type")
            sim_type = mdl.get_property_value(sim_type_prop)
            if sim_type == "Transient":
                analysis_type = "transient"
            else:
                analysis_type = "ac"
            break

    if not found_xycesim:
        mdl.info("Add a XyceSim component first.")
        return

    available_measurements = {}

    # Transient mode
    voltages = []
    currents = []
    powers = []
    # [correct list for the measurement type, string added to the UI]
    prop_name_dict = {"meas_v": [voltages, lambda y: f'V({y.replace(" ", "_")})'],
                      "meas_i": [currents, lambda y: f'I({y.replace(" ", "_")})'],
                      "meas_p": [powers, lambda y: f'P({y.replace(" ", "_")})'],
                      "meas_g": [voltages, lambda y: f'V({y.replace(" ", "_")}_gs)']}
    for component in all_components:
        component_name = component.fqn
        if mdl.get_component_type_name(component) in ["Voltage Measurement", "Node Voltage"]:
            voltages.append(f'V({component_name.replace(" ", "_")})')
        elif mdl.get_component_type_name(component) == "Current Measurement":
            currents.append(f'I({component_name.replace(" ", "_")})')
        elif mdl.get_component_type_name(component) == "Power Measurement":
            powers.append(f'P({component_name.replace(" ", "_")})')
        else:
            for prop_name in prop_name_dict.keys():
                try:
                    prop_handle = mdl.prop(component, prop_name)
                    if mdl.get_property_value(prop_handle):  # If the checkbox is marked
                        prop_name_dict[prop_name][0].append(prop_name_dict[prop_name][1](component_name))
                except Exception as e:
                    if e.__context__ == prop_name:
                        # Component doesn't have the measurement property
                        pass
    available_measurements['transient'] = {"voltages": voltages,
                                           "currents": currents,
                                           "powers": powers}

    # AC analysis mode
    voltages = []
    currents = []
    powers = []
    # [correct list for the measurement type, string added to the UI]
    prop_name_dict = {"meas_v": [voltages,
                                 lambda y: f'VP({y.replace(" ", "_")})',
                                 lambda y: f'VM({y.replace(" ", "_")})'],
                      "meas_i": [currents,
                                 lambda y: f'IP({y.replace(" ", "_")})',
                                 lambda y: f'IM({y.replace(" ", "_")})'],
                      # "meas_g":[  voltages,
                      #            lambda y: f'VgP({y.replace(" ", "_")})',
                      #            lambda y: f'VgM({y.replace(" ", "_")})'],
                      }
    for component in all_components:
        component_name = component.fqn
        if mdl.get_component_type_name(component) in ["Voltage Measurement", "Node Voltage"]:
            voltages.append(f'VM({component_name.replace(" ", "_")})')
            voltages.append(f'VP({component_name.replace(" ", "_")})')
        elif mdl.get_component_type_name(component) == "Current Measurement":
            currents.append(f'IM({component_name.replace(" ", "_")})')
            currents.append(f'IP({component_name.replace(" ", "_")})')
        else:
            for prop_name in prop_name_dict.keys():
                try:
                    prop_handle = mdl.prop(component, prop_name)
                    if mdl.get_property_value(prop_handle):  # If the checkbox is marked
                        prop_name_dict[prop_name][0].append(prop_name_dict[prop_name][1](component_name))
                        prop_name_dict[prop_name][0].append(prop_name_dict[prop_name][2](component_name))
                except Exception as e:
                    if e.__context__ == prop_name:
                        # Component doesn't have the measurement property
                        pass
    available_measurements['ac'] = {"voltages": voltages,
                                    "currents": currents,
                                    "powers": powers}

    model_name = pathlib.Path(mdl.get_model_file_path()).stem
    plot_cfg_file = pathlib.Path(mdl.get_model_file_path()).parent.joinpath(f"{model_name}_plot_cfg.json")

    new_scope = scope.Scope(available_measurements,
                            str(plot_cfg_file),
                            analysis_type)
    new_scope.exec()
