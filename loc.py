#--------------------------------------------------------------------------------
#
#       Object permanence
#       Russell Hunter
#
#--------------------------------------------------------------------------------
#
#   NOTES:
#
#   The goal:
#   Keep track of objects
#   how will I do this? 
#   
#   List of points? 
#   Make a point cloud from incoming data then turn it into objects
#   take heading, and then item distance to plot point in map (discard point if near another point (grid or quad tree???))
#
#   then like use a blur and threshold
#   and get centroid of that shape to determine the objects location
#
#   so maybe I actually do this in an image
#   and have a list of objects in known locations or that can be dynamically updated.
#
#   in github I see an alogrithm that works on a csv file? can be ouptutted to a csv though 
#       I do not think a* is the move since it will take the shortest route  and tends to hug walls
#       which is not ideal. maybe add buffer idk not my expertise
#
#   Side note:
#   Currently using pygame for all image manipulation but this should be rewritten to use PIL. I'm not familiar with it and this is just a proof of concept
#


import pygame, math, pygame.gfxdraw, pygame.transform

#world will have the location which is the base gps coords (unsure how this will go as of now), 
# a size which is the size of the image in pixels where each pixel will be some defined scale (maybe 10 cm?)
# and a lists of points of interest which will be updated when the world gets updated (image blur threshold centroid thing)
class World:
    def __init__(self, size):
        self.size = size
        self.location = [0, 0]
        self.world = pygame.Surface(size)
        self.world.fill((0, 0, 0, 1))
        self.poi = []
        self.scale = 10
        self.threshold_percentage = 128
    def updateWorld(self, rays, position, heading):
        #this should be changed as of now this is assuming that rays is a list of 360 values representing depth in meters at angle i
        #pygame.gfxdraw.pixel(self.world, position[0], position[1], (255, 255, 255))
        for i in range(360):
            pygame.gfxdraw.pixel(self.world, int(position[0] + self.scale * rays[i] * math.cos(math.radians(i))), int(position[1] + self.scale * rays[i] * math.sin(math.radians(i))), (255, 255, 255))
        
        
        intermediateSurface = pygame.Surface((20, 20))
        blurredSurface = pygame.Surface(self.size)
        #this is a bad (but fast) way of blurring but I wish to implement a better blur in combination with the threshold. I think the goal is to reimplement using PIL and or numpy. 
        pygame.transform.scale(self.world, (20, 20), intermediateSurface)
        pygame.transform.scale(intermediateSurface, self.size, blurredSurface)
        #pygame.transform.threshold(blurredSurface, self.world, (255, 255, 255, 1), threshold=(128, 128, 128, .5), set_color=(255, 255, 255, 1), set_behavior=1, search_surf=None, inverse_set=True) 
        pygame.image.save(self.world, "C:\\Users\\Russell\\Documents\\Coding\\python\\iceberg\\Keeping track of location stuff\\out.bmp")
        pygame.image.save(blurredSurface, "C:\\Users\\Russell\\Documents\\Coding\\python\\iceberg\\Keeping track of location stuff\\blur.bmp")
        
        pass


pos = (100, 100)
world = World(pos)
eyes = []
for i in range(360):
    eyes.append(1)
world.updateWorld(eyes, [50, 50], 0)

