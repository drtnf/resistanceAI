import random
from app import models, db

all_students = models.Student.query.all()
game_size = random.randint(5, 10)
students = [student.id for student in random.sample(all_students, game_size)]

game = models.Game()
game.start(students)

