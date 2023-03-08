# Welcome to TOKDOC

This protocol was designed and implemented in a server-client application by Owethu Novuka, Tiyani Mhlarhi, and Maesela Sekoele.

This was our first attempt ever at socket programming in python and in protocol design and we have since learned through the creation of this project.

# Running the project

A Linux machine (or WSL2) is highly recommended to run the server.

You are required to have [Python version 3.9](https://www.python.org/downloads/) installed and [pipenv](https://pypi.org/project/pipenv/) (which allows for the creation of Python virtual environments).

An installation guide for pipenv can be found [here](https://pypi.org/project/pipenv/#installation). 

Once those two requirements have been met:

1. cd into the src directory of the server
    
    ```
    $ cd path/to/src
    ```
    
2. Enter the virtual environment (this could take a couple minute the first time you run it)
    
    ```
    $ pipenv shell
    ```
    
3. Install the dependencies
    
    ```
    $ pipenv install
    ```
    
4. Run the server
    
    ```
    $ python server.py
    ```
    

Given that there are no errors in running the server you should see output showing the server’s name, IP address, and port which can be used to by client to connect to the server