from flask_login import logout_user
from mysql.connector import MySQLConnection, Error



from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)
import hashlib



class User:
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
    def __repr__(self):
        return f'<User: {self.username}>'




app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'



@app.before_request
def before_request():
    
    if 'user_id' in session:
        print (session['user_id'])

@app.route('/')
def home():
    return redirect(url_for('logout'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        session.pop('user_id', None)
        session.pop('username', None)
        
        pwd=hashlib.md5((request.form['password']).encode())
        pwd=str(pwd.hexdigest())
        queryExist="SELECT name, password, id, type FROM user WHERE name = %s"
        print("query exist : ", queryExist)
        try:
            cursor.execute(queryExist,(request.form['username'],))
            rowExist=cursor.fetchone()
            print("row exist: ", rowExist)
            if rowExist:
                if ((rowExist[0]==(request.form['username'])) and (rowExist[1]==pwd)):
                    print("heeelo")
                    session['username'] = rowExist[0]
                    session['user_id'] = rowExist[2]
                    if(rowExist[3]==0):
                        return redirect(url_for('student'))
                    else:
                        return redirect(url_for('teacher'))
                    
                else:
                    return redirect(url_for('login'))
        except Error as error:
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/profile')
def profile():
   
    if 'user_id' in session:
        print (session['user_id'])
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/student')
def student():
    if 'user_id' in session:
        g.stu_name = session['username']
    sql = 'SELECT course, count(course), sum(mark)  from quiz group by course'
    cursor.execute(sql,)
    Quiz = cursor.fetchall()
    print(Quiz)
    return render_template('student.html', quiz=Quiz)


@app.route('/quiz_take')
def quiz_take():
    if 'user_id' in session:
        g.stu_name = session['username']
    sql = 'SELECT question, o1, o2, o3, o4 from quiz where course=%s'
    g.name = session['sub']
    data = (
        session['sub'],
    )
    cursor.execute(sql, data)
    Quiz = cursor.fetchall()
    return render_template('quiz_take.html', quiz = Quiz)

@app.route('/student/<string:name>', methods = ['GET'])
def student_quiz_take(name):
    if 'user_id' in session:
        g.stu_name = session['username']
    if request.method == 'GET':
        session['sub']=name
        #print(name + 'Hello')
    return redirect(url_for('quiz_take'))



@app.route('/score')
def score():
    if 'user_id' in session:
        g.stu_name = session['username']
    sql = 'SELECT mark FROM user WHERE id = %s'
    data = (
        session['user_id'],
    )
    cursor.execute(sql, data)
    marks = cursor.fetchone()
    return render_template('score.html', marks=marks)

@app.route('/teacher')
def teacher():
    if 'user_id' in session:
        g.tea_name = session['username']
    return render_template('teacher.html')


@app.route('/view')
def view():
    if 'user_id' in session:
        g.tea_name = session['username']
    #quiz = Quiz.fetchall()
    query = "SELECT distinct(course) from quiz"
    cursor.execute(query,)
    Quiz = cursor.fetchall()
    return render_template('view.html', quiz=Quiz)

@app.route('/add', methods=['GET','POST'])
def add():
    if 'user_id' in session:
        g.tea_name = session['username']
    if request.method == 'POST':
        queryExist = 'SELECT course from quiz where course = %s'
        try:
            cursor.execute(queryExist, (str(request.form['addCourse']),))
            rowExist = cursor.fetchone() 
            print(rowExist)
            if not rowExist:
                sql = "INSERT INTO quiz (course, question, o1, o2, o3, o4, answer, mark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                print(sql)
                data = (
                    str(request.form['addCourse']),
                    "Sample Question",
                    "option 1",
                    "option 2",
                    "option 3",
                    "option 4",
                    "Sample Answer",
                    int(0)
                    )
                print(sql, data)
                cursor.execute(sql, data)
                conn.commit()
                return redirect(url_for('view'))
        except Error as error:  
            print("Hello")  
    return redirect(url_for('view'))

@app.route('/delete/<string:name>', methods = ['GET'])
def delete(name):
    if request.method == 'GET':
        queryExist="DELETE FROM quiz WHERE course = %s"
        try:
            print(queryExist, name)
            cursor.execute(queryExist, (str(name),))
            conn.commit()
        except Error as error:
            print("error")
    return redirect(url_for('view'))

@app.route('/view_course/delete/<string:id>', methods = ['GET'])
def delete_course(id):
    if request.method == 'GET':
        queryExist="DELETE FROM quiz WHERE id = %s"
        try:
            print(queryExist, id)
            cursor.execute(queryExist, (int(id),))
            conn.commit()
        except Error as error:
            print("error")
    return redirect(url_for('view_course'))


@app.route('/edit/<string:name>', methods = ['GET'])
def view_name(name):
    if request.method == 'GET':
        session['sub']=name
        #print(name + 'Hello')
    return redirect(url_for('view_course'))

@app.route('/view_course/add', methods=['GET','POST'])
def view_course_add():
    if 'user_id' in session:
        g.tea_name = session['username']
    if request.method == 'POST':    
        data = (
            session['sub'],
            str(request.form['addQues']),
            str(request.form['option1']),
            str(request.form['option2']),
            str(request.form['option3']),
            str(request.form['option4']),
            str(request.form['answer']),
            int(request.form['mark'])
        )
        print(data)
        sql="INSERT INTO quiz (course, question, o1, o2, o3, o4, answer, mark) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
                    print(sql, data)
                    cursor.execute(sql, data)
                    conn.commit()
                    return redirect(url_for('view_course'))
        except Error as error:
            print("hello")    
        
        
    return render_template('view_course.html')           

@app.route('/view_course')
def view_course():
    if 'user_id' in session:
        g.tea_name = session['username']
    g.name = session['sub']
    query = "SELECT * from quiz where course = %s" 
    data = (g.name, )
    cursor.execute(query, data)
    Quiz = cursor.fetchall()
    return render_template('view_course.html', quiz = Quiz)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        password=hashlib.md5(str(request.form['password']).encode())
        password=str(password.hexdigest())
    
        data = (
            str(request.form['username']),
            password,
            str(request.form['email']),
            int(request.form['type']),
            int(0)
        )
        sql="INSERT INTO user (name,password,email,type,mark) VALUES(%s,%s,%s,%s,%s)"
        try:
                    print(sql, data)
                    cursor.execute(sql, data)
                    #print("yo")
                    conn.commit()
                    return redirect(url_for('login'))
        except Error as error:
            print("hello")     
        
        
    return render_template('signup.html')           

if __name__ == '__main__':
    conn = MySQLConnection(
    host="127.0.0.1",
    user="root",
    password="",
    database="mydatabase"
    )
    cursor = conn.cursor()
    app.run()
    

    