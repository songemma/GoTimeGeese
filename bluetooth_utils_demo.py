import bluetooth_utils


def get_player_dir(p):
    d = bluetooth_utils.get_direction(p)
    if d == bluetooth_utils.DIR_UP:
        return "Up"
    elif d == bluetooth_utils.DIR_DOWN:
        return "Down"
    elif d == bluetooth_utils.DIR_LEFT:
        return "Left"
    elif d == bluetooth_utils.DIR_RIGHT:
        return "Right"


def main():
    num_players = int(input("Number of Players: "))
    bluetooth_utils.start(num_players)
    currently_displayed = ""
    while True:
        num_connected = bluetooth_utils.number_of_devices()
        to_display = f"Connected: {num_connected}/{num_players}   Input: "
        for player in range(num_players):
            to_display += f"({player + 1}, {get_player_dir(player)}) "
        if currently_displayed != to_display:
            currently_displayed = to_display
            print('\r', to_display, (' ' * 15), end='')


main()
