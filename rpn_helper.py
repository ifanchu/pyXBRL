def calculate(tokens, decimal=-1):
    """ The idea is simple, just look through tokens, there are 2 different scenarios here
        1. if we see a number, just append it to stack
        2. if we see a string and that string is an operator, then we pop once from stack as second operand, pop once again from stack to be the first operand, calculate result and append it back to stack
        After looping through tokens, if the RPN expression is valid, there should only be a single number in stack, which is our result

        Args:
            tokens A tuple or list represents an RPN expression. For example,

                [['5', '1', '2', '+', '4', '*', '+', '3', '-'], 14],

            represents its infix notation 5 + ((1 + 2) * 4) - 3

            decimal how many digits of decimal point should result reserve

        Raises:
            ValueError if the RPN expression is invalid or the token in tokens is invalid
    """
    # because python has a difference evaluation for dividing negative numbers as shown in _div, we need to define them manually instead of using int.__add__ and etc.
    def _add(first_operand, second_operand):
        return first_operand + second_operand
    def _sub(first_operand, second_operand):
        return first_operand - second_operand
    def _mul(first_operand, second_operand):
        return first_operand * second_operand
    def _div(first_operand, second_operand):
        return float(first_operand) / second_operand

    if not isinstance(decimal, int) or decimal < -1:
        raise ValueError('Given decimal must be of type int and larger than or equal to -1')
    operators = {'+':_add, '-':_sub, '*':_mul, '/':_div}
    copy = tuple(tokens)    # make a immutable copy
    stack = []
    for index in xrange(len(tokens)):
        current = tokens[index]
        # validate each token
        try:
            current = abs(float(current))
        except ValueError:
            # current token is not a number
            if current not in operators:
                raise ValueError('{0} in tokens {1} invalid'.format(current, copy))
        except TypeError:
            raise TypeError('TypeError on: {0}'.format(current))
        if current not in operators:
            stack.append(current)
        else:
            # current is a operator
            # check whether there are at least 2 numbers in stack
            if len(stack) < 2:
                raise ValueError('Given tokens is not a valid RPN expression: {0}'.format(copy))
            second_operand = stack.pop()
            first_operand = stack.pop()
            operator = operators[current]
            try:
                result = operator(first_operand, second_operand)
            except ZeroDivisionError:
                result = 0
            stack.append(result)
    if len(stack) == 1:
        ret = stack.pop()
        return ret if decimal == -1 else int(ret * (10**decimal) + 0.5) / (10**decimal)
    else:
        raise ValueError('Given tokens in not a valid RPN expression: {0}'.format(copy))

if __name__ == '__main__':
    cases = [
        # [["10","6","9","3","+","-11","*","/","*","17","+","5","+"], 22],
        [['18'], 18],
        [['2', '1', '+', '3','*'], 9],
        [['4','13','5','/','+'], 4 + 13.0/5],
        [['1','12','3','/','+','1','3','*','-'], 2],
        [['5', '1', '2', '+', '4', '*', '+', '3', '-'], 14],
        [['5', '3', '/'], 5.0/3],
    ]
    for case in cases:
        result = calculate(case[0])
        if result == case[1]:
            print 'Passed'
        else:
            print 'Failed: Input = {0}, Output = {1}, Expected = {2}'.format(case[0], result, case[1])
