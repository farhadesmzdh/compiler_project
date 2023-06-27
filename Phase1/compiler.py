class Compiler:
    def __init__(self):
        self.keywords = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return", "endif"]
        self.symbol_table = self.keywords.copy()
        self.whitespaces = [32, 10, 13, 9, 11, 12]  # 32 -> blank, 10 -> \n, 13 -> \r, 9 -> \t, 11 -> \v, 12 -> \f
        self.token_types = ["NUM", "ID", "KEYWORD", "SYMBOL", "COMMENT", "WHITESPACE"]
        self.symbols = [";", ":", "[", "]", "(", ")", "{", "}", "+", "-", "*", "=", "<", "==", ',']  # remove /
        self.string_token = ''
        self.next_line = False
        self.comment = False
        self.first = True
        self.line_number = 0
        self.error = False
        self.comment_line = 0
        self.comment_string = '/*'
        self.last_error_number = 0
        self.comment_count = 0

    def create_file(self):
        with open('tokens.txt', 'a', encoding="utf-8") as f:
            pass

    def start(self, file):
        self.create_file()
        text = open(file, "r")
        line = text.readline()
        while line:
            self.line_number += 1
            token_type = 'UNKNOWN'
            if self.comment:
                token_type = 'COMMENT'
            self.first = True
            for c in line:
                if not self.comment:
                    if token_type == 'UNKNOWN':
                        token_type = self.get_token_type(c)
                    if token_type == 'UNKNOWN':
                        continue
                token_type = self.get_next_token(c, token_type)
                if self.next_line:
                    self.next_line = False
                    self.string_token = ''
                    break
            line = text.readline()
            self.first = True
        self.write_symbol_table(list(set(self.symbol_table)))
        if self.comment:
            self.line_number = self.comment_line
            self.write_lexical_errors('Unclosed comment', self.comment_string + '...')
        if not self.error:
            self.write_no_error()

    def get_token_type(self, character):
        if character.isalpha():
            return 'ID'
        elif character.isdigit():
            return 'NUM'
        elif character in self.symbols:
            return 'SYMBOL'
        elif character == '/':
            return 'COMMENT'
        elif character == '\n' or character == ' ' or character == '\v' or character == '\r' or character == '\f' or character == '\t':
            return 'WHITESPACE'
        else:
            if not self.comment:
                self.write_lexical_errors('Invalid input', self.string_token + character)
                self.string_token = ''
        return 'UNKNOWN'

    def get_next_token(self, character, token_type):
        if self.comment:
            if self.comment_count < 5:
                self.comment_string += character
                self.comment_count += 1
            if self.string_token == '':
                if character == '*':
                    self.string_token += character
            elif self.string_token == '*':
                if character == '/':
                    self.comment = False
                    self.comment_count = 0
                    self.comment_string = '/*'
                    self.string_token = ''
                    return 'UNKNOWN'
                self.string_token = ''
                return 'UNKNOWN'
            return 'COMMENT'

        if self.string_token == '*':
            if character == '/':
                self.string_token += character
                self.write_lexical_errors('Unmatched comment', self.string_token)
                self.string_token = ''
                return 'UNKNOWN'
            else:
                self.write_token('SYMBOL', '*')
                self.string_token = ''
                token_type = 'UNKNOWN'

        if self.string_token == '=':
            if character == '=':
                self.string_token += character
                self.write_token('SYMBOL', self.string_token)
                self.string_token = ''
                return 'UNKNOWN'
            else:
                self.write_token('SYMBOL', '=')
                self.string_token = ''
                token_type = 'UNKNOWN'

        if token_type == 'UNKNOWN':
            token_type = self.get_token_type(character)

        if token_type == 'ID' or token_type == 'KEYWORD':
            if character.isalpha() or character.isdigit():
                self.string_token += character
            else:
                token_type = self.get_token_type(character)
                if token_type != 'UNKNOWN':
                    self.return_token('ID')
                    self.get_next_token(character, token_type)
                    return 'UNKNOWN'

        elif token_type == 'NUM':
            if character.isdigit():
                self.string_token += character

            else:
                token_type = self.get_token_type(character)
                if token_type == 'ID' or token_type == 'UNKNOWN':
                    self.write_lexical_errors('Invalid number', self.string_token + character)
                    self.string_token = ''
                    return 'UNKNOWN'
                if token_type != 'UNKNOWN':
                    self.return_token('NUM')
                    self.get_next_token(character, token_type)
                    return 'UNKNOWN'


        elif token_type == 'SYMBOL':
            if character == ';':
                self.write_token('SYMBOL', ';')
            elif character == ':':
                self.write_token('SYMBOL', ':')
            elif character == ',':
                self.write_token('SYMBOL', ',')
            elif character == '[':
                self.write_token('SYMBOL', '[')
            elif character == ']':
                self.write_token('SYMBOL', ']')
            elif character == '(':
                self.write_token('SYMBOL', '(')
            elif character == ')':
                self.write_token('SYMBOL', ')')
            elif character == '{':
                self.write_token('SYMBOL', '{')
            elif character == '}':
                self.write_token('SYMBOL', '}')
            elif character == '+':
                self.write_token('SYMBOL', '+')
            elif character == '-':
                self.write_token('SYMBOL', '-')
            elif character == '*':
                self.string_token += character
            elif character == '=':
                self.string_token += character
            elif character == '<':
                self.write_token('SYMBOL', '<')
            token_type = 'UNKNOWN'

        elif token_type == 'COMMENT':
            if self.string_token == '/':
                if character == '/':
                    self.next_line = True
                    self.new_line()
                    return 'UNKNOWN'
                elif character == '*':
                    self.string_token = ''
                    self.comment = True
                    self.comment_line = self.line_number
                    return 'COMMENT'
                else:
                    self.write_token('SYMBOL', '/')
                    token_type = 'UNKNOWN'
                    self.string_token = ''
                    self.get_next_token(character, token_type)
            else:
                self.string_token += character


        elif token_type == 'WHITESPACE':
            # if character == ' ':
            #   pass
            # self.write_token(token_type, ' ')
            if character == '\n':
                if not self.first:
                    self.new_line()
            # elif character == '\v':
            #   self.write_token(token_type, '\v')
            # elif character == '\r':
            #    self.write_token(token_type, '\r')
            # elif character == '\t':
            #   self.write_token(token_type, '\t')
            # elif character == '\f':
            #   self.write_token(token_type, '\f')
            token_type = 'UNKNOWN'

        return token_type

    def return_token(self, token_type):

        if token_type == 'ID':
            if self.string_token in self.keywords:
                self.write_token('KEYWORD', self.string_token)
            else:
                self.write_token('ID', self.string_token)

        elif token_type == 'NUM':
            self.write_token('NUM', self.string_token)

    def write_token(self, token_type, token_string):
        with open('tokens.txt', 'a', encoding="utf-8") as file:
            if token_type == 'ID':
                self.symbol_table.append(token_string)
            if self.first:
                if token_string != '\n':
                    file.write(f'{self.line_number}.\t({token_type}, {token_string}) ')
            else:
                file.write(f'({token_type}, {token_string}) ')
            file.close()
        self.string_token = ''
        self.first = False

    @staticmethod
    def write_no_error():
        with open('lexical_errors.txt', 'a', encoding="utf-8") as file:
            file.write('There is no lexical error.')
            file.close()

    def write_lexical_errors(self, error_type, token_string):
        with open('lexical_errors.txt', 'a', encoding="utf-8") as file:
            if not self.error:
                file.write(f'{self.line_number}.\t({token_string}, {error_type}) ')
            else:
                if self.last_error_number == self.line_number:
                    file.write(f'({token_string}, {error_type}) ')
                else:
                    file.write('\n')
                    file.write(f'{self.line_number}.\t({token_string}, {error_type}) ')
            file.close()
            self.last_error_number = self.line_number
        self.error = True

    @staticmethod
    def write_symbol_table(symbol_table):
        with open('symbol_table.txt', 'a', encoding="utf-8") as file:
            for symbol in range(len(symbol_table)):
                file.write(f'{symbol + 1}.\t{symbol_table[symbol]}\n')
            file.close()

    def new_line(self):
        if self.first:
            return
        with open('tokens.txt', 'a', encoding="utf-8") as file:
            file.write('\n')
            file.close()


def scan():
    file = 'input.txt'
    compiler = Compiler()
    compiler.start(file)


scan()
