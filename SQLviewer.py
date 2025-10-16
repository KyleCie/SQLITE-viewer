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
    
    def __getCommands(self, parsed_commands: dict[str, dict[str, dict | str] | str], difficult: bool) -> list[list[str]]:
        """
        Create a list of usable sql command from the parsed commands.
        """

        raw_commands: list[str] = [parsed_commands["element"]]
        commands: list[str] = []
        el_dict: dict[str, dict | str] = parsed_commands["parse"]

        while "parse" in el_dict.keys():
            raw_commands.append(el_dict["element"])
            el_dict = el_dict["parse"]

        raw_commands.append(el_dict["element"])
        raw_commands.reverse()

        for com in raw_commands:

            u_com = com.upper()

            where = u_com.find("WHERE")
            on = u_com.find("ON")

            if where != -1:
                if difficult:
                    l_c = [com[0:where]]
                    i_and = u_com.find("AND")

                    while i_and != -1:
                        l_c.append(com[0:i_and])
                        i_and = u_com.find("AND", i_and+1)
                    
                    l_c.append(com)
                    commands.append(l_c)
                else:
                    commands.append([com[0:where], com])

            elif on != -1:

                if difficult:
                    l_c = [com[0:on]]
                    i_and = u_com.find("AND")

                    while i_and != -1:
                        l_c.append(com[0:i_and])
                        i_and = u_com.find("AND", i_and+1)

                    l_c.append(com)
                    commands.append(l_c)
                else:
                    commands.append([com[0:on], com])

            else:
                commands.append([com])
        return commands

    def __run(self, commands: list[list[str]]) -> None:
        """
        Run the commands and show in the terminal.
        """

    def interpret(self, arg: str) -> list:
        """
        interpret a sql command.
        """

        parsed_dict = self.__parse(arg)
        #commands = self.__getCommands(parsed_dict, False)

        return parsed_dict

if __name__ == "__main__":

    dt0 = time()

    inter = Interpreter()

    dt1 = time()

    result = inter.interpret(
"""
SELECT HEROS.Titre,
(
    SELECT COUNT(*)
    FROM (
        SELECT DISTINCT ENNEMIS.Ville
        FROM ENNEMIS
        WHERE ENNEMIS.Age > (
            SELECT AVG(E2.Age)
            FROM ENNEMIS AS E2
            WHERE E2.Rang IN (
                SELECT R.Nom
                FROM Rangs AS R
                WHERE R.Niveau > (
                    SELECT MIN(R2.Niveau)
                    FROM Rangs AS R2
                    WHERE R2.Niveau IS NOT NULL
                )
            )
        )
    ) AS villes_distinctes
) AS nb_villes,
(
    SELECT SUM(ARMES.Puissance)
    FROM ARMES
    WHERE ARMES.Id_Heros = HEROS.Id
    AND ARMES.Type IN (
        SELECT T.Type
        FROM TYPES AS T
        WHERE T.Rarete = (
            SELECT MAX(TR.Rarete)
            FROM TYPES AS TR
            WHERE TR.Categorie = "légendaire"
        )
    )
) AS puissance_totale
FROM HEROS
WHERE HEROS.Id IN (
    SELECT Id
    FROM (
        SELECT HEROS.Id
        FROM HEROS
        WHERE HEROS.Force > (
            SELECT AVG(H2.Force)
            FROM HEROS AS H2
        )
    )
)
ORDER BY puissance_totale DESC;
"""
                            )
    

    dt2 = time()

    pprint(result, width=200)
    print(f"Done in {(dt2 - dt0)* 1000} ms, initiated in {(dt1 - dt0) * 1000} ms.")
