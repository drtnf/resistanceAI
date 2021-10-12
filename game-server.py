from app import app, db, socketio
from app.models import Student, Game, Round, Mission

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Student':Student, 'Game':Game, 'Round':Round, 'Mission':Mission}

if __name__ =='__main__':
    socketio.run(app)
