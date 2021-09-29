class cfgNode:
    def __init__(self, node_id, node_type, node_label):
        self.id = node_id
        self.type = node_type
        self.label = node_label
        if node_type == 'condition statement':
            self.isConditionNode = True
        else:
            self.isConditionNode = False
        self.next = None
        self.loopAndPath = False
        self.trueNode = None
        self.falseNode = None
        self.prev = None
        self.variables = []
        self.vars = []
        self.assign_decl = False

    def update_next(self, node_next):
        self.next = node_next

    def update_cond_next(self, next_true, next_false):
        self.trueNode = next_true
        self.falseNode = next_false

    def print_ids(self):
        cfg_str = " %s" % self.id
        return cfg_str

    def make_it_string(self):
        cfg_str = "{\n   id := %s" % self.id + "\n   label := " + self.label + " \n"
        cfg_str = cfg_str + " variables: "
        for var in self.variables:
            cfg_str = cfg_str + "{ type: %s" % var["type"] + " id: %s" % var["id"] + " }\n"
        if self.prev is None:
            cfg_str = cfg_str + "   prev := None" + "\n"
        else:
            cfg_str = cfg_str + "   prev node id := %s" % self.prev.id + "\n"
        if self.isConditionNode:
            if not (self.trueNode is None):
                # cfg_str = cfg_str + "   true Node :=  " + self.trueNode.make_it_string()
                cfg_str = cfg_str + "   true Node :=  " + self.trueNode.print_ids()
            else:
                cfg_str = cfg_str + "   true Node := None \n"
            if not (self.falseNode is None):
                # cfg_str = cfg_str + "\n   false node :=  " + self.falseNode.make_it_string() + "\n}\n"
                cfg_str = cfg_str + "\n   false node :=  " + self.falseNode.print_ids() + "\n"
            else:
                cfg_str = cfg_str + "   false Node := None \n"
        if self.next is None:
            cfg_str = cfg_str + "   next := None" + "\n}\n"

        else:
            cfg_str = cfg_str + "   next node id := %s" % self.next.id + "\n}\n"
            cfg_str += self.next.make_it_string()

        if not (self.trueNode is None):
            cfg_str += self.trueNode.make_it_string()
        if not (self.falseNode is None):
            cfg_str += self.falseNode.make_it_string()

        return cfg_str

    def fill_gaps(self, node):
        if self.type == "loop":
            self.falseNode = node
            return
        if node is None:
            return
        if node.id == self.id:
            return
        if self.isConditionNode:
            if not (self.falseNode is None):
                self.falseNode.fill_gaps(node)
                if node.isConditionNode:
                    self.trueNode.fill_gaps(node)
                else:
                    self.trueNode.fill_gaps(node)
            else:
                self.falseNode = node
                if node.isConditionNode:
                    self.trueNode.fill_gaps(node)
                else:
                    self.trueNode.fill_gaps(node)
            if not (self.trueNode is None):
                self.trueNode.fill_gaps(node)
            else:
                self.trueNode = node
        if self.next is None:
            if node.isConditionNode:
                if not(self.label.startswith("return")):
                    self.next = node

            else:
                if not(self.label.startswith("return")):
                    self.next = node
            return
        else:

            if node.isConditionNode:
                self.next.fill_gaps(node)
            else:
                self.next.fill_gaps(node)
        # self.next.fill_gaps(node.next)

    def fill_gaps2(self, node):

        if self.falseNode is None:
            self.falseNode = node
        else:
            self.falseNode.next = node
        if node is None:
            return
        if self.trueNode is None:
            return
        self.trueNode.next = node.get_last_node()

    def remove_waste(self):
        if self.type == "loop":
            self.next = None
            return
        elif self.isConditionNode:
            self.next = None
            self.trueNode.remove_waste()
            self.falseNode.remove_waste()
        elif not (self.next is None):
            self.next.remove_waste()

    def get_last_node(self):
        if self.next is None:
            return self
        else:
            return self.next.get_last_node()
