import pygame, sys
import math, random

pygame.init()
vec2 = pygame.math.Vector2
res = vec2(600,600)

window = pygame.display.set_mode(res)

clock = pygame.time.Clock()
dt = 1/60

def drawEllipse(a, b):
    surf = pygame.Surface((2*a, 2*b))

    surf.fill((0,0,0))
    surf.set_colorkey((0,0,0))
    pygame.draw.ellipse(surf, (200,200,200), (0,0,2*a, 2*b), 3)

    return surf

def signum(x):
    try:
        return x/abs(x)
    except:
        return 0

class Ball:
    Gravity = 900
    E = 0.8
    
    def __init__(self, pos):
        self.pos = pos 
        self.vmax = 1500
        # self.velocity = vec2(random.randint(90,190),0)
        self.velocity = vec2(0,0)

        self.stretch = 1
        self.radius = 20

        self.angle = 0

        self.touchingGround = False

    def equilibrium(self):
        self.velocity = vec2(0,0)
        self.acc = vec2(0,0)

    def stretchF(self, vel):
        return 1 + (vel.length()/self.vmax)**2

    def update(self, dt):
        self.acc = vec2(0, Ball.Gravity)

        if self.touchingGround:
            self.acc += vec2(-signum(self.velocity.x)*0.07*Ball.Gravity, 0)



        self.velocity += self.acc * dt

        if self.touchingGround:
            if abs(self.velocity.y) <= 5:
                self.velocity.y = 0
            if abs(self.velocity.x) <= 5:
                self.velocity.x = 0


        self.pos += self.velocity * dt

        self.angle = math.atan2(self.velocity.y ,self.velocity.x)

        if self.velocity.length() >= self.vmax:
            self.velocity = self.velocity.normalize()*self.vmax

        self.stretch =self.stretchF(self.velocity)

        ## collision
        if self.pos.y + self.radius >= res.y:
            self.velocity.y = -abs(self.velocity.y)*Ball.E

        if self.pos.y - self.radius <= 0:
            self.velocity.y = abs(self.velocity.y)*Ball.E

        if self.pos.x + self.radius >= res.x:
            self.velocity.x = -abs(self.velocity.x)*Ball.E
            
        if self.pos.x - self.radius <= 0:
            self.velocity.x = abs(self.velocity.x)*Ball.E

        if self.pos.y + self.radius - res.x >= 0:
            self.touchingGround = True
        else:
            self.touchingGround = False


    def isColliding(self, point):
        if (self.pos-point).length() <= self.radius:
            return 1
        return 0


        # print(self.velocity)

    def draw(self, window):
        ellipse = drawEllipse(self.radius*self.stretch,self.radius/self.stretch)        
        ellipse = pygame.transform.rotate(ellipse, -math.degrees(self.angle))

        ellipseRect = ellipse.get_rect(center=self.pos)

        window.blit(ellipse, ellipseRect)

b1 = Ball(vec2(100,20))

timeScale = 1

ballDragged = False
ballOffset = vec2(0,0)
throwVel = vec2(0,0)

while 1:
    clock.tick(100000)

    fps = clock.get_fps()
    dt = 1/fps if fps else 1/60

    dt *= timeScale
    mousePos = vec2(*pygame.mouse.get_pos())
    mouseVel = vec2(*pygame.mouse.get_rel())

    window.fill((30,30,30))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEWHEEL:
            if not ballDragged:
                if event.y > 0:
                    timeScale += 0.1
                elif event.y < 0:
                    timeScale -= 0.1
                print(timeScale)
            else:
                if event.y > 0:
                    b1.radius += 1
                elif event.y < 0:
                    b1.radius -= 0.1
                print(b1.radius)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if b1.isColliding(mousePos):
                    ballDragged = True
                    ballOffset = b1.pos - mousePos

        elif event.type == pygame.MOUSEBUTTONUP:
            
            if event.button == 1:
                if b1.isColliding(mousePos):
                    ballDragged = False
                    ballOffset = vec2(0,0)
                    
                    b1.velocity = throwVel*b1.vmax/50

    if pygame.mouse.get_pressed()[0]:
        if ballDragged:
            b1.pos = mousePos + ballOffset
            b1.equilibrium()

            if mouseVel.x or mouseVel.y:
                throwVel = mouseVel.copy()

    b1.update(dt)
    b1.draw(window)

    pygame.display.flip()