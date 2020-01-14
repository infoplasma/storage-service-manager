#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("*** INFO: LOADING PROGRAM, PLEASE BE PATIENT. ***")

import npyscreen as nps
from lun_provisioner import LunProvisionerForm, ConfigurationReviewForm
from lun_decommissioner import lun_decommissionerForm
from host_provisioner import host_provisionerForm
from host_decommissioner import host_decommissionerForm


class myEntryForm(nps.FormBaseNewWithMenus):
    def create(self):
        self.pager = self.add(nps.Pager, values=["WELCOME TO STORAGE SERVICE MANAGER", "PRESS CTRL-X TO START. THANK YOU."])
        self.menu = self.new_menu(name='OPTION MENU', shortcut=None)
        self.menu.addItem(text="LUN PROVISIONING...............", onSelect=self.lun_provisioner, shortcut='1')
        self.menu.addItem(text="LUN DECOMMISSION...............", onSelect=self.lun_decommissioner, shortcut='2')
        self.menu.addItem(text="HOST PROVISIONING..............", onSelect=self.host_provisioner, shortcut='3')
        self.menu.addItem(text="HOST DECOMMISSION..............", onSelect=self.host_decommissioner, shortcut='4')
        self.menu.addItem(text="EXODUS.........................", onSelect=self.exit_func, shortcut='0')

    def lun_provisioner(self):
        self.parentApp.switchForm("LUN PROVISIONER")

    def lun_decommissioner(self):
        self.parentApp.switchForm("LUN DECOMMISSIONER")

    def host_provisioner(self):
        self.parentApp.switchForm("HOST PROVISIONER")

    def host_decommissioner(self):
        self.parentApp.switchForm("HOST DECOMMISSIONER")

    def exit_func(self):
        # nps.notify_wait("*** INFO: EXITING PROGRAM: >>> GOODBYE! <<< ***")
        self.parentApp.switchForm(None)


class MyApplication(nps.NPSAppManaged):
    def onStart(self):
        nps.setTheme(nps.Themes.ElegantTheme)
        self.addForm('MAIN', myEntryForm, name='STORAGE SERVICE MANAGER')
        self.addForm('LUN PROVISIONER', LunProvisionerForm, name="LUN PROVISIONER")
        self.addForm('LUN DECOMMISSIONER', lun_decommissionerForm, name="LUN DECOMMISSIONER")
        self.addForm('HOST PROVISIONER', host_provisionerForm, name="HOST PROVISIONER")
        self.addForm('HOST DECOMMISSIONER', host_decommissionerForm, name="HOST DECOMMISSIONER")
        self.addForm("CONFIGURATION REVIEW", ConfigurationReviewForm, name="CONFIGURATION REVIEW")


if __name__ == "__main__":
    MyApplication().run()
    print('*** INFO: PROGRAM ENDED, GOODBYE. ***')
