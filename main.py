# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
import PIL
import vispy
import numpy as np
from vispy import scene, app, use
from vispy.color import Color
from vispy.io import imread, load_data_file, read_mesh
from vispy.scene.visuals import Mesh
from vispy.scene import transforms
from vispy.visuals.filters import TextureFilter, InstancedShadingFilter
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.scene.visuals import InstancedMesh
from vispy.io import read_png
from vispy.scene import visuals
from vispy.util import load_data_file
from scipy.spatial.transform import Rotation
import PyQt6
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pathlib
import OpenGL
from OpenGL import *

use(app='PyQt6', gl='gl+')  # needed for instanced

max_score = 12.2
diam: float = 0  # telecope diam global var
clicked_star: float = []  # clicked star global variable
angres: float = 0  # telescope angular resolution
pixres: float = 0  # telescope pixel resolution
resolution: float = 0  # telescope resolution as MAX(pixres, angres)
wavelength: float = 400  # telescope wavelength in nm
pixel_size: float = 6  # telescope pixel size
focal_dist: float = 1  # telescope focal distance

planets_visible: int = 0
total_telescope_score: float = 0  # total score for planets visible using given telescope config

  # telescope dictionary: sorted this way: diameter, focal length, pixel size
telescope_dic ={
    "Webb": [6.5, 131.4, 2.4],  #JWST pixel size is approx, as it has different pixel sizes in NIRCAM
    "Hubble": [2.4, 56.7, 10],
    "Kepler": [0.95, 27, 244],
}

script_directory = pathlib.Path(__file__).parent.resolve()
print('Set script directory as ', str(script_directory))
# reading stars
print("Reading stars from BSC...")
with open(str(script_directory) + "/files/bsc5.dat") as BSC_catalog:
    BSC_stars_raw = BSC_catalog.readlines()

#print(BSC_stars_raw[1])
print("Extracting BSC stars")
stars = []  # array for extracted data
star = [0] * 9  # an array that represents a star as follows
# extracting the following in order: 0 name (des), 1 HIP des (???). 2 RA (deg), 3 DEC (deg) (ALL 2000), 4 mag, 5 b-v
print(len(BSC_stars_raw), ' stars found in BSC')
for raw_star in BSC_stars_raw:

    if (not (raw_star[5:9] == ("NOVA"))):  # checks for novas and proceeds only if none found

        if not raw_star[75:77] == '  ':  # checks for blank line (novas and some else)
            # print(raw_star)

            star = [0] * 9

            star[0] = raw_star[4:14]  # name, Bayer or Flamsteed

            # print(raw_star[75:77]) or 76 77 according to file
            # print(raw_star[77:79])
            # print(raw_star[79:83])
            # RA hrs mins and seconds
            star[2] = 15 * (float(raw_star[75:77]) + float(raw_star[77:79]) / 60 + float(raw_star[79:83]) / 3600)
            # DEC deg mins and seconds
            star[3] = (float(raw_star[84:86]) + float(raw_star[86:88]) / 60 + float(raw_star[88:90]) / 3600)
            if raw_star[83] == '-':  # sets correct sign for declination
                star[3] *= -1

            # mag and color index Vmag 103-107 B_V 110-114
            try:
                star[4] = float(raw_star[102:107])
            except:
                star[4] = 6.0  # default value of 6
                print('no vmag, setting def')
            try:
                star[5] = float(raw_star[109:114])
            except:
                star[5] = 0.0
                # print('no B-V found, setting def')

            # stars[6] is an array of planets
            star[6] = []

            star[7] = -1  # points that mean how interesting the star is; these are equal to the highest ponts of a planet in the system or -1 if no planet
            star[8] = 4600 * (1/(0.92*star[5]+1.7)+1/(0.92*star[5]+0.62))  # Ballesteros' formula to get temp from B-V
            stars.append(star)
    else:
        print("NOVA DETECTED, skipped")

# planets

print("Reading from planet database...")
with open(str(script_directory) + "/files/final.txt") as planet_catalog:
    planet_catalog_raw = planet_catalog.readlines()



print("Reading planet parameters...")


with open(str(script_directory) + "/files/ea.csv") as ea:  # Exoplanet Archive
    Ea = ea.readlines()
    for i in range(len(Ea)):
        Ea[i] = Ea[i].split(';') #for some reason excel owerwrote the csv with ; so use ; instead of , if csv is from xcel

def restructure_data_file(file):
    for i in range(1, len(file)):
        line = file[i]
        last_space_ind = line.rfind(' ')
        if line.rfind('no data') is None: #line[last_space_ind+1:] == 'data':
            cut_line = line[0:last_space_ind]
            second_space_id = cut_line.rfind(' ')
            file[i] = [line[0:second_space_id], round(float(line[second_space_id+1:last_space_ind]), 2), round(float(line[last_space_ind+1:]),2)]
        else:
            no_data_i = line.rfind('no data')
            file[i] = [line[0:no_data_i], 'none', 'no data']
    return file

# planet format^ 0 pl_name,  1 points, 2 dist(pa), 3 ra(deg), 4 dec(deg), 5 magn, 6 mas,
# 7 temperature 8 ro density 9 g 10 tstar 11 radius of the planet in RE 12 distance to main star (semimajoraxis) 13 mass 14 parent star vmag
# reads the planet data this part finds stars for the planets in the database file, if not found - adds the stars. planets are in star array
for planet_raw in planet_catalog_raw:

    planet = planet_raw.split(',')

    for i in range (8): planet.append('')

    #print(len(planet))

    if not (planet[0] == 'pl_name'):  # filters away the first row of the document
        star_name = planet[0][0:-2]

        for i in range(1, 6):  # tries to convert values to floats
            try:
                planet[i] = float(planet[i])
            except:

                # print('planet', 'not found field', i)
                # if planet[i] == '':
                # print('field empty')
                # else:
                # print(planet[i])
                planet[i] = 'Unknown'

        # processing the parameter files
        for Ealine in Ea:
            #print('Ealine', Ealine[0])
            #print('planet', planet[0])
            if Ealine[0] == planet[0]:
                #print('found coinc', Ealine[0])
                if not (Ealine[11] is None or Ealine[11] == ''):  #Planet surface temperature
                    planet[7] = float(Ealine[11])
                else:
                    planet[7] = 'Unknown'

                if not (Ealine[8] is None or Ealine[8] == ''):  #Planet radius in Earth radii
                    planet[11] = float(Ealine[8])
                else:
                    planet[11] = 'Unknown'

                if not (Ealine[7] is None or Ealine[7] == ''):  #Orbit semi major axis (radius, but not really)
                    planet[12] = float(Ealine[7])
                else:
                    planet[12] = 'Unknown'

                if not (Ealine[12] is None or Ealine[12] == ''):  # Temperature of the main star
                    planet[10] = float(Ealine[12])
                else:
                    planet[10] = 'Unknown'

                if not (Ealine[19] is None or Ealine[19] == '' or Ealine[19] == '\n'):  # Vmag of the main star
                    planet[14] = float(Ealine[19])
                else:
                    planet[14] = 6

                if not (Ealine[9] is None or Ealine[9] == ''):  # Planet mass and derived params
                    planet[13] = float(Ealine[9])

                    if not (planet[11] is None or planet[11] == '' or planet[11] == 'Unknown'):
                        # Calculating rho, etc

                        # rho
                        planet[8] = planet[13] / (planet[11] ** 3) * 5.51
                        # g
                        planet[9] = planet[13] / (planet[11] ** 2) * 9.81

                    else:
                        planet[9] = 'Unknown'
                        planet[8] = 'Unknown'


                else:
                    planet[13] = 'Unknown'
                    planet[9] = 'Unknown'
                    planet[8] = 'Unknown'





                #print('found', planet)


        starFound = False  # marker whether the corresponding star for this planet was found in the database

        for star in stars:  # attempts to find the star corresponding to the planet

            if (abs(star[2] - planet[3]) < 0.001) and (abs(star[3] - planet[4]) < 0.001):
                # print('star found', star_name, star[0])
                star[6].append(planet)

                # point value of a star = highest pont value of a planet near it
                if star[7] < planet[1]:
                    star[7] = planet[1]

                starFound = True

        if not starFound:
            # if no such star found - add new star to catalog
            # coordinates are equal to the coords from the planet data
            # add the found planet in the planets array and assign its points score to the star
            stars.append([star_name, 0, planet[3], planet[4], planet[14], 0, [planet], planet[1], planet[10]])
            # 0 - placeholder
            # 6, 0 - placeholders for stars` Vmag and B-v! Compute/query later!
            # print('added star', [star_name, 0, planet[3], planet[4], 6, 0, [planet], planet[1]])

    #

# setup canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 800), show=True)

# Set up a viewbox t
view = canvas.central_widget.add_view()
view.bgcolor = 'b'
view.camera = 'panzoom'
view.padding = 1

color = Color("#3f51b5")  # color for box
grids = vispy.scene.visuals.GridLines((1, 1), color='w', parent=view.scene)
border = Color("#5ad5a4")

# create the stars positions array
n = len(stars)  # number of stars to draw

print('stars in database:', n)

pos = np.zeros((n, 3), dtype=np.float32)
colors = np.ndarray
  # setting star colors
for i in range(0, n):
    star = stars[i]
    pos[i][0] = np.float32(star[2])
    pos[i][1] = np.float32(star[3])
    pos[i][2] = 0
    color = Color('#ffffff')
    np.append(colors, color)  # setting color

print(pos.ndim)

# reading and adding the plane/billboard mesh for star display

try:
    texture_path = load_data_file(str(script_directory) + '/files/star_Sprite.png')
    mesh_path = load_data_file(str(script_directory) + '/files/star_Mesh_.obj')
    print(mesh_path)
except:
    print('file not found')

vertices, faces, normals, texcoords = read_mesh(mesh_path)
texture = np.flipud(imread(texture_path))

n_instances = n

instance_colors = [(1, 1, 1)] * n_instances

instance_positions = pos
face_colors = np.random.rand(len(faces), 3)
instance_transforms = []
# from_euler('z', 90, degrees=True)
instance_transforms = [Rotation.identity().as_matrix().astype(np.float32)] * n_instances
matrix = np.zeros((3, 3), np.float32)
# matrix=Rotation.from_euler('z', 90, degrees=True).as_matrix().astype(np.float32)
# print(instance_transforms[1])
# print(vispy.visuals.transforms.MatrixTransform(matrix=None).scale((1000, 0.1, 0.1)))
for i in range(n):
    scale = 1.4 * (np.exp(-stars[i][4] / 3))
    instance_transforms[i] = [[scale, 0, 0], [0, scale, 0], [0, 0, scale]]  # *instance_transforms[i]

print(instance_transforms[1])
# Create a colored `MeshVisual`.
mesh = InstancedMesh(
    vertices,
    faces,
    instance_colors=instance_colors,
    face_colors=face_colors,
    instance_positions=instance_positions,
    instance_transforms=instance_transforms,
    parent=view.scene,

)

# wireframe_filter = WireframeFilter(width=1)
shading_filter = InstancedShadingFilter(None, shininess=1)
texture_filter = TextureFilter(texture, texcoords)
# mesh.attach(wireframe_filter)
mesh.attach(shading_filter)
mesh.attach(texture_filter)
alpha_filter = Alpha()
mesh.attach(alpha_filter)

# clipper=vispy.visuals.filters.clipper.Clipper()#bounds=(0, 0, 1, 1), transform=None)
# mesh.attach(clipper)

# marker mesh

try:
    marker_mesh_path = load_data_file(str(script_directory) + '/files/marker_circ.obj')
except:
    print('file not found')

markers = []

for star in stars:
    if len(star[6]) > 0:  # if star has a planet - add to markers list
        markers.append([star[2], star[3], star[7], star[4]])
        # ra, dec, score, Vmag for size

mark_vertices, mark_faces, mark_normals, mark_texcoords = read_mesh(marker_mesh_path)
# texture = np.flipud(imread(texture_path))

mark_n_instances = len(markers)

mark_instance_colors = [(1, 1, 1)] * mark_n_instances

mark_pos = np.zeros((mark_n_instances, 3), dtype=np.float32)

#marker colors and positions
for i in range(mark_n_instances):
    marker = markers[i]
    mark_pos[i][0] = np.float32(marker[0])
    mark_pos[i][1] = np.float32(marker[1])
    mark_pos[i][2] = 0
    mark_instance_colors[i] = np.clip([np.clip((1 - marker[2] / max_score)**2, 0, 1), np.clip((marker[2] / max_score)**0.5, 0, 1), np.clip((marker[2]/max_score - 0.5)**2-0.5, 0, 1)],0,1)

mark_instance_positions = mark_pos
mark_face_colors = np.random.rand(len(mark_faces), 3)
mark_instance_transforms = [Rotation.identity().as_matrix().astype(np.float32)] * mark_n_instances
for i in range(mark_n_instances):
    try:
        scale = 5 * (np.exp(- markers[i][3] / 8)) * (markers[i][2] / max_score + 0.5)
    except:
        scale = 1
        #print(markers[i], np.exp(-markers[i][3] / 3),)
    mark_instance_transforms[i] = [[scale, 0, 0], [0, scale, 0], [0, 0, scale]]  # *instance_transforms[i]

#print(mark_instance_transforms[1])
# Create a colored `MeshVisual`.
markerMesh = InstancedMesh(
    mark_vertices,
    mark_faces,
    instance_colors=mark_instance_colors,
    face_colors=mark_face_colors,
    instance_positions=mark_instance_positions,
    instance_transforms=mark_instance_transforms,
    parent=view.scene,

)

# wireframe_filter = WireframeFilter(width=1)
mark_shading_filter = InstancedShadingFilter(None, shininess=1)
# texture_filter = TextureFilter(texture, texcoords)
# mesh.attach(wireframe_filter)
markerMesh.attach(mark_shading_filter)
# markerMesh.attach(texture_filter)
mark_alpha_filter = Alpha()
markerMesh.attach(mark_alpha_filter)


def setPreset(name):
    global pixel_size
    global focal_dist
    global diam
    tel = telescope_dic[name]
    diam = tel[0]
    focal_dist = tel[1]
    pixel_size = tel[2]

    win.focalSlider.setSliderPosition(int(focal_dist*10))
    win.pixsizeSlider.setSliderPosition(int(pixel_size*10))
    win.diamSlider.setSliderPosition(int(diam*10))



    #placeholder

def calculatePlanetVis():
    global planets_visible
    global total_telescope_score
    planets_visible = 0
    total_telescope_score = 0

    for star in stars:
        if len(star[6]) > 0:
             for planet in star [6]:
                 if not (planet[6] == 'no data' or planet[6] == 'Unknown' or planet[6] == ''):
                     if float(planet [6]) > resolution:
                          planets_visible += 1
                          total_telescope_score += planet[1]
    win.planetsObs.setText('Planets observed: ' + str(planets_visible) + '\nTotal score: ' + str(sround(total_telescope_score, 2)))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NyAHWO: Navigator Application for Habitable Worlds Observatory")
        # grid = QGridLayout()
        #self.button = QPushButton("Press Me!")
        #self.button.clicked.connect(self.the_button_was_clicked)

        layout = QHBoxLayout()
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(layout)
        leftSidebar = QWidget()
        leftSidebar.setLayout(QVBoxLayout())
        leftSidebar.setMinimumSize(330, 200)
        widget.layout().addWidget(leftSidebar)
        widget.layout().addWidget(canvas.native)  # main canvas viewport
        #widget.layout().addWidget(self.button)  # example button

        # sidebar for planet data
        self.sidebar = QDockWidget('System info', self)
        self.sidebar.setFloating(False)
        self.sidebar.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.sidebar.DockWidgetCloseable = False  # doesnt work!!!
        self.sidebar.setLayout(QVBoxLayout())
        self.sidebar.setMinimumSize(330, 500)
        # self.sidebar.setFeatures(DockWidgetCloseable = False) #the sidebar cannot be closed
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidebar)
        sidebarWidget = QWidget()
        sidebarWidget.setLayout(QVBoxLayout())
        self.list = QLabel(self)
        self.list.setWordWrap(True)
        self.list.setFont(QFont('Consolas', 14))
        self.list.setMinimumSize(320, 200)
        self.sidebar.setWidget(sidebarWidget)
        # self.sidebar.layout().addWidget(sidebarWidget)
        sidebarWidget.layout().addWidget(self.list)

        containerForTabs = QWidget()
        containerForTabs.setLayout(QVBoxLayout())
        self.planetTabs = QTabWidget(containerForTabs)
        self.planetTabs.labels = [QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel()]

        for k in range(len(self.planetTabs.labels)):
            self.planetTabs.addTab(self.planetTabs.labels[k], "Pl " + str(k + 1))
            self.planetTabs.labels[k].setFont(QFont('Consolas', 14))
        containerForTabs.layout().addWidget(self.planetTabs)
        sidebarWidget.layout().addWidget(containerForTabs)

        # left sidebar setup

        lsbLabel = QLabel()
        lsbLabel.setText('Telescope setup')
        lsbLabel.setFont(QFont('Consolas', 14))
        leftSidebar.layout().addWidget(lsbLabel)
        telescopeImg = QLabel()
        pixmap = QPixmap('C:/Users/Admin/PycharmProjects/spaceapps24/files/hwo.png')
        telescopeImg.setPixmap(pixmap.scaled(250, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        leftSidebar.layout().addWidget(telescopeImg)

        self.diamslname = QLabel()
        self.diamslname.setFont(QFont('Consolas', 14))
        self.diamslname.setText('Telescope diameter, m: 4')
        leftSidebar.layout().addWidget(self.diamslname)

        self.diamSlider = QSlider(Qt.Orientation.Horizontal, self)  # telescope diameter slider: in D*10 vals for finer control
        self.diamSlider.setMinimum(10)
        self.diamSlider.setMaximum(100)
        self.diamSlider.setSliderPosition(40)
        self.diamSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.diamSlider.setTickInterval(5)
        self.diamSlider.valueChanged.connect(self.diamchange)
        leftSidebar.layout().addWidget(self.diamSlider)

        self.focalslname = QLabel()
        self.focalslname.setFont(QFont('Consolas', 14))
        self.focalslname.setText('Focal length, m: ')
        leftSidebar.layout().addWidget(self.focalslname)

        self.focalSlider = QSlider(Qt.Orientation.Horizontal, self)  # telescope focal length slider: in F*10 vals for finer control
        self.focalSlider.setMinimum(10)
        self.focalSlider.setMaximum(2000)
        self.focalSlider.setSliderPosition(40)
        self.focalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.focalSlider.setTickInterval(50)
        self.focalSlider.valueChanged.connect(self.diamchange)
        leftSidebar.layout().addWidget(self.focalSlider)

        self.pixsizeLabel = QLabel()
        self.pixsizeLabel.setFont(QFont('Consolas', 14))
        self.pixsizeLabel.setText('Pixel size:' + str(pixel_size) + ' mkm')
        leftSidebar.layout().addWidget(self.pixsizeLabel)

        self.pixsizeSlider = QSlider(Qt.Orientation.Horizontal, self)  # telescope pixel size in nm slider: in *10 vals for finer control
        self.pixsizeSlider.setMinimum(20)
        self.pixsizeSlider.setMaximum(3000)
        self.pixsizeSlider.setSliderPosition(40)
        self.pixsizeSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pixsizeSlider.setTickInterval(100)
        self.pixsizeSlider.valueChanged.connect(self.diamchange)
        leftSidebar.layout().addWidget(self.pixsizeSlider)

        self.angresLabel = QLabel()
        self.angresLabel.setFont(QFont('Consolas', 14))
        self.angresLabel.setText('Angular resolution: mas')
        self.pixresLabel = QLabel()
        self.pixresLabel.setFont(QFont('Consolas', 14))
        self.pixresLabel.setText('Pixel ang res: mas')
        self.resLabel = QLabel()
        self.resLabel.setFont(QFont('Consolas', 14))
        self.resLabel.setText('Total ang res: mas')
        leftSidebar.layout().addWidget(self.angresLabel)
        leftSidebar.layout().addWidget(self.pixresLabel)
        leftSidebar.layout().addWidget(self.resLabel)

        presetsWisget = QWidget()
        presetsWisget.setLayout(QHBoxLayout())
        presetsLabel = QLabel()
        presetsLabel.setText('Presets')
        presetsLabel.setFont(QFont('Consolas', 14))
        leftSidebar.layout().addWidget(presetsLabel)
        leftSidebar.layout().addWidget(presetsWisget)

        hubbleButton = QPushButton()
        hubbleButton.setText('Hubble')
        hubbleButton.setFont(QFont('Consolas', 14))
        presetsWisget.layout().addWidget(hubbleButton)
        hubbleButton.clicked.connect(self.setPrHubble)

        webbButton = QPushButton()
        webbButton.setText('Webb')
        webbButton.setFont(QFont('Consolas', 14))
        presetsWisget.layout().addWidget(webbButton)
        webbButton.clicked.connect(self.setPrWebb)

        hwoButton = QPushButton()
        hwoButton.setText('HWO')
        hwoButton.setFont(QFont('Consolas', 14))
        #presetsWisget.layout().addWidget(hwoButton)
        #hwoButton.clicked.connect(self.setPrHWO)

        KeplerButton = QPushButton()
        KeplerButton.setText('Kepler')
        KeplerButton.setFont(QFont('Consolas', 14))
        presetsWisget.layout().addWidget(KeplerButton)
        KeplerButton.clicked.connect(self.setPrKepler)

        self.planetsObs = QLabel()
        self.planetsObs.setFont(QFont('Consolas', 14))
        self.planetsObs.setText('Planets observebale: \nTotal score:')
        leftSidebar.layout().addWidget(self.planetsObs)


        #
    def setPrHubble(self):
        setPreset('Hubble')
        setPreset('Hubble')
        setPreset('Hubble')
    def setPrWebb(self):
        setPreset('Webb')
        setPreset('Webb')
        setPreset('Webb')

    def setPrHWO(self):
        setPreset('Hwo')

    def setPrKepler(self):
        setPreset('Kepler')
        setPreset('Kepler')
        setPreset('Kepler')
    def diamchange(self):
        global resolution
        global diam
        global focal_dist
        global pixres
        global angres
        global pixel_size
        diam = self.diamSlider.value()/10
        focal_dist = self.focalSlider.value()/10
        pixel_size = self.pixsizeSlider.value()/10
        angres = 1.22 * wavelength / diam * ((10**(-9))*180/np.pi*3600*1000)
        pixres = pixel_size / focal_dist * ((10**(-6))*180/np.pi*3600*1000)
        resolution = max(angres, pixres)
        self.diamslname.setText('Telescope diameter, m: ' + str(round(diam, 1)))
        self.focalslname.setText('Focal length, m: ' + str(round(focal_dist, 1)))
        self.angresLabel.setText('Angular resolution: ' + str(round(angres, 4)) + 'mas')
        self.pixresLabel.setText('Pixel ang res: ' + str(round(pixres, 4)) + 'mas')
        self.resLabel.setText('Total ang res: ' + str(round(resolution, 4)) + 'mas')
        self.pixsizeLabel.setText('Pixel size: ' + str(round(pixel_size, 1)) + 'mkm')

        calculatePlanetVis()

    #def focalchange(self):
    #    self.diamchange()

    def the_button_was_clicked(self):  # for debug
        print('clicked')


win = MainWindow()


@canvas.events.mouse_press.connect
def on_mouse_press(event):
    # print('click on canvas')
    clicked_mesh = canvas.visual_at(event.pos)
    # print(clicked_mesh)
    pos1, min, min_pos = get_view_axis_in_scene_coordinates(
        event.pos, mesh
    )
    # instance_pos = mesh.instance_positions[min_pos]
    clicked_star = stars[min_pos]
    num_of_planets = len(clicked_star[6])
    win.list.setText(
        f"Star: {clicked_star[0]} \nScore: {round(clicked_star[7], 2)} \nRA: {round(clicked_star[2], 3)} deg"
        f" \nDEC: {round(clicked_star[3], 3)} deg \n"
        f"Visual mag: {round(clicked_star[4], 2)}m \n"
        f"Temperature: {sround(clicked_star[8], 0)} K\n"
        f"Planets: {num_of_planets}")
    for k in range(len(win.planetTabs.labels)):
        if k < num_of_planets:
            win.planetTabs.labels[k].setText(planetToLabelText(clicked_star[6][k]))
        else:
            win.planetTabs.labels[k].setText("None")
    # print(f"event.pos : {event.pos}")
    # print(f"min distance : {min} and min_pos : {instance_pos}")
    # print("Object:", stars[min_pos])


def get_view_axis_in_scene_coordinates(gvpos, gvmesh):
    event_pos = np.array([gvpos[0], gvpos[1], 0, 1])
    instances_on_canvas = []
    # Translate each position to corresponding 2d canvas coordinates
    for instance in gvmesh.instance_positions:
        on_canvas = gvmesh.get_transform(map_from="visual", map_to="canvas").map(instance)
        on_canvas /= on_canvas[3:]
        instances_on_canvas.append(on_canvas)

    min = 10000
    min_pos = None
    # Find the closest position to the clicked position
    for i, instance_pos in enumerate(instances_on_canvas):
        # Not minding z axis
        temp_min = np.linalg.norm(
            np.array(event_pos[:2]) - np.array(instance_pos[:2])
        )
        if temp_min < min:
            min = temp_min
            min_pos = i

    return instances_on_canvas, min, min_pos



def planetToLabelText(planet): # formulates the label text for planet tabs, including whether they are visible
    visNote = 'Unknown'

    visFactor: float = 1
    try:
        #if not (planet[6] is None or planet[6] == 'Unknown' or planet[6] == 'no data'):

            visFactor = float(planet[6]) / resolution

            if visFactor >= 2:
                visNote = 'Good'
            elif visFactor >= 1:
                visNote = 'Low'
            else:
                visNote = 'Not visible'
    except:
        visNote = 'Unknown'
        print('caught exception trying to calculate vis')

    planetStr: str = f"Name:                 {planet[0]}\n" \
                     f"Score:                {sround(planet[1], 2)}\n" \
                     f"Distance, pc:         {sround(planet[2], 2)}\n" \
                     f"Mass, Mearth:         {sround(planet[13], 2)}\n" \
                     f"Radius. Rearth:       {sround(planet[11], 2)}\n" \
                     f"Density, kg/m3:       {sround(planet[8], 2)}\n" \
                     f"g, m/s2:              {sround(planet[9], 2)}\n" \
                     f"Temperature,K:        {sround(planet[7], 0)}\n" \
                     f"Ang. Separation, mas: {sround(planet[6], 5)}\n" \
                     f"Magnitude:            {sround(planet[5], 2)}\n" \
                     f"Visibility:           {visNote}"
    return planetStr

def sround(text, length):  # Aka Safe Round, it rounds the value if it is float, but passes it through if not (ex. 'Unknown')
    res = 0
    if length is None:
        length = 2

    try:
        res = round(float(text), length)
    except:
        res = text
    return res


# view.camera = 'arcball' # enable for debug

if __name__ == '__main__':
    canvas.measure_fps()


    win.focalSlider.setSliderPosition(focal_dist)
    win.diamchange()  # updates the sliders and telescope window to set default values

    win.show()
    app.run()
    # cant' put anything here - app run is an infinite loop, and only after it is closed code here can be run
