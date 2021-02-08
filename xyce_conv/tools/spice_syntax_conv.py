import re
from pathlib import Path

def spice_to_xyce(original_file):
    complete_lines = get_complete_lines(original_file)
    fixed_lines = []
    for line in complete_lines:
        new_line = line
        new_line = fix_model_statements(new_line)
        new_line = fix_dependent_sources(new_line)
        new_line = fix_N_not_V(new_line)
        new_line = fix_TC_entries(new_line)
        new_line = fix_diode_models(new_line)
        new_line = fix_polynomials(new_line)
        new_line = fix_controlled_source_lines(new_line)
        new_line = re.sub(' +', ' ', new_line)  # Remove extra spaces
        fixed_lines.append(new_line)

    output_file = Path(original_file).parent.joinpath(Path((Path(original_file).stem + "_fixed.lib")))
    if not "_fixed_fixed.lib" in str(output_file):
        with open(output_file, "w") as wf:
            wf.writelines(fixed_lines)
        return output_file
    else:
        return original_file

def get_complete_lines(input_file):
    """ Return a list with equivalent single line statements. """
    with open(input_file) as f:
        all_lines = f.readlines()
        complete_lines = []

        for line in all_lines:
            if not line.isspace():
                if line[0] == "+":  # Construct a single line
                    complete_lines[-1] = complete_lines[-1][:-1] + " " + line[1:]
                else:
                    complete_lines.append(line)

        return complete_lines

def fix_model_statements(input_line):
    """ Fix .MODEL statement lines """

    model_statement = re.match(r"\.model", input_line, re.IGNORECASE)

    if model_statement:
        # 1 - Commas are not allowed between parameters
        input_line = input_line.replace(",", " ")

        # 2 - If parentheses are used, there must be only one before the parameters and one after

        # Get everything inside of the parentheses
        inside_pars = re.match(r"\.model\s+\w+\s\w+\(([^\n]+)\)", input_line, re.IGNORECASE)
        if inside_pars:
            inside_pars = inside_pars[1].replace("(", " ")
            inside_pars = inside_pars.replace(")", " ")
            input_line = re.sub(r"(\.model\s+\w+\s\w+\()([^\n]+)(\))", rf"\1{inside_pars}\3", input_line, re.IGNORECASE)

        # 3 - Parameters without a value are not supported (PAR=)
        input_line = re.sub(r"[, ]\w+\s*=\s*(?=\w+\s*=|$\n+)", " ", input_line)  # Remove if found

    return input_line


def fix_diode_models(input_line):
    """ LEVEL=2 must be added to diode models """
    diode_model_line = re.match(r"(\.model[^\n]+ d[\(\s]+)([^\n]+\n)", input_line, re.IGNORECASE)
    new_line = input_line

    if diode_model_line:
        model_parameters = diode_model_line[2]
        if not "level=" in model_parameters.lower():
            model_parameters = "LEVEL=2 " + model_parameters
        new_line = re.sub(r"(\.model[^\n]+d[\(\s]+)([^\n]+\n)",
                            repl=rf"\1{model_parameters}",
                            string=input_line,
                            flags=re.IGNORECASE)

    return new_line


def fix_controlled_source_lines(input_line):
    # Remove unnecessary parentheses and commas
    controlled_source_line = re.match(r"^(E|F|G|H)[\w]+", input_line, re.IGNORECASE)
    unnecessary_pars = False
    if controlled_source_line:
        unnecessary_pars = re.findall(r"TABLE[^\n]+|POLY[^\n]+|\{[^\n]+|\=[^\n]+|(\([\w, ]+\))+", input_line, flags=re.IGNORECASE)
        if unnecessary_pars == ['']:
            unnecessary_pars = False

    new_line = input_line

    if unnecessary_pars:
        for up in unnecessary_pars:
            up_fixed = up.replace("(", "").replace(",", " ").replace(")", "")
            new_line = new_line.replace(up, up_fixed)

    return new_line

def fix_polynomials(input_line):
    """ Remove parentheses and commas from POLY points """
    new_line = input_line

    poly_line = re.match(r"([^\n]+POLY\([0-9]\))(.+)", input_line, flags=re.IGNORECASE)
    if poly_line:
        subs_part = poly_line[2]
        subs_part = subs_part.replace(",", " ").replace("(", " ").replace(")", " ")

        new_line = re.sub(r"([^\n]+POLY\([0-9]\))(.+)",
                          repl=rf"\1{subs_part}",
                          string=input_line,
                          flags=re.IGNORECASE)
    return new_line

def fix_dependent_sources(input_line):
    """ Fix table syntax for dependent sources """

    table_statement = re.match(r".*table.*", input_line, flags=re.IGNORECASE)
    n_line = input_line

    # If source values come from a table
    if table_statement:

        # If there is no equal sign, the following (illegal) syntax is being used: table {expr} ((x1,y1) ... (xn,yn))
        if not "=" in table_statement[0]:
            n_line = re.sub(r"([^\n]+table\s+)([^\n]+)(?=\s*\(\s*\()\(([^\n]+)\)",
                                repl=r"\1\2 = \3",
                                string=n_line,
                                flags=re.IGNORECASE)

        # If there is an equal sign, but no commas between the values: table {expr} = (x1 y1) ... (xn yn)
        else:
            table_points_match = re.match(r"([^\n]+table\s+)([^\n]+)(\s=\s)([^\n]+)", n_line, flags=re.IGNORECASE)
            if table_points_match:
                table_points = table_points_match[4]

                new_table_points = re.sub(r"(\([^,\s]+)([,\s]+)([^,\s]+\))",
                                            repl=r"\1,\3",
                                            string=table_points,
                                            flags=re.IGNORECASE)

                n_line = re.sub(r"([^\n]+table\s+)([^\n]+)(\s=\s)([^\n]+)",
                                repl=fr"\1\2\3{new_table_points}",
                                string=input_line,
                                flags=re.IGNORECASE)
    return n_line

def fix_N_not_V(input_line):
    """ Fix cases where the PSpice netlist used N() rather than V(). """
    n_line = input_line
    n_line = re.sub(r"( N)(\([^\n]+\))",
                    repl=r" V\2",
                    string=n_line,
                    flags=re.IGNORECASE)
    return n_line

def fix_TC_entries(input_line):
    """ Temperature coefficient (TC) specification must have commas between values """
    n_line = input_line
    n_line = re.sub(r"([^\n]+)( TC\s*=\s*[^,\s]+)([\s,]+)([^,\s]+)",
                    repl=r"\1\2,\4",
                    string=n_line,
                    flags=re.IGNORECASE)
    return n_line

# Future functions, if necessary

def fix_pwl_sources(input_line):
    pass

def fix_nested_expressions(input_line):
    pass

def fix_node0_in_subcirc(input_line):
    pass
