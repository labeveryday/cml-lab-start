
#!/usr/bin/env python
"""This module interacts with the CML API"""
import os
import contextlib
import io
from virl2_client import ClientLibrary
from virl2_client.models.lab import Lab
from rich import print


class Cml:
    """Class for interacting with CML API"""
    def __init__(self, ip: str, username: str, password: str) -> ClientLibrary:
        """
        args:
            ip (str): ip or url of the cml
            username (str): user login username
            password (str): user login password
        retruns: ClientLibrary
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.connect = self._connect()
    
    def __repr__(self):
        """String representation of an Cml object"""
        return f"Cml({self.ip}, {self.username}, {self.password})"

    def _connect(self) -> ClientLibrary:
        """GET the cml client connection"""
        with contextlib.redirect_stderr(io.StringIO()):
            return ClientLibrary(url=self.ip, username=self.username,
                                     password=self.password, ssl_verify=False)

    def get_lab_list(self) -> Lab:
        """GET the list of labs ids"""
        return self.connect.all_labs()

    def start_lab(self, lab_id: str) -> None:
        """Start a lab
        args:
            lab_id (str): id of cml lab
        returns: None"""
        lab = self.connect.get_local_lab(lab_id)
        lab.start()

    def stop_lab(self, lab_id: str) -> None:
        """Stop a lab"""
        lab = self.connect.get_local_lab(lab_id)
        lab.stop()

    def stop_all_labs(self, labs: list) -> str:
        """Stop all labs
        args:
            lab_id (str): id of cml lab
        returns: None"""
        for lab in labs:
            self.stop_lab(lab.id)
        return "All labs stop successfully"

    @staticmethod
    def print_lab_list(lab_list: list, print_lab: bool=False) -> dict:
        """Static method that prints the list of labs
        args:
            lab_list (list): list of lab instances
            print_lab (bool): print lab info
        returns: dict"""
        i = 0
        labs = {}
        for lab in lab_list:
            labs[i] = lab.id
            if print_lab:
                if lab.state() == "STARTED":
                    print(f"\t[italic blue]{i}.[italic blue] " \
                          f"{lab.title:^25s} | [green]{lab.state()}[green]")
                else:
                    print(f"\t[italic blue]{i}.[italic blue] " \
                          f"{lab.title:^25s} | [red]{lab.state()}[red]")
            i += 1
        return labs


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    IP = os.getenv("CML_IP")
    USERNAME = os.getenv("CML_USERNAME")
    PASSWORD = os.getenv("CML_PASSWORD")
    print("\nWELCOME TO THE CML [italic green]START[italic green]",
                    "/", "[italic red]STOP[italic red]", "SCRIPT")
    connect = Cml(IP, USERNAME, PASSWORD)
    _lab_list = connect.get_lab_list()
    print("\nHere are a list of CML Labs:")
    _labs = connect.print_lab_list(_lab_list, print_lab=True)
    user_lab = int(input("\nEnter lab to start: ").strip())
    print(f"\n****** Currently starting LAB: {_lab_list[user_lab].title} ******\n")
    connect.start_lab(_labs[user_lab])
    print(f"- {_lab_list[user_lab].title} has started successfully.")
    print(f"- {_lab_list[user_lab].title} stats: {_lab_list[user_lab].statistics}\n")
