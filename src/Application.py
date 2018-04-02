import pygame, sys, time, os, random, math

pygame.init()
FPS = 60
width, height = 640, 480
pygame.init()
width,height = 640,480
os.environ['SDL_VIDEO_CENTERED'] = 'l'
pygame.display.set_caption('Universe Sim')
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

GRAVITATIONAL_CONSTANT = 66.7

class Vector2:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    #Math functions
    def add(self, x, y):
        self.x += x
        self.y += y
    def subtract(self, x, y):
        self.x -= x
        self.y -= y
    def multiply(self, x, y):
        self.x *= x
        self.y *= y
    def divide(self, x, y):
        self.x /= x
        self.y /= y

    #Getters and setters
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y
    def setVect(self, x, y):
        self.x = x
        self.y = y

class Entity:

    def __init__(self, x, y, mass, velocity):
        self.x = x
        self.y = y
        self.drawX = 0
        self.drawY = 0
        self.mass = mass
        self.radius = math.sqrt(math.pi*self.mass)/50
        self.netForce = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.velocity = velocity
        self.points = list()
        self.randomColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def isVisible(self):
        if(self.drawX < 0 or self.drawX > width) or (self.drawY < 0 or self.drawY > height):
            return False
        return True

    def calculateRadius(self, mass):
        self.radius = math.sqrt(math.pi*mass)/50

    def addPoints(self):
        if(len(self.points) > 100):
            self.points.remove(self.points.__getitem__(0))
        self.points.append((self.x,self.y))

    def combine(self, e):
        self.velocity.multiply(self.mass, self.mass)
        e.getVelocity().multiply(e.getMass(), e.getMass())
        self.velocity.add(e.getVelocity().getX(), e.getVelocity().getY())
        self.velocity.divide(self.mass+e.getMass(), self.mass+e.getMass())

        self.mass = self.mass+e.getMass()
        self.calculateRadius(self.mass)

    def calculateAttraction(self):
        distance, diffX, diffY, distance3 = 0.0, 0.0, 0.0, 0.0
        gravForce = Vector2(0, 0)

        for e in entities:
            if(e == self):
                continue
            diffX = e.getX() - self.x
            diffY = e.getY() - self.y
            distance = math.sqrt(math.pow(diffX, 2)+math.pow(diffY, 2))
            if(distance-(self.getRadius()+e.getRadius())<=2):
                if(self.mass >= e.getMass()):
                    self.combine(e)
                    entities.remove(e)
                else:
                    e.combine(self)
                    entities.remove(self)
            distance3 = distance * distance * distance
            if(distance3 != 0):
                gravForce.add((e.getMass()*diffX) / distance3, (e.getMass()*diffY) / distance3)

        gravForce.multiply(GRAVITATIONAL_CONSTANT, GRAVITATIONAL_CONSTANT)

        self.netForce = gravForce
        self.applyAttractionVector()

    def applyAttractionVector(self):
        self.acceleration.setVect((self.netForce.getX()/self.mass), (self.netForce.getY()/self.mass))
        self.velocity.add(self.acceleration.getX(), self.acceleration.getY())
        self.x += self.velocity.getX()
        self.y += self.velocity.getY()

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getMass(self):
        return self.mass
    def getRadius(self):
        return self.radius
    def getVelocity(self):
        return self.velocity
    def setVelocity(self, velocity):
        self.velocity = velocity

    def drawTail(self):
        for i in range(len(self.points)):
            if(i != 0):
                drawX1 = (self.points.__getitem__(i)[0]-camera.getXOffset()) / camera.getZoomLevel()
                drawY1 = (self.points.__getitem__(i)[1]-camera.getYOffset()) / camera.getZoomLevel()
                drawX2 = (self.points.__getitem__(i-1)[0] - camera.getXOffset()) / camera.getZoomLevel()
                drawY2 = (self.points.__getitem__(i-1)[1] - camera.getYOffset()) / camera.getZoomLevel()
                if ((drawX1 < 0.0 or drawX1 > width) or (drawY1 < 0 or drawY1 > height)):
                    continue
                else:
                    pygame.draw.line(screen, self.randomColor, (drawX1, drawY1), (drawX2, drawY2), 1)

    def tick(self):
        self.drawX = (self.x - camera.getXOffset()) / camera.getZoomLevel()
        self.drawY = (self.y - camera.getYOffset()) / camera.getZoomLevel()
        self.calculateAttraction()
        self.addPoints()

    def render(self):
        self.drawTail()
        zoomRadius = (int)(self.radius / camera.getZoomLevel())
        pygame.draw.circle(screen, self.randomColor, (int(self.drawX), int(self.drawY)), zoomRadius, 0)

class Camera:

    def __init__(self):
        self.xOffset = 0.0
        self.yOffset = 0.0
        self.zoomLevel = 1
        self.ZOOM_MIN = 1
        self.ZOOM_MAX = 100

    def move(self, xAmt, yAmt):
        self.xOffset += xAmt * self.zoomLevel
        self.yOffset += yAmt * self.zoomLevel

    def zoomIn(self):
        if(self.zoomLevel > self.ZOOM_MIN):
            self.xOffset += (float)(width/2.0)
            self.yOffset += (float)(width/2.0)
            self.zoomLevel-=1

    def zoomOut(self):
        if(self.zoomLevel < self.ZOOM_MAX):
            self.xOffset -= (float)(width/2.0)
            self.yOffset -= (float)(width/2.0)
            self.zoomLevel+=1

    def getXOffset(self):
        return self.xOffset
    def getYOffset(self):
        return self.yOffset
    def getZoomLevel(self):
        return self.zoomLevel
    def setPosition(self, x, y):
        self.xOffset = x
        self.yOffset = y

class Controller:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.cX = 0
        self.cY = 0
        self.drawX = 0
        self.drawY = 0
        self.entityMass = 100000
        self.holding = False
        self.placingEntity = False

    def makeEntity(self):
        self.cX = (self.cX + camera.getXOffset() / camera.getZoomLevel()) * camera.getZoomLevel()
        self.cY = (self.cY + camera.getYOffset() / camera.getZoomLevel()) * camera.getZoomLevel()
        initialVelocity = Vector2((self.x - self.cX)/20, (self.y - self.cY)/20)
        e = Entity(self.cX, self.cY, self.entityMass, initialVelocity)
        entities.append(e)
        self.entityMass = 100000
        self.placingEntity = False

    def getInput(self):
        keys = pygame.key.get_pressed()
        self.drawX, self.drawY = pygame.mouse.get_pos()
        self.x = (self.drawX + camera.getXOffset() / camera.getZoomLevel()) * camera.getZoomLevel()
        self.y = (self.drawY + camera.getYOffset() / camera.getZoomLevel()) * camera.getZoomLevel()

        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                sys.exit()
            if(event.type == pygame.MOUSEBUTTONDOWN):
                if(event.button == 1):
                    self.cX, self.cY = pygame.mouse.get_pos()
                    self.placingEntity = True
                if(event.button == 4):
                    camera.zoomIn()
                if (event.button == 5):
                    camera.zoomOut()
            if(event.type == pygame.KEYDOWN):
                #toggleable buttons
                if(event.key == pygame.K_r):
                    entities.clear()
        #held buttons
        if(pygame.mouse.get_pressed()[0]):
            self.holding = True
        else:
            self.holding = False
        if (keys[pygame.K_w]):
            camera.move(0, -2)
        if (keys[pygame.K_a]):
            camera.move(-2, 0)
        if (keys[pygame.K_s]):
            camera.move(0, 2)
        if (keys[pygame.K_d]):
            camera.move(2, 0)

        if(self.holding):
            self.placingEntity = True
        if(self.placingEntity):
            if(self.holding):
                self.entityMass += self.entityMass*.05
            else:
                self.makeEntity()

    def drawPlacementUI(self):
        if(self.placingEntity):
            radius = int((math.sqrt(math.pi * self.entityMass) /50) / camera.getZoomLevel())
            if(radius >= 1):
                pygame.draw.circle(screen, (255, 255, 255), (int(self.cX), int(self.cY)), radius, 1)
            pygame.draw.line(screen, (255,255,255), (self.cX, self.cY), (self.drawX, self.drawY), 1)

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y

    def tick(self):
        self.getInput()

    def render(self):
        self.drawPlacementUI()
        pygame.draw.circle(screen, (255, 0, 0), (int(self.drawX), int(self.drawY)), 5, 1)

entities = list()
camera = Camera()
controller = Controller()

#Main game loop
while True:
    #Handle the events
    #Do computations and render stuff on screen
    #Controller handles events
    controller.tick()
    for e in entities:
         e.tick()
    #radius = random.randint(100,200)

    screen.fill((0, 0, 0))

    for e in entities:
        if(e.isVisible()):
            e.render()
    controller.render()

    pygame.display.flip()

    clock.tick_busy_loop(FPS)