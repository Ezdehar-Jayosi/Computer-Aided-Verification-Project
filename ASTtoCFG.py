import copy
import json
import CFG
import FOL
import verify

id = 0
i = 1


# ************* AST to CFG *************

def type_check(type):
    if type == "compound_statement" or type == "block_item_list" or type == "declaration" or \
            type == "expression_statement" or type == "function_definition" or type == "jump_statement" \
            or type == "selection_statement" or type == "iteration_statement" or type == "postfix_expression":
        return True
    return False


def get_node_id():
    global id
    node_id = id
    id = id + 1
    return node_id


def make_label(data):
    label = ""
    if data.get("children") is None:
        label = data.get("text") + " "
    if data.get("type") == "unary_expression" and data.get("children")[0].get("text") == "!":
        label = " Not ( " + make_label(data.get("children")[1]) + ") "
        return label
    else:
        if data.get("type") == "logical_and_expression":
            label = " And ( " + make_label(data.get("children")[0]) + ", " + make_label(
                data.get("children")[2]) + ") "
            return label
        else:
            if data.get("type") == "logical_or_expression":
                label = " Or ( " + make_label(data.get("children")[0]) + ", " + make_label(
                    data.get("children")[2]) + ") "
                return label
    if isinstance(data.get("children"), list):
        for child in data.get("children"):
            if isinstance(child, dict) and child.get("type") != "compound_statement":
                label = label + make_label(child)
    return label


def get_var_id(data):
    var_id = ""
    if data.get("type") == "direct_declarator":
        for child in data.get("children"):
            var_id = var_id + child.get("text")
    else:
        var_id = data.get("text")
    return var_id


def containsVar(var_arr, var,var_id):
    i=0
    for v in var_arr:
        if v.get("id").strip() == var_id.strip():
            if v.get("count") == -1:
                return True
            else:
                return False
        i+=1

    var_arr.append(var)
    return True


def replaceVar(var_arr, var):
    i = 0
    for v in var_arr:
        if v.get("id").strip() == (var.get("id").strip())[1:]:
            var_arr.pop(i)
            var_arr.append(var)
            return
        i += 1


def function_node(data, func_var):
    global id
    id = 0
    label = make_label(data)
    if label.startswith("inline void ensures"):
        return
    cfg_node = CFG.cfgNode(get_node_id(), data.get("type"), label)

    # get the function args, later each new declaration will be added/modified to the variable array
    variables_list = ((data.get("children")[1]).get("children")[2]).get(
        "children")  # the parameters list of the function
    is_arr = False
    for var in variables_list:
        if var.get("type") != ",":
            var_id = get_var_id((var.get("children")[1]))
            if var_id.endswith("]"):
                var_id = var_id[:var_id.index("[")]
                var_id = var_id.strip('(')
                is_arr = True
            func_var.append(
                {"type": (var.get("children")[0]).get("type"),
                 "id": var_id,
                 "count": 0,
                 "is_arr": is_arr
                 }
            )
            is_arr = False

    cfg_node.variables = func_var
    cfg_node.vars = copy.deepcopy(func_var)
    return cfg_node


def getVariables(data, type, func_var):
    for child in (data.get("children")):
        if not (var_id == ','):
            var_id = child.get("text")
            func_var.append({
                "type": type,
                "id": var_id,
                "count": 0
            })


def find_last_node(node):
    ptr = node.next
    tmp = ptr
    while not (ptr is None):
        tmp = ptr
        ptr = ptr.next
    return tmp


def declaration_node(data, func_var):
    var_type = (data.get("children")[0]).get("type")
    children_one = data.get("children")[1]
    assign_decl = False
    if isinstance(data.get("children")[1], dict):
        label = make_label(data.get("children")[1])
        if (data.get("children")[1].get("children")) is None:
            cfg_node = CFG.cfgNode(get_node_id(), data.get("type"), label)
            # print("****************************"+label)
            if not (label == ','):
                func_var.append({
                    "type": var_type,
                    "id": label,
                    "count": -1
                })
            cfg_node.variables = func_var

            return cfg_node
        # var_id = ((data.get("children")[1]).get("children")[0]).get("text")
        func_var2 = copy.deepcopy(func_var)
        for child in (data.get("children")[1].get("children")):
            if child.get("type") == "init_declarator_list":
                for chld in child.get("children"):
                    var_id = chld.get("text")
                    # print("*eeeeee***************************%" + var_id)

                    if not (var_id == ','):
                        func_var.append({
                            "type": var_type,
                            "id": var_id,
                            "count":-1
                        })

            else:
                var_id = child.get("text")
                # print("***ccccc*************************$" + var_id)

                if var_id == 'assert' or var_id == "=":
                    break
                if not (var_id == ','):
                    func_var.append({
                        "type": var_type,
                        "id": var_id,
                        "count": 0,
                    })
                    assign_decl = True

    else:
        return
    # var_id = child.get("text")

    cfg_node = CFG.cfgNode(get_node_id(), data.get("type"), label)

    cfg_node.variables = func_var
    cfg_node.assign_decl = assign_decl
    return cfg_node


def expression_statement_node(data, func_var):
    label = make_label(data.get("children")[0])
    expr = False
    # print("label is " + label)
    #print("label is -------------------------- " + label)
    if label.startswith('assert'):  # make an assert node
        label = (" ".join(label.split()))[6:]
        l_type = "assert"
    elif label.startswith('ensures'):
        l_type = "ensures"
        tmp_l = label[label.find("("):]
        label = tmp_l[0:-1]
    else:
        l_type = data.get("type")
        expr = True
    cfg_node = CFG.cfgNode(get_node_id(), l_type, label)
    if expr:

        if label.strip().endswith("++"):
            var_id = label.split("++")[0]
        elif label.strip().endswith("--"):
            var_id = label.split("--")[0]
        else:
            var_id = label.split("=")[0]
        var_id = var_id.replace('(', '').replace(')', '')
        var = {"type": "",
               "id": var_id,
               "count": 1
               }
        var = {"type": "",
               "id": var_id,
               "count": 0
               }
        cfg_node.assign_decl=containsVar(func_var, var, var_id)
        cfg_node.vars = func_var
        replaceVar(cfg_node.vars, var)
    cfg_node.variables = func_var
    return cfg_node


def jump_statement_node(data, func_var):
    cfg_node = CFG.cfgNode(get_node_id(), "return", make_label(data))
    cfg_node.variables = func_var
    return cfg_node


def selection_statement_node(data, func_var):
    # print("doing condition statement")
    cfg_node = CFG.cfgNode(get_node_id(), "condition statement", make_label(data.get("children")[2]))
    cfg_node.variables = func_var
    children = data.get("children")
    if data.get("children")[4].get("type") == "compound_statement":
        if_data = children[4].get("children")[1]
        cfg_node.trueNode = create_cfg(if_data, func_var)
        cfg_node.trueNode.prev = cfg_node
        cfg_node.trueNode.variables = cfg_node.variables
    else:
        cfg_node.trueNode = create_cfg(data.get("children")[4], func_var)
        cfg_node.trueNode.prev = cfg_node
        cfg_node.trueNode.variables = cfg_node.variables
    if len(data.get("children")) == 7:
        if data.get("children")[6].get("type") == "compound_statement":
            else_data = children[6].get("children")[1].get("children")[0]
            cfg_node.falseNode = create_cfg(else_data, func_var)
            cfg_node.falseNode.variables = cfg_node.variables
        else:
            cfg_node.falseNode = create_cfg(data.get("children")[6], func_var)
        cfg_node.falseNode.prev = cfg_node
        cfg_node.falseNode.variables = cfg_node.variables
    cfg_node.variables = func_var
    return cfg_node


def iteration_statement_node(data, func_var):
    # print("we found a loop")
    children = data.get("children")
    if (children[0].get("type") == "FOR"):
        # cfg_node = CFG.cfgNode(get_node_id(), "FOR", "FOR")
        # node_label= make_label(data.get("children")[3])
        condition_node = make_label(data.get("children")[3].get("children")[0])
        loop_block = data.get("children")[6]
        inc = make_label(data.get("children")[4])
        inc_node = CFG.cfgNode(get_node_id(), data.get("children")[4].get("type"), inc)
        inc_node.variables = func_var
        # create a node for the initialization, the condition node is its next node
        # init_node = create_cfg(data.get("children")[2].get("children")[0], func_var)
        init_cfg_node = create_cfg(data.get("children")[2], func_var)
        # print("init_cfg_node.label is" + init_cfg_node.label)
        # init_cfg_node.variables = func_var
        if loop_block.get("type") == "compound_statement":
            loop_node = create_cfg(loop_block.get("children")[1].get("children")[0], func_var)
        else:
            loop_node = create_cfg(loop_block.get("children")[1], func_var)
        cfg_node = CFG.cfgNode(get_node_id(), "loop", condition_node)
        next_node = loop_node
        if loop_node.prev is None:
            cfg_node.trueNode = loop_node
        else:
            cfg_node.trueNode = loop_node.prev
        while not (next_node.next is None):
            next_node = next_node.next
        if next_node.type == "loop":
            next_node.falseNode = inc_node
        else:
            next_node.next = inc_node
        inc_node.next = cfg_node
        init_cfg_node.variables = func_var
        cfg_node.variables = func_var
        init_cfg_node.next = cfg_node
        cfg_node.prev = init_cfg_node

        cfg_node.isConditionNode = True
        return cfg_node
    elif (children[0].get("type") == "DO"):  # DO WHILE loop

        condition_node = make_label(data.get("children")[4])
        loop_block = data.get("children")[1]
        cfg_node = CFG.cfgNode(get_node_id(), "loop", condition_node)
    else:
        condition_node = make_label(data.get("children")[2])
        loop_block = data.get("children")[4]
        cfg_node = CFG.cfgNode(get_node_id(), "loop", condition_node)
    if loop_block.get("type") == "compound_statement":
        loop_node = create_cfg(loop_block, func_var)
    else:
        loop_node = create_cfg(loop_block, func_var)
    cfg_node.variables = func_var
    cfg_node.trueNode = loop_node
    # next_node = cfg_node.trueNode
    next_node = loop_node
    while not (next_node.next is None):
        next_node = next_node.next
    if next_node.type == "loop":
        next_node.falseNode = cfg_node
    else:
        next_node.next = cfg_node
    cfg_node.isConditionNode = True

    # cfg_node.falseNode=
    return cfg_node


def create_cfg(data, func_var):
    node = None
    if data.get("type") == "declaration":
        node = declaration_node(data, func_var)
        # return node
    elif data.get("type") == "iteration_statement":
        node = iteration_statement_node(data, func_var)
        return node
    elif data.get("type") == "expression_statement" or data.get("type") == "postfix_expression":
        node = expression_statement_node(data, func_var)
        # print("node type is " + node.type + " node label is "+node.label)
        return node
    elif data.get("type") == "function_definition":
        node = function_node(data, func_var)

    elif data.get("type") == "jump_statement":
        node = jump_statement_node(data, func_var)
        return node
    elif data.get("type") == "selection_statement":
        node = selection_statement_node(data, func_var)
        return node

    children = data.get("children")
    # print(isinstance(children, list))
    next_node = None
    next_node_tmp1 = None
    if node is None:
        var_arr = func_var
    else:
        var_arr = node.variables
    if isinstance(children, list):
        for i, subtree in enumerate(children, 0):
            if type_check(subtree.get("type")):
                if not (next_node_tmp1 is None):
                    created_node = create_cfg(subtree, var_arr)
                    if created_node.prev is None:
                        next_node.next = created_node
                        # new_next_node = next_node.next
                        new_next_node = find_last_node(next_node)
                    else:
                        next_node.next = created_node.prev
                        # new_next_node = created_node.prev.next
                        new_next_node = find_last_node(next_node)
                    # next_node.next = create_cfg(subtree, var_arr)
                    var_arr = next_node.next.variables
                    next_node.next.prev = next_node
                    if next_node.isConditionNode:
                        next_node.fill_gaps(next_node.next)

                    # next_node = next_node.next
                    next_node = new_next_node
                else:
                    next_node = create_cfg(subtree, var_arr)
                    # print("next_node label is " + next_node.label)
                    var_arr = next_node.variables
                    next_node_tmp1 = next_node
    if node is None:
        node = next_node_tmp1

    else:
        node.next = next_node_tmp1
    return node


def find_paths(cfg, paths, path):
    if (cfg is None) or ((not (cfg is None)) and (cfg.loopAndPath is True)):
        paths.append(path)
        return

    if cfg.type == 'condition statement' or cfg.type == 'loop':
        if cfg.type == 'loop':
            cfg.loopAndPath = True
            false_path = []
            true_path = []
            true_path.append({"id": cfg.id, "type": cfg.type, "label": cfg.label, "node": cfg})
            false_path.append({"id": cfg.id, "type": cfg.type, "label": cfg.label, "node": cfg})
            paths.append(path)
        else:
            path.append({"id": cfg.id, "type": cfg.type, "label": cfg.label, "node": cfg})
            false_path = copy.deepcopy(path)
            true_path = path

        find_paths(cfg.trueNode, paths, true_path)
        find_paths(cfg.falseNode, paths, false_path)
    else:
        path.append({"id": cfg.id, "type": cfg.type, "label": cfg.label, "node": cfg})
        find_paths(cfg.next, paths, path)


def find_paths_helper(paths, path, node):
    path.append({"id": node.id, "type": node.type, "label": node.label, "node": node})
    if node.next is None or \
            (node.type == "loop" and len(path) > 1):
        return
    if node.type == "condition statement" or \
            node.type == "loop":
        paths.append(copy.deepcopy(path))
        false_path = copy.deepcopy(path)
        find_paths_helper(paths, path, node.trueNode)
        find_paths_helper(paths, false_path, node.falseNode)
    else:
        find_paths_helper(paths, path, node.next)


def find_paths_main(cfg, paths):
    for node in cfg:
        subnode = node
        while not (subnode is None):
            if subnode.type == "function_definition" or subnode.type == "loop":
                paths.append([])
                find_paths_helper(paths, paths[-1], subnode)
            subnode = subnode.next


# reading JSON from a File
with open("max3.c.ast.json") as json_file:
    data = json.load(json_file)

cfg = []  # array of cfgs
variables_arr = []  # array of variables of each function
paths = []
# for each child create a cfg

children = data.get("children")
i = 0
for child in children:
    func_cfg = create_cfg(child, variables_arr)
    func_cfg.remove_waste()
    if func_cfg.type == "declaration" and func_cfg.label.startswith("assert"):
        continue
    if (len(cfg) > 0) and (cfg[-1].type == "ensures") and (cfg[-1].next is None):
        cfg[-1].next = func_cfg
        func_cfg = cfg[-1]
    else:
        cfg.append(func_cfg)
    if not (func_cfg.type == "ensures" and func_cfg.next is None):
        func_paths = []
        find_paths(func_cfg, func_paths, [])
        paths.append(func_paths)
        FOL.fol(paths)

    variables_arr = []
    i = i + 1
# func_paths = []
# find_paths_main(cfg, func_paths)
# paths.append(func_paths)
# FOL.fol(paths)
# print(cfg[0].make_it_string())
verify.checkCorrectness(paths)
