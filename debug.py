import time
import pathlib

t0 = time.time()
jsonfile = r"D:\Dropbox\Typhoon HIL\Ideas\TSE2Xyce\examples\test Target files\test.json"

jsonfile_name = pathlib.Path(jsonfile).stem

sim_parameters = {
        'timeint_abstol': '1e-6',
        'timeint_reltol': '1e-2',
        'timeint_method': '7',
        'nonlinear_maxstep': '20',
        'nonlinear_abstol': '1e-6',
        'nonlinear_reltol': '1e-3',
        'nonlinear_solver': '0',
    }
sim_parameters.update({'analysis_type': 'Transient','max_ts': '5e-7','sim_time': '3ms'})

import tse_to_xyce
from tse_to_xyce.tse2tpt_base_converter import tse2tpt

t0 = time.time()

xyce_folder_path = pathlib.Path(jsonfile).parent.joinpath('xyce')
tse2tpt.start_conversion(jsonfile, tse_to_xyce, simulation_parameters=sim_parameters)
xycefile = xyce_folder_path.joinpath(jsonfile_name + "_master.dss")

# import xyce_thcc_lib.extra.report_functions as rf
# # rf.generate_faultstudy_report(jsonfile_name)[1]
# rf.generate_report(jsonfile_name)[1]


print(time.time() - t0)

#
# Demonstrate use of create_mask function.
#
import os
import re
from typhoon.api.schematic_editor import SchematicAPI

# Path to example model
# model_path = os.path.join("D:\Dropbox\Typhoon HIL\Ideas","delete_this.tse")
#
# # Load model
# mdl = SchematicAPI()
# mdl.load(model_path)
#
# print("String representation of model:")
# complete_string = mdl.model_to_api()
# new_string = []
# for line in complete_string.splitlines():
#     if not any(["evaluate=" in line, "enabled=" in line, "visible=" in line]):
#         new_string.append(line)
# print("\n".join(new_string))
#
# for line in complete_string.splitlines():
#     re.match(r"[A-z0-9 \-_]+= mdl.create_property\(([\S\s]*?=[\S\s]*?)\)", line, flags=re.IGNORECASE)
# mdl.close_model()