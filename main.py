import glfw
from OpenGL.GLU import *
from OpenGL.GLUT import *
from numpy import *
import glfw

from component.fuel import Fuel
from component.heart import Heart
from component.objloader import *
from component.obstacle import Obstacle, getModel
from component.texture import Texture,pass_index


camera_coordinates = {
    'x-eye': 25,
    'y-eye': 25,
    'z-eye': 0,
    'x_center': 0,
    'y_center': 0,
    'z_center': 0
}
TEXTURE_NAMES = {
    'heart': 0,
    'fuel': 1,
    'background': 21
}
spaceship_position = 0
flash = 0
speed = 3
num_of_heart = 3
state = "start"
pause = False

generate = 0
fuel_generate = 0
fuel_level = 100
gameover_flash_speed = 0
gameplay_flash_speed = 0
gamestart_flash_speed = 0

MILLISECONDS = 7

factory = {}

obstacles = Obstacle()
fuel = Fuel(texture_name=TEXTURE_NAMES['fuel'])
heart = Heart(texture_name=TEXTURE_NAMES['heart'])
background_sound = pygame.mixer.Sound("assets/sound/gameStart.mp3")
texture = Texture()


def restart():
    global camera_coordinates, spaceship_position, flash, speed, num_of_heart, state, pause, generate, fuel_generate, fuel_level, background_sound
    camera_coordinates = {
        'x-eye': 25,
        'y-eye': 25,
        'z-eye': 0,
        'x_center': 0,
        'y_center': 0,
        'z_center': 0
    }
    spaceship_position = 0
    flash = 0
    speed = 3
    num_of_heart = 3
    state = "intro"
    pause = False
    generate = 0
    fuel_generate = 0
    fuel_level = 100
    background_sound = pygame.mixer.Sound("assets/sound/gamePlay.mp3.mp3")


#########################################################################
def projection_ortho(z_near=-200):
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, z_near, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init_my_scene(width, height):
    lighting()
    glClearColor(0, 0 , 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, float(width) / float(height), 20, 300.0)
    glMatrixMode(GL_MODELVIEW)


#########################################################################
def background_draw():
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1)
    glVertex(-1, 1)

    glTexCoord2f(0, 0)
    glVertex(-1, -1)

    glTexCoord2f(1, 0)
    glVertex(1, -1)

    glTexCoord2f(1, 1)
    glVertex(1, 1)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, -1)


#########################################################################

def draw_screen():
    global state, score, gameover_flash_speed, gamestart_flash_speed,gameplay_flash_speed
    glPushMatrix()
    glColor(1, 1, 1)
    projection_ortho(-220)

    if state == "start":
        gamestart_flash_speed += 1
        gamestart_index = gamestart_flash_speed // 12
        pass_index(gamestart_index, "gamestart")
        glBindTexture(GL_TEXTURE_2D, 2 + gamestart_index % 19 )
    elif state == "gameOver":
        gameover_flash_speed += 1
        gameover_index = gameover_flash_speed // 19
        pass_index(gameover_index, "gameover")
        glBindTexture(GL_TEXTURE_2D, 2 + 20 + 1 + gameover_index % 39) 
        background_sound.stop()
    else:
        glBindTexture(GL_TEXTURE_2D, TEXTURE_NAMES['background'])
    background_draw()
    if state == "gameOver":
        
        final_score = score/10
        draw_text(f"YOUR SCORE: {int(final_score)}", -.4, .5, 6, 5)
    projection_ortho()
    if state == "3" or state == "5":
        for i in range(num_of_heart):
            glPushMatrix()
            glTranslate(-0.85, 0.85, 0)
            glTranslate(i * .15, 0, 0)
            glScale(0.08, 0.08, 0)
            heart.heart_draw()
            glPopMatrix()
        glBindTexture(GL_TEXTURE_2D, -1)
        state = fuel.fuel_level_bar(fuel_level, state)
        score = (generate // 100) * 100
        final_score = score /10
        draw_text(f"SCORE: {int(final_score)}", -.9, .7)
        draw_text("press P to pause ", -.9, .6, 4)

    init_my_scene(1500, 900)
    glPopMatrix()


#########################################################################

def lighting():
    LightPos = [0, 10, 5, 1]
    LightAmb = [0, 0, 0, 0]
    LightDiff = [1, 1, 1, 1]
    LightSpec = [0.03, 0.03, 0.04, 1.0]

    MatAmbF = [1, 1, 1, 1]
    MatDifF = [1, 1, 1, 1]
    MatSpecF = [0.1, 0.1, 0.1, 1]
    MatShnF = [30]
    #####################################################################################
    glLightfv(GL_LIGHT0, GL_POSITION, LightPos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, LightAmb)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, LightDiff)
    glLightfv(GL_LIGHT0, GL_SPECULAR, LightSpec)

    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

    glMaterialfv(GL_FRONT, GL_AMBIENT, MatAmbF)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, MatDifF)
    glMaterialfv(GL_FRONT, GL_SPECULAR, MatSpecF)
    glMaterialfv(GL_FRONT, GL_SHININESS, MatShnF)


#########################################################################
def draw_vehicle():
    global spaceship_position
    # fire tail outer oval
    glPushMatrix()
    glColor(0.0784, 0.4235, 0.580)
    glTranslate(spaceship_position - 0.5, -0.1, abs(spaceship_position / 6) - 5.5)
    glRotate(5 * spaceship_position, 0, 0, 1)
    glScale(0.5, 0.5, 2)
    glutSolidSphere(0.8, 30, 30)
    glTranslate(2, 0, 0)
    glutSolidSphere(0.8, 30, 30)
    glPopMatrix()
    # fire tail inner oval
    glPushMatrix()
    glColor(0.098, 0.6549, 0.8078)
    glTranslate(spaceship_position - 0.5, 0.1, abs(spaceship_position / 6) - 5.5)
    glRotate(5 * spaceship_position, 0, 0, 1)
    glScale(0.2, 0.45, 1.7)
    glutSolidSphere(0.8, 30, 30)
    glTranslate(5, 0, 0)
    glutSolidSphere(0.8, 30, 30)
    glPopMatrix()
    # spaceship body
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glPushMatrix()
    glTranslate(spaceship_position, 0, abs(spaceship_position / 6))
    glRotate(5 * spaceship_position, 0, 0, 1)
    glScale(.6, .6, .7)
    getModel("models/Jet_01.obj").render()
    glPopMatrix()
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)


#########################################################################
def draw_text(string, x=0.0, y=0.0, size=5.0, size_line=2):
    glPushMatrix()
    projection_ortho()
    glLineWidth(size_line)
    glColor(1, 1, 1)
    glTranslate(x, y, 0)
    glScale(size / 10000, size / 10000, 1)
    string = string.encode()
    for c in string:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, c)
    init_my_scene(1000, 900)
    glPopMatrix()


#########################################################################
def switch():
    global state
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    draw_screen()

    if not num_of_heart:
        state = "gameOver"
    if pause:
        draw_text("press R to continue ", -.3, 0, 6)
        glutSwapBuffers()
    if (state == 'intro' or state == "3" or state == "5") and pause == False:
        game()
    if not pause:
        glutSwapBuffers()


#########################################################################
def camera_setup():
    global camera_coordinates, state
    if state == 'intro':
        if camera_coordinates['x-eye'] >= 0:
            camera_coordinates['x-eye'] -= 0.1
            camera_coordinates['z-eye'] -= 0.1
            camera_coordinates['y_center'] += 11 / 250
        if camera_coordinates['x-eye'] <= 0:
            state = '3'
    if state == "5":
        if camera_coordinates['y-eye'] < 50:
            camera_coordinates['y-eye'] += 0.5
            camera_coordinates['z-eye'] -= 0.5
            camera_coordinates['y_center'] -= 3 / 50
            camera_coordinates['z_center'] += 0.7

    gluLookAt(camera_coordinates['x-eye'], camera_coordinates['y-eye'], camera_coordinates['z-eye'],
              camera_coordinates['x_center'], camera_coordinates['y_center'], camera_coordinates['z_center'],
              0, 1, 0)


def game():
    global generate, fuel_generate, fuel_level, speed, state, camera_coordinates, num_of_heart, flash, score  # variables

    camera_setup()

    if state != 'intro':
        if generate % 120 == 0:
            speed = obstacles.generate_obstacle(num_of_rail=int(state), speed=speed)
        obstacles.draw_obstacles(speed=speed)
        num_of_heart, flash = obstacles.collision_detection(space_ship_position=spaceship_position,
                                                            num_of_heart=num_of_heart, speed=speed,
                                                            state=state, flash=flash)

        if generate % 1920 == 0:
            heart.generate_new_heart(num_of_rail=int(state), obstacles_x=obstacles.obstacle_x[-1], fuel_x=fuel.fuel_x)
        heart.draw_old_heart(speed)
        num_of_heart = heart.collision_detection(space_ship_position=spaceship_position, num_of_heart=num_of_heart,
                                                 speed=speed, )

        if 50 >= fuel_level >= 20 and not len(fuel.fuel_x):
            fuel.generate_new_fuel(num_of_rail=int(state), obstacles_x=obstacles.obstacle_x[-1])
        fuel.draw_old_fuel(speed=speed)
        fuel_level = fuel.collision_detection(space_ship_position=spaceship_position, fuel_level=fuel_level,
                                              speed=speed)

        if flash:
            flash -= 1
        if flash % 15 == 0:
            draw_vehicle()

        if speed < 3:
            STEP = 3
        else:
            STEP = 4
        if generate >= 4000 and state == "3":
            state = "5"
        generate += STEP
        fuel_generate += STEP
        fuel_level -= 0.2
    else:
        draw_vehicle()


#########################################################################
def keyboard_callback(key, x, y):
    global state, pause, background_sound, num_of_heart, fuel_level
    if key == b'\r' and state == "start":
        state = 'intro'
        background_sound.stop()
        background_sound = pygame.mixer.Sound(
            "assets/sound/gamePlay.mp3")
        background_sound.play(-1)
    if key == b'p':
        pause = True
    if key == b'r':
        pause = False
    if key == b'\r' and state == 'gameOver':
        restart()
        background_sound.play(-1)


def mouse_callback(x, y):
    global spaceship_position, state
    if state == "3" or state == "5":
        spaceship_position = (-x + 750) / 45
        if spaceship_position > 8 and state == '3':
            spaceship_position = 8
        elif spaceship_position < -8 and state == '3':
            spaceship_position = -8

        if spaceship_position > 16 and state == '5':
            spaceship_position = 16
        elif spaceship_position < -16 and state == '5':
            spaceship_position = -16


#########################################################################
def anim_timer(v):
    switch()
    glutTimerFunc(MILLISECONDS, anim_timer, v + 1)


def main():
    global background_sound
    glutInit(sys.argv)
    pygame.init()
    glfw.init()
    background_sound.play(-1)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1500, 900)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Race The Sun !")
    glutDisplayFunc(switch)
    glutTimerFunc(MILLISECONDS, anim_timer, 1)
    texture.init_textures()
    glutKeyboardFunc(keyboard_callback)
    glutPassiveMotionFunc(mouse_callback)
    init_my_scene(1500, 900)
    glutMainLoop()


main()
