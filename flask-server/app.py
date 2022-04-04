from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask.templating import render_template
from flask_cors import CORS
from sqlalchemy import update


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cors = CORS(app)

db = SQLAlchemy(app)

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    time = db.Column(db.String(4), unique = True)
    available = db.Column(db.Integer)

    def toDict(self):
        return dict(id=self.id, time=self.time, available=self.available)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    time_id = db.Column(db.Integer, unique = True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(15))

    def toDict(self):
        return dict(id=self.id, time=self.time_id, first=self.first_name, last=self.last_name, phone=self.phone)

@app.route('/')
def display():
    return render_template('index.html')

@app.route('/appointments', methods=['GET', 'POST'])
def displayAppointments():
    if request.method == 'POST':
        data= request.get_json()
        statement = update(TimeSlot).where(TimeSlot.id == data['time_id']).values(available=0)
        db.session.execute(statement)
        a = Appointment(time_id = data['time_id'], first_name = data['first_name'], last_name= data['last_name'], phone=data['phone'])
        db.session.add(a)
        db.session.commit()
        return(data)
    else:
        appointment = Appointment.query.all()
        return jsonify([a.toDict() for a in appointment])

@app.route('/appointments/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def displayAppointment(id):
    appointment = Appointment.query.get(id)
    appointmentDict = appointment.toDict()
    prevTime = update(TimeSlot).where(TimeSlot.id == appointmentDict['time']).values(available=1)
    if request.method == 'PATCH':
        data = request.get_json()
        newTime = update(Appointment).where(Appointment.id == id).values(time_id=data['time_id'])
        updateTime = update(TimeSlot).where(TimeSlot.id == data['time_id']).values(available=0)
        db.session.execute(prevTime)
        db.session.execute(newTime)
        db.session.execute(updateTime)
        db.session.commit()
        return data
    elif request.method == 'DELETE':
        db.session.execute(prevTime)
        db.session.delete(appointment)
        db.session.commit()
        return {'message': 'Appointment deleted'}
    else:
        return jsonify(appointment.toDict())


@app.route('/times')
def displayOpenTimes():
    time = TimeSlot.query.filter(TimeSlot.available == 1)
    return jsonify([t.toDict() for t in time])

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == '__main__':
    app.run(debug=True)