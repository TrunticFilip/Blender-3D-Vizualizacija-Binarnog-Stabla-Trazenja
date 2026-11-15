from tkinter import *;
from tkinter import colorchooser;
from tkinter import filedialog;
import os;

from random import randint;
from pathlib import Path;

otvoriBlender = True;

filename_config = 'config.txt';

file_output = open(filename_config, "w");

# Funkcija se poziva pri pritisku gumba "Generate animation"
# i zapisuje vrijednosti iz sucelja u konfiguracijsku datoteku.
def display():
    for item in dictionary:

        if item == 'inputList':
            rez = globals()['widget_' + item].get("1.0","end-1c");
            ispis = item + " = " + str(rez);
            print( ispis );
            file_output.write(ispis + "\n");
            continue;
        
        rez = globals()['widget_' + item].get();
        ispis = item + " = " + str(rez);
        print( ispis );
        file_output.write(ispis + "\n");
    
    for item in dictionary_tuples:
        rez = globals()['widget_' + item].cget('text');
        ispis = item + " = " + str(rez)
        print( ispis );
        file_output.write( ispis + "\n" );
    
    for item in dictionary_enums:
        rez = globals()['clicked_' + item].get();
        ispis = item + " = " + str(rez);
        print( ispis );
        file_output.write(ispis + "\n");

    if otvoriBlender == True:
        # Ispis u file se zatvara prije nego sto Blender krene citati config.txt.
        file_output.close();

        # Kada je gotovo ispisivanje u konfiguracijsku datoteku, pokrece se .blend datoteka,
        # koja je konfigurirana da automatski pokrene skriptu insertion.py.
        launch_blender();
    else:
        file_output.close();

# Funkcija koja se poziva pritiskom gumba "Odaberi boju" iznad prve boje.
def choose_color_1():
    color_code = colorchooser.askcolor(title ="Choose color");
    ispis = '';
    for i in color_code[0]:
        rez = round( i/255, 2);
        ispis += str(rez) + ' ';
        print(rez);
    widget_color_1.config(text=ispis);
    color_1 = ispis;

# Funkcija ista kao choose_color_1, samo se referira na gumb za drugu boju.
def choose_color_2():
    color_code = colorchooser.askcolor(title ="Choose color");
    #item = 
    ispis = '';
    for i in color_code[0]:
        rez = round( i/255, 2);
        ispis += str(rez) + ' ';
        print(rez);
    widget_color_2.config(text=ispis);
    color_2 = ispis;

# Funkcija ista kao choose_color_1, samo se referira na gumb za trecu boju.
def choose_color_3():
    color_code = colorchooser.askcolor(title ="Choose color");
    #item = 
    ispis = '';
    for i in color_code[0]:
        rez = round( i/255, 2);
        ispis += str(rez) + ' ';
        print(rez);
    widget_color_3.config(text=ispis);
    color_3 = ispis;

# Ova funkcija poziva se klikom na gumb "Generate animation" i pokrece .blend projektnu datoteku,
# koja je konfigurirana da automatski pokrene skriptu insertion.py.
def launch_blender():

    input = widget_inputList.get("1.0","end-1c");

    dozvoljeniZnakovi = {'0','1','2','3','4','5','6','7','8','9', '', ' '};
    for char in input:
        if char not in dozvoljeniZnakovi:
            print("Input nije dobar, trebaju se nalaziti samo brojevi u inputu");
            return;
    
    root_dir = Path(__file__).resolve().parent
    filename = "tree_vizualization.blend";
    path_full = Path(root_dir, filename);
    path_renders = Path(root_dir, 'renders');

    os.startfile(path_full,     'open');
    os.startfile(path_renders,  'open');
    root.destroy();

    return;


# Glavni program.

root = Tk();

globalFontSize = 15;

counter = 0;

label_main = Label(root, text = 'Tree configuration graphic user interface', font='Helvetica 15 bold', borderwidth=5).grid(    row = counter, columnspan=4);
counter += 1;

label_interval = Label(root, text = 'Interval:', font=globalFontSize);
label_interval.grid(               row = counter, column=0);

range = [5,15];
widget_interval = Scale(root, from_ = range[1], to = range[0] );
widget_interval.grid(row = counter + 1, column=0);


label_scale_sphere = Label(root, text = 'Sphere scale:', font=globalFontSize);
label_scale_sphere.grid(          row = counter, column=1);

range = [1,5];
widget_scale_sphere = Scale(root, from_ = range[1], to = range[0]);
widget_scale_sphere.grid(row = counter + 1, column=1);

label_scale_number = Label(root, text = 'Numbers scale:', font=globalFontSize).grid(        row = counter, column=2);

range = [1,5];
widget_scale_number = Scale(root, from_ = range[1], to = range[0] );
widget_scale_number.grid(row = counter + 1, column=2);

range = [3,10];
label_spaceUnit = Label(root, text = 'Space unit:', font=globalFontSize).grid(        row = counter, column=3);
widget_spaceUnit = Scale(root, from_ = range[1], to = range[0] );
widget_spaceUnit.grid(row = counter + 1, column=3);

counter += 2;

color_1 = None;
text_color_1 = (0,0,0);
label_color_1 = Label(root, text = 'Color 1:').grid(        row = counter, column=0);
button_color_1 = Button(root, text = 'Odaberi boju', command=choose_color_1 );
button_color_1.grid(row = counter + 1, column=0);
widget_color_1 = Label(root, text=text_color_1);
widget_color_1.grid(row = counter + 2, column=0);

color_2 = None;
text_color_2 = (0,0,0);
label_color_2 = Label(root, text = 'Color 2:').grid(        row = counter, column=1);
button_color_2 = Button(root, text = 'Odaberi boju', command=choose_color_2 );
button_color_2.grid(row = counter + 1, column=1);
widget_color_2 = Label(root, text=text_color_2);
widget_color_2.grid(row = counter + 2, column=1);

color_3 = None;
text_color_3 = (0,0,0);
label_color_3 = Label(root, text = 'Color 3:').grid(        row = counter, column=2);
button_color_3 = Button(root, text = 'Odaberi boju', command=choose_color_3 );
button_color_3.grid(row = counter + 1, column=2);
widget_color_3 = Label(root, text=text_color_3);
widget_color_3.grid(row = counter + 2, column=2);


dictionary = [
    'inputList',

    'interval',
    'scale_sphere',
    'scale_number',
    'spaceUnit',

    'resolution_x',
    'resolution_y',
    'resolution_percentage',

];

dictionary_tuples = [
    'color_1',
    'color_2',
    'color_3'
]

dictionary_enums = [
    'tree_type',
    'fps',
    
]



clicked_tree_type = StringVar();

options_tree_type = [
    '(BST) Binarno stablo trazenja (nebalansirano)',
    '(AVL) AVL stablo (balansirano)               '
];

clicked_tree_type.set(options_tree_type[0]);

# Callback funkcije se pozivaju nakon odabira u gumbu koji otvara padajući izbornik.
def callback_tree_type(selection):
    global tree_type;
    tree_type = selection
    return;


counter += 3;
label_AVL = Label(root, text = 'Tree type:', font=globalFontSize);
label_AVL.grid(row = counter, column=0);
tree_type = 0;
widget_tree_type = OptionMenu(root, clicked_tree_type, *options_tree_type, command=callback_tree_type);
widget_tree_type.grid(row = counter, column=1);

counter += 1;

# Otvara prozor za pretrazivanje datoteka.
# Poziva se pri pritisku gumba "Import from .txt file".
def browseFiles():
    filename_input = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")));
    filename_input_fileOnly = filename_input.rpartition('/')[2];

    label_readFromTxtFile.configure(text="Pročitana datoteka: " + filename_input_fileOnly);
    file_input  = open(filename_input, "r");
    line = file_input.readline();

    onoStoJeSadaUInputu = widget_inputList.get("1.0","end-1c");
    print("Ispisujem ono sto je trenutno u inputu: " + onoStoJeSadaUInputu);
    widget_inputList.delete('1.0', END);
    widget_inputList.insert( "1.0", line);

    file_input.close();
    return;
      
# Poziva se pri pritisku tipke za generiranje niza nasumicnih brojeva.
def randomize():
    widget_inputList.delete('1.0', END);

    random_LowerLimit = 3;
    random_UpperLimit = 20;
    random_range = randint(random_LowerLimit, random_UpperLimit);

    addedNumbers = set();

    i = 0;
    while i < random_range:
        random_int = randint(random_LowerLimit, random_UpperLimit)
        if random_int not in addedNumbers:
            widget_inputList.insert( "1.0", str(random_int) + " ");
            addedNumbers.add(random_int);
        
        i += 1;
    
    return;


frame_buttons = Frame(root);
frame_buttons.grid(row = counter, column=0, padx=15, pady=15);

label_input = Label(frame_buttons, text='Input:');
label_input.grid(row = 0, column=0);
label_readFromTxtFile = Button(frame_buttons, text="Import keys from .txt file", command=browseFiles);
label_readFromTxtFile.grid(row = 1, column=0);
label_randomize = Button(frame_buttons, text="Generate a random numbers sequence", command=randomize);
label_randomize.grid(row = 2, column=0);

widget_inputList = Text(root, width=35, height=5, font='Helvetica 15 bold');

widget_inputList.grid(row = counter, column=1, columnspan=2);

counter += 1;
frame_heading_2 = Frame(root);
frame_heading_2.grid(row=counter, columnspan=4);
label_heading_2 = Label(frame_heading_2, text='Output settings', font=globalFontSize, pady=10);
label_heading_2.grid(row=0);

counter +=1;

frame_outputSettings = Frame(root);
frame_outputSettings.grid(row = counter, padx=10, pady=10);

rows_internal = 0;
columns_internal = 0;

options_fps =[
    '24',
    '30',
    '50',
    '60',
    '120'
]


clicked_fps = StringVar();

clicked_fps.set(options_fps[0]);

def callback_fps(selection):
    global fps;
    fps = selection
    return;



label_fps = Label(frame_outputSettings, text='Frames per second:');
label_fps.grid(row = rows_internal, column=0);
fps = 24;

widget_label_fps = OptionMenu(frame_outputSettings, clicked_fps, *options_fps, command=callback_fps);

widget_label_fps.grid(row = rows_internal, column=1);
rows_internal += 1;
label_resolution_x = Label(frame_outputSettings, text='Resolution horizontal:');
label_resolution_x.grid(row = rows_internal, column=0);
widget_resolution_x = Entry(frame_outputSettings);
widget_resolution_x.insert(END, '1920');
widget_resolution_x.grid(row = rows_internal, column=1);
rows_internal += 1;
label_resolution_y = Label(frame_outputSettings, text='Resolution vertical:');
label_resolution_y.grid(row = rows_internal, column=0);
widget_resolution_y = Entry(frame_outputSettings);
widget_resolution_y.insert(END, '1080');
widget_resolution_y.grid(row = rows_internal, column=1);
rows_internal += 1;
label_resolution_percentage = Label(frame_outputSettings, text='Resolution percentage:\n(default - 100)');
label_resolution_percentage.grid(row = rows_internal, column=0);
range = [10,100]
widget_resolution_percentage = Scale(frame_outputSettings, from_ = range[0], to = range[1], orient='horizontal');
widget_resolution_percentage.set(100);

widget_resolution_percentage.grid(row = rows_internal, column=1);

rows_internal = 0;
columns_internal += 1;


counter += 1;
frame_propuh = Frame(root);
frame_propuh.grid(row = counter, pady=10);

counter +=1;
button = Button(root, text = 'Generate animation', command=display,  padx=7, pady=7, font= 'Helvetica 15' );
button.grid(row = counter, columnspan=3);


root.mainloop();

try:
    file_output.close();
except:
    pass;