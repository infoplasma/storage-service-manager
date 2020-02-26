#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import npyscreen as nps
from yaml import safe_load, safe_dump
from helper_funcs import dump_and_render, send_email


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


class LunDecommissionerLogic:
    def __init__(self, form):
        self._form = form
        self._action_type = 'terminate'
        self.SUBJ = "LUN DECOMMISSION REQUEST"

    def load_defaults(self):
        with open('config/ssm_defaults.yaml') as yaml_data:
            return safe_load(yaml_data)

    def add_device_to_deletion_list(self):

        TIER = self._form.TIER.values[self._form.TIER.value[0]]
        LDEV_PREFIX = self._form.LDEV_PREFIX.values[self._form.LDEV_PREFIX.value[0]]
        GAD = self._form.REPLICA.values[self._form.REPLICA.value[0]]
        IS_GAD = True if GAD == 'YES' else False
        self._form.LUN_GRID.values.append(
            [self._form.HOSTNAMES.value, self._form.LUN_GB.value, self._form.LUN_ID.value, TIER, LDEV_PREFIX, IS_GAD])

    def deletion_review_validate_and_transform(self):

        # Validate and transform the current config data
        data_list = self._form.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values
        tier_index = self._form.parentApp.getForm("LUN DECOMMISSIONER").TIER.value[0]
        prefix_index = self._form.parentApp.getForm("LUN DECOMMISSIONER").LDEV_PREFIX.value[0]
        replica_index = 0 if data_list[1][5] is True else 1
        data = {'hostname': data_list[1][0],
                'tier': data_list[1][3],
                'tier_index': tier_index,
                'prefix': data_list[1][4],
                'prefix_index': prefix_index,
                'replica': data_list[1][5],
                'replica_index': replica_index,
                'devices': [{'size_gb': i[1], 'lun_id': i[2]} for i in data_list if i],
                'action_type': self._action_type}
        return data

    def set_terminator_form_values(self):
        _cfg = self.load_defaults()

        self._form.HOSTNAMES.value    = _cfg['HOSTNAMES']
        self._form.TIER.values        = _cfg['TIER']
        self._form.REPLICA.values     = _cfg['REPLICA']
        self._form.LDEV_PREFIX.values = _cfg['LDEV_PREFIX']
        self._form.LUN_GB.value       = _cfg['LUN_GB']
        self._form.LUN_ID.value      = _cfg['LUN_ID']


class LunDecommissionerForm(nps.ActionFormV2):

    # Override button labels
    OK_BUTTON_TEXT = 'ADD'
    CANCEL_BUTTON_TEXT = 'DONE'

    def create(self):

        # Instantiate Decommissioner Logic
        self.Logic = LunDecommissionerLogic(self)

        self.HOSTNAMES   = self.add(nps.TitleText, name="HOSTNAMES:", color='STANDOUT')
        self.TIER        = self.add(nps.TitleSelectOne, max_height=3, name="TIER:", value=0, scroll_exit=True, rely=4)
        self.REPLICA     = self.add(nps.TitleSelectOne, max_height=2, max_width=30, name="REPLICATED:",
                                    value=0, scroll_exit=True, rely=8)
        self.LDEV_PREFIX = self.add(nps.TitleSelectOne, max_height=3, max_width=50, name="LUN TYPE:",
                                    value=0, scroll_exit=True, relx=40, rely=8)
        self.LUN_GB      = self.add(nps.TitleText, name="LUN GB: ", max_width=24, relx=2, rely=12)
        self.LUN_ID      = self.add(nps.TitleText, name="LUN ID:", max_width=34, relx=26, rely=12)
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

        self.Logic.set_terminator_form_values()

    def on_ok(self):

        # Inhibit form fields
        disable_editability(self)

        # Add more devices to the deletion list
        self.Logic.add_device_to_deletion_list()
        self.parentApp.switchForm("LUN DECOMMISSIONER")

    def on_cancel(self):

        # Enable form fields
        enable_editability(self)

        # Accept current deletion list, and switch to review form
        self.parentApp.getForm("DELETION REVIEW").wgt.values = self.LUN_GRID.values
        self.parentApp.switchForm("DELETION REVIEW")


class DeletionReviewForm(nps.ActionFormV2):

    # Override button labels
    OK_BUTTON_TEXT = 'WRITE'
    CANCEL_BUTTON_TEXT = 'ERASE'
    CANCEL_BUTTON_BR_OFFSET = (2, 14)

    def create(self):

        self.Logic = LunDecommissionerLogic(self)
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

        # Validate and transform data
        data = self.Logic.deletion_review_validate_and_transform()

        # Dump and render validated data to file
        nps.notify_wait("INFO: RENDERING CONFIGURATION DATA.")
        dump_and_render(data, "email_deletion_templo.j2")

        # Reset all Forms data
        self.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values = [[]]
        self.wgt.values = [[]]

        # Send email with rendered body and attached configuration data
        nps.notify_wait("INFO: SENDING REQUEST EMAIL.")
        send_email(self.Logic.SUBJ)

        self.parentApp.switchForm("MAIN")

    def on_cancel(self):

        nps.notify_wait("INFO: ERASING CONFIGURATION.")

        # Delete the current configuration data and restart from scratch
        self.parentApp.getForm("LUN DECOMMISSIONER").LUN_GRID.values = [[]]
        self.wgt.values = [[]]
        self.parentApp.switchForm("MAIN")
