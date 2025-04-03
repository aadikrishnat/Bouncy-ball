import pygame, sys
import math, random

pygame.init()
vec2 = pygame.math.Vector2
res = vec2(600,600)

window = pygame.display.set_mode(res)

clock = pygame.time.Clock()
dt = 1/60

def drawEllipse(a, b, fillColor=(30,30,30), outlineColor=(200,200,200)):
    surf = pygame.Surface((2*a, 2*b))

    surf.fill((1,1,1))
    surf.set_colorkey((1,1,1))
    pygame.draw.ellipse(surf, fillColor, (0,0,2*a, 2*b))
    pygame.draw.ellipse(surf, outlineColor, (0,0,2*a, 2*b), 3)

    return surf

def randDirection():
    return vec2(random.randint(-100,100), random.randint(-100,100)).normalize()

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
        self.radius = 35

        self.angle = 0

        self.touchingGround = False

        self.trail = []
        # self.maxTrailLength = 150
        self.trailFactor = 700

        self.highlighted = False

    def equilibrium(self):
        self.velocity = vec2(0,0)
        self.acc = vec2(0,0)

    def stretchF(self, vel):
        return 1 + (vel.length()/self.vmax)**2

    def update(self, dt, particleSys:"Particles"):
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

        self.stretch = self.stretchF(self.velocity)

        ## collision
        f = int(60*self.velocity.length()/self.vmax)

        if self.velocity.x or self.velocity.y:
            if self.pos.y + self.radius >= res.y:
                self.velocity.y = -abs(self.velocity.y)*Ball.E

                if self.velocity.y:
                    particleSys.create(self.pos + vec2(0,self.radius-3), vec2(0,-1), 45, f)


            if self.pos.y - self.radius <= 0:
                self.velocity.y = abs(self.velocity.y)*Ball.E
                # if self.velocity.y:
                #     particleSys.create(self.pos, vec2(0,1), 45, f)

            if self.pos.x + self.radius >= res.x:
                self.velocity.x = -abs(self.velocity.x)*Ball.E
                # if self.velocity.x:
                #     particleSys.create(self.pos, vec2(-1, 0), 45, f)

                
            if self.pos.x - self.radius <= 0:
                self.velocity.x = abs(self.velocity.x)*Ball.E
                # if self.velocity.x:
                #     particleSys.create(self.pos, vec2(1, 0), 45, f)

        if self.pos.y + self.radius - res.x >= 0:
            self.touchingGround = True
        else:
            self.touchingGround = False

        self.maxTrailLength = self.trailFactor*(self.velocity.length()/self.vmax)**2

        self.trail.append(self.pos.copy())
        if len(self.trail) >= self.maxTrailLength:
            self.trail.pop(0)


    def isColliding(self, point):
        if (self.pos-point).length() <= self.radius:
            return 1
        return 0


    def draw(self, window):

        for i in range(len(self.trail)):
            pos = self.trail[i]
            rad = (self.radius/self.stretch)*i/(len(self.trail))

            if self.highlighted:
                pygame.draw.circle(window, (150,150,150), pos, rad)
            else:
                pygame.draw.circle(window, (200,200,200), pos, rad)

        ## drawing the ball
        if self.highlighted:
            ellipse = drawEllipse(self.radius*self.stretch,self.radius/self.stretch, fillColor=(100,100,100))
        else:        
            ellipse = drawEllipse(self.radius*self.stretch,self.radius/self.stretch)

        ellipse = pygame.transform.rotate(ellipse, -math.degrees(self.angle))

        ellipseRect = ellipse.get_rect(center=self.pos)

        window.blit(ellipse, ellipseRect)

class Particles:
    class Particle:
        def __init__(self, pos, normal:vec2, angle):
            self.pos = pos
            self.velocity = normal.rotate(random.randint(-angle, angle))*random.randint(150,200)

            self.gravity = -normal.copy()*950

            self.color = pygame.Color.from_hsla((random.randint(0,360), 100, 99, 100))

            self.radius = 3

            self.dec = 2

        def update(self, dt):
            self.velocity += self.gravity * dt

            self.pos += self.velocity * dt

            self.radius -= self.dec * dt

        def draw(self, window):
            pygame.draw.circle(window, self.color, self.pos, self.radius)


    def __init__(self):
        
        self.particles = []

    def create(self, pos, normal, angle, num):
        self.startPos = pos
        for _ in range(num):
            self.particles.append(self.Particle(self.startPos.copy(), normal, angle))

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)

            if particle.radius <= 0:
                self.particles.remove(particle)
            if particle.pos.x <= 0 or particle.pos.x >= res.x:
                self.particles.remove(particle)   
            if particle.pos.y <= 0 or particle.pos.y >= res.y:
                self.particles.remove(particle)

    def draw(self, window):
        for particle in self.particles:
            particle.draw(window)
            


ball = Ball(vec2(res//2-vec2(0,50)))

particleSys = Particles()

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
                    ball.radius += 1
                elif event.y < 0:
                    ball.radius -= 0.1
                print(ball.radius)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if ball.isColliding(mousePos):
                    ballDragged = True
                    ballOffset = ball.pos - mousePos
                    ball.highlighted = True
                    particleSys.create(mousePos, vec2(0,-1), 180, 60)
                # else:
                #     p.create(mousePos, vec2(0,-1), 30)
                #     print(len(p.particles))

        elif event.type == pygame.MOUSEBUTTONUP:
            
            if event.button == 1:
                if ballDragged:
                    ballDragged = False
                    ballOffset = vec2(0,0)
                    
                    ball.velocity = throwVel*ball.vmax/50
                    ball.highlighted = False

    if pygame.mouse.get_pressed()[0]:
        
        if ballDragged:
            ball.pos = mousePos + ballOffset
            ball.equilibrium()

            if mouseVel.x or mouseVel.y:
                throwVel = mouseVel.copy()

    particleSys.update(dt)
    particleSys.draw(window)

    ball.update(dt, particleSys)
    ball.draw(window)



    pygame.display.flip()