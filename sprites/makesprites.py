import subprocess
import shlex
import sys
import logging
import os
import datetime
import math
import glob
from dateutil import relativedelta
##################################
# Generate tooltip thumbnail images & corresponding WebVTT file for a video (e.g MP4).
# Final product is one *_sprite.png file and one *_thumbs.vtt file.
#
# DEPENDENCIES: required: ffmpeg & imagemagick
#               optional: sips (comes with MacOSX) - yields slightly smaller sprites
#               optional: optipng (slight additional image compression)
#    download ImageMagick: http://www.imagemagick.org/script/index.php OR http://www.imagemagick.org/script/binary-releases.php (on MacOSX: "sudo port install ImageMagick")
#    download ffmpeg: http://www.ffmpeg.org/download.html
#    OPTIONAL download OptiPng: http://optipng.sourceforge.net/,  MANUAL: http://optipng.sourceforge.net/optipng-0.7.4.man.pdf
# jwplayer reference: http://www.longtailvideo.com/support/jw-player/31778/adding-tooltip-thumbnails/
#
# TESTING NOTES: Tested putting time gaps between thumbnail segments, but had no visual effect in JWplayer, so omitted.
#                Tested using an offset so that thumbnail would show what would display mid-way through clip rather than for the 1st second of the clip, but was not an improvement.
#                Tested using optipng in multiple spots/different orders, always same result as using once on final sprite. Note I did NOT test optipng command line options.
##################################

#CONSOLE LOGGING
logger = logging.getLogger(sys.argv[0])
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

USE_SIPS = True #True to use sips if using MacOSX (creates slightly smaller sprites), else set to False to use ImageMagick
USE_OPTIPNG = True # True to use optipng to further compress PNG files, False to skip or if not installed
THUMB_RATE_SECONDS=45 # every Nth second take a snapshot
THUMB_WIDTH=100 #100-150 is width recommended by JWPlayer; I like smaller files
SPRITE_NAME = "sprite.png"
VTTFILE_NAME = "thumbs.vtt"
OUTDIR = "thumbs"

if not len(sys.argv) > 1 :
    sys.exit("Please pass the full path to the video file for which to create thumbnails.")

class SpriteTask():
    """small wrapper class as convenience accessor for external scripts"""
    def __init__(self,videofile):
        if not os.path.exists(videofile):
            sys.exit("File does not exist: %s" % videofile)
        basefile = os.path.basename(videofile)
        basefile_nospeed = removespeed(basefile) #strip trailing speed suffix from file/dir names, if present
        newoutdir = makeOutDir(basefile_nospeed)
        fileprefix,ext = os.path.splitext(basefile_nospeed)
        spritefile = os.path.join(newoutdir,"%s_%s" % (fileprefix,SPRITE_NAME))
        vttfile = os.path.join(newoutdir,"%s_%s" % (fileprefix,VTTFILE_NAME))
        self.videofile = videofile
        self.vttfile = vttfile
        self.spritefile = spritefile
        self.outdir = newoutdir
    def getVideoFile(self):
        return self.videofile
    def getOutdir(self):
        return self.outdir
    def getSpriteFile(self):
        return self.spritefile
    def getVTTFile(self):
        return self.vttfile

def makeOutDir(videofile):
    """create unique output dir based on video file name and current timestamp"""
    base,ext = os.path.splitext(videofile)
    newoutdir = "%s.%s" % (os.path.join(OUTDIR,base),datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    if not os.path.exists(newoutdir):
        logger.info("Making dir: %s" % newoutdir)
        os.makedirs(newoutdir)
    return newoutdir

def doCmd(cmd):  #execute a shell command and return/print its output
    logger.info( "START [%s] : %s " % (datetime.datetime.now(), cmd))
    args = shlex.split(cmd) #tokenize args
    output = None
    try:
        output = subprocess.check_output(args)
    except Exception, e:
        logger.error("An exception occurred")
        raise e #todo ?
    logger.info(output)
    sys.stdout.flush()
    logger.info("END   [%s] : %s " % (datetime.datetime.now(), output))
    return output

def takesnaps(videofile,newoutdir):
    """
    take snapshot image of video every Nth second and output to sequence file names and custom directory
        reference: https://trac.ffmpeg.org/wiki/Create%20a%20thumbnail%20image%20every%20X%20seconds%20of%20the%20video
    """
    rate = "1/%d" % THUMB_RATE_SECONDS # 1/60=1 per minute, 1/120=1 every 2 minutes
    cmd = "ffmpeg -i %s -f image2 -bt 20M -vf fps=%s %s/tv%%03d.png" % (videofile,rate,newoutdir)
    doCmd (cmd)
    count = len(os.listdir(newoutdir))
    logger.info("%d thumbs written in %s" % (count,newoutdir))

def get_thumb_images(newdir):
    return glob.glob("%s/tv*.png" % newdir)

def resize(files):
    """change image output size to 100 width (originally matches size of video)
      - pass a list of files as string rather than use '*' with sips command because
        subprocess does not treat * as wildcard like shell does"""
    if USE_SIPS:
        # HERE IS MAC SPECIFIC PROGRAM THAT YIELDS SLIGHTLY SMALLER PNGs
        doCmd("sips --resampleWidth %d %s" % (THUMB_WIDTH," ".join(files)))
    else:
        # THIS COMMAND WORKS FINE TOO AND COMES WITH IMAGEMAGICK, IF NOT USING A MAC
        doCmd("mogrify -geometry %dx %s" % (THUMB_WIDTH," ".join(files)))

def get_geometry(file):
    """execute command to give geometry HxW+X+Y of each file matching command
       identify -format "%g - %f\n" *         #all files
       identify -format "%g - %f\n" onefile.png  #one file
     SAMPLE OUTPUT
        100x66+0+0 - _tv001.jpg
        100x2772+0+0 - sprite2.png
        4200x66+0+0 - sprite2h.png"""
    geom = doCmd("""identify -format "%%g - %%f\n" %s""" % file)
    parts = geom.split("-",1)
    return parts[0].strip() #return just the geometry prefix of the line, sans extra whitespace

def makevtt(spritefile,numsegments,coords,gridsize,writefile):
    """generate & write vtt file mapping video time to each image's coordinates
    in our spritemap"""
    #split geometry string into individual parts
    ##4200x66+0+0     ===  WxH+X+Y
    wh,xy = coords.split("+",1)
    w,h = wh.split("x")
    w = int(w)
    h = int(h)
    #x,y = xy.split("+")
#======= SAMPLE WEBVTT FILE=====
#WEBVTT
#
#00:00.000 --> 00:05.000
#/assets/thumbnails.jpg#xywh=0,0,160,90
#
#00:05.000 --> 00:10.000
#/assets/preview2.jpg#xywh=160,0,320,90
#
#00:10.000 --> 00:15.000
#/assets/preview3.jpg#xywh=0,90,160,180
#
#00:15.000 --> 00:20.000
#/assets/preview4.jpg#xywh=160,90,320,180
#==== END SAMPLE ========
    basefile = os.path.basename(spritefile)
    vtt = ["WEBVTT",""] #line buffer for file contents
    clipstart = 0
    # NOTE - putting a time gap between thumbnail end & next start has no visual effect in JWPlayer, so not doing it.
    clipend = THUMB_RATE_SECONDS
    for imgnum in range(1,numsegments+1):
        xywh = get_grid_coordinates(imgnum,gridsize,w,h)
        start = get_time_str(clipstart)
        end  = get_time_str(clipend)
        clipstart = clipend
        clipend += THUMB_RATE_SECONDS
        vtt.append("%s --> %s" % (start,end)) #00:00.000 --> 00:05.000
        vtt.append("%s#xywh=%s" % (basefile,xywh))
        vtt.append("") #Linebreak
    vtt =  "\n".join(vtt)
    #output to file
    writevtt(writefile,vtt)

def get_time_str(numseconds):
    """ convert time in seconds to VTT format time (HH:)MM:SS.ddd"""
    delta = relativedelta.relativedelta(seconds=numseconds)
    return "%02d:%02d:%02d.000" % (delta.hours,delta.minutes, delta.seconds)

def get_grid_coordinates(imgnum,gridsize,w,h):
    """ given an image number in our sprite, map the coordinates to it in X,Y,W,H format"""
    y = (imgnum - 1)/gridsize
    x = (imgnum -1) - (y * gridsize)
    imgx = x * w
    imgy =y * h
    return "%s,%s,%s,%s" % (imgx,imgy,w,h)

def makesprite(outdir,spritefile,coords,gridsize):
    """montage _tv*.jpg -tile 8x8 -geometry 100x66+0+0 montage.png  #GRID of images
           NOT USING: convert tv*.png -append sprite.png     #SINGLE VERTICAL LINE of images
           NOT USING: convert tv*.png +append sprite.png     #SINGLE HORIZONTAL LINE of images
     base the sprite size on the number of thumbs we need to make into a grid."""
    grid = "%dx%d" % (gridsize,gridsize)
    cmd = "montage %s/tv*.png -tile %s -geometry %s %s" % (outdir,grid,coords,spritefile)#if video had more than 144 thumbs, would need to be bigger grid, making it big to cover all our case
    doCmd(cmd)
    if USE_OPTIPNG:
        doCmd("optipng %s" % (spritefile))  #seeing 0-1% size reduction (with both sips and imagemagick)

def writevtt(vttfile,contents):
    """ output VTT file """
    with open(vttfile,mode="w") as h:
        h.write(contents)
    logger.info("Wrote: %s" % vttfile)

def removespeed(videofile):
    """some of my files are suffixed with datarate, e.g. myfile_3200.mp4;
     this trims the speed from the name since it's irrelevant to my sprite names (which apply regardless of speed);
     you won't need this if it's not relevant to your fileqnames"""
    videofile = videofile.strip()
    speed = videofile.rfind("_")
    speedlast = videofile.rfind(".")
    maybespeed = videofile[speed+1:speedlast]
    try:
        int(maybespeed)
        videofile = videofile[:speed] + videofile[speedlast:]
    except:
        pass
    return videofile


def run(task):
    outdir = task.getOutdir()
    spritefile = task.getSpriteFile()

    #create snapshots
    takesnaps(task.getVideoFile(),outdir)
    #resize them to be mini
    thumbfiles=get_thumb_images(outdir)
    resize(thumbfiles)

    #get coordinates from a resized file to use in spritemapping
    numfiles = len(thumbfiles)
    gridsize = int(math.ceil(math.sqrt(numfiles)))
    coords = get_geometry(thumbfiles[0]) #use the first file (since they are all same size) to get geometry settings

    #convert small files into a single sprite grid
    makesprite(outdir,spritefile,coords,gridsize)

    #generate a vtt with coordinates to each image in sprite
    makevtt(spritefile,numfiles,coords,gridsize,task.getVTTFile())

if __name__ == "__main__":
    videofile = sys.argv[1]
    task = SpriteTask(videofile)
    run(task)
