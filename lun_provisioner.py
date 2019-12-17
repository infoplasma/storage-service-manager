#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import npyscreen as nps
from yaml import safe_load, safe_dump
from jinja2 import Environment, FileSystemLoader


def stop_editability(self):
    self.HOSTNAMES.editable = False
    self.TIER.editable = False
    self.REPLICA.editable = False
    self.LUN_TYPE.editable = False


def enable_editablity(self):
    self.HOSTNAMES.editable = True
    self.TIER.editable = True
    self.REPLICA.editable = True
    self.LUN_TYPE.editable = True


class LunProvisionerForm(nps.ActionFormV2):
    OK_BUTTON_TEXT = 'ADD'
    CANCEL_BUTTON_TEXT = 'DONE'
    def create(self):
        with open('config/config_email.yaml') as yaml_data:
            cfg = safe_load(yaml_data)
        self.HOSTNAMES = self.add(nps.TitleText, name="HOSTNAMES:", value=cfg['HOSTNAMES'],
                                  color='STANDOUT')
        self.TIER = self.add(nps.TitleSelectOne, max_height=3, name="TIER:",
                             values=cfg['TIER'], value=0, scroll_exit=True, rely=4)
        self.REPLICA = self.add(nps.TitleSelectOne, max_height=2, max_width=30, name="REPLICATED:",
                                values=["YES", "NO"], value=0, scroll_exit=True, rely=8)
        self.LUN_TYPE = self.add(nps.TitleSelectOne, max_height=3, max_width=30, name="LUN TYPE:",
                                 values=cfg['LUN_TYPE'], value=0, scroll_exit=True, relx=40, rely=8)
        self.LUN_GB = self.add(nps.TitleText, name="LUN SIZE: ", value=cfg['LUN_GB'],
                               max_width=24, relx=2, rely=12)
        self.LUN_QTY = self.add(nps.TitleText, name="QTY:", value=cfg["LUN_QTY"],
                                max_width=34, relx=26, rely=12)
        self.LUN_GRID = self.add(nps.GridColTitles,
                                 values=[[]],
                                 col_titles=["HOSTNAME", "SIZE [GB]", "QUANTITY", "TIER", "PREFIX", "REPLICA"],
                                 columns=5,
                                 column_width=12,
                                 right_align=True,
                                 select_whole_line=False,
                                 always_show_cursor=False,
                                 rely=17,
                                 editable=False)

    def on_ok(self):
        stop_editability(self)
        TIER = self.TIER.values[self.TIER.value[0]]
        LDEV_PREFIX = self.LUN_TYPE.values[self.LUN_TYPE.value[0]]
        GAD = self.REPLICA.values[self.REPLICA.value[0]]
        IS_GAD = True if GAD == 'YES' else False
        self.LUN_GRID.values.append(
            [self.HOSTNAMES.value, self.LUN_GB.value, self.LUN_QTY.value, TIER, LDEV_PREFIX, IS_GAD])
        self.parentApp.switchForm("LUN PROVISIONER")

    def on_cancel(self):
        enable_editablity(self)
        nps.notify_wait("CONFIGURATION REVIEW.")
        self.parentApp.getForm("CONFIGURATION REVIEW").wgt.values = self.LUN_GRID.values
        self.parentApp.switchForm("CONFIGURATION REVIEW")


class configurationReviewForm(nps.ActionFormV2):

    OK_BUTTON_TEXT = 'WRITE'
    CANCEL_BUTTON_TEXT = 'ERASE'
    CANCEL_BUTTON_BR_OFFSET = (2, 14)

    def create(self):
        self.wgt = self.add(nps.GridColTitles,
                            values=self.parentApp.getForm("LUN PROVISIONER").LUN_GRID.values,
                            col_titles=["HOSTNAME", "SIZE [GB]", "QUANTITY", "TIER", "PREFIX", "REPLICA"],
                            columns=6,
                            column_width=12,
                            right_align=True,
                            select_whole_line=False,
                            always_show_cursor=False,
                            editable=False)

    def on_ok(self):
        data_list = self.parentApp.getForm("LUN PROVISIONER").LUN_GRID.values
        data = {'hostname': data_list[1][0],
                'tier': data_list[1][3],
                'prefix': data_list[1][4],
                'replica': data_list[1][5],
                'devices': [{'size_gb': i[1], 'qty': i[2]} for i in data_list if i]}
        with open("vars/output_params.yaml", "w", encoding='utf-8') as handle:
            safe_dump(data, handle, allow_unicode=True)
        nps.notify_wait("INFO: WRITING CONFIGURATION FILE.")
        with open("vars/output_params.yaml", "r") as handle:
            devs = safe_load(handle)
        j2_env = Environment(loader=FileSystemLoader("."), trim_blocks=True, autoescape=True)
        template = j2_env.get_template("templos/email_templo.j2")
        config = template.render(data=devs)
        with open("output.txt", "w") as output:
            output.write(config)

        self.parentApp.getForm("LUN PROVISIONER").LUN_GRID.values = [[]]
        self.wgt.values = [[]]
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        """
        self.wgt.values = [[]]
        self.parentApp.switchForm("LUN PROVISIONER")
        reset_values(self.parentApp.getForm("LUN PROVISIONER"))
        #enable_editablity(self.parentApp.getForm("LUN PROVISIONER"))
        nps.notify_wait("INFO: ERASING CONFIGURATION.")
        self.mem.LUN_GRID.values = [[]]
        """
        nps.notify_wait("INFO: ERASING CONFIGURATION.")
        self.parentApp.getForm("LUN PROVISIONER").LUN_GRID.values = [[]]
        self.wgt.values = [[]]
        self.parentApp.switchForm("MAIN")
