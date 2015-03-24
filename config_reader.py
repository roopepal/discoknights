from map import Map
from squaretype import SquareType

class ConfigReader(object):
    
    def read_map_config(self, input):
        
        self.config = []
        self.current_line = ''
        self.line_count = 0
        self.block_index = -1
        
        def nl():
            self.current_line = input.readline().strip()
            self.line_count += 1
            #for i in range(len(self.config)):
            #    print("config: {:}".format(self.config[i]))
            #print("line read: {:}".format(self.current_line))

                    
        #try:

        self.lines_in_file = 0
        for line in input:
            self.lines_in_file += 1
        
        input.seek(0)   
        
        nl()
        
        #header_parts = self.current_line.split()
        
        '''
        if header_parts[0] != "DISCO":
            # raise error
            print()
        if header_parts[1] != "KNIGHTS":
            # raise error
        if header_parts[2].strip().lower() != 'config':
            # raise error
        '''
                    
        while self.line_count <= self.lines_in_file:                
            
            if not self.current_line.startswith('#'): 
                nl()
            
            if self.current_line == '' or self.current_line.startswith("//"):
                continue
            
            self.config.append({'id' : self.current_line.strip("#")})
            self.block_index += 1
            nl()
            
            while not self.current_line.startswith('#') and self.line_count <= self.lines_in_file:
                if self.current_line == '' or self.current_line.startswith("//"):
                    nl()
                elif ":" in self.current_line:
                    line_parts = self.current_line.split(":")

                    if line_parts[0] == "squares":
                        self.config[self.block_index][line_parts[0]] = []
                        nl()
                        while not "}" in self.current_line:
                            self.config[self.block_index][line_parts[0]].append(self.current_line.split())
                            nl()
                        nl()
                    
                    else:
                        self.config[self.block_index][line_parts[0]] = line_parts[1].strip()
                        nl()
                        
        return self.config
        
        #except:
            #print("There was an error.")
    
    def map_from_config(self, config):
        
        m = Map()
        
        for item in config:
            if item["id"].lower() == "squaretype":
                print("Building squaretype '{:}'...".format(item["name"]))
                m.add_squaretype( SquareType( item["name"], item["short"], (item["walkable"].lower() in ["true"]), item["sprite"] ) )
                
            elif item["id"].lower() == "map":
                print("Building map...")
                m.build_map(int( item["height"] ), int( item["width"] ), item["squares"])
        
        print("Map built successfully.")
        return m