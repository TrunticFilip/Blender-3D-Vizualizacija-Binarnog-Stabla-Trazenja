##== Filip Truntic - Zavrsni rad 2023/2024. ==##

import bpy;
import math;
import os;

#from mathutils.bvhtree import BVHTree;
#import bmesh;


# Parametri koje korisnik ne bi trebao dirati. Postoje u kodu iskljucivo u svrhu debugiranja.
use_keyframes = True;
start_rendering = True;


# Da bi se parametar ispravno procitao iz config.txt, mora postojati u config_parameterslist.
config_parameterslist = [
    'input_list',
    'tree_type',

    'interval',
    'scale_sphere',
    'scale_number',
    'space_unit',
    
    'color_1',
    'color_2',
    'color_3',
    
    'resolution_x',
    'resolution_y',
    'resolution_percentage',
    'fps',
    
    'file_format',
    'ffmpeg_format',
    'ffmpeg_codec',
    'ffmpeg_constant_rate_factor',
    'ffmpeg_ffmpeg_preset'
    ];

# Pretpostavljen niz brojeva koji se koristi za rad programa, u slucaju da konfiguracijska datoteka ne postoji.
input_list = [100,6,87,36,25,90,7,43,21,17,52,84,40,14,29,61,35];

# default = 5
interval = 10; #Koliko slicica traje jedna akcija. Akcija podrazumijeva umetanje cvora, rotacija ili slicno.

# default = 1
scale_sphere    = 1;
scale_number    = 1;

color_1 = ( 0, 1, 0);
color_2 = (-1, 1, 0);
color_3 = (-1, 0, 0);

color_1_obj = bpy.data.objects['config_color_1'];
color_2_obj = bpy.data.objects['config_color_2'];
color_3_obj = bpy.data.objects['config_color_3'];

tree_type      = 'BST';
space_unit = 3; # najmanja jedinica prostora u kontekstu programa


resolution_x = 1920;
resolution_y = 1080;
resolution_percentage = 100;
fps = 24;


file_format                     = 'FFMPEG';
ffmpeg_format                   = 'MPEG4';

ffmpeg_codec                    = 'H264';
ffmpeg_constant_rate_factor     = 'MEDIUM';
ffmpeg_ffmpeg_preset            = 'GOOD';




tolerance = 2.5;

# Funkcija prima referencu na jedan cvor i vraca stranu cvora u odnosu na korijen cijelog stabla.
# Primjerice, ako je kao argument proslijeden cvor s kljucem 27 a korijen stabla sadrzi kljuc 53,
# funkcija vraca 'l' kao povratnu vrijednost.
def getside_global(node):
    if node == None or node == root_global:
        return None;
    
    
    node_iterating = node;
    while True:
        if node_iterating['parent'] != root_global:
            print("node_iterating - " + node_iterating.name + ", parent: " + node_iterating['parent'].name);
            node_iterating = node_iterating['parent'];
            continue;
        elif root_global['child_left'] == node_iterating:
            print("Nasao sam globalnu stranu!");
            return 'l';
        elif root_global['child_right'] == node_iterating:
            print("Nasao sam globalnu stranu!");
            return 'r';
        else:
            print("Nesto ne valja, ne mogu odrediti globalnu stranu cvora (sad sam unutar getside_global funkcije)");
            return None;
            
    print("Nesto ne valja, ne mogu odrediti globalnu stranu cvora (sad sam unutar getside_global funkcije)");
    return None;


# Funkcija prima referencu na jedan cvor i vraca stranu cvora u odnosu na roditelja.
# Primjerice ako se u argumentu nalazi cvor s kljucem 26 a roditelj sadrzi kljuc 28,
# funkcija vraca 'l' kao povratnu vrijednost.
# Alternativno, ako se u argumentu nalazi cvor s kljucem 30 a roditelj sadrzi kljuc 28,
# funkcija vraca 'r' kao povratnu vrijednost.
def getside_local(node):
    if node == None or node == root_global:
        return None;

    if node['parent']['child_left'] == node:
        return 'l';
    elif node['parent']['child_right'] == node:
        return 'r';
    else:
        print("Nesto ne valja, ne mogu odrediti lokalnu stranu cvora");
        return None;


# Nakon svake dodane akcije (dodavanje cvora ili rotacija), ukupno trajanje generirane mp4 datoteke raste.
# Funkcija update_last_keyframe nakon svake akcije trazi najkasniju kljucnu slicicu
# i postavlja ju kao zadnju slicicu koju program treba uzeti u obzir.
# Primjerice ako je zadnja akcija zavrsila na slicici 435,
# Funkcija podesava program tako da se mp4 datoteka generira od slicice 1 do slicice 435.
last_keyframe = 0;
def update_last_keyframe(num):
    global last_keyframe;
    if num > last_keyframe:
        last_keyframe = num;
        return True;
    return False;


# Funkcija dodaje kljucnu slicicu na objekt proslijeden u argumentu.
# Ako pri pozivu nedostaje data_path argument,
# funkcija ce dodati kljucnu slicicu na sve elementarne transformacije - location, rotation, scale.
def add_keyframe(object, location = None, data_path = None, offset = 0):
    global scene;
    
    if use_keyframes == False:
        return False;

    if location != None:
        object.location = location;
    
    if data_path == None and isinstance(object, list) and len(object) > 0:
        for o in object:
            if o == None:
                continue;
            o.keyframe_insert(data_path = 'location',          frame = scene.frame_current + offset);
            o.keyframe_insert(data_path = 'rotation_euler',    frame = scene.frame_current + offset);
            o.keyframe_insert(data_path = 'scale',             frame = scene.frame_current + offset);            
        return True;
    
    if data_path == None:
        object.keyframe_insert(data_path = 'location',          frame = scene.frame_current + offset);
        object.keyframe_insert(data_path = 'rotation_euler',    frame = scene.frame_current + offset);
        object.keyframe_insert(data_path = 'scale',             frame = scene.frame_current + offset);
        return True;

    if data_path != None:
        object.keyframe_insert(data_path = data_path,           frame = scene.frame_current + offset);
        return True;

# Funkcija koja prima jedan integer kao argument i pomice "sadasnjost" za onoliko slicica koliko iznosi argument.
# Primjerice ako je kao argument proslijeden broj 5, sadasnjost se pomice za 5 slicica unaprijed.
# Analogno tome, ako je kao argument proslijeden broj -3, sadasnjost se pomice za 3 slicice unazad.
def playhead_fwd(offset = 0):
    global scene;
    temp = scene.frame_current;
    scene.frame_current += offset;
    return;


scene           = bpy.data.scenes['Scene'];
scene_collection = bpy.data.scenes['Scene'].collection;

try:
    tree = bpy.data.collections['tree'];
    print("tree kolekcija: " + tree.name);
except:
    tree = bpy.data.collections.new(name = 'tree');
    scene_collection.children.link(tree);
    print("tree kolekcija: " + tree.name);

# Referenca na cvor koji predstavlja korijen cijelog stabla.
# Na pocetku rada programa jos ne postoji niti jedan cvor, dakle root_global jos ne postoji.
root_global = None;


iterator = bpy.data.objects['iterator'];

sphere_mesh = bpy.data.meshes['sphere'];
cylinder_mesh = bpy.data.meshes['valjak'];
text_curve = bpy.data.curves['Text'];

# Ovaj objekt je potreban za ispravno prikazivanje poveznica.
dist_prev = bpy.data.objects['dist_prev'];

# Referenca na kameru i njenu pripadajucu metu.
# Kamera je tocka u 3D prostoru iz koje promatrac vidi generiranu animaciju,
# a meta je tocka prema kojoj kamera gleda.
camera          = bpy.data.objects['camera'];
camera_target    = bpy.data.objects['camera_target'];



# Ova funkcija dodaje novi cvor u .blend datoteku.
# Posao ove funkcije je samo osigurati da cvor postoji, trazenjem logicke i prostorne pozicije bavi se addnewnode_BST.
# Funkcija stvara novi node i vraca referencu na empty object koji upravlja pozicijom cvora u prostoru.
def create_new_node(input):
    input = str(input);
    
    for obj in tree.objects:
        if obj.name == input:
            print("Cvor vec postoji, ne mogu ga opet stvoriti");
            return None;
        
    
    empty   = bpy.data.objects.new(name = input + "_empty", object_data = None);
    sphere   = bpy.data.objects.new(name = input, object_data = sphere_mesh.id_data);
    text    = bpy.data.objects.new(name = input + "_text", object_data = text_curve.id_data);
    
    #Objecti zasada postoje samo u .blend fileu, ali nisu jos dodani u scenu.
    #Dok nisu dodani u scenu, ne moze im se pristupiti ni preko sucelja ni programskim putem.
    scene_collection.objects.link(empty);
    scene_collection.objects.link(sphere);
    scene_collection.objects.link(text);
    
    #Iscrtaj obrub oko cvora.
    draw_outline(sphere);
    
    tooltip_add = tooltip_add_template.copy();
    tooltip_add.data = tooltip_add.data.copy();
    tooltip_add.animation_data.action = tooltip_add.animation_data.action.copy();
    
    tooltip_add.data.body = tooltip_add.data.body.replace('CVOR', sphere.name);
    bpy.data.collections['tooltips'].objects.link(tooltip_add);
    tooltip_add.name = 'tooltip_add_' + sphere.name;
    tooltip_add.hide_viewport = False;
    tooltip_add.keyframe_insert(data_path = 'hide_viewport');
    
    
    add_keyframe(sphere);
    sphere.scale = (0,0,0);
    add_keyframe(sphere, data_path = 'scale');
    playhead_fwd(interval);
    
    #Ovdje azuriram sadrzaj teksta.
    text.data = text.data.copy();
    text.data.body = input;
    text.location = (1.06955, 0, 0); #vrijednost x-koordinate je proizvoljna, ovako se dobije dobra vidljivost broja ispred cvora.
    text.rotation_euler = (math.radians(90), 0, math.radians(90));
    
    empty.empty_display_size = 1.05;
    empty.empty_display_type = 'SPHERE';
    
    empty_constraint = empty.constraints.new(type = 'COPY_LOCATION');
    empty_constraint.use_offset = True;
    empty_constraint.target = sphere;
    empty_constraint.target_space   = 'LOCAL';
    empty_constraint.owner_space    = 'LOCAL';
    
    empty_constraint = empty.constraints.new(type = 'COPY_SCALE');
    empty_constraint.use_offset = True;
    empty_constraint.target = sphere;
    empty_constraint.target_space   = 'LOCAL';
    empty_constraint.owner_space    = 'LOCAL';
    
    empty_constraint = empty.constraints.new(type = 'ACTION');
    empty_constraint.use_eval_time = True;
    empty_constraint.action = bpy.data.actions['empty_rotate_1'];
    empty_constraint.frame_start    = 0;
    empty_constraint.frame_end      = 20;
    
    empty_constraint = empty.constraints.new(type = 'TRACK_TO');
    empty_constraint.target = camera;
    empty_constraint.track_axis = 'TRACK_X'
    empty_constraint.up_axis    = 'UP_Z';
    empty_constraint.target_space   = 'WORLD';
    empty_constraint.owner_space    = 'LOCAL';
    
    text.parent = empty;
    
    add_keyframe(sphere);
    add_keyframe(text);
    
    if len(tree.objects) == 0: # U ovaj blok koda samo pri stvaranju prvog cvora u stablu.
        sphere.location  = (0, 0, 0);
        sphere.scale     = (scale_sphere, scale_sphere, scale_sphere);
        add_keyframe(sphere);
        
        text.scale = (scale_number * 0.2 + 0.8, scale_number * 0.2 + 0.8, scale_number * 0.2 + 0.8);
        add_keyframe(text);
        
        tooltip_add.hide_viewport = True;
        tooltip_add.keyframe_insert(data_path = 'hide_viewport');
    
        return sphere;
    
    sphere.location  = (-3, 0, 0);
    sphere.scale     = (scale_sphere, scale_sphere, scale_sphere);
    add_keyframe(sphere);
    
    text.scale = (scale_number * 0.2 + 0.8, scale_number * 0.2 + 0.8, scale_number * 0.2 + 0.8);
    add_keyframe(text);
    
    playhead_fwd(interval);
    
    
    tooltip_add.hide_viewport = True;
    tooltip_add.keyframe_insert(data_path = 'hide_viewport');
    
    
    return sphere;


# Funkcija addnewnode_BST trazi logicku i prostornu poziciju novog cvora.
# Kao argument prima jedan integer i vraca True odnosno False,
# ovisno o tome je li cvor uspjesno u stablo.
# Pored trazenja logicke i prostorne pozicije, poziva se i jedna druga funkcija,
# koja upravlja eventualnim razmicanjem cvorova.
    
def addnewnode_BST(input):

    new_node = create_new_node( str(input) );
    
    if new_node == None:
        return None;
    
    
    add_keyframe(new_node);
    playhead_fwd(interval);
    
    new_node['parent'       ]   = None;
    new_node['child_left'   ]   = None;
    new_node['child_right'  ]   = None;
    
    new_node['height_leftSubtree' ]   = 0;
    new_node['height_rightSubtree']   = 0;
        
    if len(tree.objects) == 0: # U slucaju da je stablo prazno i ovo je prvi node kojeg dodajemo.
        global root_global;
        root_global = new_node;
        tree.objects.link(new_node);
        nodes.add(new_node);
        scene_collection.objects.unlink(new_node);
        
        empty_constraint = bpy.data.objects[new_node.name + '_empty'].constraints['Action'];
        
        context_time = scene.frame_current;
        
        playhead_fwd(-interval * 2);
        
        playhead_fwd(interval * 4);
        empty_constraint.eval_time = 1;
        empty_constraint.keyframe_insert(data_path = 'eval_time');
        
        playhead_fwd(-interval * 4);    
        empty_constraint.eval_time = 0;
        empty_constraint.keyframe_insert(data_path = 'eval_time');
        
        playhead_fwd(interval * 2);
        
        scene.frame_current = context_time;
        
        return True;
    
    
    new_node_number = int(new_node.name);
    
    nodes_visited = set();
    
    iterator_node = root_global;
    iterator.location = root_global.location;
    
    # Iterator polazi od root_globala i istovremeno trazi logicku i prostornu poziciju cvora.
    counter = 0;
    while counter < len(nodes) and nodes != nodes_visited:

        iterator_number = int(iterator_node.name);
        
        allocatenew_node = None;
        moram_micati_cvorove = False;
        
        if new_node_number < iterator_number:
            if iterator_node['child_left'] == None:
                iterator_node['child_left'] = new_node;
                new_node['parent'] = iterator_node;
                iterator.location.y -= space_unit;
                iterator.location.z -= space_unit;
                allocatenew_node = iterator.location;
            else:
                iterator_node = iterator_node['child_left'];
                iterator.location = iterator_node.location;
                continue;
        elif new_node_number > iterator_number:
            if iterator_node['child_right'] == None:
                iterator_node['child_right'] = new_node;
                new_node['parent'] = iterator_node;
                iterator.location.y += space_unit;
                iterator.location.z -= space_unit;
                allocatenew_node = iterator.location;
            else:
                iterator_node = iterator_node['child_right'];
                iterator.location = iterator_node.location;
                continue;
        
        if tree_type.find('AVL') != -1:
            space_nodes_apart();
        
        if allocatenew_node != None:
            
            tree.objects.link(new_node);
            nodes.add(new_node);
            scene_collection.objects.unlink(new_node);
            
            empty_constraint = bpy.data.objects[new_node.name + '_empty'].constraints['Action'];
            
            playhead_fwd(-interval);
            
            empty_constraint.eval_time = 0;
            empty_constraint.keyframe_insert(data_path = 'eval_time');
            
            # Vracanje u sadasnjost
            playhead_fwd(interval);
            
            add_keyframe(new_node, location = allocatenew_node);
            playhead_fwd(interval);
            
            # I empty i text objecte ubacuju se u kolekciju 'tree'
            empty   = bpy.data.objects[new_node.name + "_empty"];
            text    = bpy.data.objects[new_node.name + "_text"];
            tree.objects.link(empty);
            tree.objects.link(text);
            scene_collection.objects.unlink(empty);
            scene_collection.objects.unlink(text);
            
            playhead_fwd(-interval);
            
            playhead_fwd(interval * 2);
            empty_constraint.eval_time = 1;
            empty_constraint.keyframe_insert(data_path = 'eval_time');
            playhead_fwd(-interval * 2);
            
            # Vracanje u sadasnjost
            playhead_fwd(interval);
            
            
            # Dodaje se poveznica za novi cvor
            link_targetName = "link_" + new_node['parent'].name + "_" + new_node.name;
            link = bpy.data.objects.new(name = link_targetName, object_data = cylinder_mesh.id_data);
            tree.objects.link(link);
            
            
            # Poveznica postoji, ali sakriva se prije nego sto bude potrebna u vizualizaciji.
            now = scene.frame_current;
            scene.frame_current = 1;
            link.hide_viewport = True;
            link.keyframe_insert(data_path = 'hide_viewport');
            scene.frame_current = now - interval * 2;
            link.hide_viewport = False;
            link.keyframe_insert(data_path = 'hide_viewport');
            scene.frame_current = now;
            
            link.rotation_euler = (math.radians(135), 0.0, 0.0)
            link.scale.x = 0.1;
            link.scale.y = 0.1;
            link.scale.z = 2.0;
            
            link_addconstraints(link, new_node['parent'], new_node);
            
            update_height(new_node);
            
            update_camera();
            
            update_last_keyframe(scene.frame_current);
            
            # Poziv funkcije za razmicanje cvorova.
            # Postoje dvije razlicite funkcije, ovisno o tome je li se radi o uravnotezenom ili neuravnotezenom stablu.
            if tree_type.find('AVL') != -1:
                space_nodes_apart_arg(new_node);
            elif tree_type.find('BST') != -1:
                clear_intersection(new_node);
            
            break;
            reset_iterator();
        else:
            nodes_visited.add(iterator_node);
        counter += 1;

    if tree_type.find('AVL') != -1:
        balancing();
    
    return True;

# Ova funkcija upravlja situacijama gdje se cvorovi bore za isto mjesto u 3D prostoru.
# Za argument prima referencu na jedan cvor.
# Kao sto je opisano u radu:
# Ako postoje dva cvora koji se bore za isto mjesto,
# funkcija trazi prvog zajednickog roditelja oba cvora,
# te razmice lijeva i desna podstabla tog zajednickog roditelja.
def clear_intersection(node):
    
    if node == None or node == root_global or node['parent'] == root_global:
        return None;
    
    context_time_intersect = scene.frame_current;
    
    print("Frame: " + str(scene.frame_current));
    
    coefficient = 2;
    
    node_at_this_location = find_node_at(node);
    if node_at_this_location == None:
        # Cak iako ne postoji konflikt sa cvorovima, provjerava se je li mozda postoje preklapanja u poveznicama.
        left_node  = get_node_nextto(node, 'l');
        right_node = get_node_nextto(node, 'r');
        print("Node: "                          +   node.name               );
        if left_node is not None:
            print("Frame: " + str(scene.frame_current) + " , left node - " + left_node.name);
        if right_node is not None:
            print("Frame: " + str(scene.frame_current) + " , right node - " + right_node.name);
        
        playhead_fwd(-interval);
        add_keyframe([left_node, right_node]);
        playhead_fwd( interval);
        add_keyframe([left_node, right_node]);
        
        if left_node != None and int(left_node.name) > int(node.name) and left_node.location.y < node.location.y:
            diff = abs(left_node.location.y - node.location.y);
            left_node.location.y += diff;
            node.location.y -= diff;
            add_keyframe([left_node, node]);
        elif right_node != None and int(right_node.name) < int(node.name) and right_node.location.y > node.location.y:
            diff = abs(right_node.location.y - node.location.y);
            right_node.location.y -= diff;
            node.location.y += diff;
            add_keyframe([right_node, node]);
        
        scene.frame_current = context_time_intersect;
        return None;
    
    
    print("Node: "                          +   node.name               );
    print("Node koji je ovdje otprije: "    +   node_at_this_location.name );
    
    path_this = get_path_to_top(node);
    path_other = get_path_to_top(node_at_this_location);
    
    if path_this == None or path_other == None or len(path_this) == 0 or len(path_other) == 0:
        scene.frame_current = context_time_intersect;
        return;
    
    first_common_parent = None;
    
    playhead_fwd(-interval);
    for c in nodes:
        add_keyframe(c);
    playhead_fwd( interval);
    
    for i in range(0, len(path_this) ):
        if path_this[i] == path_other[i]:
            first_common_parent = path_this[i];
            break;
    

    
    if first_common_parent == None:
        print("Negdje je doslo do greske, ne mogu naci zajednickog roditelja");
        return None;
    
    print("Prvi zajednicki roditelj: " + first_common_parent.name);     
    
    children_left    = all_children(first_common_parent['child_left'    ], 1);
    children_right   = all_children(first_common_parent['child_right'   ], 1);
    
    if len(children_left) == 0 or len(children_right) == 0:
        print("Nesto ne valja, nemam oba podstabla");
        scene.frame_current = context_time_intersect;
        return None;
    
    already_keyframed = set();
    
    while find_node_at(node) != None:
        other = find_node_at(node)
        if getside_global( other ) == getside_global(node):
            if int(other.name) > int(node.name):
                other.location.y += space_unit / 2;
                node.location.y -= space_unit / 2;
            else:
                other.location.y -= space_unit / 2;
                node.location.y += space_unit / 2;
            
        
        for c in children_left:
            c.location.y -= space_unit / coefficient;
            add_keyframe(c);
            already_keyframed.add(c);
            
            nextNodes = get_nodes_on_side(c, 'l');
            print("Cvor u lijevoj djeci prvog zajednickog roditelja: " + c.name);
            print("Nextnodes na lijevoj strani: ");
            print(nextNodes);
            if len(nextNodes) > 0:
                for n in nextNodes:
                    if n not in already_keyframed:
                        n.location.y -= space_unit / coefficient;
                        add_keyframe(n);

        for c in children_right:
            c.location.y += space_unit / coefficient;
            add_keyframe(c);
            already_keyframed.add(c);
            print("Cvor u desnoj djeci prvog zajednickog roditelja: " + c.name);
            
            nextNodes = get_nodes_on_side(c, 'r');
            print("Nextnodes na desnoj strani: ");
            print(nextNodes);
            if len(nextNodes) > 0:
                for n in nextNodes:
                    if n not in already_keyframed:
                        n.location.y += space_unit / coefficient;
                        add_keyframe(n);
        
    scene.frame_current = context_time_intersect;
    
    return;

# Poziva se u funkciji clear_intersection.
# Funkcija kao argument prima referencu na jedan cvor
# i vraca putanju od tog cvora do korijena stabla u obliku liste.
def get_path_to_top(node):
    if node == None or node == root_global or node['parent'] == root_global:
        return None;
    
    path = [];
    
    node_iterating = node;
    while True:
        if node_iterating['parent'] != None:
            path.append(node_iterating['parent']);
            node_iterating = node_iterating['parent'];
            continue;
        else:
            break;
    
    return path;

# Poziva se nad upravo dodanim cvorom.
# Svaki cvor sadrzi vlastita svojstva 'height_leftSubtree' i 'height_rightSubtree',
# koji sadrze informaciju o visini lijevog odnosno desno podstabla tog cvora.
# Ova funkcija azurira vlastita svojstva 'height_leftSubtree' i 'height_rightSubtree' svakog cvora.
def update_height(node):
    while node['parent'] != None or node != root_global:
        if node['child_left'] == None:
            node['height_leftSubtree'] = 0;
        if node['child_right'] == None:
            node['height_rightSubtree'] = 0;
    
        if node['parent']['child_left'] == node:
            node['parent']['height_leftSubtree' ] = max_height(node) + 1;
        elif node['parent']['child_right'] == node:
            node['parent']['height_rightSubtree'] = max_height(node) + 1;
        node = node['parent'];
        
    return;

# Nakon svakog dodanog cvora, visina i sirina stabla u 3D prostoru se mjenja.
# Posao ove funkcije je osiguravanje da se u generiranoj animaciji
# u svakom trenutku vidi cijelo stablo.
def update_camera():
    context_time = scene.frame_current;
    
    cam_constraint = camera.constraints['Track To'];
    
    playhead_fwd(-interval * 2);
    add_keyframe(camera);
    add_keyframe(camera_target);
    cam_constraint.keyframe_insert(data_path = 'influence');
    
    playhead_fwd(interval * 1);
    
    
    camera_constant = 1;
    offset = max(max_height(root_global), abs(maxwidth_global() / 2))

    camera.location.x = 15 + offset *   5  * space_unit / 3;
    camera.location.y = -6 + offset *   1  * space_unit / 3  ;
    camera.location.z =  1 + offset * (-1) * space_unit / 3 ;
    
    add_keyframe(camera);
    
    center = get_center();
    
    camera_target.location.y = center[1];
    camera_target.location.z = center[2];
    add_keyframe(camera_target);
    
    cam_constraint.influence *= 1 + (offset * 0.005);
    cam_constraint.keyframe_insert(data_path = 'influence');
    
    scene.frame_current = context_time;
    return;

# Kada se funkcija jednom pozove nad cvorom,
# do kraja programa se nad pozvanim objektom iscrtava crni obrub.
def draw_outline(object):
    mod = object.modifiers.new(name = 'Solidify', type = 'SOLIDIFY');
    mod.thickness = -0.1;
    mod.use_rim = True;
    mod.use_rim_only = False;
    mod.use_flip_normals = True;
    mod.material_offset = 1; # Da bi iscrtavanje obruba radilo, drugi materijal po redu treba biti onaj za iscrtavanje outlinea.

    return mod; # Ako je iz nekog razloga potrebno, funkcija vraca referencu na modifier u pitanju.

# Vraca najvecu sirinu izmedu dva cvora.
# Ako je argument izostavljen, vraca sirinu cijelog stabla.
def maxwidth_global():
    children_left    = all_children(root_global['child_left'  ], 1);
    children_right   = all_children(root_global['child_right' ], 1);
    
    width_max = -999;
    node_left   = None;
    node_right  = None;
    
    if len(children_left) <= 1 or len(children_right) <= 1:
        return -1;
    
    for n_left in children_left:
        for n_right in children_right:
            if n_left.location.z == n_right.location.z and abs( n_left.location.y - n_right.location.y ) > width_max:
                width_max = abs( n_left.location.y - n_right.location.y );
                node_left   = n_left;
                node_right  = n_right;
            
    return  ( node_left.location.y - node_right.location.y ) / 2 ;

# Funkcija vraca tocku u 3D prostoru koja predstavlja centar cijelog stabla.
def get_center():
    min_Y =  999;
    max_Y = -999;
    min_Z =  999;
    max_Z = 0; # z ne smije ici preko 0, jer se korijen nalazi na visini 0, sve ostalo je ispod 0
    for c in nodes:
        if c.location.y < min_Y:
            min_Y = c.location.y;
        if c.location.y > max_Y:
            max_Y = c.location.y;
        if c.location.z < min_Z:
            min_Z = c.location.z;
        #if c.location.y > max_Z: # ne ulazi u kod, nalazi se ovdje radi kompletnosti.
        #    max_Z = c.location.y;

    return (0,  (max_Y + min_Y) / 2 ,  (max_Z + min_Z) / 2 );


# Svaki cvor ima dva svojstva, 'height_leftSubtree' i 'height_rightSubtree'
# koja sadrze informaciju o visini lijevog odnosno desnog podstabla tog cvora.
# Funkcija vraca visinu veceg podstabla.
def max_height(node):
    return max(node['height_leftSubtree'], node['height_rightSubtree']);

# Funkcija vraca skup sa svim cvorovima trenutno sadrzanima u stablu.
def walk_tree():
    nodes = set();
    for obj in tree.objects:
        if obj.name.isdigit() == True and obj.type == 'MESH':
            nodes.add(obj);
    return nodes;

# Ponekad se dogodi da se cvorovi s razlicitom logickom pozicijom bore za istu prostornu poziciju.
# Ova funkcija se obicno poziva nad upravo dodanim cvorom.
# Na taj nacin, imamo informaciju o tome koji cvor je upravo dodan
# a koji vec postoji od prije.
def find_node_at(obj):
    if obj == None:
        return None;
    
    candidates = [];
    
    for c in nodes:
        point1 = c.location;
        point2 = obj.location;
        distance = math.dist(point1, point2);
        if distance < tolerance and c.location.z == obj.location.z and c != obj:
            candidates.append(c);
    
    # Od potencijalnih cvorova koji bi se mogli kositi s cvorom iz argumenta, vraca onaj koji je najblizi cvoru iz argumenta.
    candidates = sorted(candidates, key = lambda x:( abs(x.location.z - obj.location.z), abs(x.location.y - obj.location.y) ) );
    
    if len(candidates) > 0:
        return candidates[0];
    else:
        return None;

def reset_iterator():
    iterator.location = (0.0,0.0,0.0);
    return True;


# Ova funkcija trebala bi se pozivati samo unutar all_children.
# Rekurzivno se obilaze sva djeca i dodaju u izlaznu listu,
# pocevsi od cvora koji je pozvan u prvom pozivu ove funkcije.
def private_all_children(node, lista):
    
    if node['child_left'] != None:
        lista.append(node['child_left']);
        private_all_children(node['child_left'], lista);
        
    if node['child_right'] != None:
        lista.append(node['child_right']);
        private_all_children(node['child_right'], lista);
        
    return;

# Funkija vraca listu koja sadrzi svu djecu odredenog cvora.
# Kao argument daje se cvor od kojega zelimo dobiti svu djecu.
def all_children(node, roditeljUkljucen = None):
    djeca = [];
    
    if node == None:
        return djeca;
    
    # Dodatak u slucaju da se zeli ukljuciti i roditelja u povratnu kolekciju.
    if roditeljUkljucen == 1:
        djeca.append(node);
    
    private_all_children(node, djeca);
    return djeca;

# Slicno private_all_children, ova funkcija bi se trebala pozivati samo iz all_leaves.
def private_all_leaves(node, lista):
    if node['child_left'] != None:
        private_all_leaves(node['child_left'], lista);
    if node['child_right'] != None:
        private_all_leaves(node['child_right'], lista);

    if node['child_left'] == None and node['child_right'] == None:
        lista.append(node);
    return;


# Funkcija vraca sve cvorove u stablu bez djece, odnosno svo lisce.
def all_leaves():
    leaves = [];
    private_all_leaves(root_global, leaves);
    
    return leaves;


# Funkcija provjerava postoji li u stablu nebalansiran cvor.
# Ako takav postoji, poziva se funkcija rotation_getsolution, koja traži odgovarajuću rotaciju.
def balancing():
    root = None;
    nodes_unbalanced = [];
    
    for c in nodes:
        if abs( c['height_rightSubtree'] - c['height_leftSubtree'] ) > 1:
            nodes_unbalanced.append(c);
    
    # Ako postoji vise nebalansiranih cvorova,
    # Poredni su tako da je najnizi na prvom mjestu.
    nodes_unbalanced = sorted(nodes_unbalanced, key = lambda x: x.location.z);
    
    if len(nodes_unbalanced) > 0:
        
        if rotation_getsolution( nodes_unbalanced[0] ) == True:
            update_last_keyframe(scene.frame_current);
            
        else:
            print("Ne mogu balansirati, nesto ne valja");
            return False;
        
    return False;

# Ova funkcija traži koju rotaciju mora primijeniti, odnosno o kojem se od četiri slucaja radi.
# Kao argument prima referencu na nebalansirani cvor,
# odnosno korijen nebalansiranog (pod)stabla.
# Ako je ova funkcija pozvana, može se sa stopostotnom sigurnoscu tvrditi da je korijen nebalansiran.
# Dodatno, funkcija poziva i funkcije za bojanje čvorova pri rotaciji.
def rotation_getsolution(root):
    # Ovisno o tome kakav je put do korijena elementarnog podstabla, takva ce biti i rotacija.
    context_time = scene.frame_current;
    
    playhead_fwd(-interval);
    
    success = False;
    balance = root['height_rightSubtree'] - root['height_leftSubtree']
    

    tooltip_unbalanced = tooltip_unbalanced_template.copy();
    tooltip_unbalanced.data = tooltip_unbalanced.data.copy(); # osim objecta, iskopiraj i data
    tooltip_unbalanced.animation_data.action = tooltip_unbalanced.animation_data.action.copy(); #iskopiraj i akciju
    bpy.data.collections['tooltips'].objects.link(tooltip_unbalanced);
    
    tooltip_unbalanced.data.body = tooltip_unbalanced.data.body.replace('CVOR', root.name);
    tooltip_unbalanced.name = 'tooltip_unbalanced_' + root.name;
    tooltip_unbalanced.hide_viewport = False;
    tooltip_unbalanced.keyframe_insert(data_path = 'hide_viewport');

    scene.frame_current = context_time;
    
    if root['child_right'] == None:
        if balance < -1 and root['child_left'] != None and root['child_left']['child_left'] != None:
            lowest = root['child_left']['child_left'];
            color_paint(lowest,                      'r', trajanje = 2);
            color_paint(lowest['parent'],            'g', trajanje = 2);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 2);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_right'], lowest, rotation_type = 'r', trajanje = 2);
            
            rotation_R(root);
            
            playhead_fwd(interval * 2);
            
            success = True;
            
        elif balance < -1 and root['child_left'] != None and root['child_left']['child_right'] != None:
            lowest = root['child_left']['child_right'];
            color_paint(lowest,                      'r', trajanje = 3);
            color_paint(lowest['parent'],            'g', trajanje = 3);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 3);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_left'], lowest, rotation_type = 'lr', trajanje = 2);
            
            rotation_L(lowest['parent']);
            rotation_R(root);
            success = True;
            
            playhead_fwd(interval * 3);
        
    elif root['child_left'] == None:   
        if balance > 1 and root['child_right'] != None and root['child_right']['child_right'] != None:
            lowest = root['child_right']['child_right'];
            color_paint(lowest,                      'r', trajanje = 2);
            color_paint(lowest['parent'],            'g', trajanje = 2);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 2);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_left'], lowest, rotation_type = 'l', trajanje = 2);
            
            rotation_L(root);
            
            playhead_fwd(interval * 2);
            success = True;
        
        elif balance > 1 and root['child_right'] != None and root['child_right']['child_left'] != None:
            lowest = root['child_right']['child_left'];
            color_paint(lowest,                      'r', trajanje = 3);
            color_paint(lowest['parent'],            'g', trajanje = 3);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 3);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_right'], lowest, rotation_type = 'rl', trajanje = 3);
            
            rotation_R(lowest['parent']);
            rotation_L(root);
            
            playhead_fwd(interval * 3);
            
            success = True;
    else:
        if balance < -1 and root['child_left']['child_left'] != None and root['child_left']['child_left']['child_left'] != None:
            lowest = root['child_left']['child_left'];
            color_paint(lowest,                      'r', trajanje = 2);
            color_paint(lowest['parent'],            'g', trajanje = 2);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 2);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_right'], lowest, rotation_type = 'r', trajanje = 2);
            
            rotation_R(root);
            
            playhead_fwd(interval * 2);
            
            success = True;
            
        elif balance < -1:# and root['child_left'] != None and root['child_left']['child_right'] != None:
            lowest = root['child_left']['child_right'];
            color_paint(lowest,                      'r', trajanje = 3);
            color_paint(lowest['parent'],            'g', trajanje = 3);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 3);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_left'], lowest, rotation_type = 'lr', trajanje = 2);
            
            rotation_L(lowest['parent']);
            rotation_R(root);
            success = True;
            
            playhead_fwd(interval * 3);
        if balance > 1 and root['child_right']['child_right'] != None and root['child_right']['child_right']['child_right'] != None:
            lowest = root['child_right']['child_right'];
            color_paint(lowest,                      'r', trajanje = 2);
            color_paint(lowest['parent'],            'g', trajanje = 2);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 2);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_left'], lowest, rotation_type = 'l', trajanje = 2);
            
            rotation_L(root);
            
            playhead_fwd(interval * 2);
            success = True;
        
        elif balance > 1: #and root['child_right'] != None and root['child_right']['child_left'] != None:
            lowest = root['child_right']['child_left'];
            color_paint(lowest,                      'r', trajanje = 3);
            color_paint(lowest['parent'],            'g', trajanje = 3);
            color_paint(lowest['parent']['parent'],  'y', trajanje = 3);
            
            tooltips_rotation(lowest['parent']['parent'], lowest['parent'], lowest['parent']['child_right'], lowest, rotation_type = 'rl', trajanje = 3);
            
            rotation_R(lowest['parent']);
            rotation_L(root);
            
            playhead_fwd(interval * 3);
            
            success = True;
    
    leaves = all_leaves();
    for l in leaves:
        l['height_leftSubtree'  ] = 0;
        l['height_rightSubtree' ] = 0;
        update_height(l);
    
    if success == True:
        
        
        playhead_fwd(-interval * 2);
        tooltip_unbalanced.hide_viewport = True;
        tooltip_unbalanced.keyframe_insert(data_path = 'hide_viewport');
        playhead_fwd( interval * 2);

        return True;
    
    else:
        print("Imao sam problema s rotacijom");
        scene.frame_current = context_time;
        return False;

# Funkcija vraca ukupan broj kljucnih slicica na objektu, za dano svojstvo.
# Primjerice ako je funkcija pozvana u obliku keyframes_count(bpy.data.objects['35'], 'location'),
# funkcija vraca ukupan broj kljucnih slicica koje sadrze informaciju o lokaciji cvora s kljucem 35.
def keyframes_count(object, path):
    if path == None:
        return 0;
        
    if object is None or object.animation_data is None or object.animation_data.action is None or object.animation_data.action.fcurves is None:
        return 0;
    
    return len( object.animation_data.action.fcurves.find(path).keyframe_points );



# Za svaku poveznicu, update_visibility provjerava je li i dalje ispravno povezuje ili ju treba sakriti.
# Poziva se jednom nakon dodavanja novog cvora i obilazi sve postojece poveznice.
def update_visibility():
    print("update_visibility, frame: " + str(scene.frame_current) );
    
    staro = set();

    for obj in tree.objects:

        if obj.name.startswith('link'):
            print("    object: " + obj.name)
            
            # Prvo provjeri je li uopce smijem dodavati kljucne slicice na poveznicu.
            if obj in links_preventAddingKeyframes:
                continue;
            
            if keyframes_count(obj, 'hide_viewport') >= 3:
                # Vec po defaultu ima 2 keyframea, jos jedan nastaje skrivanjem
                links_preventAddingKeyframes.add(obj);
                continue;

            
            parent_ime = obj.name.partition('link_')[2].partition('_')[0];
            child_ime = obj.name.partition('_')[2].partition('_')[2].partition('staro')[0];
            
            parent = bpy.data.objects[parent_ime];
            child = bpy.data.objects[child_ime];
            
            
            if parent['child_left'] == child:
                print("Lijevo dijete od " + parent.name + ": " + parent['child_left'].name);
                print("Roditelj od " + parent['child_left'].name + ": " + parent['child_left']['parent'].name)
            elif parent['child_right'] == child:
                print("Desno dijete od " + parent.name + ": " + parent['child_right'].name);
                print("Roditelj od " + parent['child_right'].name + ": " + parent['child_right']['parent'].name)
            
            # Ukoliko ova poveznica vise ne povezuje prave cvorove, sakrij ju.
            if (parent['child_left'] == child or parent['child_right'] == child) and child['parent'] == parent:
                print("Poveznica " + obj.name + " i dalje ispravno povezuje, moving on");
                continue;
            else:
                print("Poveznica" + obj.name + " je zastarjela, skrivam ju");
                print("");
                obj.hide_viewport = True;
                obj.keyframe_insert(data_path = 'hide_viewport');
                links_preventAddingKeyframes.add(obj);
                staro.add(obj);
    
    
    print("Sakrio sam stare poveznice:");
    for s in staro:
        print(s.name);
    print("");

    return;

# Funkcija dodaje constraint objekte na trazenu poveznicu,
# cime osigurava da se novododane poveznice ispravno prikazuju.
def link_addconstraints(link, roditelj, node):
    
    try:
        test = link.constraints['loc_' + roditelj.name + '_' + node.name];
        print("Constraintovi s ovim imenom vec postoje, vracam se iz funkcije");
        return 0;
    except:
        pass;
    
    constraint = link.constraints.new(type = 'COPY_LOCATION');
    constraint.name = 'loc_' + roditelj.name + '_' + node.name
    constraint.target = roditelj;
    
    # Dodovanje 'track to' constrainta, gdje je objekt stalno usmjeren u neki drugi objekt, odnosno 'target'.
    constraint = link.constraints.new(type = 'TRACK_TO');
    constraint.name = 'track_' + roditelj.name + '_' + node.name
    constraint.target = node;
    constraint.track_axis = 'TRACK_Z';
    constraint.up_axis = 'UP_Y'
    constraint.target_space = 'WORLD';
    constraint.owner_space = 'WORLD';
    
    add_transform_with_external_driver(link, roditelj, node);

    for c in link.constraints:
        if c.name.find(link.name.partition('_')[2]) != -1:
            c.keyframe_insert(data_path = 'influence');
            for k in link.animation_data.action.fcurves.find('constraints["%s"].influence'%c.name).keyframe_points:
                #if int(k[0]) == scene.frame_current:
                k.interpolation = 'CONSTANT';
    
# Poziva se pri rotaciji.
# Preusmjerava poveznice s jednog na drugi cvor,
# uzevsi u obzir promjene u roditelj-dijete odnosima
# koje nastaju nakon rotacije.
def link_remap(link, roditelj, node):
    
    # Primjerice za 'link_46_36', ime_staro = 46_36.
    # Na taj nacin, lako se prepoznaju constraintovi koji odgovaraju trenutnom stanju poveznice.
    ime_staro           = link.name.partition('_')[2];
    ime_stariroditelj   = link.name.partition('_')[2].partition('_')[0];
    ime_staricvor       = link.name.partition('_')[2].partition('_')[2];
    
    for c in link.constraints:
        if c.name.find(ime_staro) != -1:
            c.influence = 0;
            c.keyframe_insert(data_path = 'influence');
            for k in link.animation_data.action.fcurves.find('constraints["%s"].influence'%c.name).keyframe_points:
                k.interpolation = 'CONSTANT';
        if c.name.find(roditelj.name + '_' + node.name) != -1:
            playhead_fwd(-interval);
            c.influence = 0;
            c.keyframe_insert(data_path = 'influence');
            playhead_fwd(interval);
            c.influence = 1;
            c.keyframe_insert(data_path = 'influence');
    
    # Funkcija ispod implicitno dodaje kljucne slicice na novim constraintovima, na trenutnoj slicici.
    link_addconstraints(link, roditelj, node);
    
    for c in link.constraints:
        if c.name.find(roditelj.name + '_' + node.name) != -1:
            playhead_fwd(-interval);
            c.influence = 0;
            c.keyframe_insert(data_path = 'influence');
            playhead_fwd(interval);
            c.influence = 1;
            c.keyframe_insert(data_path = 'influence');
            
        if c.name.find(node.name + '_' + roditelj.name) != -1:
            playhead_fwd(-interval);
            c.influence = 1;
            c.keyframe_insert(data_path = 'influence');
            playhead_fwd(interval);
            c.influence = 0;
            c.keyframe_insert(data_path = 'influence');
        
        if c.name.find(roditelj.name + '_' + node.name) != -1  or  c.name.find(node.name + '_' + roditelj.name) != -1:
            for k in link.animation_data.action.fcurves.find('constraints["%s"].influence'%c.name).keyframe_points:
                k.interpolation = 'CONSTANT';
    
    
    link.name = 'link_' + roditelj.name + '_' + node.name;

    return;

# Funkcija vrsi desnu rotaciju nad cvorom koji je proslijeden kao argument.
def rotation_R(root):

    pivot = root['child_left'];
    B = pivot['child_right'];
    
    
    targetObj_name = 'link_' + root.name + "_" + pivot.name;
    link_root_pivot = tree.objects[targetObj_name];
    link_remap(link_root_pivot, pivot, root);

    if root['parent'] != None:
        targetObj_name = 'link_' + root['parent'].name + "_" + root.name;
        link_parent_root = tree.objects[targetObj_name];
        link_remap(link_parent_root, root['parent'], pivot);
    
    if B != None:    
        targetObj_name = 'link_' + pivot.name + "_" + B.name;
        link_pivot_B = tree.objects[targetObj_name];
        link_remap(link_pivot_B, root, B);

    
    if B != None:
        B['parent'] = root;
    
    if root['parent'] != None and root['parent']['child_left'] == root:
        root['parent']['child_left'] = pivot;
    
    if root['parent'] != None and root['parent']['child_right'] == root:
        root['parent']['child_right'] = pivot;
    
    # Desnom podstablu pivota roditelj vise nije pivot, nego root.
    root['child_left'] = B;

    
    # Ako je root imao roditelja, sada pivot preuzima roditelja od roota.
    # Ovo radi i ako je root ujedno i root_global cijelog stabla.
    pivot['parent'] = root['parent'];
    
    # Sada vise nije root roditelj pivotu, nego pivot roditelj rootu.
    pivot['child_right'] = root;
    root['parent'] = pivot;
    
    
    for c in nodes:
        add_keyframe(c);
    
    playhead_fwd(interval);
    update_root();

    update_positions(root_global);
    
    for c in nodes:
        if c != None:
            space_nodes_apart_arg(c);

    
    return;

# Ista funkcija kao rotation_R, samo simetricna s obzirom na smjer djece.
def rotation_L(root):

    pivot = root['child_right'];
    B = pivot['child_left'];


    targetObj_name = 'link_' + root.name + "_" + pivot.name;
    link_root_pivot = tree.objects[targetObj_name];
    link_remap(link_root_pivot, pivot, root);

    if root['parent'] != None:
        targetObj_name = 'link_' + root['parent'].name + "_" + root.name;
        link_parent_root = tree.objects[targetObj_name];
        link_remap(link_parent_root, root['parent'], pivot);
    
    if B != None:    
        targetObj_name = 'link_' + pivot.name + "_" + B.name;
        link_pivot_B = tree.objects[targetObj_name];
        link_remap(link_pivot_B, root, B);
    
    if B != None:
        B['parent'] = root;
    
    if root['parent'] != None and root['parent']['child_left'] == root:
        root['parent']['child_left'] = pivot;
    
    if root['parent'] != None and root['parent']['child_right'] == root:
        root['parent']['child_right'] = pivot;
    
    # Desnom podstablu pivota roditelj vise nije pivot, nego root.
    root['child_right'] = B;
    
    # Ako je root imao roditelja, sada pivot preuzima roditelja od roota.
    # Ovo radi i ako je root ujedno i root_global cijelog stabla.
    pivot['parent'] = root['parent'];
    
    # Sada vise nije root roditelj pivotu, nego pivot roditelj rootu.
    pivot['child_left'] = root;
    root['parent'] = pivot;
    
        
    for c in nodes:
        add_keyframe(c);
    
    playhead_fwd(interval);
    update_root();
    update_positions(root_global);
    
    for c in nodes:
        if c != None:
            space_nodes_apart_arg(c);
    
    return;

# Uzima u obzir sve cvorove na istoj visini kao cvor u argumentu
# i razmice ih od centra.
def move_nodes_away_from_center(node, children_left = None, children_right = None):
    
    nodes_on_this_level = [];
    for n in nodes:
        if n.location.z == node.location.z:
            nodes_on_this_level.append(n);
    
    if len(nodes_on_this_level) == 0:
        return False;
    
    nodes_on_this_level = sorted(nodes_on_this_level, key = lambda x: x.location.y);
    
    
    for n in nodes_on_this_level:
        if n.location.y > node.location.y: # Ako je novododani cvor s lijeve strane roditelju, pomakni sve desno cvorove nadesno.
            n.location.y += space_unit / 2;
        elif n.location.y < node.location.y:
            n.location.y -= space_unit / 2;
        n.keyframe_insert(data_path = 'location');

    return True;

# Funkcija kao argument prime referencu na jedan cvor,
# string 'l' odnosno 'r' za stranu,
# i vraca cvor koji se prostorno nalazi najblize cvoru iz argumenta
# s lijeve ili desne strane, ovisno o argumentu.
def get_node_nextto(node, side = None):
    if side == None or (side != 'l' and side != 'r'):
        return None;
    
    nodes_sorted_Y = [];
    for n in nodes:
        if n.location.z == node.location.z:
            nodes_sorted_Y.append(n);
    
    nodes_sorted_Y = sorted(nodes_sorted_Y, key = lambda x:(-x.location.z, x.location.y));
    
    index = None;
    for i in range(0, len(nodes_sorted_Y) ):
        if nodes_sorted_Y[i] == node:
            index = i;
            break;
    
    if index == None:
        return None;
    
    try:
        if side == 'l':
            return nodes_sorted_Y[index-1];
        elif side == 'r':    
            return nodes_sorted_Y[index+1];
        else:
            print("Nesto ne valja, ne mogu odrediti stranu");
            return None;
    except IndexError:
        print("Nema trazenog cvora");
        return None;

# Funkcija kao argument prime referencu na jedan cvor,
# string 'l' odnosno 'r' za stranu,
# i vraca sve cvorove na istoj visini s lijeve odnosno desne strane.
def get_nodes_on_side(node, side = None):
    if side == None or (side != 'l' and side != 'r'):
        return None;
    
    nodes_sorted_Y = [];
    for n in nodes:
        if n.location.z != node.location.z:
            continue;
        if side == 'l' and n.location.y < node.location.y:
            nodes_sorted_Y.append(n);
        elif side == 'r' and n.location.y > node.location.y:
            nodes_sorted_Y.append(n);
    
    nodes_sorted_Y = sorted(nodes_sorted_Y, key = lambda x: x.location.y);
    
   
    return nodes_sorted_Y;

# Poziva se tijekom dodavanja svakog cvora u stablo.
# Koristi se samo pri uravnotezenim stablima.
def space_nodes_apart():
    
    moram_micati_cvorove = False;
    node_at_this_location = find_node_at(iterator);
    
    if node_at_this_location != None:
        moram_micati_cvorove = True;
        
        children_left = all_children(root_global['child_left'], 1);
        for c in children_left:
            add_keyframe(c);
            
        children_right  = all_children(root_global['child_right'], 1);
        for c in children_right:
            add_keyframe(c);
            
        playhead_fwd(interval);
    else:
        return;
    
    side = getside_local(node_at_this_location);
    
    coefficient = 2;
    counter_space_nodes_apart = 0;

    iterator_loc_beforeWhile            = iterator.location;
    node_at_this_location_loc_beforeWhile  = node_at_this_location.location;

    while find_node_at(iterator) != None:
        if counter_space_nodes_apart > 15:
            iterator.location           = iterator_loc_beforeWhile;
            node_at_this_location.location = node_at_this_location_loc_beforeWhile;
            break;
        
        if side == 'l':
            iterator.location.y             -= space_unit / coefficient;
            node_at_this_location.location.y   += space_unit / coefficient;
            
        elif side == 'r':
            iterator.location.y             += space_unit / coefficient;
            node_at_this_location.location.y   -= space_unit / coefficient;
            
        if root_global['child_left'] != None and root_global['child_right'] != None:
            for c in children_left:
                c.location.y -= space_unit / coefficient;
            for c in children_right:
                c.location.y += space_unit / coefficient;
        
        coefficient *= 2;
        counter_space_nodes_apart += 1;
        
    if moram_micati_cvorove == True:
        add_keyframe(node_at_this_location);
        for c in children_left:
            add_keyframe(c);
        for c in children_right:
            add_keyframe(c);
    
    scale_back_children_positions(children_left, children_right);
    
    return;

global_tester = False;


# Funkcija za razmicanje cvorova.
# U uravnotezenim stablima, poziva se nakon svake akcije koja bi mogla promijeniti roditelj-dijete odnose u stablu.
def space_nodes_apart_arg(node = None):
    context_time = scene.frame_current;
    
    if node == None or node == root_global:
        return;

    print("Frame: " + str(scene.frame_current) + " - Zovem space_nodes_apart, ali s argumentom");

    node_at_this_location = find_node_at(node);
    if node_at_this_location == node or node_at_this_location == None:
        scene.frame_current = context_time;
        return;
    
    
    children_left = all_children(root_global['child_left' ], 1);
    children_right  = all_children(root_global['child_right'], 1);
    
    for c in children_left:
        add_keyframe(c);
    for c in children_right:
        add_keyframe(c);
    
    
    coefficient = 2;
    
    side_this_local     = getside_local(node);
    side_other_local    = getside_local(node_at_this_location);
    side_this_global    = getside_global(node);
    side_other_global   = getside_global(node_at_this_location);
    
    this_loc_temp = node.location;
    other_loc_temp = node_at_this_location.location;
    
    counter_space_nodes_apart = 0;
    while math.dist(node_at_this_location.location, node.location) < tolerance:
        if counter_space_nodes_apart > 15:
            node.location = this_loc_temp;
            node_at_this_location.location = other_loc_temp;
            add_keyframe(node);
            add_keyframe(node_at_this_location);
            move_nodes_away_from_center(node_at_this_location, children_left, children_right);
            break;
        
        if side_this_local == 'l' and side_other_local == 'r':
            node_at_this_location.location.y -= space_unit / 5;
            node.location.y             += space_unit / 5;
        elif side_this_local == 'r' and side_other_local == 'l':
            node_at_this_location.location.y += space_unit / 5;
            node.location.y             -= space_unit / 5;

        
        if root_global['child_left'] != None and root_global['child_right'] != None:
            for c in children_left:
                c.location.y -= space_unit / 3;
                c.keyframe_insert(data_path = 'location');
            for c in children_right:
                c.location.y += space_unit / 3;
                c.keyframe_insert(data_path = 'location');
        
        coefficient *= 2;
        
        print("Udaljenost nakon " + str(counter_space_nodes_apart) + ". koraka: " + str(math.dist(node_at_this_location.location, node.location)) );
        print("Trenutno izabran node: "     + node.name             );
        print("Cvor koji je odprije tamo: " + node_at_this_location.name );
        
        counter_space_nodes_apart += 1;
    
    # Ovdje su vec dohvacena lijeva i desna djeca korijena.
    # Umjesto da se opet nanovo poziva all_children i opet trazi lijeva odnosno desna djecu korijena,
    # Reciklira se children_left i children_right iz ove funkcije.
    scale_back_children_positions(children_left, children_right);

    scene.frame_current = context_time;
    
    return;

# Funkcija provjerava jesu li lijevo i desno podstablo korijena previse razmaknuti.
# Ako jesu, priblizava lijevo i desno podstablo jedno drugome.
def scale_back_children_positions(children_left, children_right):

    sameheight_mindistance = 999;
    closestnode_left   = None;
    closestnode_right  = None;
    
    
    for n_left in children_left:
        for n_right in children_right:
            if n_left.location.z == n_right.location.z and abs(n_left.location.y - n_right.location.y) < sameheight_mindistance:
                sameheight_mindistance = abs(n_left.location.y - n_right.location.y);
                closestnode_left    = n_left;
                closestnode_right   = n_right;
    
    if closestnode_left == None or closestnode_right == None:
        return;
    
    
    while math.dist(closestnode_left.location, closestnode_right.location)  > space_unit * 2:
        for n in children_left:
            n.location.y += space_unit / 2;
            add_keyframe(n);
        for n in children_right:
            n.location.y -= space_unit / 2;
            add_keyframe(n);
            
        print("Vrtim se u while petlji unutar scale_back_children_positions");
    
    return;

# Poziva se nakon svake rotacije.
# Pocevsi od korijena cijelog stabla,
# funkcija rekurzivno resetira prostorne pozicije svih cvorova.
def update_positions(node):
    add_keyframe(node);
    
    if node == root_global:
        node.location = (0,0,0);
    
    if node['child_left'] != None:
        node['child_left'].location = node.location;
        node['child_left'].location.y -= space_unit;
        node['child_left'].location.z -= space_unit;
        update_positions(node['child_left']);
        
    if node['child_right'] != None:
        node['child_right'].location = node.location;
        node['child_right'].location.y += space_unit;
        node['child_right'].location.z -= space_unit;
        update_positions(node['child_right']);
    
    add_keyframe(node);
    return;

# Poziva se nakon svake rotacije.
# Azurira cvor koji se nalazi u varijabli root_global.
def update_root():
    global root_global;

    for c in nodes:
        if c['parent'] == None:
            root_global = c;
            return root_global;


# Stvorene poveznice, koje povezuju dva cvora, su fiksne duljine.
# Ukoliko se samo jedan od povezanih cvorova pomakne,
# udaljenost izmedu njih se povecava, dok poveznica ostaje iste duljine.
# U takvom slucaju, posljedica toga je da se poveznica ne iscrtava ispravno.
# Ova funkcija postavlja posebnu 'driver' varijablu na poveznicu,
# koja osigurava da je poveznica uvijek ispravne duljine, cak iako se jedan od cvorova pomakne.
def add_transform_with_external_driver(object, target1, target2):

    empty_ime = 'dist_' + target1.name + '_' + target2.name;
    empty = bpy.data.objects.new(name = empty_ime, object_data = None);
    scene_collection.objects.link(empty);
    empty.location = dist_prev.location;
    dist_prev.location.y += 3;
    empty.empty_display_type = 'SINGLE_ARROW';
    
    # Stvaranje nove specijalne 'driver' varijable na empty objektu.
    fcurve = empty.driver_add("scale",2);

    d = fcurve.driver;
    d.type = 'SCRIPTED';
    d.expression = 'dist / 2';

    v = d.variables.new()
    v.name = 'dist'
    v.type = 'LOC_DIFF';

    v.targets[0].id = target1;
    v.targets[1].id = target2;
    
    constraint = object.constraints.new(type='TRANSFORM');
    constraint.name = 'transform_' + target1.name + '_' + target2.name;
    constraint.target = empty;
    constraint.use_motion_extrapolate = True;
    constraint.target_space = 'LOCAL';
    constraint.owner_space  = 'LOCAL';
    
    constraint.map_from = 'SCALE';
    constraint.map_to   = 'SCALE';
    constraint.from_min_z_scale = 0.0;
    constraint.to_min_z_scale   = 0.0;
    constraint.mix_mode_scale = 'MULTIPLY';
    
    object.scale.z = 1.0; # Da bi ovo pravilno radilo, z skala mora biti = 1.
    
    return d;


sphere_red          = bpy.data.objects['sphere_red'];
sphere_green        = bpy.data.objects['sphere_green'];
sphere_yellow       = bpy.data.objects['sphere_yellow'];

controller_red      = bpy.data.objects['controller_red'];
controller_green    = bpy.data.objects['controller_green'];
controller_yellow   = bpy.data.objects['controller_yellow'];


# Funkcija kao argument prima referencu na cvor koji se zeli obojati,
# referencu na jedan od tri cvorova zaduzen za bojanje,
# te integer koji odreduje koliko ce cvor biti obojan u animaciji.
def color_paint(node, color, trajanje = 1):
    # Slicica s kojeg je funkcija pozvana, znaci da se na taj frame potrebno i vratiti.
    context_time = scene.frame_current;
    
    dict_red = {'red','red','r'};
    dict_green = {'green','green','g'};
    dict_yellow = {'yellow','yellow','y'};
    
    sphere_color      = None;
    controller_color = None
    
    if color in dict_red:
        sphere_color = sphere_red;
        controller_color = controller_red;
    elif color in dict_green:
        sphere_color = sphere_green;
        controller_color = controller_green;
    elif color in dict_yellow:
        sphere_color = sphere_yellow;
        controller_color = controller_yellow;
    
    if sphere_color == None:
        print("Ne znam koju boju trebam upotrijebiti");
        return 0;
    
    playhead_fwd(-interval);
    
    constraint_sphere = sphere_color.constraints.new(type = 'COPY_LOCATION');
    constraint_sphere.target = node;
    constraint_sphere.name = 'Location_' + node.name;
    constraint_sphere.use_offset = False;
    constraint_sphere.target_space   = 'WORLD';
    constraint_sphere.owner_space    = 'WORLD';
    
    constraint_sphere.keyframe_insert(data_path = 'influence');
    playhead_fwd(-interval);
    constraint_sphere.influence = 0;
    constraint_sphere.keyframe_insert(data_path = 'influence');
    playhead_fwd(interval);
    
    constraint_controller = controller_color.constraints['Action'];

    constraint_controller.eval_time = 0;
    constraint_controller.keyframe_insert(data_path = 'eval_time');
    playhead_fwd( interval );
    constraint_controller.eval_time = 1;

    constraint_controller.keyframe_insert(data_path = 'eval_time');

    playhead_fwd( -(interval) );
    
    for keyframe in controller_color.animation_data.action.fcurves[0].keyframe_points:
        if keyframe.co[0] == scene.frame_current:
            keyframe.interpolation = 'LINEAR';
            continue;
        if keyframe.co[0] == scene.frame_current + interval:
            keyframe.interpolation = 'LINEAR';
            continue;
    
    # Uklanjanje boju, kad dode vrijeme za to.
    playhead_fwd(interval * trajanje);
    constraint_controller.eval_time = 1;
    constraint_controller.keyframe_insert(data_path = 'eval_time');
    playhead_fwd(interval);
    constraint_controller.eval_time = 0;
    constraint_controller.keyframe_insert(data_path = 'eval_time');
    
    
    constraint_sphere.influence = 1;
    constraint_sphere.keyframe_insert(data_path = 'influence');
    
    playhead_fwd(interval);
    
    constraint_sphere.influence = 0;
    constraint_sphere.keyframe_insert(data_path = 'influence');
    
    
    # Vracanje na slicicu s koje je funkcija pozvana, odnosno vracanje u "sadasnjost".
    scene.frame_current = context_time;

    
    return 1;




arrow_root       = bpy.data.objects['arrow_root'];
arrow_pivot      = bpy.data.objects['arrow_pivot'];
arrow_B          = bpy.data.objects['arrow_B'];
arrow_lowest  = bpy.data.objects['arrow_lowest'];
    
label_root          = bpy.data.objects['label_root'];
label_pivot         = bpy.data.objects['label_pivot'];
label_B             = bpy.data.objects['label_B'];
label_lowest     = bpy.data.objects['label_lowest'];

tooltip_rotation_LL = bpy.data.objects['tooltip_rotation_LL'];
tooltip_rotation_RR = bpy.data.objects['tooltip_rotation_RR'];
tooltip_rotation_LR = bpy.data.objects['tooltip_rotation_LR'];
tooltip_rotation_RL = bpy.data.objects['tooltip_rotation_RL'];

tooltip_add_template      = bpy.data.objects['tooltip_add_template'];
tooltip_cannotAdd_template   = bpy.data.objects['tooltip_cannotAdd_template'];

tooltip_add_L_template    = bpy.data.objects['tooltip_add_L_template'];
tooltip_add_R_template    = bpy.data.objects['tooltip_add_R_template'];

tooltip_unbalanced_template   = bpy.data.objects['tooltip_unbalanced_template'];

# Potrebno za jednu funkciju, gdje je potrebno zamjeniti poredak constraintova u objektu.
def constraint_getindex(object, constraint_ime):
    for i in range(0, len(object.constraints) ):
        if object.constraints[i].name == constraint_ime:
            return i;
    return -1;

# Ova funkcija upravlja iscrtavanjem popratnih tekstualnih pomagala pri rotaciji.
# Funkcija prima reference na cvorove elementarnog podstabla u rotaciji (root, pivot, B ako postoji i lowest, tim redom),
# rotation_type koji sadrzi informaciju o tome je li se radi o lijevoj ili desnoj rotaciji,
# te integer koji odreduje koliko dugo ce se tekstualno pomagalo pojaviti u animaciji.
def tooltips_rotation(root, pivot, B, lowest, rotation_type = None, trajanje = 1):
    dict_lijevo      = {'l','left', 'lijevo'};
    dict_desno       = {'r','right', 'desno'};
    dict_lijevoDesno = {'lr','l-r','left-right', 'lijevo-desno'};
    dict_desnoLijevo = {'rl','r-l','right-left', 'desno-lijevo'};
    
    r = None; # Tip rotacije. Ako se ne uspije saznati o kojem se tipu rotacije radi, podrazumijevano None.
    
    
    if rotation_type.lower()     in dict_lijevo:
        r = 0;
    elif rotation_type.lower()   in dict_desno:
        r = 1;
    elif rotation_type.lower()   in dict_lijevoDesno:
        r = 2;
    elif rotation_type.lower()   in dict_desnoLijevo:
        r = 3;
    
    
    tooltips_list = [tooltip_rotation_RR, tooltip_rotation_LL, tooltip_rotation_RL, tooltip_rotation_LR];

    tooltips_list[r].hide_viewport = False;
    tooltips_list[r].keyframe_insert(data_path = 'hide_viewport');
    
    context_time = scene.frame_current;

    playhead_fwd( - interval * 2);
    
    
    elements = [    (arrow_root,        label_root),
                    (arrow_pivot,       label_pivot),
                    (arrow_B,           label_B),
                    (arrow_lowest,      label_lowest)
                ];


    # Postavljanje svih strelica na odgovarajuca mjesta, i dodavanje kljucnih slicica za lokaciju.
    for e in elements:
        
        context_time_2 = scene.frame_current;
    
        # Ako B uopce ne postoji, preskace se korak koji se tice B.
        if B == None and e[0] == arrow_B:
            continue;
        
        
        constr = e[0].constraints.new(type = 'COPY_LOCATION');
        constr.owner_space  = 'LOCAL';
        constr.target_space = 'WORLD';
        constr.mute = True;
        constr.keyframe_insert(data_path = 'mute');        

        if e[0] == arrow_root:
            constr.target   = root;
            constr.name     = 'Loc_' + root.name;
            
            e[1].location = root.location;
            e[1].location.x += 2;
            e[1].location.y += -5;
            e[1].location.z += 0;
            
        elif e[0] == arrow_pivot:
            constr.target   = pivot;
            constr.name     = 'Loc_' + pivot.name;
        
            e[1].location = pivot.location;
            e[1].location.x += 2;
            e[1].location.y += -5;
            e[1].location.z += 0;
            
        elif e[0] == arrow_B:
            constr.target   = B;
            constr.name     = 'Loc_' + B.name;
            
            e[1].location = B.location;
            e[1].location.x += 2;
            e[1].location.y += -4.5;
            e[1].location.z += 0;
        elif e[0] == arrow_lowest:
            constr.target   = lowest;
            constr.name     = 'Loc_' + lowest.name;
            
            e[1].location = lowest.location;
            e[1].location.x += 2;
            e[1].location.y += -5.5;
            e[1].location.z += 0;
        

        add_keyframe(e[1]);
        
        
        # Zamjena poretka constraintova.
        e[0].constraints.move(from_index = constraint_getindex(e[0], constr.name), to_index = 0);
        
        playhead_fwd(interval);
        
        for i in range(0,2):        
            e[i].hide_viewport = False;
            e[i].keyframe_insert(data_path = 'hide_viewport');

        
        constr.mute = False;
        constr.keyframe_insert('mute');
        
        playhead_fwd(interval * (trajanje + 1) );
        
        constr.mute = True;
        constr.keyframe_insert('mute');
        
        
        for i in range(0,2):        
            e[i].hide_viewport = True;
            e[i].keyframe_insert(data_path = 'hide_viewport');
        
        
        playhead_fwd(-interval * (trajanje) );
        
        add_keyframe(e[1]);
        playhead_fwd(interval * (trajanje - 1) );
        
        # Prvi tuple za root, drugi za pivot, treci za B, cetvrti za lowest.
        displacementList_lijevo = [
            (0, -3.5,  -1),
            (0, -3.5, 4),
            (0, 0, 0),
            (0, -5, 1),
        ];
        
        
        displacementList_desno = [
            (0, 8,  2),
            (0, 3.5, 2),
            (0, 0, 0),
            (0, 5, 1),
        ];
        
        displacementList_lijevoDesno = [
            (0, 5, 3),
            (0,-1, 1),
            (0,-1, 1),
            (0,-1, 1),
        ];
        
        displacementList_desnoLijevo = [
            (0,-1, 0),
            (0, 10, 1),
            (0,-1,1),
            (0, 3, 9),
        ];
        
        
        
        displacementList = [
            displacementList_lijevo,
            displacementList_desno,
            displacementList_lijevoDesno,
            displacementList_desnoLijevo
        ];
        
        
        
        c = None;
        
        if e[1] == label_root:
            c = 0;
        elif e[1] == label_pivot:
            c = 1;
        elif e[1] == label_B:
            c = 2;
        elif e[1] == label_lowest:
            c = 3;
            
            
        # U listi pomaka, za odgovarajuci tip rotacije, za odgovarajuci node,
        # preslikavaju se vrijednosti iz tuplea (x,y,z) u lokaciju od labela, odnosno e[1].
        for i in range(0,3):
            e[1].location[i] += displacementList[r][c][i];
        
        add_keyframe(e[1]);
        
        playhead_fwd(interval);
        add_keyframe(e[1]);
        
        tooltips_list[r].hide_viewport = True;
        tooltips_list[r].keyframe_insert(data_path = 'hide_viewport');
    
        

        scene.frame_current = context_time_2;
    
    
    scene.frame_current = context_time;
    
    
    return;




# Funkcija azurira postavke renderiranja prema globalnim varijablama
# sadrzanima u config_parameterslist, pri vrhu ove datoteke.
# Dodatno, u slucaju da je fps parametar postavljen na nesto osim 24,
# podesava se rendering range i time remapping da se to uzme u obzir.
def pass_config_settings_to_blender_render():
    scene.render.resolution_x           = resolution_x;
    scene.render.resolution_y           = resolution_y;
    scene.render.resolution_percentage  = resolution_percentage;
    
    scene.render.fps = fps;

    factor_fps = round( scene.render.fps / 24 , 1 );
    print("Fps: " + str(scene.render.fps) + ", factor_fps: " + str(factor_fps));
    # za 24 fps: 1   (jer 24/24 = 1  )
    # za 60 fps: 2.5 (jer 60/24 = 2.5) itd
    
    scene.render.frame_map_old = 100;
    scene.render.frame_map_new = scene.render.frame_map_old * factor_fps;
    scene.frame_end *= factor_fps;
    
    # Postavke kvalitete videa.
    scene.render.image_settings.file_format     = file_format;
    scene.render.ffmpeg.format                  = ffmpeg_format;

    scene.render.ffmpeg.codec                   = ffmpeg_codec;
    scene.render.ffmpeg.constant_rate_factor    = ffmpeg_constant_rate_factor;
    scene.render.ffmpeg.ffmpeg_preset           = ffmpeg_ffmpeg_preset;

    return;


# Postavke za boje iz konfiguracijske datoteke se prosljeduju Blenderu.
def pass_config_settings_to_blender_colors():
    color_1_obj.location = color_1;
    color_2_obj.location = color_2;
    color_3_obj.location = color_3;

    if tree_type.find('BST') != -1:
        colorSpheres = [
            bpy.data.objects['sphere_red'],
            bpy.data.objects['sphere_yellow'],
            bpy.data.objects['sphere_green']
        ]
        
        for s in colorSpheres:
            s.hide_viewport = True;
    
    return;

# Pretvara string iz argumenta u float.
def string_2_tuple_float(arg):
    return tuple(float(char) for char in arg.split(' ') );

# Pretvara string iz argumenta u integer.
def string_2_list_int(arg):
    return list(int(char) for char in arg.split(' ') );

# Pretvara string iz argumenta u boolean.
def string_2_bool(arg):
    dict_true   = {'true'};
    dict_false  = {'false'};
    
    if arg.lower() in dict_true:
        return True;
    if arg.lower() in dict_false:
        return False;
        
    return -1;


# Parametar kojem se ne moze pristupiti iz grafickog sucelja.
# Sluzi za eventualno otklanjanje gresaka u kodu.
visualize_script_while_building_enable = False;
def visualize_script_while_building(num = None):
    if visualize_script_while_building_enable == False:
        return;
    
    if num == None:
        num = 1;
    
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations = num);
    return;


# Funkcija cita konfiguracijsku datoteku config.txt i azurira odgovarajuce globalne varijable u ovoj skripti.
# Funkcija funkcionira ako su ispunjena sljedeca dva uvjeta:
# 1) parametar postoji u ovoj skripti
# 2) parametar postoji u config_parameterslist
    
# Sve varijable koje se citaju iz config.txt imaju svoj podrazumijevane vrijednosti.
# U slucaju da nesto ne valja s postavkom u config.txt, varijabla ima podrazumijevanu vrijednost da se skripta moze pravilno izvrsiti.
def read_from_config():

    filename = 'config.txt';
    
    path = os.path.join(os.path.dirname(bpy.data.filepath), filename);
    file_in = open(path, 'r');

    lines = file_in.readlines();

    for l in lines:
        if l == '\n': # Ako se radi o praznom retku, takav se samo ignorira.
            continue;
        
        delimiter                   = ' = ';
        variable    = l.partition(delimiter)[0];
        value       = l.partition(delimiter)[2].rstrip();
        
        if l.partition(delimiter)[1] != delimiter: # Ako linija nije zapisana tocno u formatu 'varijabla = vrijednost', ta linija se ne uzima u obzir.
            continue;
        
        # Primjerice
        # za interval = 5
        # partition vraca tuple ('interval',' = ','5\n')

        for obj in config_parameterslist:
            if obj == variable:

                if isinstance( globals()[obj], bool ) and isinstance( globals()[obj],  int):
                    globals()[obj] = string_2_bool(value);
                elif isinstance( globals()[obj],  int):
                    globals()[obj] = int(value);
                elif isinstance( globals()[obj],str):
                    globals()[obj] = value;
                elif isinstance( globals()[obj], tuple ):
                    globals()[obj] = string_2_tuple_float(value);
                elif isinstance( globals()[obj], list ):
                    globals()[obj] = string_2_list_int(value);
                else:
                    print("Ne mogu postaviti varijablu " + obj + " moving on");
                
    file_in.close();

    return;



def rendering_start():
    if start_rendering == False:
        print("Nemam dopustenje za renderanje, izlazim iz funkcije rendering_start()");
        return False;
    
    scene.render.filepath = r"//renders/tree_vizualization";
    
    # Umjesto ugnjezdivanja nekoliko for petlji odjednom, koristi se next funkcija.
    area = next(area for area in bpy.data.screens['Scripting'].areas    if area.type  == 'VIEW_3D');
    space = next(space for space in area.spaces                         if space.type == 'VIEW_3D');
    space.shading.type = 'MATERIAL';
    space.overlay.show_overlays = False;

    bpy.ops.render.opengl('INVOKE_DEFAULT', animation = True);
    
    return True;


# ==========================
# ***** Glavni program *****
# ==========================
print(15*'_')
print(15*'=')
print(15*'_')
print("Pocinjem program");

read_from_config();
pass_config_settings_to_blender_colors();

context_time = scene.frame_current;
scene.frame_current = scene.frame_start;


nodes = walk_tree();
links_preventAddingKeyframes = set();


print("Clanovi input_lista: ");
for i in input_list:
    print(str(i) + " , type: " + str( type(i) ));

for i in input_list:
    success = addnewnode_BST(i);
    if success == True:
        print("Uspjesno sam dodao cvor " + str(i) );
    else:
        print("Doslo je do pogreske, nisam mogao dodati cvor " + str(i) );
    print("Pomaknut cu se za 1x interval unaprijed");
    
    
    if tree_type.find('AVL') != -1:
        context = scene.frame_current;

        for c in nodes:
            clear_intersection(c);

        scene.frame_current = context;


scene.frame_current = context_time;

scene.frame_end = last_keyframe + 40;

# Krece se s renderanjem i podize prozor za generiranje video datoteke.
pass_config_settings_to_blender_render(); # Za ovu liniju koda je bitno da se pojavi tek nakon postavljanja scene.frame_end.
rendering_start();


print("Nisam naletio na pogresku");
print("Global_tester - " + str(global_tester));
