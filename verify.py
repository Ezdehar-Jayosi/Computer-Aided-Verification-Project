from python.z3 import *


# from python.z3 import Solver, Fixedpoint, SolverFor, sat
def find_preNode(path):
    i = 0
    while i < len(path) - 2:
        if path[i].get("type") == "assert":
            return path[i].get("label")
        i += 1
    return ""


def lastInv(path, var_list, last_node_indx):
    if path[last_node_indx].get("node").next is None:
        return "False"
    str = "Inv("
    for var in var_list:
        str += var.get("id").strip() + ", "
    str = str[:-2] + ")"
    return str


def forAll(variables, lastinv):
    str = "["
    i = 0
    for v in variables:
        str += v.get("id").strip() + ","
        if (i < len(lastinv)) and v.get("id") != lastinv[i].get("id"):
            str += lastinv[i].get("id").strip() + ","
            # v.append(lastinv[i])

        i += 1
    str = str[:-1] + "]"
    return str


def checkPathCorrectness(path, exec_str, first_Inv):
    post_node = ""
    pre_node = find_preNode(path)
    last_var_indx = len(path) - 1
    if path[len(path) - 1].get("type") == "assert":
        post_node = path[len(path) - 1].get("label")
        last_var_indx -= 1
    if path[len(path) - 1].get("type") == "ensures":
        post_node = path[len(path) - 1].get("label")
        if post_node.startswith("("):
            post_node = post_node[1:-1]
            last_var_indx -= 1

    # Add all variables declaration, including the new variables from assignment
    variables = path[0].get("node").variables
    if path[len(path) - 1].get("type") == "ensures" or path[len(path) - 1].get("type") == "assert":
        # variables_2 = path[len(path) - 2].get("node").variables
        t2 = path[len(path) - 2].get("T")
    else:
        # variables_2 = path[len(path) - 1].get("node").variables
        t2 = path[len(path) - 1].get("T")
    # addVariables(variables, path[0].get("T"), t2, s)

    last_Inv = lastInv(path, path[last_var_indx].get("var"), last_var_indx)
    forall = forAll(path[0].get("node").variables, path[last_var_indx].get("var"))
  
    if path[len(path) - 1].get("type") == "ensures":
        return_var = path[len(path) - 1].get("return_value")
        post_node = post_node.replace("ret", return_var)

    i = 0
    t2 = t2.replace("(", "").replace(")", "").split(',,')
    conditions = ""
    for t1 in (path[0].get("T")[1:-1]).split(',,'):
        var_name = path[0].get("var")[i].get("id").strip()
        var_name = " ".join(var_name.split())

        if var_name != (" ".join(t1.split())):
            conditions += var_name + " == " + " ".join(t1.split()) + ", "

        i += 1
    conditions = conditions[:-2]
    # actual_line =
    first_inv = False
    s_str = "s.add(ForAll(" + forall + ", Implies(And( "
    if path[0].get("type") != "function_definition":
        s_str += first_Inv
        first_inv=True
    if " ".join(pre_node.split()) != "" and " ".join(pre_node.split()) != "true":
        if  s_str[:-1].endswith("(") is False:
            s_str += ", "
        s_str += " ".join(pre_node.split())
    if " ".join(path[0].get("R").split()) != "True":
        if  s_str[:-1].endswith("(") is False:
            s_str += ", "
        s_str += " ".join(path[0].get("R").split())
    if conditions !="":
        if s_str[:-1].endswith("(") is False:
            s_str += ", "
        s_str += conditions
    if " ".join(post_node.split()) != "":
        if  s_str[:-1].endswith("(") is False:
            s_str += ", "
        s_str += "Not(" + " ".join(post_node.split()) + ")"
    s_str += "), "+last_Inv + ")))"

    exec_str.append(s_str)


def declare_variables(path, exec_str):
    variables = path[0].get("node").variables
    i = 0
    first_Inv = "Inv("
    inv = "Inv = Function(" + "'Inv'" + ", "
    for var in variables:
        var_name = var.get("id").strip()
        var_type = var.get("type")
        var_name = " ".join(var_name.split())
        var_type = " ".join(var_type.split())
        first_Inv += var_name + ", "
        if var_type == "INT":

            if var_name.endswith("]") or (var.get("is_arr") is True):  # Array variable
                inv += " ArraySort(IntSort(), IntSort()), "
                exec_str.append(var_name + " = Array('" + var_name + "', IntSort(), IntSort())")
                exec_str.append ("_" + var_name + " = Array('" + var_name + "', IntSort(), IntSort())")
            else:  # not Array variable
                inv += "IntSort(), "
                exec_str.append (var_name + " = Int('" + var_name + "')")
                exec_str.append("_" + var_name + " = Int('" + "_" + var_name + "')")
        elif var_type == "DOUBLE":

            if var_name.endswith("]"):  # Array variable
                inv += " ArraySort(IntSort(), RealSort()), "
                exec_str.append(var_name + " = Array('" + var_name + "', IntSort(), RealSort())")
                exec_str.append( "_" + var_name + " = Array('" + var_name + "', IntSort(), RealSort())")

            else:  # not Array variable
                inv += "RealSort(), "
                exec_str.append( var_name + " = Real('" + var_name + "')")
                exec_str.append("_" + var_name + " = Real('" + var_name + "')")

        i += 1
    inv += "BoolSort())"
    exec_str.append(inv)
    first_Inv = first_Inv[:-2] + ")"
    return first_Inv



def checkCorrectness(paths):
    s = Solver()
    for path in paths:
        exec_str = []
        first_inv = declare_variables(path[0], exec_str)
        for inner_path in path:
            checkPathCorrectness(inner_path, exec_str, first_inv)
        print("==========================finished first set=============================")
        for str_s in exec_str:
            print(str_s)
            exec(str_s)
        res = s.check()
        print(res)
        #print(s.model())
        if res == sat:
            print(s.model())