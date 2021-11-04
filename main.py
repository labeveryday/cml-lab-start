
#!/usr/bin/env python
import os
import contextlib
import io
from virl2_client import ClientLibrary
from dotenv import load_dotenv
from rich import print 

# This loads the .env file if it exists
load_dotenv()

# vars used for cml connection
# Enter the address or url of your cml server
IP = os.environ.get("IP")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

def connect(url: str=IP, username: str=USERNAME,
            password: str=PASSWORD) -> ClientLibrary:
    """
    
    """
    with contextlib.redirect_stderr(io.StringIO()):
        return ClientLibrary(url=url, username=username,
                             password=password, ssl_verify=False)

def get_lab_list(connect: ClientLibrary) -> list:
    return connect.all_labs()

def start_lab(connect: ClientLibrary, lab_id: str) -> None:
    print(f"Please wait.... Currently starting lab: {lab_id}")
    lab = connect.get_local_lab(lab_id)
    lab.start()

def stop_lab(connect: ClientLibrary, lab_id: str) -> None:
    lab = connect.get_local_lab(lab_id)
    lab.stop()

def print_lab_list(lab_list: list, print_lab: bool=False) -> dict:
    i = 0
    labs = {}     
    for lab in lab_list:
        labs[i] = lab.id
        if print_lab:
            print(f"\t[italic blue]{i}.[italic blue] {lab.title}")
        i += 1
    return labs


if __name__ == "__main__":
    print("\nWELCOME TO THE CML [italic green]START[italic green]",
                    "/", "[italic red]STOP[italic red]", "SCRIPT")
    connect = connect()
    lab_list = get_lab_list(connect)
    print("\nHere are a list of CML Labs:")
    labs = print_lab_list(lab_list, print_lab=True)
    user_lab = int(input("\nEnter lab to start: ").strip())
    start_lab(connect, labs[user_lab])
    print(f"\n*** Currently starting LAB: {lab_list[user_lab].title} ***\n")
    print(f"{lab_list[user_lab].title} has started successfully.\n")
    print(lab_list[user_lab].statistics)
