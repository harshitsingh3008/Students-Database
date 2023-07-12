import os
from flask import Flask
from flask import render_template,redirect,url_for
from flask import request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
db= SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Student(db.Model):
    __tablename__= 'student'
    student_id = db.Column( db.Integer,autoincrement=True,primary_key=True )
    roll_number= db.Column(db.String,unique=True,nullable=False)
    first_name = db.Column(db.String,nullable=False)
    last_name= db.Column(db.String)



class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code = db.Column(db.String,nullable=False,unique=True)
    course_name    = db.Column(db.String,nullable=False)
    course_description = db.Column(db.String)
    

class Enrollments(db.Model):
    __tablename__= 'enrollments'
    ecourse_id= db.Column(db.Integer,db.ForeignKey('course.course_id'),primary_key=True,nullable=False)
    estudent_id= db.Column(db.Integer,db.ForeignKey('student.student_id'),primary_key=True,nullable=False)
    enrollment_id = db.Column(db.Integer,autoincrement=True)

db.create_all()

@app.route("/", methods = ["GET", "POST"])
def home():
    data = Student.query.all()
    return render_template("home.html",data=data)

@app.route("/student/create",methods=["GET","POST"])
def Create_Student():
    if request.method=="GET":
        return render_template("add-student.html") 
    elif request.method=="POST":
        data = request.form
        student = Student.query.filter_by(roll_number=data["roll"]).first()
        if student:
            return render_template("exists.html")
        new_st = Student(
            roll_number = data["roll"],
            first_name = data["f_name"],
            last_name = data["l_name"]
        )
        db.session.add(new_st)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/student/<int:student_id>",methods=["GET","POST"])
def Students_Details(student_id):
    data= Student.query.filter_by(student_id=student_id).first()
    all_enrolls = Enrollments.query.filter_by(estudent_id=student_id).all()
    all_courses = []
    for e in all_enrolls:
        c = Course.query.get(e.ecourse_id)
        all_courses.append(c)
    print(all_enrolls)
    if request.method=="GET":
        return render_template("student-details.html", data = data, courses=all_courses)
    

@app.route("/student/<int:student_id>/update",methods=["GET","POST"])
def Students_Update(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if request.method=="GET":
        all_courses = Course.query.all()
        return render_template("update-student.html", data = student, courses = all_courses)
    elif request.method=="POST":
        update = request.form
        to_update = Student.query.filter_by(student_id=student_id).first()
        to_update.first_name=update["f_name"]
        to_update.last_name=update["l_name"]

        enroll=Enrollments(
            estudent_id=student.student_id,
            ecourse_id=update["course"]
        )

        db.session.add(enroll)
        db.session.commit()

    return redirect(url_for('home'))
    

    
@app.route("/student/<int:student_id>/delete",methods=["GET","POST"])
def Students_Delete(student_id):
    to_delete = Student.query.filter_by(student_id=student_id).first()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/student/<int:student_id>/withdraw/<int:course_id>", methods = ["GET", "POST"])
def Withdraw(student_id,course_id):
    to_delete = Enrollments.query.filter_by(estudent_id=student_id, ecourse_id=course_id).first()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for('home'))



@app.route("/courses",methods=["GET","POST"])
def Courses():
    data = Course.query.all()
    return render_template("course.html",data=data)


@app.route("/course/create",methods=["GET","POST"])
def Add_Course():
    if request.method=="GET":
        return render_template("add-course.html") 
    elif request.method=="POST":
        data = request.form
        course = Course.query.filter_by(course_code=data["code"]).first()

        if course:
            return render_template("exists-course.html")
        new_cr = Course(
            course_code = data["code"],
            course_name = data["c_name"],
            course_description = data["desc"]
        )
        db.session.add(new_cr)
        db.session.commit()
        return redirect(url_for('Courses'))
    

@app.route("/course/<int:course_id>",methods=["GET","POST"])
def Course_Details(course_id):
    data= Course.query.filter_by(course_id=course_id).first()
    all_enrolls = Enrollments.query.filter_by(ecourse_id=course_id).all()
    all_students = []
    for e in all_enrolls:
        std = Student.query.get(e.estudent_id)
        if(std!=None):
            all_students.append(std)
    if request.method=="GET":
        return render_template("course-details.html", data = data, students=all_students)


@app.route("/course/<int:course_id>/update",methods=["GET","POST"])
def Course_Update(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if request.method=="GET":
        return render_template("update-course.html", course=course)
    elif request.method=="POST":
        update = request.form
        to_delete = Course.query.filter_by(course_id=course_id).first()
        db.session.delete(to_delete)
        db.session.commit()
        upd_cr= Course(
            course_code = course.course_code,
            course_name = update["c_name"],
            course_description = update["desc"]
        )
        db.session.add(upd_cr)
        db.session.commit()
        return redirect(url_for('Courses'))


@app.route("/course/<int:course_id>/delete",methods=["GET","POST"])
def Course_Delete(course_id):
    to_delete = Course.query.filter_by(course_id=course_id).first()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for('Courses'))


if __name__ =="__main__":
    app.debug=True
    app.run()