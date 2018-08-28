import github
from github.GithubException import UnknownObjectException
from github import Github
from itertools import combinations
from typing import List
from AUTH import GITHUB_AUTH_TOKEN


class Student:
  class StudentNotFoundError(Exception):
    def __init__(self, studentNumber, githubUsername):
      super().__init__('Student with student number %s and Github username %s not found' %
                       (studentNumber, githubUsername))

  def __init__(self, student_number, username, surname=None):
    self.__student_number = None
    self.__username = None
    self.__surname = None
    self.set_student_number(student_number)
    self.set_username(username)
    self.set_surname(surname)
    self.__exists_on_github = None

  def get_student_number(self):
    return self.__student_number

  def set_student_number(self, student_number):
    if student_number:
      self.__student_number = student_number.lstrip().rstrip()

  def get_username(self):
    return self.__username

  def set_username(self, username):
    if username:
      self.__username = username.lstrip().rstrip().lower()

  def get_surname(self):
    return self.__surname

  def set_surname(self, surname):
    if surname:
      self.__surname = surname.lstrip().rstrip()

  def set_exists_on_github(self, exists):
    self.__exists_on_github = exists

  def exists_on_github(self):
    if self.__exists_on_github == None:
      g = Github(GITHUB_AUTH_TOKEN)
      try:
        g.get_user(login=self.__username)
        self.__exists_on_github = True
      except:
        self.__exists_on_github = False
    return self.__exists_on_github

  # Returns True if the students conflict, false otherwise.
  # The second returned variable helps identify the conflicting variable.
  def conflictsWith(self, student):
    if self.__student_number != None and self.__student_number == student.__student_number:
      return True, 'student_number'
    if self.__username != None and self.__username == student.__username:
      return True, 'username'
    return False, None

  def __eq__(self, student):
    if student == None:
      return False
    if self.get_student_number() != student.get_student_number():
      return False
    if self.get_username() != student.get_username():
      return False
    if self.get_surname() != student.get_surname():
      return False
    return True

  def __ne__(self, student):
    return not self.__eq__(student)

  def __hash__(self):
    return hash(str([self.__student_number, self.__username, self.__surname]))


class Team:
  def __init__(self, team_num=None, team_name=None, *students: List[Student]):
    self.set_team_num(team_num)
    self.__team_name = team_name
    self.__students = list()
    self.__retired = False
    self.__github_id = None
    for student in students:
      self.__students.append(student)

  def get_team_num(self):
    return self.__team_num

  def set_team_num(self, team_num):
    if team_num is not None:
      self.__team_num = int(team_num)
    else:
      self.__team_num = team_num

  def get_team_name(self):
    return self.__team_name

  def set_team_name(self, team_name):
    self.__team_name = team_name

  def get_students(self):
    return self.__students

  def is_retired(self):
    return self.__retired

  def retire(self):
    self.__retired = True

  def set_github_id(self, id):
    self.__github_id = int(id)

  def get_github_id(self):
    return self.__github_id

  def add_student(self, student: Student):
    if self.conflictsWith(student):
      raise ValueError('student already exists')
    self.__students.append(student)

  def add_students(self, *students: List[Student]):
    for student in students:
      self.add_student(student)

  def remove_student(self, student: Student):
    if student in self.__students:
      self.__students.remove(student)
      return True
    else:
      return False

  def conflictsWith(self, input):
    if isinstance(input, list) and isinstance(input[0], Student):
      students = input
    elif isinstance(input, Student):
      students = [input]
    elif isinstance(input, Team):
      students = input.get_students()
    else:
      raise ValueError('conflictsWith only allows students and teams as input')
    for student in students:
      for otherStudent in self.__students:
        conflicts, reason = student.conflictsWith(otherStudent)
        if conflicts:
          return True
    return False

  def __eq__(self, team):
    if team == None:
      return False
    if self.get_team_name() != team.get_team_name():
      return False
    if self.get_team_num() != team.get_team_num():
      return False
    if len(self.__students) != len(team.get_students()):
      return False
    for self_student in self.get_students():
      found = False
      for other_student in team.get_students():
        if self_student == other_student:
          found = True
          break
      if not found:
        return False
    return True

  def __ne__(self, team):
    return not self.__eq__(team)

  def __hash__(self):
    _str = [self.__team_name, self.__team_num]
    for student in self.__students:
      _str.append(student.get_student_number())
      _str.append(student.get_username())
      _str.append(student.get_surname())
    return hash(str(_str))
