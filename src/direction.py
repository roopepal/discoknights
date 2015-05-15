# map coordinates change, direction name, and pixel movement when walking
UP = (0, -1), "up", (2, -1)
RIGHT = (1, 0), "right", (2, 1)
DOWN = (0, 1), "down", (-2, 1)
LEFT = (-1, 0), "left", (-2, -1)

def x_step(step):
    return step[0][0]

def y_step(step):
    return step[0][1]

def get_directions():
    return [UP, RIGHT, DOWN, LEFT]