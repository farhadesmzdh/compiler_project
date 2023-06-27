import sys

from anytree import Node, RenderTree

import json


class Parser:
    all_tokens, terminals, non_terminals, stack, all_nodes, tokens_copy, first, follow = [], [], [], [], [], [], [], []
    grammar, parse_table = None, None
    shift_token = []
    keywords = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return", "endif"]
    symbols = [";", ":", "[", "]", "(", ")", "{", "}", "+", "-", "*", "=", "<", "==", ',']
    error = False

    def __init__(self):
        self.get_all_tokens()
        self.tokens_copy = self.all_tokens.copy()
        for i in range(len(self.tokens_copy)):
            self.tokens_copy[i] = self.tokens_copy[i].split("?")
        self.read_json_table()
        self.parse_tree()
        self.print_tree(self.all_nodes[-1])

    def get_all_tokens(self):
        f = open("tokens.txt", "r")
        for x in f:
            self.all_tokens.extend(x.split(' '))
        for i in self.all_tokens:
            if i == '\n':
                self.all_tokens.remove(i)

        with open(r"input.txt", 'r') as fp:
            for count, line in enumerate(fp):
                pass
        q = count + 2
        r = f'SYMBOL?$?{str(q)}'
        self.all_tokens.append(r)
        f.close()

    def read_json_table(self):
        f = open('table.json')
        data = json.load(f)

        self.grammar = data['grammar']
        self.parse_table = data['parse_table']
        self.follow = data['follow']

        for i in data['terminals']:
            self.terminals.append(i)

        for i in data['non_terminals']:
            self.non_terminals.append(i)

        f.close()

    def print_tree(self, x):
        path = 'parse_tree.txt'
        with open(path, 'w', encoding='utf-8') as f:
            i = 0
            for pre, fill, node in RenderTree(x):
                if i != 0:
                    f.write('\n')
                if node.name in self.keywords:
                    node.name = f'(KEYWORD, {node.name})'
                elif node.name in self.symbols or node.name == '/':
                    node.name = f'(SYMBOL, {node.name})'
                f.write("%s%s" % (pre, node.name))
                i += 1
            f.close()
        self.write_syntax_error(-1, 5, 'a')

    def parse_tree(self):
        self.stack.append('0')
        current_state = '0'
        red = 0
        f = 0
        while self.all_tokens and f < 7000:
            f += 1
            current_token = self.all_tokens[0].split('?')
            current_state = self.stack[-1]
            if f > 6998:
                print('fail')
            row_table_current_state = self.parse_table[current_state]
            if len(current_token) < 2:
                del self.all_tokens[0]
                continue
            if current_token[0] == 'ID' or current_token[0] == 'NUM':
                current_token[0], current_token[1] = current_token[1], current_token[0]
            if current_token[1] in row_table_current_state.keys():
                action = row_table_current_state[current_token[1]].split('_')
                if action[0] == 'shift':
                    current_state = action[1]
                    self.stack.append(current_token)
                    self.stack.append(current_state)
                    del self.all_tokens[0]
                elif action[0] == 'reduce':
                    red = action
                    grammar_rule = self.grammar[action[1]]
                    parent = Node(grammar_rule[0], children=None, parent=None)
                    temp_stack = self.stack[len(self.stack) - ((len(grammar_rule) - 2) * 2):]
                    temp_stack.reverse()
                    for rule in grammar_rule[2:]:
                        c, d = 0, 0
                        if rule != 'epsilon':
                            c = self.stack.pop()
                            d = self.stack.pop()
                            h = temp_stack.pop()
                            i = temp_stack.pop()
                        is_exist_node = False
                        for k in range(len(self.all_nodes) - 1, -1, -1):
                            n = self.all_nodes[k]
                            if n.name == rule:
                                parent_all_node = []
                                for child in parent.children:
                                    parent_all_node.append(child)
                                parent_all_node.append(n)
                                for p in range(len(parent_all_node)):
                                    u = len(parent_all_node) - 1
                                    if parent_all_node[p].name == parent_all_node[u].name:
                                        parent_all_node[p], parent_all_node[u] = parent_all_node[u], parent_all_node[p]
                                parent.children = parent_all_node
                                self.all_nodes.remove(n)
                                is_exist_node = True
                                break
                        if not is_exist_node:
                            parent_all_node = []
                            for child in parent.children:
                                parent_all_node.append(child)
                            if rule == 'ID':
                                rule = f'(ID, {h[0]})'
                                h[0], h[1] = h[1], h[0]
                                self.tokens_copy.remove(h)
                            elif rule == 'NUM':
                                rule = f'(NUM, {h[0]})'
                                h[0], h[1] = h[1], h[0]
                                self.tokens_copy.remove(h)
                            parent_all_node.append(Node(rule))
                            parent.children = parent_all_node
                    self.all_nodes.append(parent)
                    current_state = self.stack[-1]
                    self.stack.append(grammar_rule[0])
                    row_table_current_state = self.parse_table[current_state]
                    action = row_table_current_state[grammar_rule[0]].split('_')
                    current_state = action[1]
                    self.stack.append(current_state)
            else:
                if current_token[1] == 'ID' or current_token[1] == 'NUM':
                    current_token[0], current_token[1] = current_token[1], current_token[0]
                self.error = True
                del self.all_tokens[0]
                line_number = current_token[-1]
                self.write_syntax_error(line_number, 0, current_token[1])
                missed_token = ''
                current_token = self.all_tokens[0].split('?')
                if current_token[0] == 'ID' or current_token[0] == 'NUM':
                    current_token[0], current_token[1] = current_token[1], current_token[0]
                while True:
                    contain_goto = False
                    row_table_current_state = self.parse_table[current_state]
                    for key, value in row_table_current_state.items():
                        if value.startswith("goto"):
                            contain_goto = True
                            break
                    if contain_goto:
                        break
                    else:  #####################################################3
                        self.stack.pop()
                        w = self.stack[-1]
                        if type(w) == list:
                            if w[1] == '$':
                                self.write_syntax_error(w[-1], 4, 5)
                            if w[1] == 'ID' or w[1] == 'NUM':
                                w[0], w[1] = w[1], w[0]
                            w = f'({w[0]}, {w[1]})'
                        self.write_syntax_error(current_token[-1], 1, w)
                        self.stack.pop()
                        current_state = self.stack[-1]
                row_table_current_state = self.parse_table[current_state].copy()
                my_keys = list(row_table_current_state.keys())
                my_keys.sort()
                sorted_dict = {i: row_table_current_state[i] for i in my_keys}
                for key, value in sorted_dict.items():
                    if not value.startswith("goto"):
                        my_keys.remove(key)
                my_keys.sort()
                while True:
                    select = False
                    non_terminal = my_keys.copy()
                    for k in non_terminal:
                        if current_token[1] in self.follow[k]:
                            select = True
                            goto = row_table_current_state[k]
                            action = goto.split('_')
                            self.write_syntax_error(current_token[-1], 3, k)
                            # self.illegal.append(current_token)
                            self.stack.append(k)
                            self.stack.append(action[-1])
                            break
                    if select:
                        break
                    else:
                        w = current_token.copy()
                        if w[1] == '$':
                            self.write_syntax_error(w[-1], 4, 5)
                        if w[1] == 'ID' or w[1] == 'NUM':
                            w[0], w[1] = w[1], w[0]
                        self.write_syntax_error(current_token[-1], 2, w[1])
                        del self.all_tokens[0]
                        current_token = self.all_tokens[0].split('?')
                        if current_token[0] == 'ID' or current_token[0] == 'NUM':
                            current_token[0], current_token[1] = current_token[1], current_token[0]

        parent = self.all_nodes[-1]
        parent_all_node = []
        for child in parent.children:
            parent_all_node.append(child)
        parent_all_node.append(Node('$'))
        parent.children = parent_all_node

    def write_syntax_error(self, line_number, step, terminal):
        path = 'syntax_errors.txt'
        if not self.error:
            with open(path, 'a', encoding='utf-8') as f:
                f.write('There is no syntax error.')
        elif line_number != -1:
            if step == 0:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(f'#{line_number} : syntax error , illegal {terminal}\n')
            elif step == 1:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(f'syntax error , discarded {terminal} from stack\n')
            elif step == 2:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(f'#{line_number} : syntax error , discarded {terminal} from input\n')
            elif step == 3:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(f'#{line_number} : syntax error , missing {terminal}\n')
            elif step == 4:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(f'#{line_number} : syntax error , Unexpected EOF\n')
                path = 'parse_tree.txt'
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('')
                sys.exit(0)
