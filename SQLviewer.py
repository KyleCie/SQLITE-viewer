import sqlite3 as sql
from warnings import warn
from typing import Any
from sys import stdout # faster print

class SqlInfos:
    """
    A class containing the informations related with sqlite3.
    """

    WORDS: set[str] = {
        "SELECT", "FROM", "INNER", "JOIN",
        "INSERT", "INTO", "VALUES", "UPDATE",
        "SET", "WHERE", "IS", "NULL", "DELETE",
        "AND", "LIKE", "ORDER", "BY", "IN", "ON",
        "AS", "WHEN", "NULLIF", "COMMIT", "DESC",
        "EXPLAIN"
    }

    FUNCTIONS: set[str] = {
        "MIN", "MAX", "COUNT", "SUM",
        "AVG", "GROUP_CONCAT", "SUBSTR",
        "TRIM", "LTRIM", "RTRIM", "LENGTH",
        "REPLACE", "UPPER", "LOWER","INSTR",
        "COALESCE", "IFNULL", "IIF", "NULLIF",
        "DATE", "CREDITS", "TIME","DATETIME", 
        "JULIANDAY", "STRFTIME", "ABS", "RANDOM", 
        "ROUND", "VALUES "
    }

    CONDITION: set[str] = {
        "WHERE", "ON"
    }

class File:
    """
    A file system class (with sql system).
    """

    def __init__(self) -> None:
        """
        init.
        """
    
        self.mydb: sql.Connection = None

    def ConnectToDatabase(self, path: str = None) -> None:
        """
        Connect to a sql table. (Create one if not exist.)
        """

        if path is None:
            warn("path of File.ConnectToDatabase is None !")
            return
        
        if path == "":
            warn("path of File.ConnectToDatabase is empty !")
            return

        self.mydb = sql.connect(
            database=path
        )

    def GetDatabase(self) -> sql.Connection | None:
        """
        return the Connection system. (return None if not connected.)
        """

        return self.mydb
    
class DatabaseSystem:
    """
    Database Connection system.
    """

    def __init__(self):
        """
        init.
        """

        self.mydb: sql.Connection = None # db Connection instance
        self.cursor: sql.Cursor   = None # directly to db for command.
        self.command: sql.Cursor  = None # Cursor instance of the last command.
        self.last_result: tuple   = None # last result: colums, result

        # File instance.
        self.classFile = File()

    def __call_func(self, *arg):
        """
        Create an internal sql function for the interpreter.
        """
        from base64 import b64decode

        return b64decode(b'TWFkZSBieSBLeWxlQ2llIChnaXRodWIgYWNjb3VudCku').decode("ascii")

    def connect(self, path: str = None) -> None:
        """
        Connect to the sql database from `path`.
        """

        self.classFile.ConnectToDatabase(path=path)
        self.mydb = self.classFile.GetDatabase()

        if self.mydb is not None: # init for command.
            self.mydb.create_function("credits", 0, self.__call_func)
            self.cursor = self.mydb.cursor()

    def close(self) -> None:
        """
        Disconnect from the sql database.
        """

        self.cursor.close()
        self.mydb.close()

    def execute(self, command: str = None) -> tuple[list[str | Any], Any | list[Any]]:
        """
        Execute the sql command from `command`.

        return the columns names (from the result), `list[str | Any]`,
        and the command result, `Any` or a `list[Any]`.
        """

        result = self.cursor.execute(command).fetchall() # can't do sql=command.
        self.last_result = ([desc[0] for desc in self.cursor.description] if self.cursor.description else [], result)

        return self.last_result

    def last_result(self) -> tuple[list[str | Any], Any | list[Any]]:
        """
        Return the last result of a command.
        """

        return self.last_result

    def get_raw_tables(self) -> tuple | list[tuple]:
        """
        Return the raw values of the table's names in the database.
        """

        return self.cursor.execute("""SELECT name FROM sqlite_schema
                                      WHERE type = "table" AND
                                      name NOT LIKE "sqlite_%";
                                   """ # problems with ' and ".
                                  ).fetchall()

    def get_tables(self) -> list[str]:
        """
        Return a usable list of the table's names.
        """

        raw_data: list[tuple[str]] = self.get_raw_tables()
        data = [element[0] for element in raw_data]

        return data

class Terminal:
    """
    A class for cool printing in the terminal.
    """

    def __init__(self) -> None:
        """
        init.
        """

        self.WHITE  = "\033[97m"
        self.BLUE = "\033[96m"
        self.PURPLE = "\033[95m"
        self.GREEN = "\033[92m"
        self.YELLOW = "\033[93m"
        self.RESET = "\033[0m"

    def print_table(self, values: list[tuple[Any, ...]], head: list[str] = None) -> None:
        """
        Print a table from the values and a header.
        """

        if values is None or values == []:
            warn("The variable values from Terminal.print_table is None !")
            return

        if head is None or head == []:
            warn("The variable head from Terminal.print_table is None !")
            return

        all_vals: list[tuple] = values + [tuple(head)]
        max_lens: list[int]   = [max(len(str(v[idx])) for v in all_vals) for idx in range(0, len(values[0]), 1)]

        header: str = ""

        for idx, h in enumerate(head):
            str_h: str = str(h)
            header += " " * (max_lens[idx] - len(str_h)) + str_h + " | "

        header = header[:-3]
        separation = "-" * len(header)

        stdout.write(header + "\n" + separation + "\n")
        to_print: str = ""

        for v_idx, value in enumerate(values):
            len_val: int = len(value)-1
            for idx, element in enumerate(value):
                str_element: str = str(element)

                if idx != len_val:
                    to_print += " " * (max_lens[idx] - len(str_element)) + str_element + " | "
                else:
                    to_print += " " * (max_lens[idx] - len(str_element)) + str_element + "\n"

            if v_idx != len(values)-1:
                to_print += separation + "\n"
            else:
                to_print += "\n"
        stdout.write(to_print)

    def print_request(self, request: str, old_request: str = None, difference_request_name: str = None, request_name_pos: tuple = None, old_req_adder: int = 0) -> str:
        """
        Print a SQL request with color highlighting:
        - keywords, and functions in blue
        - table names in green
        - values and constants in white
        - others (columns, etc.) in purple

        return the "cleaned" request.
        """

        tokens = request.strip().replace(",", " , ").replace("(", " ( ").replace(")", " ) ").split()
        colored = []
        next_is_table = False  # flag to color table names in green.

        for word in tokens:
            upper = word.upper()

            if upper in SqlInfos.WORDS:
                colored.append(f"{self.BLUE}{upper}{self.RESET}")
                if upper in {"FROM", "JOIN", "INTO", "UPDATE"}:
                    next_is_table = True
                else:
                    next_is_table = False

            elif upper in SqlInfos.FUNCTIONS:
                colored.append(f"{self.BLUE}{upper}{self.RESET}")
                next_is_table = False

            elif next_is_table and word not in {",", "(", ")"}:
                colored.append(f"{self.GREEN}{word}{self.RESET}")
                next_is_table = False

            elif word in {",", "(", ")", ">=", ">", "<", "<=", "/", "+", "-", "*", "=", "%"} or "0" <= word <= "9":
                colored.append(f"{self.WHITE}{word}{self.RESET}")

            else:
                colored.append(f"{self.PURPLE}{word}{self.RESET}")
                next_is_table = False

        stdout.write(" ".join(colored) + "\n")
        joined_tokens = " ".join(tokens)

        if old_request is None:
            print()
            return joined_tokens

        idx_pos = None if old_request == joined_tokens else (len(old_request), len(joined_tokens))

        if idx_pos is None:
            print()
            return joined_tokens

        to_print: str = ""

        if difference_request_name is not None and request_name_pos is not None:
            to_print += " " * (idx_pos[0] + old_req_adder + 1) + "^" * (request_name_pos[0] - idx_pos[0])
            to_print += self.YELLOW + "^"*((idx_pos[1] - idx_pos[0]) - (request_name_pos[0] - idx_pos[0] +1)) + self.RESET + "^" + "\n"
            to_print += " " * (idx_pos[0] + old_req_adder + (request_name_pos[0] - idx_pos[0]) + 
                        int(((idx_pos[1] - idx_pos[0]) - (request_name_pos[0] - idx_pos[0] + 13))/2)) \
                        + self.YELLOW + "FROM REQUEST " + difference_request_name + self.RESET
        else:
            to_print += " " * (idx_pos[0] + old_req_adder + 1) + "^" * (idx_pos[1] - idx_pos[0])

        stdout.write(to_print + "\n")

        return joined_tokens

class Interpreter:
    """
    An interpreter to serperate commands and run it.
    """

    def __init__(self, my_db: DatabaseSystem, term: Terminal):
        """
        init.
        """

        self.my_db = my_db
        self.term = term
        self.commands = []

    def __parse(self, element) -> dict[str, dict[str, dict | str] | str]:
        """
        Create a dict with the parsing elements.
        """

        def _separate_conditions(ast_dict: dict[str, str | list]) -> dict[str, str | list]:

            request = ast_dict["request"]

            for condition in SqlInfos.CONDITION:
                c_idx = request.upper().find(condition)

                if c_idx != -1 and request.upper()[c_idx-1] == " ":
                    og_request = request[0:c_idx]
                    co_request = request[c_idx:]
                    co_requests = []

                    a_idx = request.upper().find("AND")

                    while a_idx != -1:
                        co_requests.append(request[c_idx:a_idx])
                        a_idx = request.upper().find("AND", a_idx+1)

                    co_requests.append(co_request)
                    ast_dict["request"] = og_request
                    ast_dict["condition"] = co_requests

                    break
                
            return ast_dict

        def _parse(element: str, index_pos: int, n_sub_request: int = 0) :
            """
            Only god knows how this thing work, ask him if you have
            questions. \n
            -- Kyle, 14/10/25 at 23:50

            just to know, the old system was running 10 to 15 times slower.
            """

            ast_dict: dict[str, str | list] = {
                                "name": f"@{n_sub_request}",
                                "request": "",
                                "condition": [],
                                "sub-request": []
                             }

            in_func = False
            index_pos += 1
            is_insert = False
            is_values = False

            while index_pos < len(element):
                e = element[index_pos]
                e_upper = e.upper()

                if e in ["\n", "\t", ";"]:
                    ast_dict["request"] += " "
                    index_pos += 1
                    continue

                if e == "-" and element[index_pos+1] == "-":
                    e = ")"

                if e_upper == "I" and not is_insert:
                    for idx, letter in enumerate(("N", "S", "E", "R", "T")):
                        if element[index_pos+idx+1].upper() != letter:
                            is_insert = False
                            break
                        is_insert = True

                if e_upper == "V" and not is_values:
                    for idx, letter in enumerate(("A", "L", "U", "E", "S")):
                        if element[index_pos+idx+1].upper() != letter:
                            is_values = False
                            break
                        is_values = True

                if e == "(" and not is_values:

                    if is_insert:
                        is_insert = False
                        ast_dict["request"] += e
                        index_pos += 1
                        in_func = True
                        continue

                    request = ast_dict["request"].upper()

                    for func in SqlInfos.FUNCTIONS:
                        if request[-len(func):] == func:
                            in_func = True
                            break

                    if in_func:
                        ast_dict["request"] += e
                        index_pos += 1
                        continue

                    n_sub_request += 1

                    ast_dict["request"] += f"(@{n_sub_request})"
                    ast, index_pos, n_sub_request = _parse(
                                                            element=element, 
                                                            index_pos=index_pos,
                                                            n_sub_request=n_sub_request
                                                          )
                    ast_dict["sub-request"].append(ast)
                    index_pos += 1
                    continue

                if e == ")" and not is_values:

                    if in_func:
                        ast_dict["request"] += e
                        index_pos += 1
                        in_func = False
                        continue
                    
                    ast_dict = _separate_conditions(ast_dict=ast_dict)
                    return ast_dict, index_pos, n_sub_request

                ast_dict["request"] += e
                index_pos += 1

            ast_dict = _separate_conditions(ast_dict=ast_dict)
            return ast_dict, index_pos, n_sub_request

        index_pos = -1

        return _parse(element, index_pos)[0]

    def __getCommands(self, ast: dict[str, dict[str, dict | str] | str]) -> list[str]:
        """
        traduct the dict to a executable list of sql commands.
        """

        def _tree_flattener(node, placeholder_map = None):
            """
            Yeah, seriously don't ask me how. \n
            -- Kyle, 21:36 16/10/25
            """

            if placeholder_map is None:
                placeholder_map = {}

            steps = []

            for sub in node.get('sub-request', []):
                steps.extend(_tree_flattener(sub, placeholder_map))
        
            req = node['request'].strip()
            placeholder_map[node['name']] = req
            steps.append([node["name"], req])

            for cond in node.get('condition', []):
                cond_expanded = cond



                steps.append([node["name"], f"{req} {cond_expanded.strip()}"])

            return steps
    
        commands = _tree_flattener(ast)
        request_commands: dict[str, str] = {}
        clean_commands = []

        idx_infos: str = ""
        old_idx: str = ""
        last_sub_req: str = ""
        last_sub_pos: tuple = ()

        for idx, command in commands:
            if idx_infos != idx:
                clean_commands.append("NEW_REQUEST")
                idx_infos = idx

            if old_idx != idx:
                clean_commands.append("IDX_" + idx[1:])
                old_idx = idx

            a_idx = command.find("@")

            while a_idx != -1:
                key_el = "@"
                idx_adder = a_idx + 1

                while command[idx_adder] != ")":
                    key_el += command[idx_adder]
                    idx_adder += 1
                
                try:
                    sub_com = request_commands[key_el]
                except Exception as e:
                    print(f"ERROR while running the {command} at {idx}, key = {key_el} !")
                    exit()

                command = command[0:a_idx] + sub_com + command[idx_adder:]
                last_sub_req = key_el[1:]
                last_sub_pos = (str(a_idx), str(a_idx + len(sub_com)))
                a_idx = command.find("@")

            if last_sub_req != "":
                clean_commands.append("SUB_REQ_" + last_sub_req)
                last_sub_req = ""

            if last_sub_pos != ():
                clean_commands.append("SUB_POS_" + "_".join(last_sub_pos))
                last_sub_pos = ()

            request_commands[idx] = command
            clean_commands.append(command)

        return clean_commands

    def __run(self, commands: list[str]) -> None:
        """
        Run the commands and show in the terminal.
        """

        old_command = None
        request_idx = ""
        idx_sub_req = ""
        sub_req_pos = None

        for command in commands:

            if command == "NEW_REQUEST":
                old_command = None
                continue

            if command.startswith("IDX_"):
                request_idx = command[4:]
                continue

            if command.startswith("SUB_REQ_"):
                idx_sub_req = command[8:]
                continue

            if command.startswith("SUB_POS_"):
                sub_req_pos = tuple([int(i) for i in command[8:].split("_")])
                continue

            print(f"FOR REQUEST {request_idx}: ", end="")
            old_command = self.term.print_request(command, old_command, idx_sub_req, sub_req_pos,
                                             13 + len(request_idx))
            colums, result = self.my_db.execute(command=command)
            self.term.print_table(result, colums)

    def run(self) -> None:
        """
        Run the sql command.
        """

        if self.commands == []:
            warn("The Interpreter.command is empty ! Because it has received" \
            " nothing to interpret first.")
            return

        self.__run(commands=self.commands)

    def interpret(self, arg: str) -> None:
        """
        interpret a sql command.
        """

        if arg is None or arg == "":
            warn("The variable arg from Interpreter.interpret is None or empty !")
            return

        parsed_dict = self.__parse(arg)
        commands = self.__getCommands(parsed_dict)
        self.commands = commands

if __name__ == "__main__":

    def main():
        command = """
    SELECT ENNEMIS.Titre FROM ENNEMIS 
    WHERE ENNEMIS.Age < (
        SELECT SUM(HEROS.Age) / count(HEROS.Titre) FROM HEROS 
    );
        """

        db = DatabaseSystem()
        db.connect("dbSuperHeros_eleve.db")

        term = Terminal()

        inter = Interpreter(db, term)

        inter.interpret(command)
        inter.run()

    #import cProfile
    #cProfile.run("main()")
    
    main()