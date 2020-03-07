'''
Created on 21.04.2018

@author: reijo.korhonen@gmail.com
'''




class View():
    
    START=0
    CONTINUE=1
    STOP=2
    
    # View.START cant be used in init
    def __init__(self, id, file_path):
        self.id=id
        self.file_path=file_path
        
    def get_id(self):
        return self.id
    def set_id(self, id):
        self.id = id
        
    def get_file_path(self):
        return self.file_path
    def set_file_path(self, file_path):
        self.file_path = file_path        
  