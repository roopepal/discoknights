UP = (0, -1)
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)

def x_step(step):
    return step[0]

def y_step(step):
    return step[1]

def get_directions():
    return [UP, RIGHT, DOWN, LEFT]