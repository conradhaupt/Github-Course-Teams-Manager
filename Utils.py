import os


# Trys alternative relative file paths
def formatFilePath(filename):
  if os.path.exists(filename):
    return filename
  tmpFilename = os.path.join(os.path.curdir, filename)
  if os.path.exists(tmpFilename):
    return tmpFilename
  tmpFilename = os.path.join(os.path.dirname(
      os.path.abspath(__file__)), filename)
  if os.path.exists(tmpFilename):
    return tmpFilename
  return filename

# Returns if the file exists
def fileExists(filename):
  return os.path.exists(formatFilePath(filename))
