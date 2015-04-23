UP = (0, -1), "up"
RIGHT = (1, 0), "right"
DOWN = (0, 1), "down"
LEFT = (-1, 0), "left"

def x_step(step):
    return step[0]

def y_step(step):
    return step[1]

def get_directions():
    return [UP, RIGHT, DOWN, LEFT]