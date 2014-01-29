#!/usr/bin/python
import sys
import makesprites
import shutil
import os

# Batch process a text file containing list of videos to make sprites for,
# and a destination directory for just the sprites/vtt files
#    files get put into DESTINATION/##/*  where ## is the 2 letter prefix of the output files, and * are output files

# python batchsprites.py filelist.txt
# python batchsprites.py filelist.txt 20  #thumbnail every 20 sec

OUTPUT_FOLDER = "/Users/vlanard/myproject_git/ubuntu/proj/prototype/static/inc/th"

if not len(sys.argv) > 1 :
    sys.exit("Please pass the full path to file containing the video list for which to create thumbnails.")

def copyFile(origfile):
    thefile = os.path.basename(origfile)
    prefix = thefile[:2] #store in subdirectory that begins with 2 letter prefix of the files within it
    outputFolder = os.path.join(OUTPUT_FOLDER,prefix)
    if not os.path.exists(outputFolder):
        try:
            os.makedirs(outputFolder)
        except:
            pass
    outfile = os.path.join(outputFolder,thefile)
    shutil.copy(origfile,outfile)

if __name__ == "__main__":
    videolist = sys.argv[1]
    thumbRate = None
    #optionally pass in a 2nd arg that is number for every Nth second you want to take a snapshot
    if len(sys.argv)> 2:
        thumbRate = int(sys.argv[2])
        print "Taking snapshot every %d seconds" % thumbRate

    with open (videolist) as fh:
        for video in fh:
            video = video.strip()
            if video.startswith("#") or not video:
                continue
            task = makesprites.SpriteTask(video)
            makesprites.run(task,thumbRate=thumbRate)
            spritefile = task.getSpriteFile()
            vttfile = task.getVTTFile()
            #batch move the generated sprites
            copyFile(spritefile)
            copyFile(vttfile)

