import bluetooth
import threading


_SERVER_UUID = "2cafd5f6-ea6c-44c4-99bf-5629bdbcab1d"
_SERVER_NAME = "Go Time Geese"
_SERVER_BACKLOG = 10
_SERVER_GAME_FULL_RESPONSE = 255

_CLIENT_ACTION_PRESSED = 100
_CLIENT_ACTION_RELEASED = 101
_CLIENT_ACTION_PAUSE = 200

DIR_UP = 1
DIR_DOWN = 2
DIR_LEFT = 3
DIR_RIGHT = 4
DIR_NONE = 5


# Internally used to manage player information in a thread-safe manner.
# Player fields are: MAC Address (0), whether the device is connected (1), the
# current directional input (2), whether the action button is pressed (3).
class _PlayerArray:
    def __init__(self, n):
        self._length = n
        self._arr = [["", False, DIR_NONE, False] for _ in range(n)]
        self._lock = threading.RLock()

    def __len__(self):
        return self._length

    def __repr__(self):
        self._lock.acquire()
        string = self._arr.__repr__()
        self._lock.release()
        return string

    def __getitem__(self, item):
        self._lock.acquire()
        player_info = tuple(self._arr[item])
        self._lock.release()
        return player_info

    def set_field(self, index, field, value):
        # Robust type-checking is needed so that we don't accidentally inject a
        # mutable reference into the data structure.
        if field == 0:
            if not isinstance(value, str):
                raise TypeError(f"Expected str, received {type(value)}.")
        elif field == 2:
            if not isinstance(value, int):
                raise TypeError(f"Expected int, received {type(value)}.")
        elif field == 1 or field == 3:
            if not isinstance(value, bool):
                raise TypeError(f"Expected bool, received {type(value)}")
        # Now, we can safely modify the underlying list.
        self._lock.acquire()
        self._arr[index][field] = value
        self._lock.release()

    def count_if(self, condition):
        self._lock.acquire()
        count = 0
        for i in range(self._length):
            player_info = tuple(self._arr[i])
            if condition(player_info):
                count += 1
        self._lock.release()
        return count

    def find_if(self, condition):
        self._lock.acquire()
        index = 0
        while index < self._length:
            player_info = tuple(self._arr[index])
            if condition(player_info):
                break
            index += 1
        self._lock.release()
        return -1 if index == self._length else index

    def lock(self):
        """Locks all access to the player array until a corresponding unlock() call.
        Not needed in most cases, but might be useful if more than one operation is
        to be performed on the array in an atomic manner."""
        self._lock.acquire()

    def unlock(self):
        """Unlocks access following a previous lock() call."""
        self._lock.release()


# In charge of receiving bytes from the supplied socket and appropriately
# update the relevant player fields for the given index. If index == -1, this
# thread will simply wait for the client to disconnect and close the socket.
class _PlayerThread(threading.Thread):
    def __init__(self, index, socket):
        super().__init__()
        self._index = index
        self._socket = socket

    def run(self):
        global _players, _paused

        # Initialize the player's input parameters (2 & 3) and set their connected
        # status (1) to True.
        if self._index != -1:
            _players.set_field(self._index, 2, DIR_NONE)
            _players.set_field(self._index, 3, False)
            _players.set_field(self._index, 1, True)

        try:
            while True:
                data = self._socket.recv(1)
                if not data:
                    break
                # TODO: Here, we should differentiate between directional input and pause requests.
                _players.set_field(self._index, 2, data[0])
        except OSError:
            pass

        # The connection has ended. Set the player's connected status back to
        # false and close the socket.
        if self._index != -1:
            _players.set_field(self._index, 1, False)
        self._socket.close()


# The main connection thread that indefinitely accepts oncoming connections
# and sends the appropriate response before handing the client socket over to
# a _PlayerThread.
class _ConnectionThread(threading.Thread):
    def __init__(self, socket):
        super().__init__()
        self._socket = socket

    def run(self):
        global _players
        while True:
            # Accept a connection from an oncoming client. If this fails, the socket is closed,
            # and we must gracefully exit the loop.
            try:
                client_socket, client_info = self._socket.accept()
            except OSError:
                self._socket.close()
                break

            # Find an index that matches the client's MAC address. If no such index exist,
            # attempt to find an empty index and reserve it for this device.
            _players.lock()
            index = _players.find_if(lambda x: x[0] == client_info[0])
            if index == -1:
                index = _players.find_if(lambda x: x[0] == "")
                if index != -1:
                    _players.set_field(index, 0, client_info[0])
            _players.unlock()

            # We wrap the code for sending the appropriate response to the client within a
            # try-except in case the client crashes or closes the connection.
            try:
                if index == -1:
                    client_socket.send(bytes([_SERVER_GAME_FULL_RESPONSE]))
                else:
                    client_socket.send(bytes([index + 1]))
                _PlayerThread(index, client_socket).start()
            except OSError:
                client_socket.close()


_players: _PlayerArray
_serverSocket: bluetooth.BluetoothSocket
_paused = False


def init(num_players: int) -> None:
    """Initializes the bluetooth_utils module. You must call this function once and
    only once at the very beginning of the main program."""
    global _players, _serverSocket

    # Prepare the server socket and advertise with _SERVER_UUID.
    _serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    _serverSocket.bind(("", bluetooth.PORT_ANY))
    _serverSocket.listen(_SERVER_BACKLOG)
    bluetooth.advertise_service(_serverSocket, _SERVER_NAME,
                                service_classes=[_SERVER_UUID, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                service_id=_SERVER_UUID)

    _players = _PlayerArray(num_players)
    _ConnectionThread(_serverSocket).start()


def number_of_devices() -> int:
    """Returns the number of devices that are currently connected to the game.
    The returned value will be between 0 and the total number of players."""
    global _players
    return _players.count_if(lambda x: x[1])


def get_paused() -> bool:
    """Returns true if one of the players has paused the game."""
    global _paused
    return _paused


def get_direction(player: int) -> int:
    """Returns the directional input currently supplied by the specified player.
    The returned value is one of DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_NONE.
    Note: Player numbering starts from 0."""
    global _players
    player_info = _players[player]
    if not player_info[1]:
        return DIR_NONE
    return player_info[2]


def get_action(player: int) -> bool:
    """Returns true if the specified player is currently pressing the action button.
    Note: Player numbering starts from 0."""
    global _players
    player_info = _players[player]
    return player_info[1] and player_info[3]


def stop() -> None:
    """Cleans up the system resources associated with the bluetooth_utils module. You must
    call this function once and only once at the very end of the main program."""
    global _serverSocket
    _serverSocket.close()
