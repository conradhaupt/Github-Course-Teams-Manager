from classroom import Student, Team
from typing import List
_WS = '<'
_WE = '>'


def _WRAP(code):
  global _WS, _WE
  return _WS + code + _WE


# GENERAL FLAGS
SEP = '-'
YEAR = _WRAP('year')

# TEAM FLAGS
TEAM_NUM = _WRAP('team_num')
TEAM_NAME = _WRAP('team_name')
TEAM_RETIRED = _WRAP('team_retired')
TEAM_GITHUB_ID = _WRAP('team_github_id')

# STUDENT FLAGS
STUD_STUD_NUM = _WRAP('student_number')
STUD_USERNAME = _WRAP('username')
STUD_FULLNAME = _WRAP('fullname')
STUD_REPEAT_MARKER = _WRAP('R')

# REPO FLAGS
REPO_NAME = _WRAP('repo_name')


def repeat_for_students(template):
  global STUD_REPEAT_MARKER
  return STUD_REPEAT_MARKER + template + STUD_REPEAT_MARKER


# LAB FLAGS
LAB_NUM = _WRAP('lab_num')


def format(template, lab_num=None, team=None, students=None, student=None, repo_name=None):
  global STUD_REPEAT_MARKER
  global TEAM_NUM, TEAM_NAME, TEAM_RETIRED, TEAM_GITHUB_ID
  global STUD_STUD_NUM, STUD_USERNAME, STUD_FULLNAME
  global LAB_NUM
  global YEAR,REPO_NAME
  parts = template.split(STUD_REPEAT_MARKER)
  if len(parts) != 3 and len(parts) != 1:
    raise ValueError('format can only contain 0/1 student repeat markers')

  if len(parts) == 3 and students == None:
    raise ValueError(
        'Cannot have repeating student section without students variable')

  if len(parts) == 1:
    res = parts[0]

    # Lab values
    if lab_num is not None:
      res = res.replace(LAB_NUM, '%d' % (lab_num))
    else:
      res = res.replace(LAB_NUM,'')

    # Team values
    if team != None:
      if team.get_team_num():
        res = res.replace(TEAM_NUM, '%03d' % (team.get_team_num()))
      if team.get_team_name():
        res = res.replace(TEAM_NAME, team.get_team_name())
    else:
      # If the team doesn't exist BUT is required, throw an error
      if (
          TEAM_NUM in res
          or TEAM_GITHUB_ID in res
          or TEAM_NAME in res
          or TEAM_RETIRED in res
      ):
        raise ValueError(
            'team is required in the formatting string but team==None')

    # Student values
    if student != None:
      res = res\
          .replace(STUD_STUD_NUM, student.get_student_number())\
          .replace(STUD_USERNAME, student.get_username())
      if student.get_fullname():
        res = res.replace(STUD_FULLNAME, student.get_fullname())
    else:
      # If the student doesn't exist BUT is required, throw an error
      if (
          STUD_STUD_NUM in res
          or STUD_USERNAME in res
          or STUD_FULLNAME in res
      ):
        raise ValueError(
            'student is required in the formatting string but student==None')
    # General values
    res = res.replace(YEAR, '2018')
    if repo_name is not None:
      res = res.replace(REPO_NAME, repo_name)
    else:
      res = res.replace(REPO_NAME,'')
  elif len(parts) == 3:
    res = format(parts[0], lab_num=lab_num, team=team,repo_name=repo_name)
    for student in students:
      res += format(parts[1], lab_num=lab_num, team=team, student=student,repo_name=repo_name)
    res += format(parts[2], lab_num=lab_num, team=team,repo_name=repo_name)

  return res
