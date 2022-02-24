from sys import stderr

import requests
import time
from pynput import keyboard
from urllib3.exceptions import NewConnectionError, MaxRetryError

ACTION_DURATION_SECONDS = 30
TRANSITION_DURATION = 10
IS_TO_COUNT_FLAG = True
CLASSES = ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE",
           "THUMB_INDEX", "THUMB_LITTLE", "THUMB_RING_LITTLE_V_SIGN",
           "INDEX_MIDDLE_RING_LITTLE", "FIST", "THUMB_UP",
           "PITCH_PALM", "ROLL_PALM", "YAWN_PALM"]


def key_press(key):
    if key == keyboard.Key.esc:
        global IS_TO_COUNT_FLAG
        IS_TO_COUNT_FLAG = (not IS_TO_COUNT_FLAG)
        print("Altered Counter Flag: ", IS_TO_COUNT_FLAG)
        # return False  # stop listener
    elif key == keyboard.Key.enter:
        print("\tPressed ENTER key!\n")


if __name__ == '__main__':
    # numClasses = int(input("Number of Classes: "))
    # classLabels = [0] * numClasses
    # classNames = [""] * numClasses
    # classDict = {}
    # for i in range(1, numClasses + 1):
    #     classLabels[i - 1] = (i % 10) if (i < 11) else (ord('a') + i - 11)
    #     classNames[i - 1] = input(str(classLabels[i - 1] if (i < 11) else chr(classLabels[i - 1])) + ") ")
    #     classDict[str(classLabels[i - 1])] = str(classNames[i - 1])

    listener = keyboard.Listener(on_press=key_press)
    listener.start()  # start to listen on a separate thread

    t = TRANSITION_DURATION
    minutes, secs = divmod(t, 60)
    print("Running the count-down for: ", '{:02d}:{:02d}'.format(minutes, secs))
    while t:
        minutes, secs = divmod(t, 60)
        timer = 'Collecting Data for Action: {:02d}) {:s} ->{:02d}:{:02d}'.format(0, CLASSES[0], minutes, secs)
        print("\r", timer, end="\r")
        time.sleep(1)
        t -= 1

    params = (('value', className),)
    try:
        response = requests.post('http://0.0.0.0:8080/annotation', params=params)  # better way to specify the host?
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        response = None
        stderr.write(str(err) + "\n")
        pass
    if response is not None and response.status_code == 200:
        print("Successfully posted action to the CSI-Pi service. Collecting data for action `", className, "`...\n")
    else:
        stderr.write("Bad Service!\nResponse Code: "
                         + str(response.status_code if response is not None else "NULL")
                         + "\nResponse: " + str(response.text if response is not None else "NULL\n"))
