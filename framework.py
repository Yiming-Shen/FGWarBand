import httpcodes
import logging
import json
import os
import pickle
from flask import Flask, request, render_template, redirect, g, send_from_directory

# Create exportable app
app = Flask(__name__)
app.troops = {'Augment Gorilla': {'Move':8, 'Fight':3, 'Shoot':0, 'Shield':10, 'Morale':2, 'Health':8, 'Cost':20, 'Notes':'Animal, Cannot carry treasure or items'},
'Lackey': {'Move':6, 'Fight':2, 'Shoot':0, 'Shield':10, 'Morale':-1, 'Health':10, 'Cost':20, 'Notes':'Melee Weapon'}, 
'Security': {'Move':6, 'Fight':2, 'Shoot':1, 'Shield':12, 'Morale':2, 'Health':12, 'Cost':80, 'Notes':'Blaster, Blade'}, 
'Engineer': {'Move':4, 'Fight':0, 'Shoot':3, 'Shield':12, 'Morale':2, 'Health':10, 'Cost':60, 'Notes':'Blaster, Repair Kit'}, 
'Medic': {'Move':5, 'Fight':0, 'Shoot':0, 'Shield':12, 'Morale':3, 'Health':10, 'Cost':50, 'Notes':'Blade, Medkit'}, 
'Commando': {'Move':8, 'Fight':4, 'Shoot':0, 'Shield':10, 'Morale':4, 'Health':12, 'Cost':100, 'Notes':'Stealth Suit, Blade, Needle Gun'}, 
'Combat Droid': {'Move':3, 'Fight':2, 'Shoot':4, 'Shield':14, 'Morale':0, 'Health':14, 'Cost':150, 'Notes':'Mechanoid, Dual Blaster, Claws'},               
}
app.wizard = {'Captain': {'Move':5, 'Fight':2, 'Shoot':2, 'Shield':12, 'Morale':4, 'Health':12, 'Cost':0,  'Skillset': [], 'Specialism':None, 'Items':[], 'Experience':0}}
app.apprentice = {'Ensign': {'Move':7, 'Fight':0, 'Shoot':-1, 'Shield':10, 'Morale':2, 'Health':8,'Skillset': [], 'Specialism':None, 'Cost':250, 'Items':[], 'Experience':0}}
app.specialisms = [ 'Engineering', 'Psychology', 'Marksman', 'Tactics', 'Melee', 'Defence' ]
app.skillsets = { 'Engineering' : ['Repair', 'Sabotage', 'Augment'], 'Psychology': [ 'Bolster', 'Terror', 'Counter'], 'Marksman': ['Aim', 'Pierce', 'Reload'], 'Tactics': ['Squad', 'Ambush', 'Surround'], 'Melee': ['Block', 'Risposte', 'Dual'], 'Defence': ['Shield', 'Sacrifice', 'Resolute'] }
app.weapon = [ 'Blaster', 'Needle Gun', 'Blade', 'Cannon', 'Whip']
app.cost = { 'Blaster':5, 'Needle Gun':12, 'Blade':3, 'Cannon':15, 'Whip':5 }

@app.route('/', methods=['GET'])
def welcome_page():
    return app.send_static_file('index.html'), httpcodes.OK

def sumband(createdband):
    total = 0;
    for item in   createdband['Captain']['Items']:
        total = total + app.cost[item]
    if 'Ensign' in createdband.keys():
        total = total + 250
        for item in   createdband['Captain']['Items']:
            total = total + app.cost[item]
    for troop in createdband['Troops']:
        total = total + app.troops[troop]['Cost']
    return total

def validate_band(createdband):
    ''' Need to write the validation '''
    return True

def validate_band(oldband,newband):
    return True

@app.route('/new', methods=['GET','POST'])
def new_warband():
    if request.method == 'GET':
       return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon), httpcodes.OK
    if request.method == 'POST':
       bandname = request.form['bandname']
       capspec = request.form['capspec']
       capskill = request.form['capskill']
       capweap = request.form['capweap']
       troops = json.loads(request.form['troops']) 
       createdband = dict()
       createdband['Name'] = bandname
       createdband['Captain'] = dict(app.wizard['Captain'])
       createdband['Captain']['Specialism'] = capspec
       createdband['Captain']['Skillset'].append(capskill)
       createdband['Captain']['Items'].append(capweap)
       if 'hasensign' in request.form.keys():
           
           ensspec = request.form['ensspec']
           ensskill = request.form['ensskill']
           ensweap = request.form['ensweap']
           createdband['Ensign'] = dict(app.apprentice['Ensign'])
           createdband['Ensign']['Specialism'] = ensspec
           createdband['Ensign']['Skillset'].append(ensskill)
           createdband['Ensign']['Items'].append(ensweap)
       createdband['Troops'] = []
       for item in troops:
           if item != "Empty":
               createdband['Troops'].append(item)
       if len(createdband['Troops']) > 9 :
           return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon), httpcodes.BAD_REQUEST
       createdband['Treasury'] = 500 - sumband(createdband)
       if createdband['Treasury'] < 0:
          return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon), httpcodes.BAD_REQUEST
       pickle.dump(createdband, open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"),bandname), "wb"))   
       return render_template('blankband.html', specs = app.specialisms, skills = app.skillsets, people=app.troops, wizard=app.wizard, apprentice=app.apprentice),httpcodes.CREATED


@app.route('/edit', methods=['GET'])
def edit_warband():
    if os.path.isdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands")):
       bands = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"))
    else:
       os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"))
       bands = None
    if request.method == 'GET':
       return render_template('bandlist.html', bands=bands), httpcodes.OK


@app.route('/edit/<band>', methods=['GET','POST'])
def edit_given_warband(band):

    loadedband = pickle.load(open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"),band), "rb"))
    if request.method == 'GET':
       return render_template('editband.html', band=loadedband,  people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon), httpcodes.OK
    if request.method == 'POST':
       
       bandname = request.form['bandname']
       capspec = request.form['capspec']
       #capskill = request.form['capskill']
       skills = json.loads(request.form['capskill'])
       capweap = request.form['capweap']
       troops = json.loads(request.form['troops'])
       capmov = request.form['capmove']
       capfig = request.form['capfight']
       capsho = request.form['capshoot']
       capshi = request.form['capshield']
       capmor = request.form['capmorale']
       caphea = request.form['caphealth']
       capexp = request.form['capexperience']
       createdband = dict()
       createdband['Name'] = bandname
       createdband['Captain'] = dict(app.wizard['Captain'])
       createdband['Captain']['Specialism'] = capspec
       createdband['Captain']['Skillset'].extend(skills)
       createdband['Captain']['Items'].append(capweap)
       createdband['Captain']['Move'] = capmov
       createdband['Captain']['Fight'] = capfig
       createdband['Captain']['Shoot'] = capsho
       createdband['Captain']['Shield'] = capshi
       createdband['Captain']['Morale'] = capmor
       createdband['Captain']['Health'] = caphea
       createdband['Captain']['Experience'] = capexp
       if 'hasensign' in request.form.keys():

           ensspec = request.form['ensspec']
           #ensskill = request.form['ensskill']
           eskills = json.loads(request.form['ensskill'])
           ensmov = request.form['ensmove']
           ensfig = request.form['ensfight']
           enssho = request.form['ensshoot']
           ensshi = request.form['ensshield']
           ensmor = request.form['ensmorale']
           enshea = request.form['enshealth']
           ensexp = request.form['ensexperience']
           ensweap = request.form['ensweap']
           createdband['Ensign'] = dict(app.apprentice['Ensign'])
           createdband['Ensign']['Specialism'] = ensspec
           createdband['Ensign']['Skillset'].extend(eskills)
           createdband['Ensign']['Items'].append(ensweap)
           createdband['Ensign']['Move'] = ensmov 
           createdband['Ensign']['Fight'] = ensfig
           createdband['Ensign']['Shoot'] = enssho 
           createdband['Ensign']['Shield'] = ensshi 
           createdband['Ensign']['Morale'] = ensmor 
           createdband['Ensign']['Health'] = enshea 
           createdband['Ensign']['Experience'] = ensexp 
       createdband['Troops'] = []
       for item in troops:
           if item != "Empty":
              createdband['Troops'].append(item)
       if len(createdband['Troops']) > 9 :
           return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon), httpcodes.OK
       if validate_band(loadedband,createdband):
           createdband['Treasury'] = 500 - sumband(createdband)
           pickle.dump(createdband, open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"),bandname), "wb"))
           return render_template('editband.html', band=createdband, people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon),httpcodes.OK
       else:
           return render_template('editband.html', band=loadedband,  people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon), httpcodes.BAD_REQUEST

@app.route('/delete/<band>', methods=['GET'])
def delete_given_warband(band):
    os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands",band))
    if os.path.isdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands")):
       bands = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"))
    else:
       os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"))
       bands = None
    if request.method == 'GET':
       return render_template('bandlist.html', bands=bands), httpcodes.OK


if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000)
