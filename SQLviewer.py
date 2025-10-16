import sqlite3 as sql
from warnings import warn
from typing import Any
from pprint import pprint
from time import time

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

        # File instance.
        self.classFile = File()

    def connect(self, path: str = None) -> None:
        """
        Connect to the sql database from `path`.
        """

        self.classFile.ConnectToDatabase(path=path)
        self.mydb = self.classFile.GetDatabase()

        if self.mydb is not None: # init for command.
            self.cursor = self.mydb.cursor()

    def close(self) -> None:
        """
        Disconnect from the sql database.
        """

        self.cursor.close()
        self.mydb.close()

    def execute(self, command: str = None) -> Any | list[Any]:
        """
        Execute the sql command from `command`.
        return the command result, `Any` or a `list[Any]`.
        """

        self.command = self.cursor.execute(command) # can't do sql=command.
        return self.command.fetchall()

    def last_result(self) -> Any | list[Any]:
        """
        Return the last result of a command.
        """

        return self.command.fetchall()

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

class Interpreter:
    """
    An interpreter to serperate commands and run it.
    """

    def __init__(self, my_db: DatabaseSystem):
        """
        init.
        """

        self.my_db = my_db
        self.commands = []

    def __parse(self, element) -> dict[str, dict[str, dict | str] | str]:
        """
        Create a dict with the parsing elements.
        """

        SQL_FUNCTIONS: set[str] = {
            "MIN", "MAX", "COUNT", "SUM",
            "AVG", "GROUP_CONCAT", "SUBSTR",
            "TRIM", "LTRIM", "RTRIM", "LENGTH",
            "REPLACE", "UPPER", "LOWER","INSTR",
            "COALESCE", "IFNULL", "IIF", "NULLIF",
            "DATE", "TIME","DATETIME", "JULIANDAY",
            "STRFTIME", "ABS", "RANDOM", "ROUND"
        }

        SQL_CONDITION: set[str] = {
            "WHERE", "ON"
        }

        def _separate_conditions(ast_dict: dict[str, str | list]) -> dict[str, str | list]:

            request = ast_dict["request"]

            for condition in SQL_CONDITION:
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
            """

            ast_dict: dict[str, str | list] = {
                                "name": f"@{n_sub_request}",
                                "request": "",
                                "condition": [],
                                "sub-request": []
                             }

            in_func = False
            index_pos += 1

            while index_pos < len(element):
                e = element[index_pos]

                if e in ["\n", "\t", ";"]:
                    ast_dict["request"] += " "
                    index_pos += 1
                    continue

                if e == "-" and element[index_pos+1] == "-":
                    e = ")"

                if e == " " and element[index_pos+1] == " ":
                    index_pos += 1
                    continue

                if e == "(":

                    request = ast_dict["request"].upper()

                    for func in SQL_FUNCTIONS:
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

                if e == ")":

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
            Yeah, seriously don't ask me. \n
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

                for ph, ph_req in placeholder_map.items():
                    if ph in cond_expanded:
                        cond_expanded = cond_expanded.replace(ph, f"({ph_req})")

                steps.append([node["name"], f"{req} {cond_expanded.strip()}"])

            return steps
    
        commands = _tree_flattener(ast)

        request_commands: dict[str, str] = {}
        clean_commands = []

        for idx, command in commands:
            
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

                a_idx = command.find("@" \
                "")

            request_commands[idx] = command
            clean_commands.append(command)

        return clean_commands

    def __run(self, commands: list[str]) -> None:
        """
        Run the commands and show in the terminal.
        """

        for command in commands:
            print(f"FOR: {command}:")
            result = self.my_db.execute(command=command)
            print(result, "\n")

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

        parsed_dict = self.__parse(arg)
        commands = self.__getCommands(parsed_dict)
        self.commands = commands

if __name__ == "__main__":

    dt0 = time()

    db = DatabaseSystem()
    db.connect("dbSuperHeros_eleve.db")

    inter = Interpreter(db)

    dt1 = time()

    parsed = inter.interpret(
"""
SELECT ENNEMIS.Titre FROM ENNEMIS 
WHERE ENNEMIS.Age < (
	SELECT SUM(HEROS.Age)/count(HEROS.Titre) FROM HEROS 
	WHERE HEROS.Ville = "Alberta"
	) 
AND ENNEMIS.id_SE IN (
	SELECT HEROS.Id FROM HEROS 
	WHERE HEROS.Titre = "Wolverine"
);
"""
                            )
    

    dt2 = time()

    inter.run()

    dt3 = time()

    print(f"Done in {(dt2 - dt0)* 1000} ms, initiated in {(dt1 - dt0) * 1000} ms, and runned in {(dt3 - dt2) * 1000} ms.")
    print(f"TOTAL: {(dt3 - dt0) * 1000} ms.")

    inter.my_db.close() # close the database.