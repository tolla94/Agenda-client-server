# -*- coding: utf-8 -*-
# Classe per la gestione delle notifiche
# Notifiche prestabilite: mezzora, un ora e il giorno prima
import requests


class ClassSignalQueue:
    def __init__(self, login_manager, db_manager):
        # Liste è un dizionario (act,user)
        self.modified_queue = []
        self.mod_error_queue = []
        self.activity_queue = []
        self.act_error_queue = []
        self.login_manager = login_manager
        self.db_manager = db_manager

    def add_to_modified(self, id_act):
        app_list = self.db_manager.get_users_from_activity(id_act)
        time = self.db_manager.time_now()
        for item in app_list:
            item['action'] = "update"
            item['attempt'] = 0
            item['date'] = time
            self.modified_queue.append(item)

    def add_to_activity(self):
        time = self.db_manager.time_now()
        list_id = self.get_id_from_activity()
        for act in self.db_manager.today_act:
            # Manca un ora
            if act['date']['hour'] - 1 == time['hour'] and act['date']['minute'] == time[
                'minute'] and act not in list_id:
                self.add_to_activity_app(self.db_manager.get_users_from_activity(act['ID']), time)
            # Manca mezz'ora
            if self.add_to_activity_minute(act, time, list_id):
                self.add_to_activity_app(self.db_manager.get_users_from_activity(act['ID']), time)
        self.add_to_activity_tomorrow(time, list_id)

    @staticmethod
    def add_to_activity_minute(act, time, list_id):
        if (act['date']['hour'] == time['hour'] and act['date']['minute'] - 30 == time['minute'] and act[
            'ID'] not in list_id) or act['date']['hour'] + 1 == time['hour'] and act['date']['minute'] + 30 == time[
            'minute'] and act not in list_id:
            return True

    def add_to_activity_tomorrow(self, time, list_id):
        for act in self.db_manager.tomorrow_act:
            # Manca un giorno
            if act['date']['hour'] == time['hour'] and act['date']['minute'] == time['minute'] and act not in list_id:
                self.add_to_activity_app(self.db_manager.get_users_from_activity(act['ID']), time)

    def add_to_activity_app(self, app_list, time):
        for item in app_list:
            item['action'] = "reminder"
            item['attempt'] = 0
            item['date'] = time
            self.activity_queue.append(item)

    def get_id_from_activity(self):
        list_return = []
        for act in self.activity_queue:
            if act['ID'] not in list_return:
                list_return.append(act['ID'])
        return list_return

    def check_modified(self):
        for activity in self.db_manager.modified_act:
            self.add_to_modified(activity)
            self.db_manager.modified_act.remove(activity)

    def clean_queue(self):
        # Controllo se hanno due mesi di differenza ed elimino
        time = self.db_manager.time_now()
        for item in self.mod_error_queue:
            if time['month'] == item['time']['month'] + 2:
                self.mod_error_queue.pop(item)
        for item in self.act_error_queue:
            if time['month'] == item['time']['month'] + 2:
                self.act_error_queue.pop(item)

    # Id, nome/tempo che manca 24 = giorno,1 = ora,30 = minuti
    # Effettua 5 tentativi, al sesto mette la richiesta nella coda di errore
    def send(self):
        for user in self.modified_queue:
            try:
                requests.post(self.login_manager.from_user_get_ip(user['user']), data={user['act']})
            except:
                if user['attempt'] < 5:
                    user['attempt'] += 1
                else:
                    self.mod_error_queue.append(user)

        for user in self.activity_queue:
            try:
                requests.post(self.login_manager.from_user_get_ip(user['user']), data={user['act']})
            except:
                if user['attempt'] < 5:
                    user['attempt'] += 1
                else:
                    self.act_error_queue.append(user)

    # Funzione che dal login di un utente ritorno le cose che mancano
    def send_user_logged(self, id_user):
        list_return = []
        for user in range(0, len(self.mod_error_queue), 1):
            if self.mod_error_queue[user]['user'] == id_user:
                list_return.append(self.mod_error_queue.pop(user))
        for user in range(0, len(self.act_error_queue), 1):
            if self.act_error_queue[user]['user'] == id_user:
                list_return.append(self.act_error_queue.pop(user))
        return list_return
