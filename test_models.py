from app import models, db

student_deets_list = [
    {"id": "123", "first_name": "Amy",   "last_name": "Lastname", "agent_name": "AmyAgent"},
    {"id": "462", "first_name": "Bob",   "last_name": "Lastname", "agent_name": "BobAgent"},
    {"id": "835", "first_name": "Chloe", "last_name": "Lastname", "agent_name": "ChloeAgent"},
    {"id": "231", "first_name": "Dave",  "last_name": "Lastname", "agent_name": "DaveAgent"},
    {"id": "754", "first_name": "Ellie", "last_name": "Lastname", "agent_name": "EllieAgent"},
    {"id": "953", "first_name": "Fred",  "last_name": "Lastname", "agent_name": "FredAgent"},
    {"id": "482", "first_name": "Gwen",  "last_name": "Lastname", "agent_name": "GwenAgent"},
]

db.drop_all()
db.create_all()

students = []
for student_deets in student_deets_list:
    student = models.Student(**student_deets)
    db.session.add(student)
    students.append(student)

game = models.Game()
db.session.add(game)
db.session.commit()
game.start(students)

