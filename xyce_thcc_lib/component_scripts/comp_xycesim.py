import sys
import pathlib
import importlib
import tse_to_xyce
import subprocess
from PyQt5 import QtWidgets, QtCore

keep_open = {}

class LocateXyce(QtWidgets.QWidget):
    def __init__(self, mdl):
        super().__init__()
        self.mdl = mdl

    def parse_file(self):
        choose_file = QtWidgets.QFileDialog()
        self.mdl.info(r"Please find the Xyce executable folder. It is located by default on C:\Program Files\Xyce *version*\bin.")

        file, _ = choose_file.getOpenFileName(self, 'Find the Xyce executable', r'C:\Program Files', 'Xyce Executable (Xyce.exe)')

        if file:
            return file
        else:
            return False

def sim_with_xyce(mdl, mask_handle, xyce_simulator_path):
    try:
        ih = mdl.get_parent(mask_handle)  # Component handle
    except:
        mdl.info(
            "If this XyceSim component was copied from another model, please save and reload this model or add a new XyceSim from the Library Explorer.")
        raise Exception()

    sim_params_dict = {}

    timeint_abstol = mdl.get_property_disp_value(mdl.prop(ih, "timeint_abstol"))
    timeint_reltol = mdl.get_property_disp_value(mdl.prop(ih, "timeint_reltol"))
    timeint_method_dict = {"Trapezoidal": "7", "Gear": "8"}
    timeint_method = mdl.get_property_disp_value(mdl.prop(ih, "timeint_method"))
    sim_params_dict['timeint_abstol'] = timeint_abstol
    sim_params_dict['timeint_reltol'] = timeint_reltol
    sim_params_dict['timeint_method'] = timeint_method_dict[timeint_method]

    analysis_type = mdl.get_property_disp_value(mdl.prop(ih, "sim_type"))
    sim_params_dict['analysis_type'] = analysis_type
    if analysis_type == "Transient":
        sim_time = mdl.get_property_disp_value(mdl.prop(ih, "sim_time"))
        max_ts = mdl.get_property_disp_value(mdl.prop(ih, "max_ts"))
        sim_params_dict['sim_time'] = sim_time
        sim_params_dict['max_ts'] = max_ts
        nonlinear_solver_dict = {"Newton": "0", "Gradient": "1", "Trust region": "2"}
        nonlinear_solver = mdl.get_property_disp_value(mdl.prop(ih, "nonlinear_solver"))
        voltage_limiting = mdl.get_property_disp_value(mdl.prop(ih, "voltage_limiting"))
        nonlinear_maxstep = mdl.get_property_disp_value(mdl.prop(ih, "nonlinear_maxstep"))
        nonlinear_abstol = mdl.get_property_disp_value(mdl.prop(ih, "nonlinear_abstol"))
        nonlinear_reltol = mdl.get_property_disp_value(mdl.prop(ih, "nonlinear_reltol"))
        calculate_operation_point = mdl.get_property_disp_value(mdl.prop(ih, "calculate_operation_point"))
        sim_params_dict['nonlinear_solver'] = nonlinear_solver_dict[nonlinear_solver]
        sim_params_dict['voltage_limiting'] = voltage_limiting
        sim_params_dict['nonlinear_maxstep'] = nonlinear_maxstep
        sim_params_dict['nonlinear_abstol'] = nonlinear_abstol
        sim_params_dict['nonlinear_reltol'] = nonlinear_reltol
        if type(calculate_operation_point) == str:
            sim_params_dict['calculate_operation_point'] = calculate_operation_point == "True"
        else:
            sim_params_dict['calculate_operation_point'] = calculate_operation_point
    elif analysis_type == "AC small-signal":
        start_f = mdl.get_property_disp_value(mdl.prop(ih, "start_f"))
        end_f = mdl.get_property_disp_value(mdl.prop(ih, "end_f"))
        num_points = mdl.get_property_disp_value(mdl.prop(ih, "num_points"))
        sim_params_dict['start_f'] = start_f
        sim_params_dict['end_f'] = end_f
        sim_params_dict['num_points'] = num_points

    # Export to JSON to the Target Files folder
    mdl.export_model_to_json()

    # Get the path to the exported JSON
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = mdlfile.split('\\')[-1].split('.')[0]
    mdlfile_folder = '/'.join(mdlfile.split('\\')[0:-1])
    mdlfile_target_folder = mdlfile_folder + '/' + mdlfile_name + ' Target files'
    json_file_path = mdlfile_target_folder + '/' + mdlfile_name + '.json'

    import xyce_thcc_lib.gui_scripts.xycesim as xc
    # importlib.reload(xc)
    from xyce_thcc_lib.gui_scripts.xycesim import XyceOutput

    mainwindow = XyceOutput(mdl, json_file_path, sim_params_dict, xyce_simulator_path)
    mainwindow.show()
    keep_open.update({'xycewin': mainwindow})

    ok_button = mdl.get_ns_var("ok_button_handle")
    ok_button.click()

def get_xyce_simulator_path(mdl, mask_handle):
    locate_xyce_dialog = LocateXyce(mdl)
    xyce_path = locate_xyce_dialog.parse_file()
    if xyce_path:
        return str(xyce_path)

def test_xyce_available(mdl, mask_handle):

    xyce_available = False

    try:
        with open("xyce_simulator_path.txt") as f:
            xyce_simulator_path = f.readline()
            subprocess.run(xyce_simulator_path)
            xyce_available = True
    except FileNotFoundError:
        try:
            xyce_simulator_path = get_xyce_simulator_path(mdl, mask_handle)
            if xyce_simulator_path:
                xyce_simulator_path = pathlib.Path(xyce_simulator_path)
                if str(xyce_simulator_path.parent) not in sys.path:
                    sys.path.append(str(xyce_simulator_path.parent))
                subprocess.run(f"{str(xyce_simulator_path)}")
                xyce_available = True
                with open("xyce_simulator_path.txt", "w") as f:
                    f.write(f"{str(xyce_simulator_path)}")
        except FileNotFoundError:
            pass

    if not xyce_available:
        raise Exception("Could not find a valid Xyce simulator executable. Please install and locate the file.")
    else:
        return xyce_simulator_path

def start_sim(mdl, mask_handle):
    xyce_simulator_path = test_xyce_available(mdl, mask_handle)
    sim_with_xyce(mdl, mask_handle, xyce_simulator_path)


def open_sa(mdl):
    if keep_open.get('xycewin'):
        keep_open['xycewin'].plot_data()
    else:
        mdl.info('No plot data.')

def update_display(mdl, mask_handle):
    sim_type = mdl.get_property_disp_value(mdl.prop(mask_handle, "sim_type"))

    end_f = mdl.prop(mask_handle, "end_f")
    mdl.hide_property(end_f)
    start_f = mdl.prop(mask_handle, "start_f")
    mdl.hide_property(start_f)
    num_points = mdl.prop(mask_handle, "num_points")
    mdl.hide_property(num_points)
    sim_time = mdl.prop(mask_handle, "sim_time")
    mdl.hide_property(sim_time)
    max_ts = mdl.prop(mask_handle, "max_ts")
    mdl.hide_property(max_ts)

    if sim_type == "Transient":
        mdl.show_property(sim_time)
        mdl.show_property(max_ts)
    elif sim_type == "AC small-signal":
        mdl.show_property(start_f)
        mdl.show_property(end_f)
        mdl.show_property(num_points)