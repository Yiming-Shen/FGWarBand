import httpcodes
import json
import os
import pickle
from flask import Flask, request, render_template, redirect, g, send_from_directory, url_for

# Create exportable app
app = Flask(__name__)
app.troops = {'Augment Gorilla': {'Move': 8, 'Fight': 3, 'Shoot': 0, 'Shield': 10, 'Morale': 2, 'Health': 8, 'Cost': 20,
                                  'Notes': 'Animal, Cannot carry treasure or items'},
              'Lackey': {'Move': 6, 'Fight': 2, 'Shoot': 0, 'Shield': 10, 'Morale': -1, 'Health': 10, 'Cost': 20,
                         'Notes': 'Melee Weapon'},
              'Security': {'Move': 6, 'Fight': 2, 'Shoot': 1, 'Shield': 12, 'Morale': 2, 'Health': 12, 'Cost': 80,
                           'Notes': 'Blaster, Blade'},
              'Engineer': {'Move': 4, 'Fight': 0, 'Shoot': 3, 'Shield': 12, 'Morale': 2, 'Health': 10, 'Cost': 60,
                           'Notes': 'Blaster, Repair Kit'},
              'Medic': {'Move': 5, 'Fight': 0, 'Shoot': 0, 'Shield': 12, 'Morale': 3, 'Health': 10, 'Cost': 50,
                        'Notes': 'Blade, Medkit'},
              'Commando': {'Move': 8, 'Fight': 4, 'Shoot': 0, 'Shield': 10, 'Morale': 4, 'Health': 12, 'Cost': 100,
                           'Notes': 'Stealth Suit, Blade, Needle Gun'},
              'Combat Droid': {'Move': 3, 'Fight': 2, 'Shoot': 4, 'Shield': 14, 'Morale': 0, 'Health': 14, 'Cost': 150,
                               'Notes': 'Mechanoid, Dual Blaster, Claws'},
              }
app.wizard = {
    'Captain': {'Move': 5, 'Fight': 2, 'Shoot': 2, 'Shield': 12, 'Morale': 4, 'Health': 12, 'Cost': 0, 'Skillset': [],
                'Specialism': None, 'Items': [], 'Experience': 0}}
app.apprentice = {'Ensign': {'Move': 7, 'Fight': 0, 'Shoot': -1, 'Shield': 10, 'Morale': 2, 'Health': 8, 'Skillset': [],
                             'Specialism': None, 'Cost': 250, 'Items': [], 'Experience': 0}}
app.specialisms = ['Engineering', 'Psychology', 'Marksman', 'Tactics', 'Melee', 'Defence']
app.skillsets = {'Engineering': ['Repair', 'Sabotage', 'Augment'], 'Psychology': ['Bolster', 'Terror', 'Counter'],
                 'Marksman': ['Aim', 'Pierce', 'Reload'], 'Tactics': ['Squad', 'Ambush', 'Surround'],
                 'Melee': ['Block', 'Risposte', 'Dual'], 'Defence': ['Shield', 'Sacrifice', 'Resolute']}
app.weapon = ['Blaster', 'Needle Gun', 'Blade', 'Cannon', 'Whip']
app.cost = {'Blaster': 5, 'Needle Gun': 12, 'Blade': 3, 'Cannon': 15, 'Whip': 5}
app.accounts = {'a': 'a', 'b': 'b', 'c': 'c'}
app.loggeduser = ""


# make users directory if not exist. return the dictionary of all user information
def checkUsers():
    if os.path.isdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users")):
        users = pickle.load(
            open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"), "rb"))
    else:
        os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"))
        os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"))
        users = {}
        pickle.dump(users,
                    open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"),
                         "wb"))
    return users


@app.route('/')
def welcome_page():
    return app.send_static_file('index.html'), httpcodes.OK


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    users = checkUsers()
    if request.method == 'GET':
        if app.loggeduser == "":
            return render_template('login.html', accounts=users), httpcodes.OK
        else:
            return redirect(url_for("myaccount_page"))
    if request.method == 'POST':
        name = request.form['user']
        app.loggeduser = name
        return redirect(url_for("myaccount_page"))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    users = checkUsers()
    if request.method == 'GET':
        return render_template('register.html', accounts=users), httpcodes.OK
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        users[name] = password
        app.loggeduser = name
        pickle.dump(users,
                    open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"),
                         "wb"))
        os.mkdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), name))
        return redirect(url_for("myaccount_page"))


@app.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        app.loggeduser = ""
        return redirect(url_for("login_page"))


@app.route('/myaccount', methods=['GET'])
def myaccount_page():
    if app.loggeduser == "":
        return redirect(url_for("login_page"))
    else:
        bands = os.listdir(
            os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
        return render_template('myaccount.html', name=app.loggeduser, bands=bands), httpcodes.OK


@app.route('/new', methods=['GET', 'POST'])
def new_warband():
    if request.method == 'GET':
        if app.loggeduser == "":
            return redirect(url_for("login_page"))
        else:
            bands = os.listdir(
                os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
            return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice,
                                   specs=app.specialisms, skills=app.skillsets, weaps=app.weapon,
                                   weapcost=app.cost, userbands=bands), httpcodes.OK
    if request.method == 'POST':
        bandname = request.form['bandname']
        capspec = request.form['capspec']
        capskill = request.form['capskill']
        capweap1 = request.form['capweap1']
        capweap2 = request.form['capweap2']
        troops = json.loads(request.form['troops'])
        createdband = dict()
        createdband['Name'] = bandname
        createdband['Treasury'] = request.form['currency']
        createdband['Public'] = request.form['pub']
        createdband['Captain'] = dict(app.wizard['Captain'])
        createdband['Captain']['Specialism'] = capspec
        createdband['Captain']['Skillset'] = []
        createdband['Captain']['Skillset'].append(capskill)
        createdband['Captain']['Items'] = []
        createdband['Captain']['Items'] += [capweap1]
        createdband['Captain']['Items'] += [capweap2]
        if 'hasensign' in request.form.keys():
            ensspec = request.form['ensspec']
            ensskill = request.form['ensskill']
            ensweap = request.form['ensweap']
            createdband['Ensign'] = dict(app.apprentice['Ensign'])
            createdband['Ensign']['Specialism'] = ensspec
            createdband['Ensign']['Skillset'] = []
            createdband['Ensign']['Skillset'].append(ensskill)
            createdband['Ensign']['Items'] = []
            createdband['Ensign']['Items'] += [ensweap]
        createdband['Troops'] = []
        for item in troops:
            if item != "Empty":
                createdband['Troops'].append(item)
        pickle.dump(createdband, open(os.path.join(
                                os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"),
                                             app.loggeduser), bandname), "wb"))
        return redirect(url_for("myaccount_page"))


@app.route('/edit_<band>', methods=['GET', 'POST'])
def edit_given_warband(band):
    loadedband = pickle.load(
        open(os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser), band),
            "rb"))
    if request.method == 'GET':
        if app.loggeduser == "":
            return redirect(url_for("login_page"))
        else:
            return render_template('editband.html', band=loadedband, people=app.troops, wizard=app.wizard,
                                   apprentice=app.apprentice, specs=app.specialisms, skills=app.skillsets,
                                   weaps=app.weapon, weapcost=app.cost), httpcodes.OK
    if request.method == 'POST':
        bandname = request.form['bandname']
        capspec = request.form['capspec']
        skills = json.loads(request.form['capskill'])
        capweap1 = request.form['capweap1']
        capweap2 = request.form['capweap2']
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
        createdband['Treasury'] = request.form['currency']
        createdband['Public'] = request.form['pub']
        createdband['Captain'] = dict(app.wizard['Captain'])
        createdband['Captain']['Specialism'] = capspec
        createdband['Captain']['Skillset'] = []
        createdband['Captain']['Skillset'].extend(skills)
        createdband['Captain']['Items'] = []
        createdband['Captain']['Items'] += [capweap1]
        createdband['Captain']['Items'] += [capweap2]
        createdband['Captain']['Move'] = capmov
        createdband['Captain']['Fight'] = capfig
        createdband['Captain']['Shoot'] = capsho
        createdband['Captain']['Shield'] = capshi
        createdband['Captain']['Morale'] = capmor
        createdband['Captain']['Health'] = caphea
        createdband['Captain']['Experience'] = capexp
        if 'hasensign' in request.form.keys():
            createdband['Ensign'] = dict(app.apprentice['Ensign'])
            if 'haden' in request.form.keys():
                eskills = json.loads(request.form['ensskill'])
                createdband['Ensign']['Skillset'].extend(eskills)
            else:
                eskills = request.form['ensskill']
                createdband['Ensign']['Skillset'] = []
                createdband['Ensign']['Skillset'].append(eskills)
            ensspec = request.form['ensspec']
            ensmov = request.form['ensmove']
            ensfig = request.form['ensfight']
            enssho = request.form['ensshoot']
            ensshi = request.form['ensshield']
            ensmor = request.form['ensmorale']
            enshea = request.form['enshealth']
            ensexp = request.form['ensexperience']
            ensweap = request.form['ensweap']
            createdband['Ensign']['Specialism'] = ensspec
            createdband['Ensign']['Items'] = []
            createdband['Ensign']['Items'] += [ensweap]
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
        pickle.dump(createdband, open(os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"),
                         app.loggeduser), bandname), "wb"))
        return redirect(url_for("myaccount_page"))


@app.route('/view', methods=['GET'])
def view():
    if app.loggeduser == "":
        return redirect(url_for("login_page"))
    else:
        bands = {}
        bandir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands")
        userfolders = os.listdir(bandir)
        for username in userfolders:
            if username != app.loggeduser:
                if username != ".DS_Store":
                    userpath = os.path.join(bandir, username)
                    userbands = os.listdir(userpath)
                    bands[username] = []
                    for band in userbands:
                        loadedband = pickle.load(open(os.path.join(userpath, band), "rb"))
                        if loadedband['Public'] == "public":
                            bands[username].append(band)
        return render_template('publicbandlist.html', bands=bands)


@app.route('/view/<user>_<band>', methods=['GET'])
def view_band(user, band):
    loadedband = pickle.load(
        open(os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), user), band),
            "rb"))
    if request.method == 'GET':
        if app.loggeduser == "":
            return redirect(url_for("login_page"))
        else:
            return render_template('viewband.html', user=user, band=loadedband, people=app.troops, wizard=app.wizard,
                                   apprentice=app.apprentice, specs=app.specialisms, skills=app.skillsets,
                                   weaps=app.weapon), httpcodes.OK


@app.route('/delete_<band>', methods=['GET'])
def delete_given_warband(band):
    os.remove(
        os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser),
                     band))
    if request.method == 'GET':
        if app.loggeduser == "":
            return redirect(url_for("login_page"))
        else:
            return redirect(url_for("myaccount_page"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
