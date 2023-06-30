import maya.cmds as cmds
import random
import math

class Root:
    def __init__(self,x,y,z, ang):
        
        # Create a list of control points for the spline
        control_points = [(0, 0, 0), (0.1, 0.1, 0), (0.25, 0.05,0), (0.4, 0, 0)]

        # Create a curve using the control points
        self.curve = cmds.curve(d=3, p=control_points)
        self.mesh = cmds.revolve(self.curve, ch=1)
        
        cmds.select(self.mesh)
        cmds.rotate(0,ang,0)
        
        cmds.select(self.mesh)
        cmds.move(x,y,z) 
        
        cmds.delete(self.curve)
         

class Tree:
    def __init__(self, x, y, z, name):
        self.joints = []
        self.position = (x, y, z);
        self.mesh = cmds.file("./bin/plug-ins/forest_assets/tree.obj", i=True, type='OBJ', rnn=True, gr=True, gn=name);
        self.name = name
        # Select the object you want to assign the red Hypershade material to
        object_name = f'{self.name}|polySurface1'  # Replace with the name of your object
        
        # Create a red Lambert material
        red_material = cmds.shadingNode("lambert", asShader=True)
        cmds.setAttr(red_material + ".color", 0.03, 0.1, 0.03, type="double3")
        
        # Create a shading group
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(red_material + ".outColor", shading_group + ".surfaceShader", force=True)
        
        # Assign the shading group to the object
        cmds.sets(object_name, edit=True, forceElement=shading_group)
        self.angle = ang = random.randint(1,360);
        #self.mesh = cmds.polySphere(radius=0.2, subdivisionsX=20, subdivisionsY=20)[0];
        cmds.select(self.name)
        cmds.scale(7,7,7,r=True)
        cmds.move(0,1.9,0)
        cmds.move(*self.position, relative=True)
        
        cmds.rotate(0, self.angle,0, relative=True)
        cmds.select(deselect=True)
        
        self.generate_joints()
        self.name = cmds.group([self.name, self.joints[0]])
                
    def gen_roots(self):
        roots = list()
        for i in range(4):
            roots.append(Root(*self.position, (90*i) + self.angle).mesh[0])
        
        self.name = cmds.group([self.name, cmds.group(roots)])
    
    def generate_joints(self):
        height = 4
        step = height/10
        
        pos_x = self.position[0]
        pos_y = self.position[1]
        pos_z = self.position[2]
        
        while (pos_y <= self.position[1] + height):  
            self.joints.append(cmds.joint(p=(pos_x, pos_y, pos_z)))
            pos_y += step
        
        cmds.skinCluster(self.joints[0],f'{self.name}|polySurface1', dr=4.5)
    
    def animate_wind(self, wind_speed):
        for j in self.joints:
            cmds.setKeyframe(j, at="rx", v=0, t=0);
        
        wind_offset = random.randint(0,50)
        for idx, j in enumerate(self.joints):
            wind_factor = 0
            if (idx- 10):
                wind_factor = wind_speed / (10 - idx)
            
            deg = (1 * 50 * wind_factor)/10
            if(deg > 10):
                deg = 5
            cmds.setKeyframe(j, at="rx", v=deg, t=50 + wind_offset);
        
        
              
        for idx, j in enumerate(self.joints):
           cmds.setKeyframe(j, at="rx", v=0, t=100 + wind_offset);

        
    
def toggle_visibility(object_name):
    visibility_attr = object_name + ".visibility"
    current_visibility = cmds.getAttr(visibility_attr)
    new_visibility = not current_visibility
    cmds.setAttr(visibility_attr, new_visibility)

def create_rain(width, height, wind_speed, quantity):
    cmds.polyPlane(n='rain_plane',w=width, h=height, sx=width*quantity, sy=height*quantity)[0]
    cmds.select('rain_plane')
    cmds.move (0 - (wind_speed / 2),15,0, 'rain_plane', r=True)
    
    toggle_visibility('rain_plane')
    
    cmds.emitter(type='omni',name="particlesobj1", r= 10, sro= 0,nuv= 0, cye= 'none', cyi= 1, spd= 1, srn= 0, nsp= 1, tsp= 0, mxd= 0, mnd= 0,dx= 0, dy= 0, dz= 1, sp= 0)
    cmds.nParticle()
    cmds.connectDynamic(em="particlesobj1")
    
    cmds.setAttr ("nucleus1.gravity", 5)
    cmds.setAttr ("nucleus1.usePlane", 1)
    cmds.setAttr ("nucleus1.windSpeed", wind_speed)
    cmds.setAttr("nParticleShape1.color[0].color_Color", 0.7, 0.8, 1, type= "double3" )
    cmds.setAttr("nParticleShape1.lifespanMode", 1)
    cmds.setAttr("nParticleShape1.lifespan", 2.3)
    cmds.select('nParticle1')
    cmds.select('nParticle1')
    cmds.vortex(pos= [0, 0, 0], m =10, att= 1.5, ax= 0, ay=1, az= 0, mxd =-1, vsh= 'none', vex= 0, vof= [0 ,0, 0], vsw= 360, tsr= 0.5)

def generate_terrain(width, height, density, wind, roots, height_ditribution):
    #remove items
    cmds.select(all=True)
    cmds.delete()
    
    #Creates the floor 
    cells_width = 1; 
    segments_width = math.floor(width / cells_width);
    segments_height = math.floor(height / cells_width); 
    floor = cmds.polyPlane(width=width, height=height, subdivisionsX=segments_width, subdivisionsY=segments_height)[0];
    
    texture_path = './bin/plug-ins/forest_assets/grass.jpg'
    imported_model = floor
    shader = cmds.shadingNode('lambert', asShader=True)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
    
    # Assign the texture to the shader
    texture_file = cmds.file(texture_path, q=True, loc=True)
    file_node = cmds.shadingNode('file', asTexture=True)
    cmds.setAttr(file_node + '.repeatU', segments_height)
    cmds.setAttr(file_node + '.repeatV', segments_width)
    cmds.setAttr('%s.fileTextureName' % file_node, texture_file, type='string')
    cmds.connectAttr('%s.outColor' % file_node, '%s.color' % shader)
    
    # Apply the shader to the model
    cmds.select(imported_model)
    cmds.hyperShade(assign=shader)
    
    for i in range(segments_width * segments_height):
        current_position = cmds.xform(f'{floor}.vtx[{i}]', query=True, translation=True, worldSpace=True)
        cmds.move(current_position[0], random.random() * height_ditribution, current_position[2],f'{floor}.vtx[{i}]')
    
    
    #Spawn trees
    cells = []
    for w in range(segments_width * segments_height):
        cells.append(0)
        
    if(density > (segments_width * segments_height) - 1):
        density = (segments_width * segments_height) - 1
    current_tree = 1
    trees = []
    while (current_tree <= density):
 
        cell_idx = random.randint(0, (segments_width * segments_height) - 1)
        
        if(cells[cell_idx] == 1):
            continue
        else:
            cells[cell_idx] = 1
        
        current_tree += 1
        cell_pos = cmds.xform(f'{floor}.vtx[{cell_idx}]', query=True, translation=True, worldSpace=True)
        #pos_x = (0 - (width / 2)) + (col * cells_width)
        pos_x = cell_pos[0]
        pos_y = cell_pos[1]
        pos_z = cell_pos[2]
        #pos_z = (height / 2) - (row * cells_width) 
        tree = Tree(pos_x, pos_y, pos_z, f'tree{current_tree}')
        tree.animate_wind(wind)
        if(roots):
            tree.gen_roots()
        trees.append(tree.name)
    
    cmds.group(trees, name="trees")
     
    
    #Generate Rain
    create_rain(width, height, wind,1)
    cmds.select(deselect=True)
    pass
    

class Window(object):
    def __init__(self):
        self.win = "forestPluginWindow" #Window name
        self.title = "Forest Plugin"       #Window title
        self.dimensions = (500,500)
        
        #avoids duplicated
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win, window=True)
        
        self.win = cmds.window(self.win, title=self.title, widthHeight=self.dimensions)
        
        cmds.columnLayout(adjustableColumn=True)
        
        cmds.text(self.title)
        cmds.separator(height = 20)
        
        self.enviroment_size = cmds.floatFieldGrp(label="Size:", value1=10.0, value2=10.0, numberOfFields=2)
        self.enviroment_hd = cmds.floatFieldGrp(label="Height_distribution:", value1=10.0, numberOfFields=1)
        self.tree_density = cmds.radioButtonGrp(label="Tree Density", labelArray3=["Few", "Some", "Many"], numberOfRadioButtons=3, select=1)
        self.rain_density = cmds.radioButtonGrp(label="Rain Density", labelArray3=["Light", "Moderated", "Intense"], numberOfRadioButtons=3, select=1)
        self.enable_roots = cmds.checkBox(label="Roots")
        cmds.separator(height = 20)
        self.generate_button = cmds.button(label="generate", command=lambda _: self.generate_enviroment())
        
    def init_GUI(self):
        cmds.showWindow(self.win)
        pass
    
    def get_check_state(self, checkbox):
        return cmds.checkBox(checkbox, q=True, v=True)
    
    def get_radio_selection(self, radio_button_group):
        return cmds.radioButtonGrp(radio_button_group, q=True, select=True)
        pass
    
    def get_size(self):
        return cmds.floatFieldGrp(self.enviroment_size, q=True, value=True)
    def get_hs(self):
        return cmds.floatFieldGrp(self.enviroment_hd, q=True, value=True)[0]
        
    def generate_enviroment(self):
        tree_density_val = self.get_radio_selection(self.tree_density)
        rain_density_val = self.get_radio_selection(self.rain_density)
        enable_roots_val = self.get_check_state(self.enable_roots)
        size_val = self.get_size()
        hs = self.get_hs() / 10
        density = round((size_val[0] * size_val[1]) / (2 * (4-tree_density_val)))
        generate_terrain(width=size_val[0],height=size_val[1], density=density, wind=(rain_density_val - 1) * 3, roots=enable_roots_val, height_ditribution=hs)

        

plugin = Window()
plugin.init_GUI()
