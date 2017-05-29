import numpy as np
from requests.utils import quote
from skimage.measure import find_contours, points_in_poly, approximate_polygon
from skimage import io
from skimage import color
from threading import Thread

center_latitude = None ##put latitude here 
center_longitude = None ##put longitude here 
mapZoom = str(20)
midX = 300
midY = 300
# Styled google maps url showing only the buildings
safeURL_Style = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xffffff|weight:1')
urlBuildings = "http://maps.googleapis.com/maps/api/staticmap?center=" + str_Center + "&zoom=" + mapZoom + "&format=png32&sensor=false&size=" + str_Size + "&maptype=roadmap&style=visibility:off&style=" + safeURL_Style

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

print(mainBuilding)