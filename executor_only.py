"""
Только вычислитель выражений.
"""

from math import sqrt
from sys import stderr

def is_number(string):
    """
    Является ли строка int или float?
    :param string: Строка, которую надо проверить
    :return: True/False, в зависимости от того, пройдена ли проверка
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def exec_op(op_type, first_arg, second_arg=""):
    """
    Вычисление значения операции.
    :param op_type: Тип операции, строка как в исходном выражении.
    Поддерживаются: + - * ** % // / √
    :param first_arg: Первый аргумент
    :param second_arg: Второй аргумент (необязателен, например, в корне)
    :return: Вычисленное значение в виде int или float
    """
    if op_type == "√":
        return sqrt(float(first_arg))
    if op_type == "/":
        return float(first_arg) / float(second_arg)
    use_float = False
    if "." in first_arg or "." in second_arg:
        use_float = True
    if op_type == "+":
        if use_float:
            return float(first_arg) + float(second_arg)
        return int(first_arg) + int(second_arg)
    if op_type == "-":
        if use_float:
            return float(first_arg) - float(second_arg)
        return int(first_arg) - int(second_arg)
    if op_type == "//":
        if use_float:
            return float(first_arg) // float(second_arg)
        return int(first_arg) // int(second_arg)
    if op_type == "%":
        if use_float:
            return float(first_arg) % float(second_arg)
        return int(first_arg) % int(second_arg)
    if op_type == "**":
        if use_float:
            return float(first_arg) ** float(second_arg)
        return int(first_arg) ** int(second_arg)
    if use_float:
        return float(first_arg) * float(second_arg)
    return int(first_arg) * int(second_arg)


def exec_expr(expression, stage=0):
    """
    Вычисление арифметического выражения
    :param expression: Выражение, значение которого требуется вычислить
    :param stage: Этап вычислений
    :return: Вычисленное значение в виде строки
    """

    if not expression:
        raise ValueError(expression)

    # Этап 1. Удаляем пробелы
    expression = expression.strip().replace(" ", "").replace("--", "+")

    # Этап 2. Если есть выражения в скобках, считаем их
    if expression.find("(") != -1:
        bracket_expr = []
        level = 0
        left_round_bracket = -1
        right_round_bracket = -1
        expr_len = len(expression)
        for index in range(expr_len):
            sym = expression[index]
            if sym == "(":
                level += 1
                if level == 1:
                    left_round_bracket = index
            elif sym == ")":
                if level == 1:
                    right_round_bracket = index
                if -1 < left_round_bracket < right_round_bracket < expr_len:
                    bracket_expr.append(
                        expression[left_round_bracket + 1:right_round_bracket])
                level -= 1

        if level != 0:
            raise ValueError(expression)

        for b_expr in bracket_expr:
            expression = expression.replace("(" + b_expr + ")",
                                            exec_expr(b_expr))
        return expression if is_number(expression) else exec_expr(expression)

    # Этап 2.5. Некорректное выражение: открывающей нет, а закрывающая есть!
    elif expression.find(")") != -1:
        raise ValueError(expression)
    # Этап 3. "Расчленяем" выражение на слагаемые,
    # считаем их отдельно, затем складываем
    elif stage == 0 and (
            expression.find("+") != -1 or expression.find("-", 1) != -1):
        parts = []
        first_part_sym = 0
        last_sym = "+"
        for index in range(len(expression)):
            if expression[index] in ["+", "-"] and (
                    index == 0 or expression[index - 1].isdigit()):
                if expression[first_part_sym:index]:
                    parts.append([last_sym, expression[first_part_sym:index]])
                    first_part_sym = index + 1
                    last_sym = expression[index]
        parts.append([last_sym, expression[first_part_sym:]])
        result = "0"
        for part in parts:
            result = str(exec_op(part[0], result,
                                 part[1] if is_number(part[1])
                                 else exec_expr(part[1], stage=1)
                                 )
                         )
        return result

    # Этап 4. "Расчленяем" слагаемые на множители,
    # считаем их отдельно, затем умножаем
    elif expression.count("*") % 2 or expression.find(
            "/") != -1 or expression.find("%") != -1:
        parts = []
        first_part_sym = 0
        last_sym = "*"
        expression = expression.replace("**", "POW")
        for index in range(len(expression)):
            if expression[index] == "%":
                parts.append([last_sym, expression[first_part_sym:index]])
                first_part_sym = index + 1
                last_sym = expression[index]
            elif expression[index] == "*":
                if expression[first_part_sym:index]:
                    parts.append([last_sym, expression[first_part_sym:index]])
                    first_part_sym = index + 1
                    last_sym = expression[index]
            elif expression[index] == "/":
                if expression[index - 1] != expression[index] and \
                        expression[index + 1] != expression[index]:
                    parts.append([last_sym, expression[first_part_sym:index]])
                    first_part_sym = index + 1
                    last_sym = expression[index]
                else:
                    if expression[index - 1] == expression[index]:
                        parts.append(
                            [last_sym, expression[first_part_sym:index - 1]])
                        first_part_sym = index + 1
                        last_sym = "//"
        parts.append([last_sym, expression[first_part_sym:]])
        result = "1"
        for part in parts:
            result = str(exec_op(part[0], result,
                                 part[1] if is_number(
                                     part[1]) else exec_expr(
                                     part[1].replace("POW", "**"))))
        return result

    # Этап 5. Считаем степени. Поведение как в Python, 2 ** 5 ** 3 = 2 ** 125
    elif expression.find("**") != -1:
        parts = expression.split("**")[::-1]
        result = parts[0]
        for i in range(1, len(parts)):
            result = str(
                exec_op("**", parts[i] if is_number(parts[i]) else exec_expr(
                    parts[i]),
                        result if is_number(result) else exec_expr(result)))
        return result

    # Этап 6. Считаем корни
    elif not is_number(expression):
        expression = expression.replace("+", "")
        if not is_number(expression):
            return str(exec_op("√", exec_expr(expression[1:])))

    # Этап 7. Возвращаем ответ
    return expression


try:
    inp = input("Введите выражение: ")
    res1 = exec_expr(inp)
    res2 = eval(inp)
    print("Результат exec_expr:", res1)
    print("Результат      eval:", res2)
    try:
        print("Разница:", abs(float(res1) - res2))
        print("Значения ", "не " if abs(float(res1) - res2) > 1e-6 else "",
              "равны", sep="")
    except OverflowError:
        print("Разница:", abs(int(res1) - res2))
        print("Значения ", "не " if abs(int(res1) - res2) else "", "равны",
              sep="")
except (ValueError, SyntaxError):
    print("\033[91mНекорректное выражение", file=stderr)
    exit(1)
