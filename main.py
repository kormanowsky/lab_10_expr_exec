"""
Лабораторная работа 10. Автор - Михаил Кормановский, ИУ7-11Б, МГТУ им. Баумана
"""


def is_number(string):
    """
    Является ли строка int или float?
    :param string: Строка, которую надо проверить
    :return: True/False, в зависимости от того, пройдена ли проверка
    """
    for sym in string:
        if not sym.isdigit() and sym != ".":
            return False
    return True


def exec_op(op_type, first_arg, second_arg=1):
    """
    Вычисление значения операции.
    :param op_type: Тип операции, строка как в исходном выражении.
    Поддерживаются: + - * ** % // / √
    :param first_arg: Первый аргумент
    :param second_arg: Второй аргумент (необязателен, например, в корне)
    :return: Вычисленное значение в виде int или float
    """
    if op_type == "√":
        return float(first_arg) ** 0.5
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


def exec_expr(expression):
    """
    Вычисление арифметического выражения
    :param expression: Выражение, значение которого требуется вычислить
    :return: Вычисленное значение в виде строки
    """

    # Этап 1. Удаляем пробелы, заменяем запятые на точки
    expression = expression.strip().replace(" ", "").replace(",", ".")

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
            return expression

        for b_expr in bracket_expr:
            expression = expression.replace("(" + b_expr + ")",
                                            exec_expr(b_expr))
        return expression if is_number(expression) else exec_expr(expression)

    # Этап 2.5. Некорректное выражение: открывающей нет, а закрывающая есть!
    elif expression.find(")") != -1:
        raise ValueError(expression)
    # Этап 3. "Расчленяем" выражение на слагаемые,
    # считаем их отдельно, затем складываем
    elif expression.find("+") != -1 or expression.find("-", 1) != -1:
        parts = []
        first_part_sym = 0
        last_sym = "+"
        for index in range(len(expression)):
            if expression[index] in ["+", "-"] and (
                    index == 0 or expression[index - 1] != "e"):
                parts.append([last_sym, expression[first_part_sym:index]])
                first_part_sym = index + 1
                last_sym = expression[index]
        parts.append([last_sym, expression[first_part_sym:]])
        result = "0"
        for part in parts:
            result = str(exec_op(part[0], result,
                                 part[1] if is_number(part[1])
                                 else exec_expr(part[1])
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
        for index in range(len(expression)):
            if expression[index] == "%":
                parts.append([last_sym, expression[first_part_sym:index]])
                first_part_sym = index + 1
                last_sym = expression[index]
            elif expression[index] == "*" and (
                    index == 0 or expression[index - 1] != "*" or index == len(
                expression) - 1 or expression[index + 1] != "*"):
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
                                     part[1])))
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
        return str(exec_op("√", exec_expr(expression[1:])))

    # Этап 7. Возвращаем ответ
    return expression


text = [
    line.strip() for line in """(1-2+3-e)Не Дун бегал от огня, в панике размахивая своими 
    когтищами, и раз за 
    разом натыкался ими на ближайшие здания.

Такой выбор мишеней не мог не радовать Мо Фаня и Чжао Мань Яня.

Пламя все еще не отступало, а Чжао Мань Янь уже закончил свою магию среднего 
уровня.

«Благословление света: Святая стена!»

Перед Чжао Мань Янем появилась огромная стена яркого света, которую он направил 
в сторону Не Дуна. Пламени было недостаточно для того, чтобы прожечь кожу 
вампира, но от удара этой стены света его тут же обожгло.

Чжао Мань Янь увидел, что выбранная магия оказалось настолько успешной, и начал 
снова формировать систему магии света. И второй удар нанес еще более серьезный 
ущерб по злому вампиру!

2 + 5 % (4 + 2 ** 0.5) - 1 // 3 + 20 // 10 + 4 ** (10 - 2)
""".split("\n") if len(line)]

longest_line_len = 0
for line in text:
    line_len = len(line)
    if longest_line_len < line_len:
        longest_line_len = line_len

print("Лабораторная работа 10. Автор - Михаил Кормановский, ИУ7-11Б")

command = None
while command != "E":

    if command is None:
        command = "M"

    if command == "1":
        for line in text:
            print(line.ljust(longest_line_len))
    elif command == "2":
        for line in text:
            print(line.rjust(longest_line_len))
    elif command == "3":
        for line in text:
            line_len = len(line)
            words = line.split()
            words_len = len(words)
            if words_len < 2:
                print(line)
            else:
                space_width = (longest_line_len - line_len + words_len) // (
                        words_len - 1)
                print(*words[:-1], sep=" " * space_width, end="")
                print(
                    words[-1].rjust(
                        longest_line_len - line_len +
                        len(words[-1]) + words_len - 1 -
                        space_width * (words_len - 2)
                    )
                )
    elif command == "4" or command == "5":

        word = input("Введите слово для {}:".format(
            "удаления" if command == "4" else "замены")
        )

        new_word = ""
        if command == "5":
            new_word = input("Введите слово, на которое заменить:")

        text = [line.replace(word, new_word) for line in text]

        for line in text:
            line_len = len(line)
            if longest_line_len < line_len:
                longest_line_len = line_len

        print(*text, sep="\n")

    elif command == "6":
        incorrect_expressions = []
        for line in text:
            expressions = []
            expr_started = False
            expr = ""
            prev_sym = None
            for sym in line:
                if sym.isdigit() or \
                        sym in ["*", "+", "-", "/", "(", "%", "√"] or \
                        expr_started and sym in [" ", ".", ")"] and \
                        prev_sym not in [" ", "."]:
                    if expr_started:
                        expr += sym
                    else:
                        expr = sym
                        expr_started = True
                elif expr_started:
                    expressions.append(expr.strip())
                    expr_started = False
                prev_sym = sym
            if expr_started:
                expressions.append(expr.strip())

            for expr in expressions:
                try:
                    line = line.replace(expr, exec_expr(expr))
                except (OverflowError, ZeroDivisionError, ValueError):
                    incorrect_expressions.append(expr)
            print(line)
        if incorrect_expressions:
            import sys

            print("\033[91mНайдены некорректные выражения:", *incorrect_expressions,
                  sep="\n", file=sys.stderr)
            print('\033[0m')

    elif command == "7":

        max_words_count = 0
        max_words_index = -1
        for index in range(len(text)):
            line = text[index]
            line_words_count = 0
            for word in line.split():
                word = word.strip()
                word_letters = {}
                for letter in word:
                    if letter in word_letters:
                        word_letters[letter] += 1
                    else:
                        word_letters[letter] = 1
                all_letters_twice = True
                for letter in word_letters:
                    if word_letters[letter] < 2:
                        all_letters_twice = False
                        break
                if all_letters_twice:
                    line_words_count += 1
            if line_words_count > max_words_count:
                max_words_count = line_words_count
                max_words_index = index
        if max_words_count == 0:
            print("Нет таких строк")
        else:
            print("Искомая строка:")
            print(text[max_words_index])

    elif command == "M":
        print("Доступные команды:")
        print("1 - Выравнивание по левому краю")
        print("2 - Выравнивание по правому краю")
        print("3 - Выравнивание по ширине")
        print("4 - Удаление заданного слова")
        print("5 - Замена заданного слова")
        print("6 - Вычисление арифметического выражения")
        print("7 - Найти предложение, в котором максимальное "
              "количество слов, в которых "
              "каждая буква входит не менее двух раз.")
        print("M - Вывод списка команд")
        print()
        print("E - Выход")
    else:
        print("Неизвестная команда!")

    command = input("Введите команду:").upper()

print("До свидания!")
