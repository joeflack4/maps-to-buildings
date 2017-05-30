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
key = 'AIzaSyC7vVBPCrVhXzj-Dug1B-cPlUsiTw4p5-4'

def getBuildingsMap(center_latitude, center_longitude, zoom, midX, midY, key):  # Styled google map showing only building outlines.
    str_Center = str(center_latitude) + ',' + str(center_longitude)
    str_Size = str(midX*2) + 'x' + str(midY*2)  # Not really sure the ideal size to use here.
    mapZoom = str(zoom)
    safeURL_Style = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xffffff|weight:1')
    urlBuildings = "http://maps.googleapis.com/maps/api/staticmap?center=" + str_Center + "&zoom=" + mapZoom + "&format=png32&sensor=false&size=" + str_Size + "&key=" + key + "&maptype=roadmap&style=visibility:off&style=" + safeURL_Style
    # print('Query: ' + urlBuildings)  # Debugging.
    return urlBuildings

def getPixelCoordinatesOfBuildings(urlBuildings, midX, midY):
    mainBuilding = None
    imgBuildings = io.imread(urlBuildings)
    gray_imgBuildings = color.rgb2gray(imgBuildings)
    # will create inverted binary image
    binary_imageBuildings = np.where(gray_imgBuildings > np.mean(gray_imgBuildings), 0.0, 1.0)
    contoursBuildings = find_contours(binary_imageBuildings, 0.1)

    for n, contourBuilding in enumerate(contoursBuildings):
        if (contourBuilding[0, 1] == contourBuilding[-1, 1]) and (contourBuilding[0, 0] == contourBuilding[-1, 0]):
            # check if it is inside any other polygon, so this will remove any additional elements
            isInside = False
            skipPoly = False
            for othersPolygon in contoursBuildings:
                isInside = points_in_poly(contourBuilding, othersPolygon)
                if all(isInside):
                    skipPoly = True
                    break

            if skipPoly == False:
                center_inside = points_in_poly(np.array([[midX, midY]]), contourBuilding)
                if center_inside:
            # approximate will generalize the polygon
                    mainBuilding = approximate_polygon(contourBuilding, tolerance=2)

    print('Main building: ' + mainBuilding)

if __name__ == '__main__': 
    urlBuildings = getBuildingsMap(center_latitude, center_longitude, zoom, midX, midY, key)
    getPixelCoordinatesOfBuildings(urlBuildings, midX, midY)
