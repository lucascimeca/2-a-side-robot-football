class Object:
    def __init__(self,x,y,size,direction,magnitude):
        self.x          = x
        self.y          = y
        self.size       = size
        self.direction  = direction
        # sum of x and y components since last frame
        self.magnitude  = magnitude
