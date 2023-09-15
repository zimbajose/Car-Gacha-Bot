# Car-gacha bot
A fun little car gacha bot to satisfy your car lust

## Dependencies
This bot requires the following libraries:

- Discord py
- Mysql connector

Installation commands with pip:
#####
    pip install discord.py
    pip install mysql-connector-python


## Gacha commands
This bot has a car gacha function, in which you can roll for random cars.

### Gacha command
    $car gacha
Rolls for a random car

## Car viewing commands

### Garage command
    $car garage
Shows all the cars that the user has obtained

### Search command
    $car search <car name>
Searches and displays a car. It will show a prompt with up to 5 cars with similar names, the user may use the reactions to awnser which car is to be displayed.


## Car trading commands

### Sell command
    $car sell <car name>
It will search among the user's cars for cars of similar names, similar to the search command it will then send a prompt, that the user will use reactions to select one of the cars, after that it will send a confirmation prompt, if the user reacts with the checkbox the car will be removed from the user's possessions and money will be added to him.

## Other commands

### Balance command
    #car balance
This command will send the user's amount of gacha money that he has on chat.

## Other links

### The datasets i used for gathering the cars
https://www.kaggle.com/datasets/prasertk/gran-turismo-6-carsd