symbol_dict = {"+": "Add", "-": "Sub", "*": "Mul", "/": "Div", "**": "Pow"}


class Symbol:
    """
    Parent class of all valid symbols
    """

    precedence = -1
    right_parens = False

    def __add__(self, after):
        return Add(self, after)

    def __sub__(self, after):
        return Sub(self, after)

    def __mul__(self, after):
        return Mul(self, after)

    def __truediv__(self, after):
        return Div(self, after)

    def __pow__(self, after):
        return Pow(self, after)

    def __radd__(self, prev):
        return Add(prev, self)

    def __rsub__(self, prev):
        return Sub(prev, self)

    def __rmul__(self, prev):
        return Mul(prev, self)

    def __rtruediv__(self, prev):
        return Div(prev, self)

    def __rpow__(self, prev):
        return Pow(prev, self)

    def simplify(self):
        return self

    left_parens = False


class Var(Symbol):
    """
    Class representing variable symbols
    """

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, assigments):
        return assigments.get(self.name, None)

    def __eq__(self, other):
        if isinstance(other, Var):
            return self.name == other.name
        return False

    def deriv(self, wrt):
        if self.name == wrt:
            return Num(1)
        else:
            return Num(0)

    precedence = 100


class Num(Symbol):
    """
    Class representing numerical values as symbols
    """

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, assigments):
        return float(self.n)

    def __eq__(self, other):
        if isinstance(other, Num):
            return float(self.n) == float(other.n)
        return False

    def deriv(self, wrt):
        return Num(0)

    precedence = 100


class BinOp(Symbol):
    """
    Parent class of all binary operations
    """

    def __init__(self, left, right):
        if isinstance(left, (int, float)):
            self.left = Num(left)
        elif isinstance(left, str):
            self.left = Var(left)
        else:
            self.left = left

        if isinstance(right, (int, float)):
            self.right = Num(right)
        elif isinstance(right, str):
            self.right = Var(right)
        else:
            self.right = right

    def __str__(self):
        ret_str_l = f"{self.left}"
        ret_str_m = f" {self.opp} "
        ret_str_r = f"{self.right}"

        if self.left.precedence < self.precedence or (
            self.left.precedence <= self.precedence and self.left_parens
        ):  
            ret_str_l = "(" + ret_str_l + ")"

        if self.right.precedence < self.precedence:
            ret_str_r = "(" + ret_str_r + ")"

        elif self.right_parens and self.right.precedence == self.precedence:  
            ret_str_r = "(" + ret_str_r + ")"

  
        return ret_str_l + ret_str_m + ret_str_r

    def __repr__(self):
        name = symbol_dict[self.opp]

        return f"{name}({repr(self.left)}, {repr(self.right)})"

    def eval(self, assignments):  

        l_eval = self.left.eval(assignments)
        r_eval = self.right.eval(assignments)

    

        if None in (l_eval, r_eval):
            raise NameError

        return self.operate(l_eval, r_eval)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return (
            (self.left == other.left)
            and (self.right == other.right)
            and (self.opp == other.opp)
        )


class Add(BinOp):
    opp = "+"
    precedence = 5
    right_parens = False

    def operate(self, l_eval, r_eval):
        return l_eval + r_eval

    def deriv(self, wrt):
        return self.left.deriv(wrt) + self.right.deriv(wrt)

    def simplify(self):
        l_simpl = self.left.simplify()
        r_simpl = self.right.simplify()

        if l_simpl == Num(0) and r_simpl == Num(0):
            return Num(0)
        elif l_simpl == Num(0):
            return r_simpl
        elif r_simpl == Num(0):
            return l_simpl

        if isinstance(l_simpl, Num) and isinstance(r_simpl, Num):
            return Num(l_simpl.n + r_simpl.n)

        return l_simpl + r_simpl


class Sub(BinOp):
    opp = "-"
    precedence = 5
    right_parens = True

    def operate(self, l_eval, r_eval):
        return l_eval - r_eval

    def deriv(self, wrt):
        return self.left.deriv(wrt) - self.right.deriv(wrt)

    def simplify(self):
        l_simpl = self.left.simplify()
        r_simpl = self.right.simplify()

        if l_simpl == Num(0) and r_simpl == Num(0):
            return Num(0)

        elif r_simpl == Num(0):
            return self.left.simplify()


        if isinstance(l_simpl, Num) and isinstance(r_simpl, Num):
            return Num(l_simpl.n - r_simpl.n)

        return l_simpl - r_simpl


class Mul(BinOp):
    opp = "*"
    precedence = 10
    right_parens = False

    def operate(self, l_eval, r_eval):
        return l_eval * r_eval

    def deriv(self, wrt):
        return Add(
            Mul(self.left, self.right.deriv(wrt)), Mul(self.right, self.left.deriv(wrt))
        )

    def simplify(self):
        l_simpl = self.left.simplify()
        r_simpl = self.right.simplify()

        if l_simpl == Num(0) or r_simpl == Num(0):
            return Num(0)
        elif l_simpl == Num(1):
            return self.right.simplify()
        elif r_simpl == Num(1):
            return self.left.simplify()

        if isinstance(l_simpl, Num) and isinstance(r_simpl, Num):
            return Num(l_simpl.n * r_simpl.n)
        return l_simpl * r_simpl


class Div(BinOp):
    opp = "/"
    precedence = 10
    right_parens = True

    def operate(self, l_eval, r_eval):
        return l_eval / r_eval

    def deriv(self, wrt):
        return Div(
            Sub(
                Mul(self.right, self.left.deriv(wrt)),
                Mul(self.left, self.right.deriv(wrt)),
            ),
            Mul(self.right, self.right),
        )

    def simplify(self):
        l_simpl = self.left.simplify()
        r_simpl = self.right.simplify()

        if l_simpl == Num(0):  # or r_simpl == Num(0):
            return Num(0)
       
        elif r_simpl == Num(1):
            return self.left.simplify()

        
        if isinstance(l_simpl, Num) and isinstance(r_simpl, Num):
            return Num(l_simpl.n / r_simpl.n)

        return l_simpl / r_simpl


class Pow(BinOp):
    opp = "**"
    precedence = 10
    right_parens = False
    left_parens = True

    def operate(self, l_eval, r_eval):
        return l_eval**r_eval

    def deriv(self, wrt):
        return Mul(
            Mul(self.right, Pow(self.left, self.right - 1)), self.left.deriv(wrt)
        )

    def simplify(self):
        l_simpl = self.left.simplify()
        r_simpl = self.right.simplify()

        if r_simpl == Num(0):
            return Num(1)
        elif r_simpl == Num(1):
            return l_simpl
        elif l_simpl == Num(0) and (
            isinstance(r_simpl, Var) or (isinstance(r_simpl, Num) and r_simpl.n > 0)
        ):
            return Num(0)


        if isinstance(l_simpl, Num) and isinstance(r_simpl, Num):
            return Num(l_simpl.n**r_simpl.n)

        return l_simpl**r_simpl


def case(tokenized):
    tokenized.pop()
    if tokenized[0] == "":
        tokenized.pop(0)

    return tokenized

def tokenize(inp_str):
    """
    Given an input string, outputs a list of parentheses, variable names, numbers, or operands. 
    """
    tokenized = []
    num_add = ""

    for i, char in enumerate(inp_str + "|"):   
        if char == " " or char == ")":
            pass

        elif (char.isdigit() or char == "." or (char == "-" and (inp_str[i + 1].isdigit() or inp_str[i + 1] == "."))):
            num_add += char

        else:
            if num_add != "":
                tokenized.append(num_add)

            tokenized.append(char)
            num_add = ""

    tokenized = case(tokenized)

    return tokenized


def parse(tokens):
    """
    Given a list of valid tokens, converts the list to an expression of establishes symbols and operations. 
    """
    symbol_dict_class = {"+": Add, "-": Sub, "*": Mul, "/": Div, "**": Pow}

    def parse_expression(index):
        token = tokens[index]

        if token[0] == "-" or token[0].isdigit() or token[0] == ".":
            return (Num(float(token)), index + 1)

        elif token.isalpha():
            return (Var(token), index + 1)

        elif token == "(":
            left_exp, opp_ind = parse_expression(index + 1)
            operator = tokens[opp_ind]
            right_exp, right_paren = parse_expression(opp_ind + 1)

            cur_exp = symbol_dict_class[operator](left_exp, right_exp)

            return cur_exp, right_paren  

    parsed_expression, next_index = parse_expression(0)
    print(parsed_expression)
    return parsed_expression


def expression(expression_str):
    """
    Handles the interface between tokenize and parse. Cleans up the Pow and Mul edge case. 
    Returns a 
    """
    tokenized_lst = tokenize(expression_str)
    new_tok_list = []
    for i, token in enumerate(tokenized_lst):
        if token == "*" and tokenized_lst[i + 1] == "*":
            continue
        elif token == "*" and tokenized_lst[i - 1] == "*":
            new_tok_list.append("**")
        else:
            new_tok_list.append(token)

    tokenized_lst = new_tok_list
    parsed = parse(tokenized_lst)

    return parsed


if __name__ == "__main__":
    exp = expression("2 * (5 + 3) **1")
    print(exp)
    pass
