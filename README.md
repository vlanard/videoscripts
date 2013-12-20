videoscripts
============


sprites
============
Python scripts to generate tooltip thumbnail images for videos (e.g. mp4,m4v)  & associated WebVTT files for use with JWPlayer.
Written for MacOSX 10.9, Python 2.7, JWPlayer 6 but should be portable to all major OS's.

makesprites.py
--------------
Python script to generate thumbnail images for a video, put them into an grid-style sprite,
and create a Web VTT file that maps the sprite images to the video segments.

Required dependencies (expected in PATH):
* ffmpeg [download here](http://www.ffmpeg.org/download.html)
* imagemagick [download here](http://www.imagemagick.org/script/index.php) or [here](http://www.imagemagick.org/script/index.php) or on Mac, use Macports: <pre>sudo port install ImageMagick</pre>

Optional dependencies that can improve png compression:
* sips (part of MAC OSX)
* optipng [download here](http://optipng.sourceforge.net/), and see [command line reference manual](http://optipng.sourceforge.net/optipng-0.7.4.man.pdf)

Reference Articles:
* http://www.longtailvideo.com/support/jw-player/31804/basic-tooltip-thumbs
* http://www.longtailvideo.com/support/jw-player/31778/adding-tooltip-thumbnails/

Sample Usage:

    python makesprites.py /path/to/myvideofile.mp4

You may want to customize the the following variables in makesprites.py:

    USE_SIPS = True         # True if using MacOSX (creates slightly smaller sprites), else set to False to use ImageMagick resizing
    USE_OPTIPNG = True      # True to use optipng to further compress PNG files, False to skip or if not installed
    THUMB_RATE_SECONDS=45   # every Nth second take a snapshot of the video (tested with 30,45,60)
    THUMB_WIDTH=100         # 100-150 is width recommended by JWPlayer, smaller size = smaller sprite for user to download

And just for reference, here's a simplified version of my JWPlayer javascript that links the VTT file to my videos (which are listed in an external SMIL file). 

    <script>
    jwplayer('player1').setup({
        width: '100%',
        aspectratio: "711:400",
        primary: "flash",
        playlist: [{
            sources: [{
                file: "/video/smil/153/",
                type: "rtmp",
            }],
            tracks:[{
                file: "http://www.myserver.com/static/inc/th/myvideofile_thumbs.vtt",
                kind: "thumbnails"
            }]
        }]
    });
    </script>
    
And a sample of a generated WebVTT file.

<pre>
WEBVTT

00:00:00.000 --> 00:00:35.000
myvideofile_sprite.png#xywh=0,0,100,55

00:00:35.000 --> 00:01:20.000
myvideofile_sprite.png#xywh=100,0,100,55

00:01:20.000 --> 00:02:05.000
myvideofile_sprite.png#xywh=200,0,100,55

00:02:05.000 --> 00:02:50.000
myvideofile_sprite.png#xywh=300,0,100,55

00:02:50.000 --> 00:03:35.000
myvideofile_sprite.png#xywh=0,55,100,55

00:03:35.000 --> 00:04:20.000
myvideofile_sprite.png#xywh=100,55,100,55
</pre>

    
batchsprites.py
--------------
Sample wrapper script for batch processing a bunch of videos, to make sprites & VTT files for each one, then copy them to a target folder,
where they will be web-accessible by JWPlayer track URL.  Note - this URL must use same domain as your webserver (per JWPlayer).

Expects a file name as input. File should be simple text file containing a list of video files (with fully qualified paths or relative paths from script directory).
It generates thumbnails/sprites for each video, then copies the sprite & vtt file to a destination folder defined in the `OUTPUT_FOLDER` variable.

Usage:

    python batchsprites.py filelist.txt

Sample filelist.txt contents:

    /Users/vlanard/valbiz/video/video1_circ5.mp4
    ../../archive/an/video1_circ1n2_wc_1500.m4v
    ../../archive/an/video1_circ1n4_wc_1500.m4v
    ../../archive/an/video1_circ2n3_wc_1500.m4v
    ../../archive/an/video1_circ3n4_wc_1500.m4v
