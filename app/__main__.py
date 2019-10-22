import os

from os import path, makedirs
import numpy as np
from requests.utils import quote
from skimage.measure import find_contours, points_in_poly, approximate_polygon
from skimage import io
from skimage import color
from threading import Thread


# Our home on google maps: https://www.google.com/maps/place/704+N+Madeira+St,+Baltimore,+MD+21205/@39.299129,-76.5863645,20z/data=!4m5!3m4!1s0x89c80465cdcc3777:0xad15178619e0a8a5!8m2!3d39.2991228!4d-76.5860862
# Print of urlBuildings: http://maps.googleapis.com/maps/api/staticmap?center=39.299129,-76.5863645&zoom=20&format=png32&sensor=false&size=600x600&key=AIzaSyC7vVBPCrVhXzj-Dug1B-cPlUsiTw4p5-4&maptype=roadmap&style=visibility:off&style=feature%3Alandscape.man_made%7Celement%3Ageometry.stroke%7Cvisibility%3Aon%7Ccolor%3A0xffffff%7Cweight%3A1
center_latitude = 39.299129 
center_longitude = -76.5863645 
zoom = 20
midX = 300
midY = 300
key = os.getenv('GOOGLE_API_KEY')
config = {
    'output': {
        'directory': './output'
    }
}
images = {
    'source': {
        'value': None,
        'save': True,
        'save_name': 'source.png'
    },
    'grayscale': {
        'value': None,
        'save': True,
        'save_name': 'grayscale.png'
    },
    'binary': {
        'value': None,
        'save': True,
        'save_name': 'binary.png'
    },
}

def getBuildingsMap(center_latitude, center_longitude, zoom, midX, midY, key):  # Styled google map showing only building outlines.
    str_Center = str(center_latitude) + ',' + str(center_longitude)
    str_Size = str(midX*2) + 'x' + str(midY*2)  # Not really sure the ideal size to use here.
    mapZoom = str(zoom)
    safeURL_Style = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xffffff|weight:1')
    urlBuildings = "http://maps.googleapis.com/maps/api/staticmap?center=" + str_Center + "&zoom=" + mapZoom + "&format=png32&sensor=false&size=" + str_Size + "&key=" + key + "&maptype=roadmap&style=visibility:off&style=" + safeURL_Style
    # print('Query: ' + urlBuildings)  # DEBUG
    return urlBuildings

def save_images(image_input, options):
    if not path.exists(options['directory']):
        makedirs(options['directory'])
    # Note: Not sure what this does exactly, but should have somethign to do with image quality.
    # I get the following warning.
    #   C:\Anaconda3_2.5.0_3.5.1_64\lib\site-packages\skimage\util\dtype.py:111: 
    #   UserWarning: Possible precision loss when converting from float64 to uint16 "%s to %s" % (dtypeobj_in, dtypeobj))
    # io.use_plugin('freeimage')

    # Note: The following two lines are probably easier to read.
    # for image in images:
        # if images[image]['save'] is True:
    for image in [v for k, v in image_input.items() if v['save'] is True]:
        io.imsave('output/' + image['save_name'], image['value'])

def getPixelCoordinatesOfBuildings(urlBuildings, midX, midY):
    images['source']['value'] = io.imread(urlBuildings)
    images['grayscale']['value'] = color.rgb2gray(images['source']['value'])
    # Will create inverted binary image.
    images['binary']['value'] = np.where(images['grayscale']['value'] > np.mean(images['grayscale']['value']), 0.0, 1.0)
    contours = find_contours(images['binary']['value'], 0.1)

    for n, contourBuilding in enumerate(contours):
        if (contourBuilding[0, 1] == contourBuilding[-1, 1]) and (contourBuilding[0, 0] == contourBuilding[-1, 0]):
            # Check if it is inside any other polygon, so this will remove any additional elements.
            isInside = False
            skipPoly = False
            for othersPolygon in contours:
                isInside = points_in_poly(contourBuilding, othersPolygon)
                if all(isInside):
                    skipPoly = True
                    break

            if skipPoly == False:
                center_inside = points_in_poly(np.array([[midX, midY]]), contourBuilding)
                if center_inside:
                    # Approximate will generalize the polygon.
                    mainBuilding = approximate_polygon(contourBuilding, tolerance=2)
                    print('Main building: ' + str(mainBuilding))  # DEBUG

if __name__ == '__main__': 
    urlBuildings = getBuildingsMap(center_latitude, center_longitude, zoom, midX, midY, key)
    getPixelCoordinatesOfBuildings(urlBuildings, midX, midY)
    save_images(images, config['output'])
