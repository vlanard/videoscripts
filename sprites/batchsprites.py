#!/usr/bin/python
import sys
import makesprites
import shutil
import os

# Batch process a text file containing list of videos to make sprites for, and a destination directory for just the sprites/vtt files

OUTPUT_FOLDER = "/Users/vlanard/gigabody_git/ubuntu/gigab/prototype/static/inc/th"

if not len(sys.argv) > 1 :
    sys.exit("Please pass the full path to file containing the video list for which to create thumbnails.")

def copyFile(origfile):
    if not os.path.exists(OUTPUT_FOLDER):
        try:
            os.makedirs(OUTPUT_FOLDER)
        except:
            pass
    thefile = os.path.basename(origfile)
    outfile = os.path.join(OUTPUT_FOLDER,thefile)
    shutil.copy(origfile,outfile)

videolist = sys.argv[1]
with open (videolist) as fh:
    for video in fh:
        task = makesprites.SpriteTask(video.strip())
        makesprites.run(task)
        spritefile = task.getSpriteFile()
        vttfile = task.getVTTFile()
        #batch move the generated sprites
        copyFile(spritefile)
        copyFile(vttfile)

