import math
import pygame

# this parameter indicate a step which will be used as a dt in calculation of new position
STEP = 25
# internal FPS timer in pygame
clock = pygame.time.Clock()
# width and height of
WIDTH = 1000
HEIGHT = 1000

BIG_WIDTH = 500
BIG_HEIGHT = 500

SMALL_WIDTH = 100
SMALL_HEIGHT = 100

DIAMETER = 150
RADIUS = DIAMETER // 2
SMALL_RECT_COLOR = (0, 255, 0)
CIRCLE_COLOR = (0, 0, 255)


# parameter are circle center coords. and rectangle coords, also circle radius
def circle_rectangle_collision(cx, cy, rx, ry, rw, rh, cr):
    edgeX = cx
    edgeY = cy
    # check which side of rectangle is closest to circle
    if cx < rx:
        # left edge
        edgeX = rx
    elif cx >= (rx + rw):
        # right edge
        edgeX = rx + rw
    if cy < ry:
        # top edge
        edgeY = ry
    elif cy > (ry + rh):
        edgeY = ry + rh

    # calculate distance on X-axis and Y-axis, between circle center and closest edge of rectangle
    distX = edgeX - cx
    distY = edgeY - cy
    # use Pythagorean Theorem to get distance(this is why abs was not used at previous lines)
    dist = math.sqrt(distX * distX + distY * distY)

    if dist <= cr:
        return True
    else:
        return False


# verify if second rectangle is inside first_one
def is_inside_rectangle(r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h):
    if (r1x < r2x) and (r1y < r2y) and (r1w + r1x > r2w + r2x) and (r1h + r1y > r2h + r2y):
        return True
    return False


# verify if a circle is inside a rectangle, and check type of collision
# 1-Right collision 2- Bottom Collision
def is_inside_circle(cx, cy, cr, rx, ry, rw, rh):
    if (cx + cr) < (rx + rw) and (cx - cr) > rx and (cy - cr) > ry:
        if (cy + cr) < (ry + rh):
            return True, 1
        else:
            return False, 2
    return False, 1


if __name__ == '__main__':
    pygame.init()
    # get ready principal display section
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    rect1 = pygame.Rect(0, 0, BIG_WIDTH, BIG_HEIGHT)
    # set big rectangle to the center of screen
    rect1.center = (WIDTH / 2, HEIGHT / 2)
    pygame.draw.rect(surface, (255, 255, 255), rect1)
    # draw second rectangle (the small one)
    rect2 = pygame.Rect(STEP, STEP, SMALL_WIDTH, SMALL_HEIGHT)
    rect2.center = (rect1.centerx - (rect1.centerx - SMALL_WIDTH - STEP) / 2,
                    rect1.centery - (rect1.centery - SMALL_HEIGHT - STEP) / 2)
    pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
    # draw circle
    cirle1 = pygame.draw.circle(surface, CIRCLE_COLOR,
                                (rect1.centerx - (rect1.centerx - STEP) / 2 + RADIUS,
                                 rect1.centery - (rect1.centery - STEP) / 2 + RADIUS), RADIUS)

    pygame.display.flip()
    run = True
    while run:

        # check if small rectangle is on last position in  big rectangle(right-bottom corner)
        if rect2.centerx < int(rect1.centerx + (rect1.centerx - STEP - SMALL_WIDTH) / 2) or \
                rect2.centery < int(rect1.centery + (rect1.centery - STEP - SMALL_HEIGHT) / 2):
            # check if circle is inside in  big rectangle(right-bottom corner)
            if cirle1.centerx < int(rect1.centerx + (rect1.centerx - STEP) / 2 - RADIUS) or \
                    cirle1.centery < int(rect1.centery + (rect1.centery - STEP) / 2 - RADIUS):

                # 1 Check if small rectangle have collision with bigger one

                if is_inside_rectangle(rect1.x, rect1.y, rect1.w, rect1.h, rect2.x, rect2.y, rect2.w, rect2.h):
                    # 2. Validate circle position inside big rectangle
                    if is_inside_circle(cirle1.centerx, cirle1.centery, RADIUS, rect1.x, rect1.y, rect1.w,
                                        rect1.h)[0]:

                        # 3. Validate rectangle/circle collision
                        if circle_rectangle_collision(cirle1.centerx, cirle1.centery, rect2.x, rect2.y, rect2.w,
                                                      rect2.h, RADIUS):
                            # 4. We are free to move circle as here is collision
                            cirle1.centerx += STEP
                            pygame.draw.circle(surface, CIRCLE_COLOR, cirle1.center, RADIUS)
                            pygame.display.update()
                            # this position is one invalid so clear surface in RED
                            surface.fill((255, 0, 0))
                            pygame.draw.rect(surface, (255, 255, 255), rect1)
                            pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
                            print("Still Colision")
                        else:
                            # 5. No collision so we move circle until last position and after move small rectangle.
                            # if for y-axis we are on last row with circle
                            if cirle1.centery == int(rect1.centery + (rect1.centery - STEP) / 2 - RADIUS):
                                # if we overlapp on next move circle outside
                                if (cirle1.centerx + STEP) >= \
                                        int(rect1.centerx + (rect1.centerx - STEP) / 2 - RADIUS):
                                    # move circle at beginning, and move one step small rectangle
                                    cirle1.center = (rect1.centerx - (rect1.centerx - STEP) / 2 + RADIUS,
                                                     rect1.centery - (rect1.centery - STEP) / 2 + RADIUS)
                                    rect2.centerx += STEP
                                    if rect2.centerx + STEP >= int(rect1.centerx +
                                                                   (rect1.centerx - STEP - SMALL_HEIGHT) / 2):
                                        surface.fill((255, 0, 0))
                                    pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
                                    pygame.draw.circle(surface, CIRCLE_COLOR, cirle1.center, RADIUS)
                                    pygame.display.update()
                            # not on last row, so move circle on x-axis
                            # verify if here is circle outside, big triangle, after incrementation
                            cirle1.centerx += STEP
                            if cirle1.centerx < int(rect1.centerx + (rect1.centerx - STEP) / 2 - RADIUS):
                                pygame.draw.circle(surface, CIRCLE_COLOR, cirle1.center, RADIUS)
                                pygame.display.update()
                                surface.fill((0, 0, 0))
                                print("No Colision")
                            else:
                                # invalid position
                                surface.fill((255, 0, 0))
                            pygame.draw.rect(surface, (255, 255, 255), rect1)
                            pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
                    # circle is outside big rectangle
                    else:

                        # must decide if there was a right edge collision or a bottom edge one
                        if (is_inside_circle(cirle1.centerx, cirle1.centery, RADIUS, rect1.x, rect1.y, rect1.w,
                                             rect1.h)[1] == 1):

                            cirle1.centery += STEP
                            cirle1.centerx = rect1.centerx - (rect1.centerx - STEP) / 2 + RADIUS
                            print("Collision Circle-Rectangle Right")
                        elif (is_inside_circle(cirle1.centerx, cirle1.centery, RADIUS, rect1.x, rect1.y, rect1.w,
                                               rect1.h)[1] == 2):
                            print("Collision Circle-Rectangle Bottom")
                            cirle1.center = (rect1.centerx - (rect1.centerx - STEP) / 2 + RADIUS,
                                             rect1.centery - (rect1.centery - STEP) / 2 + RADIUS)
                            rect2.centerx += STEP

                        # also a invalid position
                        surface.fill((255, 0, 0))
                        pygame.draw.rect(surface, (255, 255, 255), rect1)
                        pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
                        pygame.draw.circle(surface, CIRCLE_COLOR, cirle1.center, RADIUS)
                        pygame.display.flip()
                else:
                    # must decide if we are outside on last row + last column -> means FINAL POSITION
                    if rect2.centery + STEP >= int(rect1.centery + (rect1.centery - STEP - SMALL_HEIGHT) / 2) and \
                            rect2.centerx >= int(rect1.centerx + (rect1.centerx - STEP - SMALL_HEIGHT) / 2):
                        # we are at the end so just stop:
                        print("Final")
                        break
                    # must put rectangle in new row
                    rect2.centery += STEP
                    rect2.centerx = rect1.centerx - (rect1.centerx - STEP - SMALL_WIDTH) / 2
                    # also a invalid position
                    surface.fill((255, 0, 0))
                    pygame.draw.rect(surface, (255, 255, 255), rect1)
                    pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
                    pygame.display.update()
            # circle is in out position
            else:
                cirle1.center = (rect1.centerx - (rect1.centerx - STEP) / 2 + RADIUS,
                                 rect1.centery - (rect1.centery - STEP) / 2 + RADIUS)
                # change small rectangle
                rect2.centerx += STEP
                # also a invalid position
                surface.fill((255, 0, 0))
                pygame.draw.rect(surface, (255, 255, 255), rect1)
                pygame.draw.rect(surface, SMALL_RECT_COLOR, rect2)
                pygame.draw.circle(surface, CIRCLE_COLOR, cirle1.center, RADIUS)
                pygame.display.update()
        else:
            print("Small rectangle out of bound. We must stop!")
            break
    clock.tick(5)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        pygame.quit()
        exit()
