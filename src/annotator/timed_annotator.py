import time
from sys import stderr

import requests
from pynput import keyboard
from urllib3.exceptions import NewConnectionError, MaxRetryError

ACTION_DURATION_SECONDS = 5
TRANSITION_DURATION_SECONDS = 3
IS_TO_PAUSE_IN_REST = False
TO_END_PROGRAM = False
IGNORED_CLASS_LABEL = "none"
CLASSES = ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE",
           "THUMB_LITTLE", "THUMB_RING_LITTLE_V_SIGN", "THUMB_INDEX",
           "STRAIGHT_STATIC", "FIST", "THUMB_UP",
           "PITCH_PALM", "ROLL_PALM", "YAWN_PALM"]


def key_press(key):
    # NOTE: Only pausing during `NONE` action, since the collected CSI data would be labeled continuously.
    if key == keyboard.Key.esc:
        global IS_TO_PAUSE_IN_REST
        IS_TO_PAUSE_IN_REST = (not IS_TO_PAUSE_IN_REST)
        print("Altered Pause/Resume Flag: ", "PAUSED" if IS_TO_PAUSE_IN_REST else "RESUMED")
    elif key == keyboard.Key.backspace:
        global TO_END_PROGRAM
        TO_END_PROGRAM = True
        return False  # stop listener


def post_next_action_label(class_name):
    params = (('value', class_name),)
    try:
        resp = requests.post('http://0.0.0.0:8080/annotation', params=params)  # better way to specify the host?
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return resp


def print_response(resp, class_name):
    if resp is not None and resp.status_code == 200:
        print("Posted NEW action `{:s}` to perform now ...".format(class_name))
    else:
        stderr.write("Bad Service!\nResponse Code: "
                     + str(resp.status_code if resp is not None else "NULL")
                     + "\nResponse: " + str(resp.text if resp is not None else "NULL\n"))


if __name__ == '__main__':
    print("Attaching keyboard listener ...")
    listener = keyboard.Listener(on_press=key_press)
    listener.start()  # start to listen on a separate thread
    print("\tESC = pause/resume (in resting state only)\n\tBACKSPACE = end program\n\n")

    repetition = 1
    totalActions = len(CLASSES)
    currAction = 0
    while True:
        className = CLASSES[currAction]
        if not TO_END_PROGRAM:
            print("\nNEXT action: ", className)

        print_response(post_next_action_label(IGNORED_CLASS_LABEL), IGNORED_CLASS_LABEL)
        t = TRANSITION_DURATION_SECONDS
        while t > 0:
            time.sleep(1)
            if TO_END_PROGRAM:
                break
            if IS_TO_PAUSE_IN_REST:
                print("PAUSED! Press ESC to resume ...")
            else:
                minutes, secs = divmod(t, 60)
                print('\tNONE ==> {:02d}:{:02d}'.format(minutes, secs))
                t -= 1
        if TO_END_PROGRAM:
            break
        else:
            print("-------------------------------TIME-UP-------------------------------\n\n")

        print_response(post_next_action_label(className), className)
        t = ACTION_DURATION_SECONDS
        while t > 0:
            if TO_END_PROGRAM:
                break
            minutes, secs = divmod(t, 60)
            # put end='\r' to see the count-down in the same line
            print('\tRep-{:d} # {:d}) {:s}  ->  {:02d}:{:02d}'
                  .format(repetition, currAction + 1, className, minutes, secs))
            time.sleep(1)
            t -= 1
        print("===============================TIME-UP===============================\n\n")

        currAction = (currAction + 1) % totalActions
        if currAction == 0:
            repetition += 1
