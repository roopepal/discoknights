class SquareType(object):
    '''
    This class defines the types of squares on the map.
    '''
    
    def __init__(self, name, walkable):
        '''
        Creates a new square type.
        
        @param self.name: (String) The name of the square type.
        @param self.walkable: (Boolean) Whether a character walk into a square of this type.
        '''
        
        self.name = name
        self.walkable = walkable
    
    def get_name(self):
        return self.name
            
    def is_walkable(self):
        if self.walkable:
            return True
        else:
            return False
    
    def __eq__(self, obj):
        return isinstance(obj, SquareType) and obj.get_name() == self.name
    
    def __str__(self):
        self.ret = "{:5}".format(self.name)
        return self.ret