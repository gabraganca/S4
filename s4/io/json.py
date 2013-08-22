"""
Created on Thu Aug 22 17:09:57 2013

@author: gbra
"""
import json

class JSON:
    """JSON handling"""
    
    def __init__(self, filename, dic = {}):
        self.file = filename
        self.dic = dic
    
    def save(self):
        """Save file in JSON format"""
        with open(self.file, 'w') as f:
            json.dump(self.dic, f, sort_keys = True, indent = 4, 
                      separators=(',', ':'))        
    
    def load(self):
        """Load a JSON file into a dictionary"""
        self.dic =  json.load(open(self.file))
