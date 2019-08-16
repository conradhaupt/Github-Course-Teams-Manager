import argparse
import config as Config
import terminal as term
import os
import Utils
from enum import Enum
import sys

__func_teams_add_from_file = None
__func_team_add = None
__func_retire_team = None
__func_modify_team = None
__func_list_students = None
__func_list_teams = None
__func_sync_teams = None
__func_repo_add = None
__parser = None


def processArguments():
  global __parser
  # Process arguments
  if not __parser:
    raise RuntimeError('Please run setupArguments() before processArguments()')
  args = __parser.parse_args()
  args.func(args)


def __parse_teams_add_from_file(args):
  global __func_teams_add_from_file
  if args.file:
    if os.path.exists(Utils.formatFilePath(args.file)):
      Config.student_csv_filename = Utils.formatFilePath(
          args.file)
    else:
      term.error('Could not find %s, using default filename' %
                 (args.file))
  if args.save_teams_file:
    if not os.path.exists(Utils.formatFilePath(args.save_teams_file)):
      Config.valid_teams_filename = Utils.formatFilePath(args.save_teams_file)
    else:
      term.error('Found already existing file %s to save valid teams to, please delete it to run the program' %
                 (args.save_teams_file))
      sys.exit()
  if args.error_teams_file:
    if not os.path.exists(Utils.formatFilePath(args.error_teams_file)):
      Config.error_teams_filename = Utils.formatFilePath(
          args.error_teams_file)
    else:
      term.error('Found already existing file %s to save teams with errors to, please delete it to run the program' %
                 (args.error_teams_file))
      sys.exit()
  if args.error_students_file:
    if not os.path.exists(Utils.formatFilePath(args.error_students_file)):
      Config.error_students_filename = Utils.formatFilePath(
          args.error_students_file)
    else:
      term.error('Found already existing file %s to save students with errors to, please delete it to run the program' %
                 (args.error_students_file))
      sys.exit()
  if callable(__func_teams_add_from_file):
    __func_teams_add_from_file(args)


def __parse_team_add(args):
    # Process student details from CLI
  student_details = []
  for s in args.student:
    student_details.append((s[0], s[1], s[2]))

  # Check if there's a custom team name
  team_name = None
  if args.name:
      team_name = args.name

  team_num = None
  if args.number:
      team_num = args.number

  if callable(__func_team_add):
    __func_team_add(args, student_details, team_name = team_name, team_num = team_num)


def __parse_list_students(args):
  global __func_list_students
  githubSync = args.github
  sort = args.sort
  retired = args.retired
  if callable(__func_list_students):
    __func_list_students(args, githubSync, sort,retired=retired)


def __parse_list_teams(args):
  global __func_list_teams
  listMembership = True if args.members else False
  sort = True if args.sort else False
  team_numbers = None if args.team_num is None else args.team_num
  retired = args.retired
  if callable(__func_list_teams):
    __func_list_teams(args, sort, listMembership, team_numbers=team_numbers, retired=retired)


def __parse_retire_team(args):
  global __func_retire_team
  team_num = args.teamNum
  if callable(__func_retire_team):
    __func_retire_team(args, team_num)


class ModifyTeamAction(Enum):
  STUDENT_ADD = 1
  STUDENT_REMOVE = 2


def __parse_modify_team(args):
  global __func_modify_team
  #   new_students=None,remove_students=None,new_team_num=None,new_team_name=None

  # Team details
  team_num = args.teamNum
  inplace = args.inplace

  # Default values
  new_students = None
  new_team_num = None
  new_team_name = None
  ignore_multiple_teams = False
  remove_student_username = None
  remove_student_number = None
  action = None

  # Detect the modification being made
  if args.modification is None:
    # This isn't really allowed
    return

  if args.modification == 'student':
    ## Modifying student ##

    # Check if there's a student operation
    if args.crud is None:
      # This isn't really allowed
      return

    # Handle operations
    if args.crud == 'add':
      ## Adding student ##
      action = ModifyTeamAction.STUDENT_ADD
      ignore_multiple_teams = args.ignore_multiple_teams
      new_students = []
      for stud in args.student:
        new_students.append((
            stud[0],
            stud[1],
            stud[2]
        ))
    if args.crud == 'remove':
      ## Removing student ##
      action = ModifyTeamAction.STUDENT_REMOVE
      if args.student_number:
        remove_student_number = args.student_number
      elif args.username:
        remove_student_username = args.username
  else:
    # This isn't really allowed
    return
  if callable(__func_modify_team):
    __func_modify_team(
        args,
        action=action,
        team_num=team_num,
        inplace=inplace,
        # Add students
        new_students=new_students,
        ignore_multiple_teams=ignore_multiple_teams,
        # Remove students
        remove_student_number=remove_student_number,
        remove_student_username=remove_student_username,
        # Used to change the team name or number
        new_team_num=new_team_num,
        new_team_name=new_team_name
    )


def __parse_sync_teams(args):
  global __func_sync_teams
  team_nums = None if args.team_num is None else args.team_num
  team_num_negate = None if args.team_num_negate is None else args.team_num_negate,
  check_membership = args.membership
  if callable(__func_sync_teams):
    __func_sync_teams(args, args.dry_run, team_nums,team_num_negate,check_membership)


def __parse_repo_add(args):
  global __func_repo_add
  team_nums = None if args.team_num is None else args.team_num
  team_num_negate = None if args.team_num_negate is None else args.team_num_negate
  lab_num = args.number if args.number is not None else None
  repo_type_name = args.name if args.name is not None else None
  if callable(__func_repo_add):
    __func_repo_add(args, lab_num, team_nums, team_num_negate=team_num_negate, dry_run=args.dry_run,repo_type_name=repo_type_name)


def setupArguments(
    funcTeamsAddFromFile=None,
    funcTeamAdd=None,
    funcListStudents=None,
    funcListTeams=None,
    funcRetireTeam=None,
    funcModifyTeam=None,
    funcSyncTeams=None,
    funcRepoAdd=None
):
  global __parser
  global __func_teams_add_from_file
  global __func_team_add
  global __func_retire_team
  global __func_modify_team
  global __func_list_students
  global __func_list_teams
  global __func_sync_teams
  global __func_repo_add
  global __func_team_add
  __func_teams_add_from_file = funcTeamsAddFromFile
  __func_team_add = funcTeamAdd
  __func_retire_team = funcRetireTeam
  __func_modify_team = funcModifyTeam
  __func_list_students = funcListStudents
  __func_list_teams = funcListTeams
  __func_sync_teams = funcSyncTeams
  __func_repo_add = funcRepoAdd

  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(title='commands')

  # Parent parsers that contain repeated information
  student_parser = argparse.ArgumentParser(add_help=False)
  student_parser.add_argument(
      '-s',
      '--student',
      type=str,
      nargs=3,
      metavar=('student_number', 'username', 'fullname'),
      help='Team member/student details',
      required=True,
      action='append'
  )
  student_search_parser = argparse.ArgumentParser(add_help=False)
  student_search_terms = student_search_parser.add_mutually_exclusive_group(
      required=True
  )
  student_search_terms.add_argument(
      '-N',
      '--student-number',
      type=str,
      help='Student number'
  )
  student_search_terms.add_argument(
      '-U',
      '--username',
      type=str,
      help='Github username'
  )

  ## team ##
  team_parser = subparsers.add_parser(
      'team',
      help='Manage teams'
  )
  team_subparsers = team_parser.add_subparsers()

  ## add new teams from file ##
  addTeamsFromFile_Parser = team_subparsers.add_parser(
      'add-from-file',
      help='Add new students and their teams to the database'
  )
  addTeamsFromFile_Parser.add_argument(
      '-f',
      '--file',
      help='File of new teams to be added to the database',
      type=str
  )
  addTeamsFromFile_Parser.add_argument(
      '-s',
      '--save-teams-file',
      help='The csv file to which valid teams should be saved',
      type=str
  )
  addTeamsFromFile_Parser.add_argument(
      '-e',
      '--error-teams-file',
      help='The file to which teams that had an error should be saved. Leave blank to not save to any file.',
      type=str
  )
  addTeamsFromFile_Parser.add_argument(
      '-E',
      '--error-students-file',
      help='The file to which students that had an error should be saved. Leave blank to not save to any file.',
      type=str
  )
  addTeamsFromFile_Parser.set_defaults(func=__parse_teams_add_from_file)

  ## add team from CLI ##
  addTeam_Parser = team_subparsers.add_parser(
      'add',
      help='Add a new team',
      parents=[student_parser]
  )
  addTeam_Parser.add_argument(
      '-n',
      '--number',
      help='The team number to use',
      type=int
  )
  addTeam_Parser.add_argument(
      '-N',
      '--name',
      help='Custom team name to use',
      type=str
  )
  addTeam_Parser.add_argument(
      '-r',
      '--retire',
      help='Retire conflicting teams',
      action='store_true'
  )
  addTeam_Parser.set_defaults(func=__parse_team_add)

  ## Retire a team ##
  retireTeam_parser = team_subparsers.add_parser(
      'retire',
      help='Retire a team'
  )
  retireTeam_parser.add_argument(
      'teamNum',
      help='The number of the team to be modified',
      type=int
  )
  retireTeam_parser.set_defaults(func=__parse_retire_team)

  ## Modify team ##
  modifyTeams_parser = team_subparsers.add_parser(
      'modify',
      help='Modify a team'
  )
  modifyTeams_parser.add_argument(
      'teamNum',
      help='The number of the team to be modified',
      type=int
  )
  modifyTeams_parser.add_argument(
      '-i',
      '--inplace',
      help='Modify the team in-place (i.e. don\'t create a new team',
      action='store_true'
  )

  ## team modifications ##
  modifyTeams_subparsers = modifyTeams_parser.add_subparsers(
      title='Modifications to apply to the given team',
      dest='modification'
  )
  modifyTeams_subparsers.required = True

  ## student modifications ##
  student_modifyTeams_parser = modifyTeams_subparsers.add_parser(
      'student'
  )
  student_modifyTeams_subparsers = student_modifyTeams_parser.add_subparsers(
      dest='crud'
  )
  student_modifyTeams_subparsers.required = True

  ## Add student to team ##
  addStudent_modifyTeams_parser = student_modifyTeams_subparsers.add_parser(
      'add',
      help='Add more student/s',
      parents=[student_parser]
  )
  addStudent_modifyTeams_parser.add_argument(
      '-I',
      '--ignore-multiple-teams',
      help='Ignore other teams that may contain the given student',
      action='store_true'
  )
  addStudent_modifyTeams_parser.set_defaults(func=__parse_modify_team)

  ## Remove student from team ##
  removeStudent_modifyTeams_parser = student_modifyTeams_subparsers.add_parser(
      'remove',
      help='Remove student/s',
      parents=[student_search_parser]
  )
  removeStudent_modifyTeams_parser.set_defaults(func=__parse_modify_team)

  ## repo ##
  repo_parser = subparsers.add_parser(
      'repo',
      help='Manage repos'
  )
  repo_subparsers = repo_parser.add_subparsers()

  ## add repo ##
  addrepo_parser = repo_subparsers.add_parser(
      'new'
  )
  addrepo_parser.add_argument(
      '-n',
      '--number',
      help='The number for the lab repo to create',
      type=int
  )
  addrepo_parser.add_argument(
      '-N',
      '--name',
      help='The name of the repo to create',
      type=str
  )
  addrepo_parser.add_argument(
      '-t',
      '--team-num',
      help='Create a repo for specific teams identified by the team number',
      type=int,
      nargs='+',
      metavar='num'
  )
  addrepo_parser.add_argument(
      '-T',
      '--team-num-negate',
      help='Do not create repos for teams identified by the following team numbers',
      type=int,
      nargs='+',
      metavar='num'
  )
  addrepo_parser.add_argument(
      '-d',
      '--dry-run',
      help='Verify with Github but don\'t modify anything on Github',
      action='store_true'
  )
  addrepo_parser.set_defaults(func=__parse_repo_add)

  ## sync ##
  sync_parser = subparsers.add_parser(
      'sync',
      help='Synchronise the local database with Github'
  )
  sync_subparsers = sync_parser.add_subparsers()

  ## sync teams ##
  sync_teams_parser = sync_subparsers.add_parser('teams')
  sync_teams_parser.add_argument(
      '-d',
      '--dry-run',
      help='Verify with Github but don\'t modify anything on Github',
      action='store_true'
  )
  sync_teams_parser.add_argument(
      '-t',
      '--team-num',
      help='Only sync teams identified by the following team numbers',
      type=int,
      nargs='+',
      metavar='num'
  )
  sync_teams_parser.add_argument(
      '-T',
      '--team-num-negate',
      help='Do not sync teams identified by the following team numbers',
      type=int,
      nargs='+',
      metavar='num'
  )
  sync_teams_parser.add_argument(
      '-m',
      '--membership',
      help='Update student membership for existing teams (use when modifying teams)',
      action='store_true'
  )
  sync_parser.set_defaults(func=__parse_sync_teams)

  ## list ##
  list_parser = subparsers.add_parser(
      'list',
      help='List entries/objects'
  )
  list_parser.add_argument(
      '-g',
      '--github',
      help='List status of Github sync for all listed items',
      action='store_true'
  )
  list_parser.add_argument(
      '-s',
      '--sort',
      help='Sort entries lexographically',
      action='store_true'
  )
  list_parser.add_argument(
      '-r',
      '--retired',
      help='Only list those teams and students that are in a retired team',
      action='store_true'
  )
  list_subparsers = list_parser.add_subparsers(title='objects to list')
  ## list students ##
  list_students_parser = list_subparsers.add_parser(
      'students',
      help='List students'
  )
  list_students_parser.set_defaults(func=__parse_list_students)
  ## list teams ##
  list_teams_parser = list_subparsers.add_parser(
      'teams',
      help='List teams'
  )
  list_teams_parser.add_argument(
      '-m',
      '--members',
      help='List members of teams',
      action='store_true'
  )
  list_teams_parser.add_argument(
      '-s',
      '--sort',
      help='Sort teams by team number',
      action='store_true'
  )
  list_teams_parser.add_argument(
      '-t',
      '--team-num',
      help='List only teams identified by the following team numbers',
      type=int,
      nargs='+',
      metavar='num'
  )
  list_teams_parser.set_defaults(func=__parse_list_teams)

  __parser = parser
