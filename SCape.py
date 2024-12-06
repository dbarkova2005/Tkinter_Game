import math
from random import randint as rand, choice

import tkinter as tk
from PIL import Image, ImageTk


def configure_window():
    """
    Configures the main game window settings.
    """
    window.title("Scape")
    window.attributes("-fullscreen", True)
    window.configure(background="#5A5A5A")


def configure_canvas():
    """
    Prompts the user to enter a valid username.
    Once valid:
        - Configures and displays the canvas.
        - Sets default keybinds.
    """
    global pause_btn

    if not is_paused:
        if not valid_user:
            prompt_label.place(relx=0.5, rely=0.5, anchor="center")

            username = input("Please enter your username: ")
            while not (username.isalpha() and len(username) <= 20):
                username = input("Please enter your username: ")

            validate_user(username)
        else:
            pause_btn = tk.Button(window, text="Pause",
                                  font=("Arial", 14, "bold"),
                                  highlightbackground="#5A5A5A",
                                  command=pause_game)
            pause_btn.pack(side='right', anchor="n")
            timer_label.pack(anchor="n", pady=15)

    canvas.focus_set()
    canvas.configure(width=800, height=600, bg="#3a343b")
    canvas.pack(pady=85)

    canvas.bind(f"<{keybinds['left']}>", lambda event: movement(event, "left"))
    canvas.bind(f"<{keybinds['right']}>",
                lambda event: movement(event, "right"))
    canvas.bind(f"<{keybinds['down']}>", lambda event: movement(event, "down"))
    canvas.bind(f"<{keybinds['up']}>", lambda event: movement(event, "up"))

    canvas.bind("<b>", boss_button)
    canvas.bind("<e>", shooting_mechanic)


def format_time(seconds):
    """
    Converts a time duration in seconds to a formatted string of
    minutes and seconds.

    Parameters:
        seconds (int): The time in seconds at a specific point.

    Returns:
        str: A string representing the time in "MM:SS" format.
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02}:{secs:02}"


def update_timer():
    """
    Updates the countdown timer every second. When the timer reaches zero:
    - Displays "Game Over!" and pauses the timer.
    - Creates an empty "logs.txt" file.
    """
    global time_left
    global is_paused

    if not is_paused:
        if time_left > 0:
            time_left -= 1
            timer_label.config(text=f"Timer: {format_time(time_left)}")
            window.after(1000, update_timer)
        else:
            timer_label.config(text="Game Over!")
            is_paused = True
            file = open("logs.txt", "w")
            file.close()


def hide_canvas():
    """
     Pauses the game and hides the canvas and associated UI elements:
        - pause button
        - timer label
    """
    global is_paused

    is_paused = True
    canvas.pack_forget()
    pause_btn.pack_forget()
    timer_label.pack_forget()
    window.update()


def validate_user(username):
    """
    Validates and loads a user's saved game data from logs.txt based on their
    username.

    If the username is new, it is added to the logs and the game starts from
    the beginning. If the username already exists, the user's progress is
    loaded, including the unlocked rooms, inventory and remaining time. The
    state variables are updated accordingly.

    Parameters:
        username (str): The player's username to validate and load or create
        a saved game for.
    """
    global valid_user
    global uname
    global unlocked_exist
    global has_pistol
    global unlocked_room_2
    global unlocked_room_1
    global has_key
    global time_left
    global location

    uname = username
    file = open("logs.txt", "r")
    logs = file.read().strip()
    file.close()
    if "Username: " + uname.strip() not in logs:
        file = open("logs.txt", "a")
        file.write("Username: " + uname.strip() + "\n\n")
        file.close()
        generate_room("room_0")
        location = "room_0"
    else:
        try:
            file = open("logs.txt", "r")
            lines = file.readlines()
            file.close()
            stripped_lines = [line.strip().split(": ", 1)[-1]
                              for line in lines]
            unlocked_exist = stripped_lines[-1] == 'True'
            has_pistol = stripped_lines[-2] == 'True'
            unlocked_room_2 = stripped_lines[-3] == 'True'
            unlocked_room_1 = stripped_lines[-4] == 'True'
            has_key = stripped_lines[-5] == 'True'
            time_left = int(stripped_lines[-6])
            coordinates = stripped_lines[-7]
            location = stripped_lines[-8]
            generate_room(location)
            canvas.move(character_can, -(char_x-int(coordinates[1:4])),
                        -(char_y-int(coordinates[8:11])))
            if location == "room_1":
                generate_room_1()
            elif location == "room_2":
                generate_room_2()
                if has_pistol:
                    start_shooting_game(3, 50, "red")
        except IndexError:
            generate_room("room_0")
            location = "room_0"
    prompt_label.destroy()
    valid_user = True
    configure_canvas()


def generate_room(room):
    """
    Generates the layout of the specified room, including walls, doors, and
    items on the canvas.
    First, the previous room's objects are cleared from the canvas
    (except for the character),and the items associated with the new room
    are displayed. If the player doesn't have the key in room_0, it is
    placed on the canvas.

    Parameters:
        room (str): The name of the room to generate.
    """
    global key_can

    all_items = canvas.find_all()
    for item in all_items:
        if item != character_can:
            canvas.delete(item)

    for i in range(0, 13):
        if i == 5 or i == 6:
            if room == "room_1":
                canvas.create_rectangle(350, 570, 490, 600, fill="brown")
                canvas.create_image((48*i)+22*(i+1.7), 38, image=wall)
            elif room == "room_2":
                canvas.create_rectangle(350, 0, 490, 30, fill="brown")
                canvas.create_image((48*i)+22*(i+1.7), 568, image=wall)
            else:
                canvas.create_rectangle(350, 570, 490, 600, fill="brown")
                canvas.create_rectangle(350, 0, 490, 30, fill="brown")
        else:
            canvas.create_image((48*i)+22*(i+1.7), 568, image=wall)
            canvas.create_image((48*i)+22*(i+1.7), 38, image=wall)

    for i in range(1, 8):
        if i == 4 or i == 5:
            if room == "room_0":
                canvas.create_rectangle(0, 410, 38, 265, fill="gold")
            else:
                canvas.create_image(38, (48*i)+22*(i+0.98), image=wall)
        else:
            canvas.create_image(38, (48*i)+22*(i+0.98), image=wall)
        canvas.create_image(768, (48*i)+22*(i+0.98), image=wall)

    if location == "room_0" and not has_key:
        key_can = canvas.create_image(300, 300, image=key)
        canvas.tag_raise(character_can)

    canvas.update()


def wall_collision(cx, cy):
    """
    Detects whether the character collides with the walls of the room based on
    the coordinates.

    Parameters:
        - cx (int): The x-coordinate of the character's position.
        - cy (int): The y-coordinate of the character's position.

    Returns:
        - False (bool): if the character is away from the wall.
        - True (bool): if the character is next to the wall.
    """
    if cx-73 < 25 or 733-cx < 25:
        return False
    elif cy-73 < 30 or 533-cy < 25:
        return False
    else:
        return True


def obstacle_collision(cy):
    """
    Detects whether the character collides with the obstancle in room_1 based
    on the coordinates.

    Parameters:
        - cy (int): The y-coordinate of the character's position.

    Returns:
        - False (bool): if the character is away from the obstacle
        - True (bool): if the character is next to the obstacle
    """
    if cy > 200:
        return False
    else:
        return True


def walk_between_rooms(cx, cy):
    """
    Moves the character between rooms based on its coordinates.

    This function checks the character's position and room access.
    It updates the character's location and generates the corresponding
    room layout.
    If the player has successfully escaped, a winner's screen is displayed with
    the score and options to view the leaderboard or quit.

    Parameters:
        - cx (int): The x-coordinate of the character's position.
        - cy (int): The y-coordinate of the character's position.
    """
    global location
    global chest_win
    global instructions_win
    global password_win
    global is_paused
    global pause_btn
    global total_time
    global score

    if location == "room_0":
        if cx > 384 and cx < 465 and cy < 100:
            if unlocked_room_1 is True:
                location = "room_1"
                generate_room(location)
                generate_room_1()
                canvas.move(character_can, 0, 400)
                try:
                    password_win.destroy()
                except NameError:
                    pass

        if (cx > 384 and cx < 470 and cy > 510) and unlocked_room_2 is True:
            location = "room_2"
            generate_room(location)
            generate_room_2()
            canvas.move(character_can, 0, -400)
        elif (cx > 384 and cx < 470 and cy > 510) and unlocked_room_2 is False:
            password_entry()

        if cy > 280 and cy < 390 and cx < 100:
            if unlocked_exist is True:
                is_paused = True
                pause_btn.pack_forget()
                canvas.unbind("<b>")
                total_time = initial_time - time_left
                total_time = format_time(total_time)
                score = time_left
                winner = tk.Label(window,
                                  text="CONGRATULATIONS!\nYou've escaped in "
                                  + total_time + ".\nYour score is: "
                                  + str(score),
                                  font=("Garamond", 30, "bold"),
                                  bg="gold", fg="black")
                winner.place(relx=0.5, rely=0.5, anchor="center")
                leaderboard_btn = tk.Button(window, text="Leaderboard",
                                            font="Arial, 18",
                                            command=display_leaderboard)
                leaderboard_btn.place(relx=0.5, rely=0.59, anchor="center")
                quit_btn = tk.Button(window, text="Quit", font="Arial, 18",
                                     command=window.destroy)
                quit_btn.place(relx=0.5, rely=0.63, anchor="center")
                clear_logs = open("logs.txt", "w")
                clear_logs.close()
                update_leaderboard(uname, score)
    elif location == "room_1":
        if cx > 384 and cx < 470 and cy > 510:
            location = "room_0"
            generate_room(location)
            canvas.move(character_can, 0, -400)
            try:
                instructions_win.destroy()
            except NameError:
                pass
            try:
                chest_win.destroy()
            except NameError:
                pass
    elif location == "room_2":
        if cx > 384 and cx < 470 and cy < 100 and unlocked_room_2:
            location = "room_0"
            generate_room(location)
            canvas.move(character_can, 0, 400)


def object_collision():
    """
    Detects collisions between the character and interactive objects
    in the current room.

    This function checks if the character's bounding box overlaps with
    the bounding boxes of the objects surrounding it. When an overlap is
    detected, it triggers the relevant event based on the object.
    """
    global key_can
    global scroll_can
    global pistol_can
    global has_key
    global has_pistol
    global is_chest_open
    global open_scroll
    global chest_id
    global unlocked_room_1
    global unlocked_room_2

    char_box = canvas.bbox(character_can)
    if not has_key and location == "room_0":
        key_box = canvas.bbox(key_can)
        if (char_box[0] < key_box[2] and char_box[2] > key_box[0] and
                char_box[1] < key_box[3] and char_box[3] > key_box[1]):
            has_key = True
            unlocked_room_1 = True
            canvas.delete(key_can)
            canvas.update()

    if location == "room_1":
        scroll_box = canvas.bbox(scroll_can)
        if (char_box[2] > scroll_box[0] and char_box[0] < scroll_box[2] and
                char_box[3] > scroll_box[1] and char_box[1] < scroll_box[3]):
            if not open_scroll:
                open_scroll = True
                read_scroll()
        else:
            open_scroll = False

        for num in chest_id:
            chest_box = canvas.bbox(num)
            if (char_box[2] > chest_box[0] and char_box[0] < chest_box[2] and
                    char_box[3] > chest_box[1] and char_box[1] < chest_box[3]):
                if not is_chest_open:
                    is_chest_open = True
                    open_chest(num)
            else:
                is_chest_open = False

    if not has_pistol and location == "room_2":
        pistol_box = canvas.bbox(pistol_can)
        if (char_box[2] > pistol_box[0] and char_box[0] < pistol_box[2] and
                char_box[3] > pistol_box[1] and char_box[1] < pistol_box[3]):
            has_pistol = True
            unlocked_room_2 = False
            canvas.delete(pistol_can)
            canvas.update()
            start_shooting_game(3, 50, "red")


def movement(event, dir):
    """
    Moves the character in the specified direction (right, left, up, down)
    by a set distance of 20px and checks for interactions with the walls,
    obstacles, and objects in the room. If the movement causes a collision,
    the character's position is adjusted accordingly.

    Parameters:
        - event: The event object passed by the event handler, used for key
        press detection.
        - dir (str): The direction of movement.
    """
    global is_paused
    char_x = canvas.coords(character_can)[0]
    char_y = canvas.coords(character_can)[1]
    dx = 0
    dy = 0
    new_char_x = char_x
    new_char_y = char_y

    if not is_paused:
        if dir == "right":
            new_char_x = char_x + 20
            dx = 20
        elif dir == "left":
            new_char_x = char_x - 20
            dx = -20
        elif dir == "up":
            new_char_y = char_y - 20
            dy = -20
        elif dir == "down":
            new_char_y = char_y + 20
            dy = 20

        walk_between_rooms(new_char_x, new_char_y)

        if wall_collision(new_char_x, new_char_y):
            if location == "room_2" and not obstacle_collision(new_char_y):
                dy = 0
                canvas.move(character_can, dx, dy)
            else:
                canvas.move(character_can, dx, dy)
        else:
            pass

        object_collision()


def pause_game():
    """
    Pauses the game by hiding the game canvas and displaying the pause menu
    with options.
    Ensures that any open windows are closed before showing the pause menu.
    """

    hide_canvas()

    try:
        password_win.destroy()
    except NameError:
        pass
    try:
        instructions_win.destroy()
    except NameError:
        pass
    try:
        chest_win.destroy()
    except NameError:
        pass

    pause_win.configure(background="#5A5A5A")
    btn_continue = tk.Button(pause_win, text="Continue", font=("Arial", 30),
                             command=continue_game)
    btn_keybinds = tk.Button(pause_win, text="Key Binds",
                             font=("Arial", 30), command=change_keybinds)
    btn_leaderboard = tk.Button(pause_win, text="Leaderboard",
                                font=("Arial", 30),
                                command=display_leaderboard)
    btn_savequit = tk.Button(pause_win, text="Save & Quit",
                             font=("Arial", 30),
                             command=save_and_quit)

    btn_continue.grid(row=1, column=2)
    btn_keybinds.grid(row=2, column=2)
    btn_leaderboard.grid(row=3, column=2)
    btn_savequit.grid(row=4, column=2)

    pause_win.place(relx=0.5, rely=0.5, anchor="center")


def continue_game():
    """
    Continues the game by displaying the game canvas and hiding the pause
    menu with options. Ensures that any open windows are closed before
    continuing the game.
    """
    global return_btn
    global is_paused
    global leaderboard_win
    global change_keybinds_win

    is_paused = False

    pause_win.place_forget()
    fake_screen.place_forget()
    try:
        return_btn.place_forget()
    except NameError:
        pass
    try:
        leaderboard_win.destroy()
    except NameError:
        pass
    try:
        change_keybinds_win.destroy()
    except NameError:
        pass

    window.update()
    configure_canvas()
    update_timer()


def boss_button(event):
    """
    Displays the fake work screen with a return button on the bottom.
    Ensures that any open windows are closed before displaying the screen.
    """
    global return_btn
    global is_paused

    try:
        change_keybinds_win.destroy()
    except NameError:
        pass
    try:
        instructions_win.destroy()
    except NameError:
        pass
    try:
        chest_win.destroy()
    except NameError:
        pass
    try:
        password_win.destroy()
    except NameError:
        pass
    try:
        leaderboard_win.destroy()
    except NameError:
        pass

    hide_canvas()

    canvas.unbind("<b>")
    fake_screen.place(x=0, y=0, relwidth=1, relheight=1)
    window.update()

    return_btn = tk.Button(window, text="Return", font=("Arial", 14),
                           highlightbackground="white", padx=5, pady=5,
                           command=continue_game)
    return_btn.place(relx=0.95, rely=0.95, anchor="center")


def generate_room_1():
    """
    Generates the layout of room 1 by creating four chests at predefined
    positions and storing their identifiers. Also creates a scroll object
    at a specified position.
    """
    global scroll_can
    global chest_id

    chest_id = []

    for i in range(1, 5):
        temp_chest = None
        temp_chest = canvas.create_image((120*i+100), 200, image=chest)
        chest_id.append(temp_chest)
    scroll_can = canvas.create_image(420, 400, image=scroll)
    canvas.tag_raise(character_can)
    canvas.update()


def read_scroll():
    """
    Displays a set of instructions for the room 2 challenge when the
    player interacts with a scroll object. If the instructions window
    is already open, it prevents reopening to avoid duplication.
    """

    global instructions_win

    riddle = ("Inside the chests a secret resides,\n" +
              "A splash of colour and a number to guide.\n" +
              "A game with an oval ball in play,\n" +
              "Where colours hold the clues to the way.\n" +
              "But one rule's key, so don't forget:\n" +
              "The vowel stays firm — it's fixed, it's set!")

    if "instructions_win" in globals() and instructions_win.winfo_exists():
        return

    instructions_win = tk.Frame(window)
    instructions_win.configure(background="#5A5A5A")

    instructions = tk.Label(
        instructions_win,
        text=riddle,
        bg="#3b3b3b",
        fg="white",
        font="Arial 18")

    instructions.grid(row=1, column=2)

    close = tk.Button(instructions_win, text="Close",
                      command=instructions_win.destroy)
    close.grid(row=2, column=2)

    instructions_win.place(relx=0.77, rely=0.5)


def open_chest(num):
    """
    Displays the interior of each chest in room 2 when the player
    interacts with the object. Each chest displays a different label
    and background color. If the chest is already open, it prevents
    reopening to avoid duplication.

    Parameters:
        - num (int): The identifier for the chest to open.
    """
    global chest_win
    global chest_id

    chest_text = ""
    chest_bg = ""
    chest_fg = "white"

    if "chest_win" in globals() and chest_win.winfo_exists():
        return

    chest_win = tk.Frame(window)

    if num == chest_id[0]:
        chest_text = "SEVEN"
        chest_bg = "blue"
        chest_win.configure(background="blue")
    elif num == chest_id[1]:
        chest_text = "TWO"
        chest_bg = "green"
        chest_win.configure(background="green")
    elif num == chest_id[2]:
        chest_text = "FIVE"
        chest_bg = "yellow"
        chest_fg = "black"
        chest_win.configure(background="yellow")
    elif num == chest_id[3]:
        chest_text = "EIGHT"
        chest_bg = "red"
        chest_win.configure(background="red")

    chest_interior = tk.Label(chest_win, text=chest_text, bg=chest_bg,
                              fg=chest_fg, font="Arial 30")
    chest_interior.grid(row=1, column=2)

    close = tk.Button(chest_win, text="Close", command=chest_win.destroy)
    close.grid(row=2, column=2)

    chest_win.place(relx=0.1, rely=0.5)


def password_entry():
    """
    Displays a password prompt allowing the user to enter a 5-character
    password. If the password window is already open, it prevents
    reopening to avoid duplication.
    """
    global password_win
    global pswd_attempts

    if "password_win" in globals() and password_win.winfo_exists():
        return

    password_win = tk.Frame(window)
    password_prompt = tk.Label(password_win,
                               text="Enter a 5 character password below:",
                               bg="#5A5A5A", fg="white")
    password_prompt.grid(row=0, column=1, padx=10, pady=5)

    password_input = tk.Entry(password_win, show="*", width=20)
    password_input.grid(row=1, column=1, padx=10, pady=5)

    submit_button = tk.Button(
        password_win, text="Submit",
        command=lambda: submit_password(password_input, result))
    submit_button.grid(row=4, column=1, pady=5)
    close_button = tk.Button(
        password_win, text="Close",
        command=lambda: (password_win.destroy(), canvas.focus_set()))
    close_button.grid(row=5, column=1)

    result = tk.Label(password_win, text="", bg="#5A5A5A", fg="white")
    result.grid(row=6, column=1, pady=5)

    password_win.place(relx=0.85, rely=0.5, anchor="center")


def submit_password(password_input, result):
    """
    Handles the password submission, validating the user's input:
        - If the correct password is entered, it unlocks room 2.
        - If the cheat code is entered, it unlocks the exit.
        - For invalid attempts, it shows an error message and provides
        hints after
        multiple attempts.

    Parameters:
        - password_input (tk.Entry): The input field for the user to
        enter the password.
        - result (tk.Label): Label to display the result of the
        password attempt.
    """
    global password_win
    global pswd_attempts
    global unlocked_room_2
    global unlocked_exist
    global time_left
    global initial_time

    password = password_input.get()

    correct_password = "8u275"
    if password == correct_password:
        unlocked_room_2 = True
        password_win.destroy()
        canvas.focus_set()
    elif password == "cheat":
        unlocked_exist = True
    elif password == "xtime":
        time_left = 20 * 60
        initial_time = time_left
    else:
        result.config(text="Invalid password. Try again.", fg="red")
        canvas.focus_set()
        if unlocked_room_1:
            pswd_attempts += 1

        hint_1 = tk.Label(password_win, text="game: rugby",
                          bg="#5A5A5A", fg="white")
        hint_2 = tk.Label(password_win, text="red, green, blue, yellow",
                          bg="#5A5A5A", fg="white")
        if pswd_attempts > 5:
            hint_1.grid(row=2, column=1, pady=5)
        if pswd_attempts > 12:
            hint_2.grid(row=3, column=1, pady=5)


def generate_room_2():
    """
    Generates the layout of room 2 by placing a pistol on the side if
    it has not been picked up yet.
    """
    global pistol_can
    canvas.create_rectangle(75, 220, 730, 240, fill="#5A5A5A")
    if not has_pistol:
        pistol_can = canvas.create_image(120, 120, image=pistol)
        canvas.tag_raise(character_can)


def start_shooting_game(speed, size, colour):
    """
    Starts the shooting game by creating a target on the canvas that
    moves horizontally. The target is represented as circle with a
    random starting position and it moves in the horizontal direction
    at a set speed.

    Parameters:
        - speed (int): The speed at which the target moves.
        - size (int): The size of the target (diameter of the circle).
        - colour (str): The color of the target.
    """
    global target
    global timestamp

    timestamp = time_left

    dir_list = [1, -1]
    x1 = rand(91, 710-size)
    y1 = 400
    x2 = x1 + size
    y2 = y1 + size

    target = canvas.create_oval(x1, y1, x2, y2, fill=colour)
    dx = choice(dir_list)*speed
    move_target(target, dx)


def move_target(target, dx):
    """
    Moves the target horizontally across the canvas. If the target
    reaches the edge of the canvas, it will bounce back in the
    opposite direction. This function is called every 10 milliseconds
    to ensure the target movement.

    Parameters:
        - target (Canvas object): The object to move.
        - dx (int): The movement direction (positive or negative value).
    """
    if canvas.coords(target):
        if canvas.coords(target)[0] < 90 or canvas.coords(target)[2] > 720:
            dx = -dx
        canvas.move(target, dx, 0)
        window.after(10, move_target, target, dx)


def shooting_mechanic(event):
    """
    When the player is in room 2 and has the pistol, the function captures
    the current mouse pointer position and triggers a bullet to shoot
    towards that position.

    Parameters:
        - event: The event object passed by the event handler, used for
        key press detection.
    """
    if location == "room_2" and has_pistol:
        x_pos = canvas.winfo_pointerx() - canvas.winfo_rootx()
        y_pos = canvas.winfo_pointery() - canvas.winfo_rooty()

        shoot_bullet(x_pos, y_pos)


def shoot_bullet(x_pos, y_pos):
    """
    Creates a bullet at the character's position and sets it to move
    towards the mouse pointer.

    Parameters:
        - x_pos (int): The x-coordinate of the mouse pointer.
        - y_pos (int): The y-coordinate of the mouse pointer.
    """

    global bullet
    dx = x_pos - canvas.coords(character_can)[0]
    dy = y_pos - canvas.coords(character_can)[1]
    distance = math.sqrt(dx**2 + dy**2)
    dx /= distance
    dy /= distance

    bullet = canvas.create_oval(canvas.bbox(character_can)[0] + 23,
                                canvas.bbox(character_can)[1] + 23,
                                canvas.bbox(character_can)[2] - 28,
                                canvas.bbox(character_can)[3] - 28,
                                fill="black")

    move_bullet(bullet, dx, dy)

    detect_bullet_overlap()


def move_bullet(bullet, dx, dy):
    """
    Moves the bullet across the canvas in the mouse pointer direction
    every 5 milliseconds. The bullet is moved by a factor of 10, which
    determines its speed. If the bullet moves outside the defined
    boundaries, it is deleted. The function dynamically adjusts the
    target size based on the elapsed time and points.

    Parameters:
        - bullet (Canvas object): The bullet to moved on the canvas.
        - dx (float): The change in the x-coordinate of the bullet.
        - dy (float): The change in the y-coordinate of the bullet.
    """
    canvas.move(bullet, dx * 10, dy * 10)
    bullet_coords = canvas.coords(bullet)

    if bullet_coords:
        if (
            bullet_coords[0] < 70
            or bullet_coords[1] < 70
            or bullet_coords[2] > 730
            or bullet_coords[3] > 535
        ):
            canvas.delete(bullet)
        else:
            window.after(5, move_bullet, bullet, dx, dy)
            if timestamp - time_left > 8 and points < 5:
                canvas.coords(target, canvas.coords(target)[0], 400,
                              canvas.coords(target)[0]+60, 460)
            elif (timestamp - time_left > 15 and
                    (points > 4 and points < 10)):
                canvas.coords(target, canvas.coords(target)[0], 400,
                              canvas.coords(target)[0]+38, 438)
            elif (20 < timestamp - time_left < 31) and (9 < points < 12):
                canvas.coords(target, canvas.coords(target)[0], 400,
                              canvas.coords(target)[0]+18, 418)
            elif timestamp - time_left > 30 and (9 < points < 12):
                canvas.coords(target, canvas.coords(target)[0], 400,
                              canvas.coords(target)[0]+27, 427)


def detect_bullet_overlap():
    """
    Checks for object collision between the bullet and the target.
    If the bullet hits the target, it deletes both the bullet and the
    target, increments the score, and adjusts the difficulty based
    on the current points. If the player has reached a certain point
    threshold, it unlocks room 2 and the exit.

    This function is called continuously every 10 milliseconds after
    a bullet it shot.
    """
    global bullet
    global target
    global points
    global unlocked_room_2
    global unlocked_exist

    if bullet and target:
        bullet_coords = canvas.coords(bullet)
        target_coords = canvas.coords(target)

        if bullet_coords and target_coords:
            if (bullet_coords[2] > target_coords[0] and
                    bullet_coords[0] < target_coords[2] and
                    bullet_coords[3] > target_coords[1] and
                    bullet_coords[1] < target_coords[3]):
                canvas.delete(target)
                canvas.delete(bullet)
                points += 1
                if points < 5:
                    start_shooting_game(3, 50, "red")
                elif points > 4 and points < 10:
                    start_shooting_game(5, 28, "blue")
                elif points > 9 and points < 12:
                    start_shooting_game(10, 12, "yellow")
                elif points > 11:
                    canvas.delete(target)
                    canvas.delete(bullet)
                    unlocked_room_2 = True
                    unlocked_exist = True
                    canvas.unbind("<e>")

            else:
                window.after(10, detect_bullet_overlap)


def save_and_quit():
    """
    Saves the current game state to a log file, inlcluding player
    location, unlocked rooms, inventory and remaining time, and
    exits the game.
    """
    char_coords = canvas.coords(character_can)
    global time_left
    print(time_left)

    logs = open("logs.txt", "a")
    logs.write("location: " + location + "\n")
    logs.write("coordinates: " + str(char_coords) + "\n")
    logs.write("time_left: " + str(time_left) + "\n")
    logs.write("has_key status: " + str(has_key) + "\n")
    logs.write("unlocked_room_1 status: " + str(unlocked_room_1) + "\n")
    logs.write("unlocked_room_2 status: " + str(unlocked_room_2) + "\n")
    logs.write("has_pistol status: " + str(has_pistol) + "\n")
    logs.write("unlocked_exit status: " + str(unlocked_exist) + "\n")
    logs.close()

    window.destroy()


def update_leaderboard(uname, score):
    """
    Updates the leaderboard by reading the existing entries, adding a
    new entry, sorting the players by their scores in descending order,
    and writing the top 5 players back to the leaderboard file.

    Parameters:
        - uname (str): The username of the player.
        - score (int): The score of the player.
    """
    leaderboard = []
    with open("leaderboard.txt", "r") as file:
        for line in file:
            if line.strip():
                try:
                    rank, data = line.split(".", 1)
                    player, score_str = data.strip().rsplit(" ", 1)
                    leaderboard.append((player, score_str))
                except ValueError:
                    pass

    leaderboard.append((uname, str(score)))
    leaderboard = sorted(leaderboard, key=lambda x: int(x[1]),
                         reverse=True)[:5]

    with open("leaderboard.txt", "w") as file:
        for i, (player, p_score) in enumerate(leaderboard, 1):
            file.write(f"{i}. {player} {p_score}\n")
        for i in range(len(leaderboard) + 1, 6):
            file.write(f"{i}.\n")


def display_leaderboard():
    """
    Reads the leaderboard from the relevant text file and displays
    the player names with their scores on the screen.
    """
    global leaderboard_win

    try:
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()

        leaderboard = ""
        for i in range(5):
            if i < len(lines):
                leaderboard += lines[i].strip() + "\n"
            else:
                leaderboard += str(i + 1) + ".\n"

        leaderboard_win = tk.Frame(window)
        leaderboard_win.place(relx=0.8, rely=0.4)

        lb = tk.Label(leaderboard_win, text="LEADERBOARD",
                      font="Arial 22 bold",
                      bg="royal blue", fg="gold")
        leaderboard_display = tk.Label(leaderboard_win,
                                       text=leaderboard,
                                       font="Arial 16")
        lb.pack()
        leaderboard_display.pack()
    except (FileNotFoundError, IndexError, AttributeError, TypeError):
        pass


def change_keybinds():
    """
    Creates a frame and allows the player to change the movement
    key binds. Each button triggers the capture of a new key for
    the corresponding action.
    """
    global change_keybinds_win

    pause_win.place_forget()

    change_keybinds_win = tk.Frame(window)
    change_keybinds_win.place(relx=0.5, rely=0.5, anchor="center")

    change_up_btn = tk.Button(change_keybinds_win, text="UP",
                              command=lambda: capture_keypress("up"))
    change_up_btn.grid(row=1, column=2)

    change_down_btn = tk.Button(change_keybinds_win, text="DOWN",
                                command=lambda: capture_keypress("down"))
    change_down_btn.grid(row=3, column=2)

    change_left_btn = tk.Button(change_keybinds_win, text="LEFT",
                                command=lambda: capture_keypress("left"))
    change_left_btn.grid(row=2, column=1, pady=50)

    change_right_btn = tk.Button(change_keybinds_win, text="RIGHT",
                                 command=lambda: capture_keypress("right"))
    change_right_btn.grid(row=2, column=3, pady=50)

    continue_btn = tk.Button(change_keybinds_win, text="Continue",
                             command=continue_game)
    continue_btn.grid(row=4, column=2)

    bind_instruction = tk.Label(change_keybinds_win,
                                text="Press the button followed " +
                                "by a key to bind")
    bind_instruction.grid(row=0, column=2)


def capture_keypress(drn):
    """
    This function unbinds the previous key associated with the action
    and waits for the player to press a new key, which becomes the new
    key bind for that action.

    Parameters:
        - drn (str): The direction/action for which the keybind is
        being captured
    """
    action = drn
    previous_key = keybinds[action]
    canvas.unbind(f"<{previous_key}>")
    canvas.bind("<Key>", lambda event: change_keybind(event, action))
    canvas.focus_set()


def change_keybind(event, action):
    """
    This function captures the key the player presses and updates the
    keybinding for the specified action.

    Parameters:
        - event: The event object passed by the event handler, used for
        key press detection.
        - action (str): The action (movement direction) for which the
        new key bind is set.
    """
    capture = event.keysym
    keybinds[action] = capture
    canvas.unbind("<Key>")


window = tk.Tk()
canvas = tk.Canvas(window)
pause_win = tk.Frame(window)

up = "Up"
down = "Down"
left = "Left"
right = "Right"

keybinds = {
    "up": up,
    "down": down,
    "left": left,
    "right": right
}

is_paused = False
valid_user = False
unlocked_room_1 = False
unlocked_room_2 = False
unlocked_exist = False
has_key = False
open_scroll = False
is_chest_open = False
has_pistol = False

pswd_attempts = 0
points = 0
timestamp = 0
location = "room_0"

timer = 0
time_left = 10 * 60
initial_time = time_left
timer_label = tk.Label(window, text="Timer: " + str(timer),
                       font="Arial 40")
prompt_label = tk.Label(window,
                        text="Please enter your username\n" +
                        "in the terminal before playing",
                        font=("Arial", 35))

wall = Image.open("images/wall.png")
wall = wall.resize((70, 70), Image.NEAREST)
wall = ImageTk.PhotoImage(wall)

character = Image.open("images/female_adventurer.png")
character = character.resize((50, 60), Image.NEAREST)
character = ImageTk.PhotoImage(character)
character_can = canvas.create_image(665, 485, image=character)
char_x = 665
char_y = 485

chest = Image.open("images/chest.png")
chest = chest.resize((60, 45), Image.NEAREST)
chest = ImageTk.PhotoImage(chest)

scroll = Image.open("images/scroll.png")
scroll = scroll.resize((30, 30), Image.NEAREST)
scroll = ImageTk.PhotoImage(scroll)

key = Image.open("images/key.png")
key = key.resize((35, 22), Image.NEAREST)
key = ImageTk.PhotoImage(key)

pistol = Image.open("images/pistol.png")
pistol = pistol.resize((24, 20), Image.NEAREST)
pistol = ImageTk.PhotoImage(pistol)

work = Image.open("images/work.png")
work = work.resize((1520, 945), Image.NEAREST)
work = ImageTk.PhotoImage(work)
fake_screen = tk.Label(window, image=work)


configure_window()
configure_canvas()
update_timer()


window.mainloop()
