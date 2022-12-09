"""
    Uses x, y, z coordinate system
        x - left/right, y - up/down, z - forward/back
"""

import simplegui
import math
import time

""" Renderer """
windowSize = (1280, 720)
aspectRatio = windowSize[0] / windowSize[1]
vertexBuffer = []
drawOrder = []
lastTime = 0
currentTime = 0

""" Objects """
""" Camera """
# Overhead
cameraOrigin = [0, 0, -5]
cameraRotationEulers = [0, 0, 0] # (0, 0, 0) faces the positive z
cameraVelocity = [0, 0, 0]
frustumVertical = 0
frustumHorizontal = 0

# Data
cameraVerticalFOV = 90
cameraHorizontalFOV = 0 # Editing value will do nothing, calculated based upon cameraVerticalFOV
cameraMoveSpeed = 1

""" Cube """
# Overhead
# FUR, FUL, FLR, FLL, CUR, CUL, CLR, CLL
pointDirectionVectors = ["000", "100", "010", "110", "001", "101", "011", "111"]
cubeOrigin = [0, 0, 0]
cubeRotationEulers = [0, 0, 0]
cubePoints = []
# Data
cubeColor = "Green"
sideLength = 1

def GatherInput():
    global sideLength
    global cameraOrigin
    global cameraMoveSpeed
    
    input("[DISCLAIMER]\nThis is merely a demonstration and a work in progress\nThere are still many errors\n\n[PRESS ENTER TO CONTINUE]")
    
    sideLength = int(input("How large would you like the cube to be?"))
    cameraOrigin[2] = -sideLength - 5
    cameraMoveSpeed = int(input("How fast would you like the camera to move?"))

def DeltaTime():
    return currentTime - lastTime

def GenerateVectors():
    global pointDirectionVectors
    
    multiplier = 1
    finalVectors = []
    
    for binary in pointDirectionVectors:
        vector = []
        for i in range(3):
            if binary[i] == "1":
                multiplier = -1
            else:
                multiplier = 1
            vector.append(1 * multiplier)
        finalVectors.append(list(vector))
        
    pointDirectionVectors = finalVectors
    
def CalculateHorizontalFOV():
    global cameraHorizontalFOV
    global frustumVertical
    global frustumHorizontal
    
    unitVertical = math.tan(math.radians(cameraVerticalFOV / 2)) * 2
    unitHorizontal = unitVertical * aspectRatio
    
    horizontalFOV = math.degrees(math.atan2(unitHorizontal / 2, 1) * 2)
    
    cameraHorizontalFOV = horizontalFOV
    
    frustumVertical = unitVertical
    frustumHorizontal = unitHorizontal
    
def GenerateDrawOrder():
    global drawOrder
    
    # Far
    drawOrder.append("0230")
    drawOrder.append("0310")
    # Upper
    drawOrder.append("4014")
    drawOrder.append("4154")
    # Lower
    drawOrder.append("2672")
    drawOrder.append("2732")
    # Left
    drawOrder.append("1371")
    drawOrder.append("1751")
    # Right
    drawOrder.append("4624")
    drawOrder.append("4204")
    # Close
    drawOrder.append("5765")
    drawOrder.append("5645")
    
def InitConstants():
    GenerateVectors()
    CalculateHorizontalFOV()
    GenerateDrawOrder()
    
def Pythagorean(a, b):
    h = math.sqrt((a ** 2) + (b ** 2))
    return h

#def Flatten

def CalculateVerticalPlacement(point):
    horizontalDistance = math.fabs(cameraOrigin[2] - point[2])
    verticalDistance = math.fabs(cameraOrigin[1] - point[1])
    
    angleFromCam = math.degrees(math.atan2(verticalDistance, horizontalDistance))
    heightFromCam = math.tan(math.radians(angleFromCam))
    
    distanceFromTop = frustumVertical / 2
    if point[1] < cameraOrigin[1]:
        distanceFromTop += heightFromCam
    else:
        distanceFromTop -= heightFromCam
    
    screenSpaceComponent = distanceFromTop / frustumVertical
        
    return screenSpaceComponent
    
def CalculateHorizontalPlacement(point):
    horizontalDistance = math.fabs(cameraOrigin[0] - point[0])
    verticalDistance = math.fabs(cameraOrigin[2] - point[2])
    
    angleFromCam = math.degrees(math.atan2(horizontalDistance, verticalDistance))
    widthFromCam = math.tan(math.radians(angleFromCam))
    
    distanceFromLeft = frustumHorizontal / 2
    if point[0] < cameraOrigin[0]:
        distanceFromLeft -= widthFromCam
    else:
        distanceFromLeft += widthFromCam
        
    screenSpaceComponent = distanceFromLeft / frustumHorizontal
    return screenSpaceComponent

def CalculateScreenCoordinates(point):
    x = CalculateHorizontalPlacement(point) * windowSize[0]
    y = CalculateVerticalPlacement(point) * windowSize[1]
    
    return (x, y)
    
def Generate3DCubePoints():
    global cubePoints
    
    workingLength = sideLength / 2
    workingPoints = []
    
    for vector in pointDirectionVectors:
        point = []
        for i in range(0, 3):
            point.append(vector[i] * workingLength)
        workingPoints.append(point)
        
    cubePoints = workingPoints

def MoveCamera():
    global cameraOrigin
    
    for i in range(0, 3):
        cameraOrigin[i] += cameraVelocity[i] * DeltaTime()
    
def DownHandler(key):
    global cameraVelocity
    
    if key == 87:
        cameraVelocity[2] += cameraMoveSpeed
    elif key == 65:
        cameraVelocity[0] -= cameraMoveSpeed
    elif key == 83:
        cameraVelocity[2] -= cameraMoveSpeed
    elif key == 68:
        cameraVelocity[0] += cameraMoveSpeed
    elif key == 32:
        cameraVelocity[1] += cameraMoveSpeed
    elif key == 16:
        cameraVelocity[1] -= cameraMoveSpeed
    
def UpHandler(key):
    global cameraVelocity
    
    if key == 87:
        cameraVelocity[2] -= cameraMoveSpeed
    elif key == 65:
        cameraVelocity[0] += cameraMoveSpeed
    elif key == 83:
        cameraVelocity[2] += cameraMoveSpeed
    elif key == 68:
        cameraVelocity[0] -= cameraMoveSpeed
    elif key == 32:
        cameraVelocity[1] -= cameraMoveSpeed
    elif key == 16:
        cameraVelocity[1] += cameraMoveSpeed
    
def draw(canvas):
    global vertexBuffer
    global currentTime
    global lastTime
    
    currentTime = time.time()
    
    MoveCamera()
    
    Generate3DCubePoints()
    vertexBuffer = []
    
    for vertex in cubePoints:
        vertexBuffer.append(CalculateScreenCoordinates(vertex))
        
    for tri in drawOrder:
        vertecies = []
        for i in range(0, 4):
            vertecies.append(vertexBuffer[int(tri[i])])
        canvas.draw_polyline(vertecies, 1, "Green")
        
    lastTime = currentTime

# Create a frame and assign callbacks to event handlers
InitConstants()

GatherInput()

frame = simplegui.create_frame("3D", windowSize[0], windowSize[1])
frame.set_keydown_handler(DownHandler)

frame.add_label("Controls:", 50)
frame.add_label("W/S = Forward/Back",)
frame.add_label("A/D = Left/Right")
frame.add_label("Space/Shift = Up/Down")

frame.set_keyup_handler(UpHandler)
frame.set_draw_handler(draw)
frame.start()