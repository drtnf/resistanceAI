import unittest, os
from app import app, db
from app.models import Student, Plays, Game, Round, Mission
import time

class StudentModelCase(unittest.TestCase):

  def setUp(self):
      basedir = os.path.abspath(os.path.dirname(__file__))
      app.config['SQLALCHEMY_DATABASE_URI']=\
          'sqlite:///'+os.path.join(basedir,'test.db')
      self.app = app.test_client()#creates a virtual test environment
      db.create_all()
      s1 = Student(id='1', last_name='One', first_name='Student', agent_name='Agent1')
      s2 = Student(id='2', last_name='Two', first_name='Student', agent_name='Agent2')
      s3 = Student(id='3', last_name='Three', first_name='Student', agent_name='Agent3')
      s4 = Student(id='4', last_name='Four', first_name='Student', agent_name='Agent4')
      s5 = Student(id='5', last_name='Five', first_name='Student', agent_name='Agent5')
      
      db.session.add(s1)
      db.session.add(s2)
      db.session.add(s3)
      db.session.add(s4)
      db.session.add(s5)
      db.session.commit()

  def tearDown(self):
      db.session.remove()
      db.drop_all()

  def test_game(self):
      game = Game()  
      s1 = Student.query.get('1')
      s2 = Student.query.get('2')
      s3 = Student.query.get('3')
      s4 = Student.query.get('4')
      s5 = Student.query.get('5')
      game.start([s1,s2,s3,s4,s5])


if __name__=='__main__':
    unittest.main(verbosity=2)





