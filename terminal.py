from colorama import init, Fore, Back, Style
from math import ceil, log10
from sys import exit
from typing import List
from classroom import Student, Team

init(autoreset=True,convert=True)

def emphasise(text):
  if type(text) != str.__class__:
    text = str(text)
  return Style.BRIGHT + text


def status(msg):
  print(msg)


def announce(msg):
  status(Fore.YELLOW + emphasise(msg) + Style.RESET_ALL)


def error(msg):
  print(Fore.RED + msg)


def warning(msg):
  print(Fore.LIGHTMAGENTA_EX + msg)


def input_prompt(msg):
  return input(Fore.GREEN + msg + Style.RESET_ALL)


def debug(msg):
  print(Fore.YELLOW + '[DEBUG]' + msg)


def confirm(msg, default=True):
  POSITIVE_RESPONSE = 'yes'
  response = input_prompt(msg)
  if ((not response) == default) or (response and response.lower() in POSITIVE_RESPONSE.lower()):
    return True
  else:
    return False


def process(msg):
  print(Fore.BLUE + msg + "...")


def heading(head, paddingTop=False):
  if paddingTop:
    print('')
  print(Fore.BLUE + Style.BRIGHT + head)


def warningHeading(head, paddingTop=False):
  if paddingTop:
    print('')
  print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + head)


def errorHeading(head, paddingTop=False):
  if paddingTop:
    print('')
  print(Fore.RED + Style.BRIGHT + head)


def option(listList, msg_prompt, paddingTop=True, paddingBottom=False, paddingInner=False):
  raise NotImplementedError('Terminal\'s option() requires a cross-platform alternative to python-inquirer')
  # if paddingTop:
  #   print('')
  # results = inq.prompt([inq.Checkbox('results', message=msg_prompt, choices=[
  #                      (x, str(i)) for i, x in enumerate(listList)])])
  # if paddingInner:
  #   print('')
  # if paddingBottom:
  #   print('\n')
  # choices = [int(x) for x in results['results']]
  # for choice in choices:
  #   if choice < 0 or choice > len(listList):
  #     error(Fore.RED + emphasise(choice) + " is not a valid choice")
  #     raise IndexError()
  # return choices


def listItems(listList, paddingTop=False, paddingBottom=True):
  if paddingTop:
    print('')
  for item in listList:
    print(" - " + str(item))
  if paddingBottom:
    print('')


def listStudents(listStudents: List[Student], reasons=None, highlightExistence=True, paddingTop=False, paddingBottom=True):
  if paddingTop:
    print('')
  printFormat_DoesntExist = ' - %s (' + Fore.RED + '%s' + Fore.RESET + ')'
  printFormat_Exists = ' - %s (' + Fore.GREEN + '%s' + Fore.RESET + ')'
  printFormat = ' - %s (%s)'
  for iStudent, student in enumerate(listStudents):
    if not highlightExistence:
      line_format = printFormat
    else:
      if not student.exists_on_github():
        line_format = printFormat_DoesntExist
      else:
        line_format = printFormat_Exists
    if reasons is not None:
      line_format += ' [reason=%s]' % (reasons[iStudent])

    print(line_format % (student.get_student_number(), student.get_username()))
  if paddingBottom:
    print('')


def listTeams(listTeams: List[Team], highlightExistence=True, paddingTop=False, paddingBottom=True, list_membership=True):
  if paddingTop:
    print('')
  TEAM_SEPERATOR_LENGTH = 30
  _print_bottom_seperator = True
  for team in listTeams:
    if not team.get_team_num():
      print('-' * TEAM_SEPERATOR_LENGTH)
      _print_bottom_seperator = True
    else:
      seperatorLine = ' \'%s\' - [%03d] ' % (team.get_team_name(),
                                             team.get_team_num())
      seperatorLine = str(
          '-' * int((TEAM_SEPERATOR_LENGTH - len(seperatorLine)) / 2)) + seperatorLine
      seperatorLine = seperatorLine + \
          ('-' * (TEAM_SEPERATOR_LENGTH - len(seperatorLine)))
      print(seperatorLine)
    if team.get_students():
      _print_bottom_seperator = True
    else:
      _print_bottom_seperator = False
    if list_membership:
      listStudents(team.get_students(), highlightExistence=highlightExistence,
                   paddingTop=False, paddingBottom=False)
  if _print_bottom_seperator:
    print('-'*TEAM_SEPERATOR_LENGTH)
  if paddingBottom:
    print('')



def list_enumerate(listList, emphasised=False, paddingTop=False, paddingBottom=True):
  if emphasised:
    prefix = Style.BRIGHT
  else:
    prefix = ""
  if paddingTop:
    print('')
  idWidth = ceil(log10(len(listList)))
  for idx, item in enumerate(listList):
    print(prefix + " " + '{0:0{width}}'.format(idx,
                                               width=idWidth) + " - " + Style.NORMAL + str(item))
  if paddingBottom:
    print('')


__loading_indeterminate_count = 0
__loading_indeterminate_max = 3


def loading_indeterminate(msg, length=20):
  global __loading_indeterminate_count
  global __loading_indeterminate_max
  __loading_indeterminate_count = __loading_indeterminate_count + 1
  __loading_indeterminate_count = (
      __loading_indeterminate_count) % __loading_indeterminate_max
  if not __debug__:
    endChar = '\n'
  else:
    endChar = '\r'
  print(Fore.BLUE + msg + ''.join(
      ["."] * (__loading_indeterminate_count + 1)) + ''.join([' '] * (__loading_indeterminate_max - __loading_indeterminate_count + 1)), end=endChar)
  return len(msg) + len(str(Fore.BLUE)) + len(str(max))*2 + 1 + length


__loading = False
__msg = None
__loading_max = 100
__loading_length = None


def loading(msg=None, current=0, max=None, length=20):
  global __loading, __loading_max, __msg,__loading_length
  # Calculate caching variables
  if not __loading:
    __loading_max = max
    __loading_length = length
  if __loading_length is None:
    __loading_length = length
  if max is None:
    if __loading_max is None:
      __loading_max = 100
  else:
    __loading_max = max
  __loading = True
  if msg != None:
    __msg = msg + ': '

  # Calculate loading bar values
  nLoaded = int(current * loading_length() / loading_max())
  nNotLoaded = loading_length() - nLoaded
  if not __debug__:
    endChar = '\n'
  else:
    endChar = '\033[K\r'

  # Print loading bar
  print(
      Fore.BLUE +
      "[" +
      ''.join(["X"] * nLoaded) +
      ''.join(['-'] * nNotLoaded) +
      "] %d/%d " % (current, loading_max()) +
      loading_msg(),
      end=endChar
  )


def isLoading():
  global __loading
  return __loading


def loading_msg():
  global __msg
  return __msg


def loading_max():
  global __loading_max
  return __loading_max


def loading_length():
  global __loading_length
  return __loading_length


def endloading(msg, length=20):
  __loading = False
  if len(msg) < length:
    print("\r\033[K" + Fore.GREEN + msg + ''.join([' '] * (length - len(msg))))
  else:
    print(msg)
