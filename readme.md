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

## Auctions
Periodically this bot will send auction messages, where users can bid for a random car, this auctions do do not have weights for car rarities, so getting a rare car in a auction is much more likely.
There are a few steps for having auctions active in your server, you must first use the $car auction set command to choose a channel to host auctions, and then use the $car auction activate for your server to start receiving auctions.
Once a auction occurs a user may use the arrow reaction to bid 20% on the current value of the car, or the double arrow to bid 40% on the current value of the car.

### Set command
    $car auction set
This command will set the current channel as host for auctions, if auctions are activated the bot will periodically send auction prompts to the set channel.

### Activate command
    $car auction activate
This command will activate car auctions in the server, this command can only be used if there is a valid host channel, setted using the set command.

### Deactivate command
    #car auction deactivate
this command will deactivate car auctions in the server, this command can only be used if there is a valid host channel, setted using the set command.

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