from math import sqrt
import tkinter as tk
import random
import numpy


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.direction = [1, -1]
        self.direction /= numpy.linalg.norm(self.direction)
        self.speed = 3
        self.filename = tk.PhotoImage(file = "/Users/junseo/Desktop/2022-2학기/게임프로그래밍입문/실습/Ball/ball2.png")
        item = canvas.create_image(x, y, anchor = tk.CENTER,
                                  image = self.filename)
        self.center = canvas.coords(item)
        self.width = self.filename.width()
        self.height = self.filename.height()
        super(Ball, self).__init__(canvas, item)

    def get_position(self):
        self.center = self.canvas.coords(self.item)
        x = self.center[0]
        y = self.center[1]
        return [x-self.width/2, y-self.height/2, x+self.width/2, y+self.height/2]
    
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        if len(game_objects) > 1:
            box1 = game_objects[0].get_position()
            box2 = game_objects[1].get_position()
            if box1[0] == box2[0] or box1[2] == box2[2]:
                self.direction[0] *= -1
            else:
                self.direction[1] *= -1

        elif len(game_objects) == 1:
            collide_point = []
            collision_box = game_objects[0].get_position()
            collision_box = [collision_box[0] - self.width/2, collision_box[1] - self.height/2,
                            collision_box[2] + self.width/2, collision_box[3] + self.height/2]
            for i in range(4):
                if i%2 == 0:
                    D = self.width**2/4 - ((collision_box[i] - self.center[0])**2)
                    if D > 0:
                        a = self.center[1] + sqrt(D)
                        b = self.center[1] - sqrt(D)
                        if collision_box[1] < a < collision_box[3] and collision_box[1] < b < collision_box[3]:
                            self.direction[0] *= -1
                        elif collision_box[1] < a < collision_box[3]:
                            collide_point.append([collision_box[i], a])
                        elif collision_box[1] < b < collision_box[3]:
                            collide_point.append([collision_box[i], b])

                else:
                    D = self.height**2/4 - ((collision_box[i] - self.center[1])**2)
                    if D > 0:
                        a = self.center[0] + sqrt(D)
                        b = self.center[0] - sqrt(D)
                        if collision_box[0] < a < collision_box[2] and collision_box[0] < b < collision_box[2]:
                            self.direction[1] *= -1   
                        elif collision_box[0] < a < collision_box[2]:
                            collide_point.append([a, collision_box[i]])
                        elif collision_box[0] < b < collision_box[2]:
                            collide_point.append([b, collision_box[i]])   

            if len(collide_point) == 2:
                normal = []
                normal.append(self.center[0] - (collide_point[1][0] + collide_point[0][0])/2)
                normal.append(self.center[1] - (collide_point[1][1] + collide_point[0][1])/2)
                normal /= numpy.linalg.norm(normal)

                dotpro = normal[0]*self.direction[0] + normal[1]*self.direction[1]
                if dotpro < 0:
                    bounce = []
                    bounce.append(-2*dotpro*normal[0] + self.direction[0])
                    bounce.append(-2*dotpro*normal[1] + self.direction[1])
                    self.direction = bounce / numpy.linalg.norm(bounce)

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 800
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.text = None
        self.level = 1
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        
        self.hud = None
        self.setup_level()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))

    def setup_level(self):
        self.unbind('<space>')
        self.canvas.delete(self.text)

        if self.level == 1:
            for x in range(5, self.width - 5, 75):
                rand1 = random.randint(0, 9)
                rand2 = random.randint(0, 9)
                rand3 = random.randint(0, 9)
                if rand1 in range(7):
                    self.add_brick(x + 37.5, 50, 2)
                if rand2 in range(7):
                    self.add_brick(x + 37.5, 70, 1)
                if rand3 in range(7):
                    self.add_brick(x + 37.5, 90, 1)

        elif self.level == 2:
            for x in range(5, self.width - 5, 75):
                rand1 = random.randint(0, 9)
                rand2 = random.randint(0, 9)
                rand3 = random.randint(0, 9)
                if rand1 in range(8):
                    self.add_brick(x + 37.5, 50, 3)
                if rand2 in range(8):
                    self.add_brick(x + 37.5, 70, 2)
                if rand3 in range(8):
                    self.add_brick(x + 37.5, 90, 1)

        elif self.level == 3:
            for x in range(5, self.width - 5, 75):
                rand1 = random.randint(0, 9)
                rand2 = random.randint(0, 9)
                rand3 = random.randint(0, 9)
                rand4 = random.randint(0, 9)
                if rand1 in range(9):
                    self.add_brick(x + 37.5, 50, 3)
                if rand2 in range(9):
                    self.add_brick(x + 37.5, 70, 3)
                if rand3 in range(9):
                    self.add_brick(x + 37.5, 90, 2)
                if rand4 in range(9):
                    self.add_brick(x + 37.5, 110, 1)
        
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200,
                                    'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200,
                                    'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s  Level: %s' % (self.lives, self.level)
        if self.hud is None:
            self.hud = self.draw_text(70, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            if self.level == 3 :
                self.draw_text(300, 200, 'You win!')
            else:
                self.level += 1
                self.text = self.draw_text(300, 200, 'Press Space to start next level')
                self.canvas.bind('<space>', lambda _: self.setup_level())
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(10, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = Game(root)
    game.mainloop()
