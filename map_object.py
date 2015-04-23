class MapObject(object):
    '''
    Defines a map object.
    '''
    
    def __init__(self, object_type):
        '''
        Creates a object on the map.
        '''
        self.type = object_type
        self.map = None
        self.location = None
        
    def added_to_map(self, current_map, location):
        '''Takes care of updating the object attributes when the object is added to a map.'''
        self.map = current_map
        self.location = location

    def __str__(self):
        return self.type.name