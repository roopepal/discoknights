from direction import x_step, y_step, get_directions

class Coordinates(object):
    '''
    This class defines a simple coordinate pair: x, y.
    '''
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_neighbor(self, direction):
        return Coordinates(self.x + x_step(direction), self.y + y_step(direction))
    
    def get_neighbors(self):
        return [ self.get_neighbor(direction) for direction in get_directions() ]
    
    def __eq__(self, obj):
        return self.x == obj.get_x() and self.y == obj.get_y()
    
    def __str__(self):
        return "({:}, {:})".format(self.x,self.y)