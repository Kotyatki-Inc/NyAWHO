import PyInstaller.__main__

PyInstaller.__main__.run(['main.py', '--onefile', '--add-data=files/ea.csv:files', '--add-data=files/final.txt:files',
                          '--add-data=files/bsc5.dat:files', '--add-data=files/star_Mesh_.obj:files',
                          '--add-data=files/star_Sprite.png:files', '--add-data=files/marker_circ.obj:files',
                          '--collect-all=vispy',
                          '--hidden-import=vispy.glsl', '--hidden-import=OpenGL'])# '--hidden-import OpenGL', '--hidden-import vispy.glsl'])
