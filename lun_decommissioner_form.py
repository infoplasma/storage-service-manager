#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import npyscreen as nps
from yaml import safe_load, safe_dump
from jinja2 import Environment, FileSystemLoader
from email_sender import send_email
from lun_decommissioner_logic import LunDecommissionerLogic


def disable_editability(self):
    self.HOSTNAMES.editable = False
    self.TIER.editable = False
    self.REPLICA.editable = False
    self.LDEV_PREFIX.editable = False


def enable_editability(self):
    self.HOSTNAMES.editable = True
    self.TIER.editable = True
    self.REPLICA.editable = True
    self.LDEV_PREFIX.editable = True


class LunDecommissionerForm(nps.ActionFormV2):
    OK_BUTTON_TEXT = 'ADD'
    CANCEL_BUTTON_TEXT = 'DONE'

    @staticmethod
    def _load_defaults():
        with open('config/ssm_defaults.yaml') as yaml_data:
            return safe_load(yaml_data)

    def create(self):
        _cfg = self._load_defaults()
        self.HOSTNAMES   = self.add(nps.TitleText, name="HOSTNAMES:", value=_cfg['HOSTNAMES'],
                                    color='STANDOUT')
        self.TIER        = self.add(nps.TitleSelectOne, max_height=3, name="TIER:",
                                    values=_cfg['TIER'], value=0, scroll_exit=True, rely=4)
        self.REPLICA     = self.add(nps.TitleSelectOne, max_height=2, max_width=30, name="REPLICATED:",
                                    values=_cfg['REPLICA'], value=0, scroll_exit=True, rely=8)
        self.LDEV_PREFIX = self.add(nps.TitleSelectOne, max_height=3, max_width=50, name="LUN TYPE:",
                                    values=_cfg['LDEV_PREFIX'], value=0, scroll_exit=True, relx=40, rely=8)
        self.LUN_GB      = self.add(nps.TitleText, name="LUN GB: ", value=_cfg['LUN_GB'],
                                    max_width=24, relx=2, rely=12)
        self.LUN_ID     = self.add(nps.TitleText, name="LDEV ID:", value=_cfg["LUN_ID"],
                                    max_width=34, relx=26, rely=12)
        self.LUN_GRID    = self.add(nps.GridColTitles,
                                    values=[[]],
                                    col_titles=["HOSTNAME", "SIZE [GB]", "ID", "TIER", "PREFIX", "REPLICA"],
                                    columns=5,
                                    column_width=12,
                                    right_align=True,
                                    select_whole_line=False,
                                    always_show_cursor=False,
                                    rely=17,
                                    editable=False)

    def on_ok(self):
        # Add more devices to the deletion list
        disable_editability(self)
        TIER = self.TIER.values[self.TIER.value[0]]
        LDEV_PREFIX = self.LDEV_PREFIX.values[self.LDEV_PREFIX.value[0]]
        GAD = self.REPLICA.values[self.REPLICA.value[0]]
        IS_GAD = True if GAD == 'YES' else False
        self.LUN_GRID.values.append(
            [self.HOSTNAMES.value, self.LUN_GB.value, self.LUN_ID.value, TIER, LDEV_PREFIX, IS_GAD])
        self.parentApp.switchForm("LUN DECOMMISSIONER")

    def on_cancel(self):
        # Accept current deletion list, and switch to review form
        enable_editability(self)
        # nps.notify_wait("CONFIGURATION REVIEW.")
        self.parentApp.getForm("DELETION REVIEW").wgt.values = self.LUN_GRID.values
        self.parentApp.switchForm("DELETION REVIEW")


class DeletionReviewForm(nps.ActionFormV2):
    OK_BUTTON_TEXT = 'WRITE'
    CANCEL_BUTTON_TEXT = 'ERASE'
    CANCEL_BUTTON_BR_OFFSET = (2, 14)

    def create(self):
        self.wgt = self.add(nps.GridColTitles,
                            values=self.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values,
                            col_titles=["HOSTNAME", "SIZE [GB]", "LUN ID", "TIER", "PREFIX", "REPLICA"],
                            columns=6,
                            column_width=12,
                            right_align=True,
                            select_whole_line=False,
                            always_show_cursor=False,
                            editable=False)

    def on_ok(self):
        # Validate, transform, write the current config data and send the email
        data_list = self.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values
        tier_index = self.parentApp.getForm("LUN DECOMMISSIONER").TIER.value[0]
        prefix_index = self.parentApp.getForm("LUN DECOMMISSIONER").LDEV_PREFIX.value[0]
        replica_index = 0 if data_list[1][5] is True else 1
        data = {'hostname': data_list[1][0],
                'tier': data_list[1][3],
                'tier_index': tier_index,
                'prefix': data_list[1][4],
                'prefix_index': prefix_index,
                'replica': data_list[1][5],
                'replica_index': replica_index,
                'devices': [{'size_gb': i[1], 'lun_id': i[2]} for i in data_list if i]}
        with open("vars/params.yaml", "w", encoding='utf-8') as handle:
            safe_dump(data, handle, allow_unicode=True)
        nps.notify_wait("INFO: WRITING CONFIGURATION FILE.")
        with open("vars/params.yaml", "r") as handle:
            devs = safe_load(handle)
        j2_env = Environment(loader=FileSystemLoader("."), trim_blocks=True, autoescape=True)
        template = j2_env.get_template("templos/email_deletion_templo.j2")
        config = template.render(data=devs)
        with open("output.txt", "w") as output:
            output.write(config)
        self.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values = [[]]
        self.wgt.values = [[]]
        nps.notify_wait("*** INFO: SENDING CONFIGURATION DATA. ***")
        send_email()
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        # Delete the curent configuration data and restart from scratch
        """
        self.wgt.values = [[]]
        self.parentApp.switchForm("LUN PROVISIONER")
        reset_values(self.parentApp.getForm("LUN PROVISIONER"))
        #enable_editablity(self.parentApp.getForm("LUN PROVISIONER"))
        nps.notify_wait("INFO: ERASING CONFIGURATION.")
        self.mem.LUN_GRID.values = [[]]
        """
        nps.notify_wait("INFO: ERASING CONFIGURATION.")
        self.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values = [[]]
        self.wgt.values = [[]]
        self.parentApp.switchForm("MAIN")
