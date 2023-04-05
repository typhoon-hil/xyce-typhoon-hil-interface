import ast

# Return all components (including inside subsystems)
def all_circuit_components(model, parent_comp=None):
    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = model.get_items(parent_comp)
    else:  # Top level call
        all_components = model.get_items()

    for comp in all_components:
        try:
            type_name = model.get_component_type_name(comp)
            if type_name:
                component_list.append(comp)
            else:  # Component is a subsystem
                component_list.extend(all_circuit_components(model, comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def update_display(mdl, mask_handle, edited=None):
    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)
    # Update the visible part of this inductor's mask
    # Property handles
    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    inductors_dict_prop = mdl.prop(this_ind_mask, "inductors_dict")
    inductors_dict = ast.literal_eval(mdl.get_property_value(inductors_dict_prop))
    create_coupling_prop = mdl.prop(this_ind_mask, "create_coupling")
    coupling_coefficient_prop = mdl.prop(this_ind_mask, "coupling_coefficient")
    add_prop = mdl.prop(this_ind_mask, "add")
    select_coupled_prop = mdl.prop(this_ind_mask, "select_coupled")
    current_coupling_coefficient_prop = mdl.prop(this_ind_mask, "current_coupling_coefficient")
    change_prop = mdl.prop(this_ind_mask, "change")
    remove_prop = mdl.prop(this_ind_mask, "remove")

    coupled_to_dict = couplings_dict.get(this_ind.item_fqid)
    # Available inductors to couple to
    names_of_available_inductors = list(inductors_dict.values())
    # Removes itself
    names_of_available_inductors.remove(inductors_dict.get(this_ind.item_fqid))

    # If this inductor is coupled to others
    if coupled_to_dict:
        names_of_the_coupled_inductors = []
        for coupind_fqid in coupled_to_dict.keys():
            names_of_the_coupled_inductors.append(inductors_dict.get(coupind_fqid))
            if names_of_available_inductors:
                names_of_available_inductors.remove(inductors_dict.get(coupind_fqid))
        mdl.set_property_combo_values(select_coupled_prop, names_of_the_coupled_inductors)

        # If a coupling has just been edited
        if edited:
            coupind_fqid = mdl.get_item(edited).item_fqid
            mdl.set_property_disp_value(current_coupling_coefficient_prop, coupled_to_dict[coupind_fqid])
            mdl.set_property_disp_value(select_coupled_prop, edited)
            mdl.disable_property(change_prop)
        elif names_of_the_coupled_inductors:
            mdl.set_property_value(select_coupled_prop, names_of_the_coupled_inductors[0])
            coupind_fqid = mdl.get_item(names_of_the_coupled_inductors[0]).item_fqid
            mdl.set_property_disp_value(current_coupling_coefficient_prop, coupled_to_dict[coupind_fqid])
            mdl.disable_property(change_prop)
        mdl.enable_property(remove_prop)
        mdl.enable_property(current_coupling_coefficient_prop)
    # If this inductor is not coupled to others
    else:
        mdl.set_property_combo_values(select_coupled_prop, ['None'])
        mdl.set_property_disp_value(current_coupling_coefficient_prop, "0")
        mdl.disable_property(current_coupling_coefficient_prop)
        mdl.disable_property(change_prop)
        mdl.disable_property(remove_prop)

    # If there are inductors available to couple to in the schematic level
    if names_of_available_inductors:
        mdl.set_property_combo_values(create_coupling_prop, names_of_available_inductors)
        mdl.set_property_value(create_coupling_prop, names_of_available_inductors[0])
        mdl.set_property_disp_value(create_coupling_prop, names_of_available_inductors[0])
        mdl.enable_property(add_prop)
        mdl.enable_property(coupling_coefficient_prop)
    else:
        mdl.set_property_combo_values(create_coupling_prop, ["No inductors available"])
        mdl.set_property_value(create_coupling_prop, "No inductors available")
        mdl.set_property_disp_value(create_coupling_prop, "No inductors available")
        mdl.disable_property(add_prop)
        mdl.disable_property(coupling_coefficient_prop)


def add_coupling(mdl, mask_handle):
    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)
    # Property handles
    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    create_coupling_prop = mdl.prop(this_ind_mask, "create_coupling")
    select_coupled_prop = mdl.prop(this_ind_mask, "select_coupled")
    coupling_coefficient_prop = mdl.prop(this_ind_mask, "coupling_coefficient")
    # Name of the inductor currently selected to be added
    selected_ind = mdl.get_property_disp_value(create_coupling_prop)
    # Current select_coupled values
    select_coupled_list = mdl.get_property_combo_values(select_coupled_prop)

    if not selected_ind == "No inductors available":
        ind_handle = mdl.get_item(name=selected_ind)
        coupled_to_dict = couplings_dict.get(this_ind.item_fqid)
        counterpart_coupled_to_dict = couplings_dict.get(ind_handle.item_fqid)
        # Create the first dict entries if there are no couplings for ind_handle yet
        coupling_coefficient_value = mdl.get_property_disp_value(coupling_coefficient_prop)
        if coupled_to_dict:
            coupled_to_dict.update({ind_handle.item_fqid: coupling_coefficient_value})
        else:
            coupled_to_dict = {ind_handle.item_fqid: coupling_coefficient_value}
        if counterpart_coupled_to_dict:
            counterpart_coupled_to_dict.update({this_ind.item_fqid: coupling_coefficient_value})
        else:
            counterpart_coupled_to_dict = {this_ind.item_fqid: coupling_coefficient_value}

        couplings_dict.update({this_ind.item_fqid: coupled_to_dict})
        couplings_dict.update({ind_handle.item_fqid: counterpart_coupled_to_dict})

        # Update couplings_dict of all inductors:
        for item in all_circuit_components(mdl):
            try:
                if mdl.get_component_type_name(item) == "Coupled Inductor":
                    couplings_dict_property = mdl.prop(item, "couplings_dict")
                    mdl.set_property_combo_values(couplings_dict_property, [str(couplings_dict)])
                    mdl.set_property_value(couplings_dict_property, str(couplings_dict))
                    mdl.refresh_icon(item)
            except:
                pass

    update_display(mdl, this_ind_mask, edited=selected_ind)


def selected_a_coupled_inductor(mdl, mask_handle):
    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)

    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    select_coupled_prop = mdl.prop(this_ind_mask, "select_coupled")
    current_coupling_coefficient_prop = mdl.prop(this_ind_mask, "current_coupling_coefficient")
    change_prop = mdl.prop(this_ind_mask, "change")

    coupled_to_dict = couplings_dict.get(this_ind.item_fqid)
    displayed_ind = mdl.get_property_disp_value(select_coupled_prop)
    coupind_fqid = mdl.get_item(displayed_ind).item_fqid
    mdl.set_property_disp_value(current_coupling_coefficient_prop, coupled_to_dict[coupind_fqid])
    mdl.disable_property(change_prop)


def remove_coupling(mdl, mask_handle):
    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)

    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    select_coupled_prop = mdl.prop(this_ind_mask, "select_coupled")
    displayed_ind = mdl.get_property_disp_value(select_coupled_prop)
    ind_handle = mdl.get_item(displayed_ind)

    coupled_to_dict = couplings_dict.get(this_ind.item_fqid)
    counterpart_coupled_to_dict = couplings_dict.get(ind_handle.item_fqid)

    coupled_to_dict.pop(ind_handle.item_fqid)
    counterpart_coupled_to_dict.pop(this_ind.item_fqid)

    # Update couplings_dict of all inductors:
    for item in all_circuit_components(mdl):
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                couplings_dict_property = mdl.prop(item, "couplings_dict")
                mdl.set_property_combo_values(couplings_dict_property, [str(couplings_dict)])
                mdl.set_property_value(couplings_dict_property, str(couplings_dict))
                mdl.refresh_icon(item)
        except:
            pass

    update_display(mdl, this_ind_mask)


def change_coupling_value(mdl, mask_handle):
    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)

    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    select_coupled_prop = mdl.prop(this_ind_mask, "select_coupled")
    displayed_ind = mdl.get_property_disp_value(select_coupled_prop)
    ind_handle = mdl.get_item(displayed_ind)
    current_coupling_coefficient_prop = mdl.prop(this_ind_mask, "current_coupling_coefficient")

    coupled_to_dict = couplings_dict.get(this_ind.item_fqid)
    counterpart_coupled_to_dict = couplings_dict.get(ind_handle.item_fqid)

    new_value = mdl.get_property_disp_value(current_coupling_coefficient_prop)

    coupled_to_dict.update({ind_handle.item_fqid: new_value})
    counterpart_coupled_to_dict.update({this_ind.item_fqid: new_value})

    # Update couplings_dict of all inductors:
    for item in all_circuit_components(mdl):
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                couplings_dict_property = mdl.prop(item, "couplings_dict")
                mdl.set_property_combo_values(couplings_dict_property, [str(couplings_dict)])
                mdl.set_property_value(couplings_dict_property, str(couplings_dict))
        except:
            pass

    update_display(mdl, this_ind_mask, edited=displayed_ind)


def edited_current_coupling_box_value(mdl, mask_handle, new_value):
    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)

    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    select_coupled_prop = mdl.prop(this_ind_mask, "select_coupled")
    current_coupling_coefficient_prop = mdl.prop(this_ind_mask, "current_coupling_coefficient")
    change_prop = mdl.prop(this_ind_mask, "change")

    displayed_ind = mdl.get_property_disp_value(select_coupled_prop)
    displayed_coupling_value = mdl.get_property_disp_value(current_coupling_coefficient_prop)
    coupled_to_dict = couplings_dict.get(this_ind.item_fqid)

    ind_handle = mdl.get_item(displayed_ind)

    if coupled_to_dict[ind_handle.item_fqid] == str(new_value):
        mdl.disable_property(change_prop)
    else:
        mdl.enable_property(change_prop)


def update_all_inductors(mdl, item_handle):
    # items = mdl.get_items()
    items = all_circuit_components(mdl)

    ind_count = 0
    for item in items:
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                ind_count = ind_count + 1
        except:
            pass

    this_ind_mask = item_handle
    this_ind = mdl.get_parent(this_ind_mask)

    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))
    inductors_dict_prop = mdl.prop(this_ind_mask, "inductors_dict")
    inductors_dict = ast.literal_eval(mdl.get_property_value(inductors_dict_prop))

    # When the model is loaded, the fqids change
    if this_ind.item_fqid not in inductors_dict and len(inductors_dict) == ind_count:
        # Replace inductors_dict entries
        new_fqids = {}
        for ind_fqid in list(inductors_dict):
            # Get the handle by the name
            ind = mdl.get_item(inductors_dict[ind_fqid])
            # user may rename right after opening the model
            if ind:
                # Set the new fqid for this name
                inductors_dict[ind.item_fqid] = inductors_dict.pop(ind_fqid)
                new_fqids[ind_fqid] = ind.item_fqid
            else:
                mdl.info(
                    "Current known limitation: cannot rename a Coupled Inductor before double-clicking one of them, after opening a saved model. Please undo the changes or reopen the model.")
                raise Exception("Error when updating Coupled Inductors.")

        # Replace couplings_dict entries
        for ind_fqid in list(couplings_dict):
            coupled_to_dict = couplings_dict[ind_fqid]
            for coupled_ind_fqid in list(coupled_to_dict):
                new_fqid = new_fqids[coupled_ind_fqid]
                if coupled_to_dict.get(coupled_ind_fqid):
                    coupled_to_dict.update({new_fqid: coupled_to_dict.pop(coupled_ind_fqid)})
            couplings_dict[new_fqids[ind_fqid]] = couplings_dict.pop(ind_fqid)

    # If the model wasn't just loaded
    else:
        list_of_inductors = []

        for item in items:
            try:
                if mdl.get_component_type_name(item) == "Coupled Inductor":
                    list_of_inductors.append(item)
                    inductors_dict.update({item.item_fqid: mdl.get_name(item)})
            except:
                pass
        # Remove deleted inductors
        for ind_fqid in list(inductors_dict):
            # If that fqid cannot be found in the current list of Coupled Inductor components
            if not ind_fqid in [i.item_fqid for i in list_of_inductors]:
                inductors_dict.pop(ind_fqid, None)
                # Also update the couplings
                couplings_dict.pop(ind_fqid, None)
                for coupled_to_dict in list(couplings_dict.values()):
                    coupled_to_dict.pop(ind_fqid, None)

    # Update dicts of every inductor
    for item in items:
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                inductors_dict_property = mdl.prop(item, "inductors_dict")
                couplings_dict_property = mdl.prop(item, "couplings_dict")
                mdl.set_property_combo_values(inductors_dict_property, [str(inductors_dict)])
                mdl.set_property_combo_values(couplings_dict_property, [str(couplings_dict)])
                # Also must set the property value
                mdl.set_property_value(inductors_dict_property, str(inductors_dict))
                mdl.set_property_value(couplings_dict_property, str(couplings_dict))
                mdl.refresh_icon(item)
        except:
            pass


def pre_compile(mdl, mask_handle):
    import ast

    this_ind_mask = mask_handle
    this_ind = mdl.get_parent(this_ind_mask)

    # Property handles
    couplings_dict_prop = mdl.prop(this_ind_mask, "couplings_dict")
    couplings_dict = ast.literal_eval(mdl.get_property_value(couplings_dict_prop))

    inductors_dict_prop = mdl.prop(this_ind_mask, "inductors_dict")
    inductors_dict = ast.literal_eval(mdl.get_property_value(inductors_dict_prop))

    items = all_circuit_components(mdl)
    ind_count = 0
    raise_error_topology_change = False

    for item in items:
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                if not mdl.get_name(item) in inductors_dict.values():
                    # Renamed
                    raise_error_topology_change = True
                ind_count = ind_count + 1
        except:
            pass

    if not ind_count == len(inductors_dict):
        # Deleted/added
        raise_error_topology_change = True

    if raise_error_topology_change:
        mdl.info(
            "A Coupled Inductor was added/removed/renamed. Please double-click any Coupled Inductor component to update before starting Xyce.")

    for ind_fqid in inductors_dict:
        for coupled_to_dict in list(couplings_dict.values()):
            found_entry = coupled_to_dict.pop(ind_fqid, None)
            if found_entry:
                coupled_to_dict[inductors_dict[ind_fqid]] = found_entry

        has_couplings = couplings_dict.pop(ind_fqid, None)
        if has_couplings:
            couplings_dict[inductors_dict[ind_fqid]] = has_couplings

    # Adds self inductances to couplings_dict to allow coupling coefficient calculation
    # Substitutes fqids by inductor names
    for item in items:
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                self_inductance_property = mdl.prop(item, "L")
                ind_self = mdl.get_property_value(self_inductance_property)
                ind_name = mdl.get_name(item)

                for key, coupled_to_dict in couplings_dict.items():
                    if key == ind_name:
                        coupled_to_dict.update({ind_name: ind_self})
        except:
            pass

    for item in all_circuit_components(mdl):
        try:
            if mdl.get_component_type_name(item) == "Coupled Inductor":
                xyce_couplings_dict_property = mdl.prop(item, "xyce_couplings_dict")

                if raise_error_topology_change:
                    mdl.set_property_combo_values(xyce_couplings_dict_property, 0)
                    mdl.set_property_value(xyce_couplings_dict_property, 0)
                else:
                    mdl.set_property_combo_values(xyce_couplings_dict_property, [str(couplings_dict)])
                    mdl.set_property_value(xyce_couplings_dict_property, str(couplings_dict))
        except:
            pass