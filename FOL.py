import copy


def replaceVar(var_arr, var):
    i = 0
    for v in var_arr:
        if v.get("id").strip() == (var.get("id").strip())[1:]:
            var_arr.insert(i, var)
            var_arr.pop(i + 1)
            # var_arr.append(var)
            return
        i += 1


def make_T(variables):
    t = "("
    for var in variables:
        # print("printing var type " + var.get("type") + " ")
        # print("printing var id " + var.get("id") + " ")

        if (var.get("id")).endswith("[ ]"):
            var_name = (var.get("id"))[:-4]
        else:
            var_name = var.get("id")
        t = t + " " + var_name + ",, "
    t = t.strip()
    t = t[:-2] + ")"
    return t


def getLabel(cond_label):
    if "<=" in cond_label:
        label_arr = cond_label.split("<=")
        op = "<="

    elif ">=" in cond_label:
        label_arr = cond_label.split("<")
        op = ">="

    elif "<" in cond_label:
        label_arr = cond_label.split("<")
        op = "<"
    elif ">" in cond_label:
        label_arr = cond_label.split(">")
        op = ">"
    elif "==" in cond_label:
        label_arr = cond_label.split("==")
        op = "=="
    elif "!=" in cond_label:
        label_arr = cond_label.split("!=")
        op = "!="

    var = label_arr[0]
    value = label_arr[1]
    r_var = var.replace('(', '').replace(')', '')
    r_var = r_var.strip()
    value = value.replace('(', '').replace(')', '')
    value = value.strip()
    # if the var is and arr
    if value.endswith("]"):
        n_value = value[:value.index("[")]
        n_value = n_value.strip('(')
        arr_index = value[value.index("[") + 1:value.rindex("]")]
        value = " Select ( " + n_value + "," + arr_index + ")"
    if r_var.endswith("]"):
        # print("---------------------------------------------------------------------------------------------------")
        arr_name = r_var[:r_var.index("[")]
        arr_name = arr_name.strip('(')
        arr_index = r_var[r_var.index("[") + 1:r_var.rindex("]")]
        var = " Select ( " + arr_name + "," + arr_index + ")"
    return var + " " + op + " " + value


def condition_fol(route, indx):
    route[indx]["T"] = route[indx + 1].get("T")
    route[indx]["var"] = route[indx + 1].get("var")
    label = getLabel(route[indx].get("label"))
    r = " And (" + route[indx + 1].get("R") + ", "
    if route[indx].get("node").trueNode.id == route[indx + 1].get("id"):
        route[indx]["R"] = r + label + " )"
    else:
        route[indx]["R"] = r + " Not ( " + label + ") )"



def setTR_v1(route, indx):
    route[indx]["R"] = route[indx + 1]["R"]
    route[indx]["T"] = route[indx + 1]["T"]
    route[indx]["var"] = route[indx + 1]["var"]
    if route[indx].get("type") == "declaration":

        # print("label is " + route[indx].get("node").label + " is in is " + str("=" in route[indx].get("node").label))
        if "=" in route[indx].get("node").label:
            var = (route[indx].get("node").label).split("=")[0]
            value = (route[indx].get("node").label).split("=")[1]
            value = value.replace('(', '').replace(')', '')
            value = value.strip()
            if value.endswith("]"):
                n_value = value[:value.index("[")]
                n_value = n_value.strip('(')
                arr_index = value[value.index("[") + 1:value.rindex("]")]
                value = " Select ( " + n_value + "," + arr_index + ")"
            # print("==== var is =====" + var.strip() + "======== val is ======== "+value)
            # print("T is   "+route[indx].get("T"))
            route[indx]["T"] = route[indx].get("T").replace(" " + var.strip(), " " + value.strip())


def setTR_v2(route, indx):
    route[indx]["R"] = " True "
    route[indx]["T"] = make_T(route[indx].get("node").variables)
    route[indx]["var"] = copy.deepcopy(route[indx].get("node").variables)
    if route[indx].get("type") == "declaration":
        # print("label is " + route[indx].get("node").label + " is in is " + str("=" in route[indx].get("node").label))
        if "=" in route[indx].get("node").label:
            var = (route[indx].get("node").label).split("=")[0]
            value = (route[indx].get("node").label).split("=")[1]
            # print("==== var is =====" + var.strip() + "======== val is ======== " + value)
            # print("T is   " + route[indx].get("T"))
            if value.endswith("]"):
                n_value = value[:value.index("[")]
                n_value = n_value.strip('(')
                arr_index = value[value.index("[") + 1:value.rindex("]")]
                value = " Select ( " + n_value + "," + arr_index + ")"
            route[indx]["T"] = route[indx].get("T").replace(" " + var.strip(), " " + value.strip())


def setRT(route, indx):
    if len(route) == indx + 1:
        # setTR_v2(route, indx)
        route[indx]["R"] = " True "
        route[indx]["T"] = make_T(route[indx].get("node").variables)
        route[indx]["var"] = copy.deepcopy(route[indx].get("node").variables)

    else:
        # setTR_v1(route, indx)
        route[indx]["R"] = route[indx + 1].get("R")
        route[indx]["T"] = route[indx + 1].get("T")
        route[indx]["var"] = route[indx + 1].get("var")


def assignment_fol(route, indx):
    label = route[indx].get("label")
    label = label.strip()
    if label.endswith("--"):
        var = label.split("--")[0]
        value = " (" + var + "- 1 )"
    if label.endswith("++"):
        var = label.split("++")[0]
        value = " (" + var + "+ 1 )"
    else:  # var = value
        var = label.split("=")[0]
        value = label.split("=")[1]

    setRT(route, indx)
    r_var = var.replace('(', '').replace(')', '')
    r_var = r_var.strip()
    value = value.replace('(', '').replace(')', '')
    value = value.strip()
    t_var = r_var
    # if the var is and arr
    if value.endswith("]"):
        n_value = value[:value.index("[")]
        n_value = n_value.strip('(')
        arr_index = value[value.index("[") + 1:value.rindex("]")]
        value = " Select ( " + n_value + "," + arr_index + ")"
    if r_var.endswith("]"):
        # print("---------------------------------------------------------------------------------------------------")
        arr_name = r_var[:r_var.index("[")]
        arr_name = arr_name.strip('(')
        arr_index = r_var[r_var.index("[") + 1:r_var.rindex("]")]
        value = " Store ( " + arr_name + "," + arr_index + "," + "(" + value + ")" + ")"
        # route[indx]["T"] = route[indx]["T"].replace(var, new_val)
        # t_var = arr_name
        # print("----------------------------------values is" + value +"---------------------------------------------------")
        # print("----------------------------------t_var  is" + t_var +"---------------------------------------------------")
        # print("----------------------------------r_var  is" + r_var +"---------------------------------------------------")
    # print("1============== "+route[indx].get("T")+" ================1")
    route[indx]["T"] = route[indx].get("T").replace(" " + t_var, " " + value)
    # print("2============== "+route[indx].get("T") + " ================2")
    # print("3============== "+route[indx].get("R") + " ================3")
    route[indx]["R"] = route[indx].get("R").replace(" " + r_var, " " + value)
    route[indx]["var"] = route[indx].get("var")
    if route[indx].get("var") is None:
        route[indx]["var"] = route[indx].get("node").variables
    if route[indx].get("node").assign_decl is False:
        t_var = "_" + t_var
    replaceVar(route[indx].get("var"), {"type": "",
                                        "id": t_var,
                                        "count": 0
                                        })
    # print("4============== " + route[indx].get("R") + " ================4")


def findReturnNode(route):
    i = 0
    # print("len route is " + str(len(route)) + " =================================================================")
    while i < len(route):
        # print("====================================" +route[i].get("label")+"=========================================")
        if route[i].get("label").startswith("return"):
            ret = route[i].get("label")
            # print("--------------found it at indx "+ str(i) + "---------------")
            return (ret.replace("return", "")).strip("")[:-1]
        i += 1
    return None


def fol_create(route, indx):
    if indx < len(route) - 1:
        fol_create(route, indx + 1)
    node_type = route[indx].get("type")
    if node_type == "ensures" and indx == 0:
        ensure_node = route.pop(0)
        return_var = findReturnNode(route)
        if not (return_var is None):
            return_var = (return_var.strip())[:-1]
            # print("return var is " + return_var + "-----------------------------------------------")
            # new_ensures_label = ensure_node.get("label").replace("ret", return_var)
            # print(" new_ensures_label " + new_ensures_label + "-----------------------------------------------")

            ensure_node = {"id": ensure_node.get("id"), "type": ensure_node.get("type"),
                           "label": ensure_node.get("label"),
                           "node": ensure_node.get("node"), "return_value": return_var}
        route.append(ensure_node)
    if node_type == "condition statement" or node_type == "loop":
        condition_fol(route, indx)
    elif node_type == "expression_statement" or node_type == "postfix_expression":
        assignment_fol(route, indx)
    elif node_type == "return" or (indx == len(route) - 1):
        setTR_v2(route, indx)
    elif node_type == "function_definition" or node_type == "declaration" or node_type == "assert":
        setTR_v1(route, indx)


def fol(routes):
    for route in routes:
        for rt in route:
            fol_create(rt, 0)
