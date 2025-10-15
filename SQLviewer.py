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

        def _parse(element: str, index_pos: int) -> tuple[dict[str, dict[str, dict | str] | str], int]:
            """
            Only god knows how this thing work, ask him if you have
            questions. \n
            -- Kyle, 14/10/25 at 23:50
            """

            el_dict: dict[str, dict[str, dict | str] | str] = {"element": ""}

            index_pos += 1
            is_word: bool = False

            while index_pos < len(element):

                e = element[index_pos]

                if e in ["\n", "\t", ";"]: # remove tabs and newlines.
                    el_dict["element"] += " "
                    index_pos += 1
                    continue

                if e == " ": # remove excess spaces.
                    if element[index_pos+1] == " ":
                        index_pos += 1
                        continue

                if e == "(": 
                    # how is this working
                    last_word = el_dict["element"].upper()

                    for func in SQL_FUNCTIONS: # is a func ?
                        if last_word[-len(func):] == func:
                            el_dict["element"] += "("
                            is_word = True
                            index_pos += 1
                            break
                    
                    if is_word == True: # it's a func.
                        continue

                    el_dict["parse"], index_pos = _parse(element, 
                                                         index_pos)
                    continue

                if e == ")":
                    if not is_word: # not func
                        return el_dict, index_pos+1
                    is_word = False # func

                if e == "-": # comment
                    if element[index_pos+1] == "-":
                        return el_dict, index_pos+1

                el_dict["element"] += e
                index_pos += 1

            return el_dict, index_pos
        
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
        commands = self.__getCommands(parsed_dict, False)

        return commands

if __name__ == "__main__":

    dt0 = time()

    inter = Interpreter()

    dt1 = time()

    result = inter.interpret(
"""
SELECT ENNEMIS.Nom, HEROS.Nom FROM ENNEMIS INNER JOIN HEROS
ON ENNEMIS.Ville LIKE "%City%" and HEROS.Ville LIKE "%City%"
and ENNEMIS.Age > HEROS.Age and ENNEMIS.Age < (
	SELECT SUM(HEROS.Age)/count(HEROS.Titre) FROM HEROS
    WHERE HEROS.Age > (SELECT AVG(HEROS.Age) FROM HEROS)
); -- pas sur
"""
                            )
    

    dt2 = time()

    pprint(result, width=200)
    print(f"Done in {(dt2 - dt0)* 1000} ms, initiated in {(dt1 - dt0) * 1000} ms.")
