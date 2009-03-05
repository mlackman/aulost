import os

def findFilesEndsWith(endsWith, path):
    foundFiles = []
    for root,dir,files in os.walk(path):
            for file in files:
                if file.endswith(endsWith):
                    foundFiles.append(file)
    return foundFiles
