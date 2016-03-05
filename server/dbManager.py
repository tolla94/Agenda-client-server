# -*- coding: utf-8 -*-
import json
import sys
import datetime
import file_url


class ClassDbManager:
    def __init__(self):
        # Dizionario del db
        self.db_file = {'user': file_url.USER,
                        'project': file_url.PROJECT,
                        'location': file_url.LOCATION,
                        'group': file_url.GROUP,
                        'activity': file_url.ACTIVITY,
                        'holiday': file_url.HOLIDAY}
        self.er = '<img src="https://goo.gl/'
        # Liste di dizionari ordinate con le attività di oggi e domani
        self.today_act = []
        self.tomorrow_act = []
        # Data di default, viene modificata al primo avvio di check_today_tomorrow_act()
        self.last_check = {'day': 12, 'month': 11, 'year': 1955, 'hour': 06, 'minute': 38}

    def do_login(self, usr, psw):
        # Dizionario di appoggio
        list_app = self.open_file('user')
        for user in list_app:
            if user['username'] == usr and user['password'] == psw:
                return True
        return False

    def get_activity_from_id_act(self, id_att):
        # Da una id di una attività restituire gli attributi
        # Seleziono da activity l'attività con id passato
        # diz_cond : field, table, where
        # Dizionario di appoggio
        list_app = self.open_file('activity')
        for row in list_app:
            if row['ID'] == id_att:
                return row
        return False

    def get_participants_from_group(self, id_group):
        # Da una id di un gruppo restituire id partecipanti
        # Seleziono da utenti tutti quelli che tra i gruppi hanno quello passato
        # Dizionario di appoggio
        list_app = self.open_file('user')
        # Dizionario di ritorno
        list_return = []
        for row in list_app:
            for group in row['groups']:
                if group['ID'] == id_group:
                    dict_app = {row['ID']: row['username']}
                    list_return.append(dict_app)
                    break
        return list_return

    def get_name_from_id_projects(self, list_id_proj):
        # Da una lista di id progetti restituire id e nome
        # Seleziono da progetti quelli che mi servono e li passo
        # Dizionario di appoggio
        list_app = self.open_file('project')
        # Dizionario di ritorno
        dict_return = dict()
        for proj in list_id_proj:
            for row in list_app:
                if row['ID'] == proj:
                    dict_return = {'ID': row['ID'], 'name': row['name']}
                    break
        return dict_return

    def get_proj_from_id_proj(self, id_proj):
        # Da id del progetto restituire tutto
        # Seleziono il progetto che mi serve e lo restituisco
        # Dizionario di appoggio
        list_app = self.open_file('project')
        for row in list_app:
            if row['ID'] == id_proj:
                return row
        return False

    def get_pjmanager_email(self, id_proj):
        # Da id del progetto restituisco la mail del project manager
        # Seleziono il progetto, ricavo id del PM, lo cerco tra gli utenti e restituisco la mail
        list_app_proj = self.open_file('project')
        list_app_user = self.open_file('user')
        app = 0
        for row in list_app_proj:
            if row['ID'] == id_proj:
                app = row['projectManager']
                break
        for row in list_app_user:
            if row['ID'] == app:
                return row['email']
        return False

    def is_teamleader(self, id_user):
        # Dall'user id trovo se è un teamleader
        # Ricevo l'ID dal login_manager e lo ricerco nel database utenti
        # Apro il file che mi serve
        list_app = self.open_file('user')
        for row in list_app:
            if row['ID'] == id_user:
                return self.is_teamleader_check(row)
        return False

    def is_projectmanager(self, id_user):
        # Dall'user id trovo se è un project manager
        list_app = self.open_file('project')
        for row in list_app:
            if row['projectManager'] == id_user:
                return True
        return False

    def get_today_activities_from_proj(self, id_proj):
        # Da un id progetto trovo tutte le attività
        # Cerco in activity tutte quelle con id progetto uguale a quello richiesto
        # ID, nome, inizio, fine con ora e minuti delle attività di oggi e nome della stanza
        list_app = self.open_file('activity')
        list_act = []
        for row in list_app:
            if row['project'] == id_proj:
                list_act.append(row)
        # Controllo che siano di oggi
        list_today = self.check_act_is_today(list_act)
        list_return = []
        for row in list_today:
            dict_app = {}
            if row['project'] == id_proj:
                dict_app['ID'] = row['ID']
                dict_app['name'] = row['name']
                dict_app['begin'] = {'hour': row['date']['hour'], 'minute': row['date']['minute']}
                hour_app = self.calc_duration(row['date'], row['duration'])
                dict_app['end'] = {'hour': hour_app['hour'], 'minute': hour_app['minute']}
                dict_app['room'] = self.get_room_from_id(row['location'])
                dict_app['type'] = row['type']
                list_return.append(dict_app)
        return list_return

    def check_act_is_today(self, list_act):
        list_keys = []
        list_return = []
        for act in self.today_act:
            list_keys.append(act['ID'])
        for act in list_act:
            if act['ID'] in list_keys:
                list_return.append(act)
        return list_return

    def get_holidays_from_proj(self, id_proj):
        # Da un id di un progetto restituisco tutte le vacanze degli utenti
        # Cerco l'id del gruppo dal progetto, lo confronto nella tabella user
        list_app_proj = self.open_file('project')
        list_app_user = self.open_file('user')
        dict_return = dict()
        app = 0
        for row in list_app_proj:
            if row['ID'] == id_proj:
                app = row['group']
                break
        for row in list_app_user:
            for group in row['groups']:
                if group['ID'] == app:
                    dict_return[row['ID']] = self.get_holiday_from_id(row['holiday'])
        return dict_return

    def get_holiday_from_id(self, hol):
        list_hol = self.open_file('holiday')
        list_return = []
        for holiday in list_hol:
            if holiday['ID'] in hol:
                list_return.append(holiday)
        return list_return

    def get_group_name_from_group(self, id_group):
        # Da un id di un gruppo restituice il nome
        list_app = self.open_file('group')
        for row in list_app:
            if row['ID'] == id_group:
                return row['name']
        return False

    def get_users_from_activity(self, id_act):
        # Da una id di una attività restituire id, user, tentativi
        # Seleziono da activity l'attività con id passato
        # diz_cond : field, table, where
        list_app = self.open_file('activity')
        list_return = []
        dict_app = dict()
        for row in list_app:
            if row['ID'] == id_act:
                for user in row['participants']:
                    dict_app['act'] = id_act
                    dict_app['user'] = user
                    list_return.append(dict_app)
                return list_return
        return list_return

    def check_activity(self):
        # Controllo tutte le attività e restituisco quelle con scadenza = 1 ora, 30 min, 24 ore
        actual_time = self.time_now()
        # Controllo scadenza ora e 30 min
        list_return = self.secondary_hour_check_activity(actual_time)
        list_app = self.secondary_day_check_activity(actual_time)
        list_return[len(list_app):] = list_app[:]
        return list_return

    def secondary_hour_check_activity(self, actual_time):
        list_return = []
        for act in self.today_act:
            # Controllo ora
            if act['date']['hour'] == actual_time['hour'] and act['date']['minute'] == actual_time['minute']:
                list_app = self.secondary_check_activity(act, 1)
                list_return[len(list_app):] = list_app[:]
            # Controllo 30 min
            # Se l'ora è la stessa basta controllare la differenza tra i minuti
            # Se l'ora è maggiore di uno controllo la differenza tra i minuti
            # ma quelli dell'attività vanno incrementati di 60
            if (act['date']['hour'] == actual_time['hour'] and (
                        act['date']['minute'] - actual_time['minute']) == 30) or (
                                act['date']['hour'] - 1 == actual_time['hour'] and (
                                    act['date']['minute'] + 60 - actual_time['minute']) == 30):
                list_app = self.secondary_check_activity(act, 30)
                list_return[len(list_app):] = list_app[:]
        return list_return

    def secondary_day_check_activity(self, actual_time):
        list_return = []
        # Controllo scadenza 24 h
        for act in self.tomorrow_act:
            if act['date']['hour'] == actual_time['hour'] and act['date']['minute'] == actual_time['minute']:
                list_app = self.secondary_check_activity(act, 24)
                list_return[len(list_app):] = list_app[:]
        return list_return

    def secondary_check_activity(self, act, time):
        dict_app = dict()
        list_return = []
        list_app = self.get_users_from_activity(act)
        for user in list_app:
            dict_app['act'] = user['act']
            dict_app['user'] = user['user']
            dict_app['attempt'] = 1
            dict_app['date'] = time
            list_return.append(dict_app)
        return list_return

    def check_today_tomorrow_act(self):
        # Controllo tutte le attività di oggi e domani
        # Lista di appoggio
        list_app = self.open_file('activity')
        # Orario attuale
        actual_time = self.time_now()
        # Se l'ultima volta che è stato aggiornato è oggi non esegue il controllo
        if self.last_check['day'] == actual_time['day'] or self.last_check['month'] == actual_time['month'] or \
                        self.last_check['hour'] == actual_time['hour']:
            return
        for row in list_app:
            if row['date']['year'] == actual_time['year'] and row['date']['month'] == actual_time['month']:
                if row['date']['day'] == actual_time['day']:
                    dict_app = {'ID': row['ID'], 'date': row['date']}
                    self.today_act.append(dict_app)
                # +1 per il giorno dopo
                if row['date']['day'] == actual_time['day'] + 1:
                    dict_app = {row['ID']: row['date']}
                    self.tomorrow_act.append(dict_app)
        self.order_list()
        self.last_check = actual_time

    def order_list(self):
        # Ordino le due liste con gli eventi di oggi e domani
        # Today
        app_list = []
        for app in range(0, len(self.today_act), 1):
            dict_min = self.today_act[0]
            n_min = 0
            for act in range(0, len(self.today_act), 1):
                # Se l'ora nel dict_min è maggiore cambio
                if dict_min['date']['hour'] > self.today_act[act]['date']['hour']:
                    dict_min = self.today_act[act]
                    n_min = act
                    # Se l'ora nel dict_min è uguale ma i minuti sono maggiori cambio
                if dict_min['date']['hour'] == self.today_act[act]['date']['hour'] and dict_min['date']['minute'] > \
                        self.today_act[act]['date']['minute']:
                    dict_min = self.today_act[act]
                    n_min = act
            app_list.append(dict_min)
            self.today_act.pop(n_min)
        self.today_act = app_list
        self.order_list_tomorrow()

    def order_list_tomorrow(self):
        # Tomorrow
        app_list = []
        for act in range(0, len(self.tomorrow_act), 1):
            dict_min = self.tomorrow_act[0]
            n_min = 0
            for act2 in range(0, len(self.tomorrow_act), 1):
                # Se l'ora nel dict_min è maggiore cambio
                if dict_min['date']['hour'] > self.tomorrow_act[act]['date']['hour']:
                    dict_min = self.tomorrow_act[act]['date']
                    n_min = act
                    # Se l'ora nel dict_min è uguale ma i minuti sono maggiori cambio
                if dict_min['date']['hour'] == self.tomorrow_act[act]['date']['hour'] and dict_min['date']['minute'] > \
                        self.tomorrow_act[act]['date']['minute']:
                    dict_min = self.tomorrow_act[act]['date']
                    n_min = act
            app_list.append(dict_min)
            self.tomorrow_act.pop(n_min)
        self.tomorrow_act = app_list
        # Toyota

    def from_user_get_id(self, user):
        # Dal nome utente restituisco id
        list_app = self.open_file('user')
        for row in list_app:
            if row['username'] == user:
                return row['ID']
        return False

    def from_id_get_user(self, id_user):
        # Dal nome utente restituisco id
        list_app = self.open_file('user')
        for row in list_app:
            if row['ID'] == id_user:
                return row['username']
        return False

    def get_proj_from_user(self, id_usr):
        # Prendo tutti i gruppi dell'utente e li confronto con quelli dei progetti
        # Ma prima controllo se è project manager
        list_usr = self.open_file('user')
        list_proj = self.open_file('project')
        # Lista di appoggio
        list_app = []
        dict_return = dict()

        for user in list_usr:
            if user['ID'] == id_usr:
                for group in user['groups']:
                    list_app.append(group['ID'])
                break
        for proj in list_proj:
            if proj['group'] in list_app:
                dict_return[proj['ID']] = proj['name']
            if proj['projectManager'] == id_usr:
                dict_return[proj['ID']] = proj['name']
        return dict_return

    def get_room_from_id(self, id_room):
        # Dall'id di una stanza restituisco il nome
        list_app = self.open_file('location')
        app_return = ""
        for room in list_app:
            if room['ID'] == id_room:
                app_return += room['building'] + "-" + room['room']
                return app_return
        return False

    def get_activity_day(self, day):
        # Da un giorno restituisco un dizionario con le attività di quel giorno (ID, name, begin, end)
        list_app = self.open_file('activity')
        list_return = []
        for activity in list_app:
            dict_app = {}
            if activity['date']['day'] == day['day'] and activity['date']['month'] == day['month'] and activity['date'][
                'year'] == day['year']:
                dict_app['hour'] = activity['date']['hour']
                dict_app['minute'] = activity['date']['minute']
                dict_duration = self.calc_duration(dict_app, activity['duration'])
                list_return.append(
                    {'ID': activity['ID'], 'name': activity['name'], 'begin': activity['date'], 'end': dict_duration,
                     'type': activity['type'], 'room': self.get_room_from_id(activity['location']),
                     'participants': activity['participants']})
        return list_return

    def get_holidays_day(self, day):
        # Da un giorno restituisco una lista con dentro le vacanze di quel giorno
        list_app = self.open_file('holiday')
        list_return = []
        for holiday in list_app:
            if holiday['begin']['year'] <= day['year'] <= holiday['end']['year'] and holiday['begin']['month'] <= day[
                'month'] <= holiday['end']['month'] and holiday['begin']['day'] <= day['day'] <= holiday['end']['day']:
                list_return.append(holiday)
        return list_return

    def get_activity_info(self, id_act, id_user):
        # Da un id di un attività un dizionario con le info:
        dict_return = dict()
        dict_return['activity'] = self.get_activity_from_id_act(id_act)
        dict_return['participants'] = self.get_participants_from_activity(id_act)
        dict_return['group'] = self.get_group_name_from_activity(id_act)
        dict_return['location'] = self.get_room_from_activity(id_act)
        dict_return['modify'] = self.can_modify(id_act, id_user)
        return dict_return

    def get_participants_from_activity(self, id_act):
        list_act = self.open_file('activity')
        dict_return = dict()
        for activity in list_act:
            if activity['ID'] == id_act:
                for part in activity['participants']:
                    dict_return[part] = self.from_id_get_user(part)
                return dict_return
        return False

    def get_group_name_from_activity(self, id_act):
        # Dall'attività trovo l'id del gruppo, poi chiamo get_group_name_from_group
        list_act = self.open_file('activity')
        for activity in list_act:
            if activity['ID'] == id_act:
                if activity['type'] == 'group':
                    return self.get_group_name_from_group(activity['group'])
                return False
        return False

    def get_room_from_activity(self, id_act):
        # Dall'attività trovo l'id della stanza, poi chiamo get_room_from_id
        list_act = self.open_file('activity')
        for activity in list_act:
            if activity['ID'] == id_act:
                return self.get_room_from_id(activity['location'])
        return False

    def can_modify(self, id_act, id_user):
        # Funzione cattivella, restituisce true se:
        # - Utente è taeamleader del suo gruppo
        # - Attività singola di un partecipante
        # - É project manager e attività di progetto o singola
        # - L'utente é lo stesso dell'attività singola
        # Attività di gruppo
        id_group = self.get_group_from_activity(id_act)
        if id_group:
            level = self.get_level_user_group(id_user, id_group)
            type_act = self.get_type_activity_from_activity(id_act)  # 'group' o 'project'
            # Controllo che il gruppo dell'attività sia tra i gruppi di chi sta visualizzando dove è teamleader
            list_team_group = self.get_group_where_lvl(id_user, 'teamleader')
            if level == 'teamleader' and type_act == 'group' and id_group in list_team_group:
                return True
            # Project manager
            if not level and type_act == 'project':
                return True
            return False
        return self.can_modify_app(id_act, id_user)

    def can_modify_app(self, id_act, id_user):
        # Attività singola
        # Il project manager può sempre
        if self.is_projectmanager_of(id_user, self.get_id_proj_from_activity(id_act)):
            return True
        # Il teamleader
        # Dall'attività salgo al progetto, trovo tutti i gruppi
        # Trovo tutti i gruppi dell'utente dove è teamleader
        # Trovo tutti i gruppi del creatore dove è partecipant
        # Merge
        if self.mega_merge(id_act, id_user):
            return True
        return False

    def mega_merge(self, id_act, id_user):
        id_proj = self.get_id_proj_from_activity(id_act)
        # Lista di gruppi del progetto
        list_proj_group = [self.get_group_from_proj(id_proj)]
        list_proj_group += self.from_group_return_sub(self.get_group_from_proj(id_proj))
        # Lista di gruppi del tipello che guarda ed è teamleader
        list_team_group = self.get_group_where_lvl(id_user, 'teamleader')
        # Lista di gruppi dove quello che ha creato è partecipante o teamleader, potrebbe aver creato lui l'evento
        list_part_group = self.get_group_where_lvl(self.get_creator_act(id_act), 'participant')
        list_part_group += self.get_group_where_lvl(self.get_creator_act(id_act), 'teamleader')
        # Tiro fuori il risultato
        # set(a).intersection(b)
        merge = set(list_part_group).intersection(set(list_team_group).intersection(list_proj_group))
        if merge:
            return True
        return False

    def get_creator_act(self, id_act):
        list_act = self.open_file('activity')
        for activity in list_act:
            if activity['ID'] == id_act:
                return activity['creator']
        return False

    def get_group_where_lvl(self, id_user, level):
        # Da un id user ritorno tutti i gruppi dove è teamleader
        list_user = self.open_file('user')
        list_return = []
        for user in list_user:
            if user['ID'] == id_user:
                list_return += self.get_group_where_lvl_app(user['groups'], level)
        return list_return

    def get_group_from_proj(self, id_proj):
        # Da un progetto restituisco l'id del gruppo
        list_proj = self.open_file('project')
        for project in list_proj:
            if project['ID'] == id_proj:
                return project['group']
        return False

    def is_projectmanager_of(self, id_user, id_proj):
        # Da un attività restituisco l'id del gruppo
        list_proj = self.open_file('project')
        for project in list_proj:
            if project['ID'] == id_proj and project['projectManager'] == id_user:
                return True
        return False

    def get_id_proj_from_activity(self, id_act):
        # Da un attività restituisco l'id del progetto
        list_act = self.open_file('activity')
        for activity in list_act:
            if activity['ID'] == id_act:
                return activity['project']
        return False

    def get_group_from_activity(self, id_act):
        # Da un attività restituisco l'id del gruppo
        list_act = self.open_file('activity')
        for activity in list_act:
            if activity['ID'] == id_act:
                return activity['group']
        return False

    def get_level_user_group(self, id_user, id_group):
        list_app = self.open_file('user')
        for user in list_app:
            if user['ID'] == id_user:
                return self.get_level_user_group_app(user['groups'], id_group)
        return False

    def get_type_activity_from_activity(self, id_act):
        # Da un attività restituisco il tipo
        list_act = self.open_file('activity')
        for activity in list_act:
            if activity['ID'] == id_act:
                return activity['type']
        return False

    def from_group_return_sub(self, id_group):
        # Da un gruppo ritorno un sottogruppo
        list_group = self.open_file('group')
        for group in list_group:
            if group['ID'] == id_group:
                return group['subgroup']
        return []

    def get_locations(self):
        # Ritorno tutti gli edifici
        list_location = self.open_file('location')
        list_return = []
        for location in list_location:
            list_return.append({location['ID']: location['building'] + "-" + location['room']})
        return list_return

    def get_teamleader_groups(self, id_usr):
        # Ritorno tutti i gruppi di cui è teamleader
        list_user = self.open_file('user')
        list_return = []
        for user in list_user:
            if user['ID'] == id_usr:
                list_return += self.get_teamleader_groups_app(user['groups'])
                break
        # Avendo assegnano l'id sia alla chiave che al valore posso usarli per ricavare il nome del gruppo
        for group in list_return:
            group['ID'] = self.get_group_name_from_group(group['ID'])
        return list_return

    def get_participants_from_proj(self, id_proj):
        # Da un id di un progetto trovo tutti i partecipanti
        # Prendo il gruppo padre e trovo tutti quelli che partecipano
        list_proj = self.open_file('project')
        list_usr = self.open_file('user')
        id_group = 0
        list_return = []
        for proj in list_proj:
            if proj['ID'] == id_proj:
                id_group = proj['group']
                break
        for user in list_usr:
            for group in user:
                if group['ID'] == id_group:
                    list_return.append({user['ID']: user['username']})
                    break
        return list_return

    def get_not_participants_from_proj(self, id_proj):
        # Trovo il gruppo del progetto, cerco tutti gli utenti che non sono dentro a quel gruppo
        list_proj = self.open_file('project')
        list_usr = self.open_file('user')
        id_group = 0
        list_return = []
        for proj in list_proj:
            if proj['ID'] == id_proj:
                id_group = proj['group']
                break
        for user in list_usr:
            found = True
            for group in user:
                if group['ID'] == id_group:
                    found = False
                    break
            if found:
                list_return.append({user['ID']: user['username']})
        return list_return

    def get_participants_name_lvl_group(self, id_group):
        # Da un id di un gruppo restituisco tutti i nomi dei partecipanti con livello
        list_usr = self.open_file('user')
        list_return = []
        for user in list_usr:
            for group in user['groups']:
                if group['ID'] == id_group:
                    dict_app = {user['ID']: {'username': user['username'], 'level': group['level']}}
                    list_return.append(dict_app)
                    break
        return list_return

    def everybody(self):
        # Restituisco tutti gli utenti
        list_usr = self.open_file('user')
        list_return = []
        for user in list_usr:
            list_return.append({user['ID']: user['username']})
        return list_return

    def user_father_group(self, id_group):
        # Restituisco gli utenti del gruppo padre
        # Trovo i partecipanti del gruppo figlio, quelli del gruppo padre e restituisco la differenza
        list_son = self.get_participants_from_group(id_group)
        id_father = 0
        list_group = self.open_file('group')
        for group in list_group:
            if group['ID'] == id_group:
                id_father = group['father']
                break
        if id_father:
            list_father = self.get_participants_from_group(id_father)
            return [user for user in list_father if user not in list_son]
        return False

    def user_holiday(self, id_usr):
        # Restituisco tutte le vacanze dell'utente
        list_usr = self.open_file('user')
        for user in list_usr:
            if user['ID'] == id_usr:
                return self.get_holiday_from_id(user['holiday'])
        return False

    def from_user_get_groups(self, id_usr):
        list_usr = self.open_file('user')
        list_return = []
        for user in list_usr:
            if user['ID'] == id_usr:
                for group in user['groups']:
                    list_return.append(group['ID'])
        return list_return

    def from_group_get_users(self, id_group):
        list_usr = self.open_file('user')
        list_return = []
        for user in list_usr:
            for group in user['groups']:
                if group['ID'] == id_group:
                    list_return.append(user['ID'])
                    break
        return list_return

    def from_user_get_acts(self, id_usr):
        list_act = self.open_file('activity')
        list_return = []
        for activity in list_act:
            for participant in activity['participants']:
                if participant['ID'] == id_usr:
                    list_return.append(activity['ID'])
                    break
        return list_return

    def from_user_hol(self, id_usr):
        list_usr = self.open_file('user')
        for user in list_usr:
            if user['ID'] == id_usr:
                return user['holiday']
        return []

    def room_occupied(self, day_act, begin, dur):
        # Da una lista di attività della giornata, l'ora di inizio e la durata
        # rispondo con le stanze occupate in quel lasso di tempo
        end = self.calc_duration(begin, dur)
        list_return = []
        for activity in day_act:
            if (activity['begin']['hour'] >= begin['hour'] and activity['begin']['hour'] > end['hour']) or (
                            activity['begin']['hour'] <= begin['hour'] and activity['end']['hour'] >= end['hour']) or (
                            begin['hour'] < activity['end']['hour'] <= end['hour']) or (
                            activity['begin']['hour'] == begin['hour'] and (
                                    (activity['begin']['minute'] >= begin['minute'] and
                                             activity['begin']['minute'] > end[
                                             'minute']) or (
                                                activity['begin']['minute'] <= begin['minute'] and activity['end'][
                                            'minute'] >=
                                            end['minute']) or (
                                            begin['minute'] < activity['begin']['minute'] <= end['minute']))):
                list_return.append(activity['room'])
        return list_return

    @staticmethod
    def home():
        return 'Welcome to TollaServer! V:0.1'

    @staticmethod
    def omg_tolla():
        return open(sys.path[1] + '/server/app.html', "r").read()

    def open_file(self, filename, method="r"):
        try:
            f = open(self.db_file[filename], method)
        except IOError:
            return False
        else:
            return json.load(f)

    def error(self, app):
        if app:
            return self.er + '5UL9yj">'
        else:
            return self.er + 'dmr6pW">'

    ####################################################################################################################
    # Parte di gestione controllo e inserimento nel db
    ####################################################################################################################

    def insert_activity(self, act):
        # act ha dentro {"name": "","project":, "type": "", "creator":,"location":,"group":,"description": "",
        # "participants": [],"date": {"day", "month", "year", "hour", "minute"}, "duration": 2}
        #  Ricevo una attività, controllo che non dia fastidio a nulla, in caso di esito negativo la inserisco

        # Ricevo tutte le attività di quel giorno (ID, name, begin, end)
        day_act = self.get_activity_day(act['date'])
        day_hol = self.get_holidays_day(act['date'])
        # Controllo subito se la stanza non è già occupata
        list_occ_room = self.room_occupied(day_act, act['date'], act['duration'])
        for acttivity in day_act:
            if acttivity['room'] in list_occ_room:
                return "Error: Stanza occupata"
        # Controllo se è un attività singola
        if act['type'] == 'single':
            ids_act = self.get_activites_rel_al_activity(act['creator'])
            ids_hol = self.get_holidays_rel_alone_activity(act['creator'])
        else:
            ids_act = self.get_activites_rel_activity(act['group'])
            ids_hol = self.get_holidays_rel_activity(act['group'])
        # Faccio un intersezione tra tutte le attività di gruppo e quelle del giorno
        for acttivity in day_act:
            if not acttivity['ID'] in ids_act:
                day_act.remove(act)  ## Controllare
        # Faccio una intersezione tra le festività e quelle del giorno
        for hol in day_hol:
            if not hol['ID'] in ids_hol:
                day_hol.remove(hol)  ## Controllare
        # Ci sono delle vacanze in quel giorno
        if day_hol:
            return "Error: Esistono delle vacanze"
        data_end = self.calc_duration(act['date'], act['duration'])
        list_error = self.is_there_something_activity(act['date'], data_end, day_act)
        if list_error:
            return list_error
            # Implementazione programma teo

    def insert_holiday(self, hol, id_usr):
        # hol ha dentro {"begin": {"day", "month", "year"}, "end": {"day", "month","year"}, "name"}
        # id_usr mi serve per capire di chi è la vacanza
        #  Ricevo una vacanza, controllo che non dia fastidio a nulla, in caso di esito negativo la inserisco
        ids_act = self.get_activites_rel_holiday(id_usr)
        # Trovo tutte le attività in quel periodo
        days_act = []
        for year in range(hol['begin']['year'], hol['end']['year'], 1):
            for month in range(hol['begin']['month'], hol['end']['month'], 1):
                for day in range(hol['begin']['day'], hol['end']['day'], 1):
                    days_act.append(self.get_activity_day({'day': day, 'month': month, 'year': year}))
        list_error = self.is_there_something_holiday(id_usr, days_act)
        if list_error:
            return list_error
            # Implementazione programma teo

    def is_there_something_activity(self, date_star, date_end, day_act):
        # Activity edition
        # Controllo che non ci sia nulla in quella data
        # Mi arrivano:
        #   - due date date_start = {hour, minute, day, month, year} e date_end = {hour, minute}.
        #   - day_act e day_hol, due liste contenenti le attività e vacanze di quel giorno
        # Rispondo se c'è già qualcosa
        # Se è una vacanza devo controllare tutte quelle che iniziano prima e finiscono dopo
        # Se è una attività devo controllare che sia di quel giorno e la data di inizio non si incroci con una delle due
        list_return = []
        for activity in day_act:
            date_end_anct = self.calc_duration(activity['date'], activity['duration'])
            """
            if activity['date']['hour'] >= date_star['hour'] and activity['date']['hour'] > date_end['hour']:
                list_return.append({'activity': activity})
            if activity['date']['hour'] <= date_star['hour'] and date_end_anct['hour'] >= date_end['hour']:
                list_return.append({'activity': activity})
            if date_star['hour'] < date_end_anct['hour'] <= date_end['hour']:
                list_return.append({'activity': activity})
            if activity['date']['hour'] == date_star['hour']:
                if activity['date']['minute'] >= date_star['minute'] and activity['date']['minute'] > date_end[
                    'minute']:
                    list_return.append({'activity': activity})
                if activity['date']['minute'] <= date_star['minute'] and date_end_anct['date']['minute'] >= \
                        date_end['minute']:
                    list_return.append({'activity': activity})
                if date_star['minute'] < activity['date']['minute'] <= date_end['minute']:
                    list_return.append({'activity': activity})
            """
            if (activity['date']['hour'] >= date_star['hour'] and activity['date']['hour'] > date_end['hour']) or (
                            activity['date']['hour'] <= date_star['hour'] and date_end_anct['hour'] >= date_end[
                        'hour']) or (date_star['hour'] < date_end_anct['hour'] <= date_end['hour']) or (
                            activity['date']['hour'] == date_star['hour'] and ((activity['date']['minute'] >= date_star[
                        'minute'] and activity['date']['minute'] > date_end['minute']) or (
                                    activity['date']['minute'] <= date_star['minute'] and date_end_anct['date'][
                                'minute'] >= date_end['minute']) or (
                                    date_star['minute'] < activity['date']['minute'] <= date_end['minute']))):
                list_return.append({'activity': activity})
        return list_return

    def is_there_something_holiday(self, id_usr, ids_act):
        # Holiday edition
        # Controllo che non ci sia nulla in quella data e nelle successive
        # Mi arriva una data {day, month, year} e rispondo se c'è già qualcosa
        # Se è una vacanza devo controllare tutte quelle che iniziano prima e finiscono dopo
        # Se è una attività devo controllare che sia di quel giorno e la data di inizio non si incroci con una delle due
        list_return = []
        for activity in ids_act:
            if id_usr in activity['participant']:
                list_return.append(activity)
        return list_return

    def get_activites_rel_al_activity(self, id_usr):
        # Parto da un utente e trovo tutte le attività dei suoi gruppi
        list_group = self.from_user_get_groups(id_usr)
        list_app_usr = []
        list_act = []
        for group in list_group:
            set(list_app_usr).union(self.from_group_get_users(group))
        for user in list_app_usr:
            set(list_act).union(self.from_user_get_acts(user))
        return list_act

    def get_activites_rel_activity(self, id_group):
        # Parto da un gruppo e trovo tutti i gruppi degli utenti con quel gruppo
        # Trovo tutte le attività con quei gruppi
        list_usr = self.open_file('user')
        list_group = []
        list_app_usr = []
        list_act = []
        for user in list_usr:
            for group in list_usr['groups']:
                if group['ID'] == id_group:
                    list_group.append(self.from_user_get_groups(user['ID']))
                    break
        for group in list_group:
            set(list_app_usr).union(self.from_group_get_users(group))
        for user in list_app_usr:
            set(list_act).union(self.from_user_get_acts(user))
        return list_act

    def get_holidays_rel_alone_activity(self, id_usr):
        # Parto dall'utente e trovo tutte le sue vacanze
        return self.from_user_hol(id_usr)

    def get_holidays_rel_activity(self, id_group):
        # Parto da un gruppo e trovo tutti gli utenti
        # Trovo tutte le vacanze degli utenti
        list_usr = self.open_file('user')
        list_app_usr = []
        list_hol = []
        for user in list_usr:
            for group in list_usr['groups']:
                if group['ID'] == id_group:
                    list_app_usr.append(user['ID'])
                    break
        for user in list_app_usr:
            set(list_hol).union(self.from_user_hol(user))
        return list_hol

    def get_activites_rel_holiday(self, id_usr):
        # Parto da un utente e trovo tutti i gruppi degli utenti correlati
        # Trovo tutte le attività con gli utenti
        list_group = self.from_user_get_groups(id_usr)
        list_app_usr = []
        list_act = []
        for group in list_group:
            set(list_app_usr).union(self.from_group_get_users(group))
        for user in list_app_usr:
            set(list_act).union(self.from_user_get_acts(user))
        return list_act

    @staticmethod
    def time_now():
        # Ricevo la data di oggi
        app = datetime.datetime.today()
        # Assegno i valori alla lista actual_time
        actual_time = dict()
        actual_time['day'] = int(app.strftime("%d"))
        actual_time['month'] = int(app.strftime("%m"))
        actual_time['year'] = int(app.strftime("%Y"))
        actual_time['hour'] = int(app.strftime("%H"))
        actual_time['minute'] = int(app.strftime("%M"))
        actual_time['seconds'] = int(app.strftime("%S"))
        return actual_time

    @staticmethod
    def calc_duration(dict_hour, duration):
        # Funzione che data una data calcola la durata
        # Calcolo della durata in ore con resto
        rest = duration % 60
        n_hour = duration / 60
        dict_hour['hour'] += n_hour
        dict_hour['minute'] += rest
        return dict_hour

    @staticmethod
    def is_teamleader_check(row):
        # Funzione di supporto per non far piangere sonarqube
        for group in row['groups']:
            if group['level'] == 'teamleader':
                return True
        return False

    @staticmethod
    def get_teamleader_groups_app(groups):
        list_return = []
        for group in groups:
            if group['level'] == 'teamleader':
                list_return.append(group['ID'])
        return list_return

    @staticmethod
    def get_level_user_group_app(groups, id_group):
        for group in groups:
            if group['ID'] == id_group:
                return group['level']
        return False

    @staticmethod
    def get_group_where_lvl_app(groups, level):
        list_return = []
        for group in groups:
            if group['level'] == level:
                list_return.append(group['ID'])
        return list_return


"""
                if (activity['date']['hour'] >= date_star['hour'] and  activity['date']['hour'] > date_end['hour']) or (activity['date']['hour'] <= date_star['hour'] and  date_end_anct['hour'] >= date_end['hour']) or (date_star['hour'] < date_end_anct['hour'] <= date_end['hour']) or (activity['date']['hour'] == date_star['hour'] and ((activity['date']['minute'] >= date_star['minute'] and activity['date']['minute'] > date_end['minute']) or (activity['date']['minute'] <= date_star['minute'] and date_end_anct['date']['minute'] >= date_end['minute']) or (date_star['minute'] < activity['date']['minute'] <= date_end['minute']))):
"""
