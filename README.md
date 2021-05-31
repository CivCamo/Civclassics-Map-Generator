# Civclassics-Map-Generator
*A python based generator for automatically creating an image of the [Civclassics](https://www.reddit.com/r/civclassics/) world political claims.*

![mapheaderImage](/mapGenHeader.png)

### How it works:

This generator works by pulling the polygon data from [CCmap's](http://ccmap.github.io) github, claims can be submitted through the [Unified Map project's discord](https://discord.gg/hKJ9hQXB5S), also known as the IMC. Which then creates a few matplotlib fills, then exports, resizes, creates a few files, then overlays and merges other images (such as `ocean.png`, which you can customise the colour of, or even comment out!) onto the `basemap.png` file.

*The `basemap.png` file and the script are the only files you need to generate a map.*

In the end, you'll have a file called `mapNoBackground.png`, which you can use for the basis of your map! You can add a solid background colour by looking towards the end of the script, and uncommenting a few lines out - I left these because it may be more desirable to manually take things from here, and there is still work to be done.

The generator will also do text, however this is somewhat slow and inaccurate, and manual editing is still required at this point. Increasing the variables `    dpiRes = 500`, `width = 5000`, and `height = 5000` will also effect speed of both the polygon's and text generation. The vars currently set seem to be a good compromise between quality and speed.

### Requirements:

* python3.7
* pip3

### Pip modules:

* opencv_python
* matplotlib
* blend_modes
* requests
* numpy
* adjustText
* Pillow

*if these don't work with the latest version, set an env up and use the `requirements.txt` file*

### Usage:
```
python civMapGen.py
```
