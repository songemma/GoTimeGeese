import bluetooth_utils

# Initialize the bluetooth_utils module.
num_players = int(input("Number of Players: "))
bluetooth_utils.init(num_players)

print("Here we go.")
currently_displayed = ""
while True:
    num_connected = bluetooth_utils.number_of_devices()
    to_display = f"Connected: {num_connected}/{num_players}   Input: "
    for player in range(num_players):
        to_display += f"({player + 1}, {bluetooth_utils.get_direction(player)}) "
    if currently_displayed != to_display:
        currently_displayed = to_display
        print('\r', to_display, (' ' * 10), end='')

# At the moment, the program never reaches this line since the only way to get it
# to terminate is to force-close it. However, I still included it for demonstration
# purposes.
bluetooth_utils.stop()
