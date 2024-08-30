from sqlalchemy import func,desc,select,and_

from conf.models import Grade,Teacher,Student,Group,Subject
from conf.db import session
def select_01():
    '''
    SELECT
        s.id,
        s.fullname,
        round(AVG(g.grade),2)AS average_grade
    FROM students s
    JOIN grades g ON s.id = g.student_id
    GROUP BY s.id
    ORDER BY average_grade DESC
    LIMIT 5;
    '''
    result = session.query(Student.id, Student.fullname, func.round(func.avg(Grade.grade), 2).label('average_grade')) \
        .select_from(Student).join(Grade).group_by(Student.id).order_by(desc('average_grade')).limit(5).all()
    return result

def select_02():
    '''
    SELECT
        s.id,
        s.fullname,
        round(AVG(g.grade),2)AS average_grade
    FROM grades g
    JOIN students s ON s.id = g.student_id
    WHERE g.subject_id = 1
    GROUP BY s.id
    ORDER BY average_grade DESC
    LIMIT 1;
    '''
    result = session.query(Student.id, Student.fullname, func.round(func.avg(Grade.grade), 2).label('average_grade')) \
        .select_from(Grade).join(Student).where(Grade.subjects_id ==1).group_by(Student.id).order_by(desc('average_grade')).limit(1).all()
    return result

def select_03():
    '''
    SELECT
        groups.name,
        ROUND(AVG(grades.grade), 2) AS average_grade
    FROM groups
    JOIN students ON groups.id = students.group_id
    JOIN grades ON students.id = grades.student_id
    WHERE grades.subject_id = 1
    GROUP BY groups.name;
    '''
    result = session.query(Group.name, func.round(func.avg(Grade.grade), 2).label('average_grade')) \
        .select_from(Group).join(Student).join(Grade).where(Grade.subjects_id ==1).group_by(Group.name).all()
    return result
def select_04():
    '''
    SELECT
	ROUND(AVG(grades.grade), 2) AS average_grade
FROM grades;
    '''
    result = session.query(func.round(func.avg(Grade.grade), 2).label('average_grade')) \
        .select_from(Grade).all()
    return result

def select_05():
    '''
    SELECT
        subjects.name
    FROM subjects
    JOIN teachers ON subjects.teacher_id =teachers.id
    WHERE teachers.id = 2;
    '''
    result = session.query(Subject.name).select_from(Subject).join(Teacher).where(Teacher.id == 2).all()
    return result

def select_06():
    '''
    SELECT
        g.id ,
        s.fullname
    FROM students s
    JOIN groups g ON s.group_id = g.id
    WHERE g.id = 2;
    '''
    result = session.query(Group.id, Student.fullname).select_from(Student).join(Group).where(Group.id == 2).all()
    return result

def select_07():
    '''
    SELECT
        students.fullname,
        grades.grade
    FROM students
    JOIN grades ON students.id = grades.student_id
    JOIN subjects ON grades.subject_id = subjects.id
    JOIN groups ON students.group_id = groups.id
    WHERE groups.id = 2 AND subjects.id = 3;
    '''
    result = session.query(Student.fullname, Grade.grade).select_from(Student).join(Grade).join(Subject).join(Group).where(Group.id == 2 ,Subject.id ==3).all()
    return result

def select_08():
    '''
   SELECT
        ROUND(AVG(g.grade), 2) AS average_grade
    FROM grades g
    JOIN subjects s ON g.subject_id = s.id
    WHERE s.teacher_id = 2;

    '''
    result = session.query( func.round(func.avg(Grade.grade), 2).label('average_grade')) \
        .select_from(Grade).join(Subject).where(Subject.teacher_id == 2).all()
    return result

def select_09():
    '''
    SELECT
        s.name
    FROM subjects s
    JOIN grades g ON s.id= g.subject_id
    WHERE g.student_id = 1;
    '''
    result = session.query(Subject.name).select_from(Subject).join(Grade).where(Grade.student_id == 1).all()
    return result

def select_10():
    '''
    SELECT
        s.name
    FROM subjects s
    JOIN grades g ON s.id= g.subject_id
    JOIN students ON g.student_id = students.id
    WHERE g.student_id = 2 AND s.teacher_id =3;
    '''
    result = session.query(Subject.name).select_from(Subject).join(Grade).join(Student).where(Grade.student_id == 2, Subject.teacher_id ==3).all()
    return result


if __name__ == '__main__':
    print(select_07())