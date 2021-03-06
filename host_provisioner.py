import npyscreen as nps
from writers import write_output, write_yaml
from yaml import safe_load


# TODO: ADD PORT MAPPING COMMANDS
# TODO: MANUALLY ENTER THE LUN ID
# TODO: GET NAA IDENTIFIER AND ADD TO EMAIL MESSAGE



class host_provisionerForm(nps.ActionForm):

    def create(self):
        with open('config/unused_config.yaml') as yaml_data:
            cfg = safe_load(yaml_data)
        self.LDEVS = self.add(nps.TitleText, name="Ldev ID's:", value=cfg['LDEVS'])
        self.LDEVS_GB = self.add(nps.TitleText, name="CAPACITY, GB:", value=cfg['LDEVS_GB'])
        self.GAD_RES_NAME = self.add(nps.TitleFixedText, name="GAD_RES_NAME:", value=cfg['GAD_RES_NAME'])
        self.SER_PRI = self.add(nps.TitleFixedText, name="SER_PRI:", value=cfg['SER_PRI'])
        self.SER_SEC = self.add(nps.TitleFixedText, name="SER_SEC:", value=cfg['SER_SEC'])
        self.GAD_SEL = self.add(nps.TitleSelectOne, max_height=2, name="REPLICATED:",
                                values=["YES", "NO"], value=0, scroll_exit=True)
        self.POOL_ID_SEL = self.add(nps.TitleSelectOne, max_height=3, name="POOL ID:",
                                    values=cfg['POOL_ID'], value=0, scroll_exit=True)
        self.LDEV_PREFIX_SEL = self.add(nps.TitleSelectOne, max_height=6, name="LDEV_PREFIX:",
                                        values=cfg['LDEV_PREFIX'], value=0, scroll_exit=True)
        self.GAD_DEV_GRP_SEL = self.add(nps.TitleSelectOne, max_height=6, name="GAD GROUP:",
                                        values=cfg['DEFAULT_GROUPS'], value=0, scroll_exit=True)

    def on_ok(self):
        LDEVS = self.LDEVS.value.upper().split(",")
        LDEVS_GB = self.LDEVS_GB.value.split(",")
        POOL_ID_SEL = self.POOL_ID_SEL
        POOL_ID = POOL_ID_SEL.values[POOL_ID_SEL.value[0]].split(":")[0]
        LDEV_PREFIX_SEL = self.LDEV_PREFIX_SEL
        LDEV_PREFIX = LDEV_PREFIX_SEL.values[LDEV_PREFIX_SEL.value[0]]
        LDEV_PREFIX = LDEV_PREFIX.rstrip("_")
        GAD_SEL = self.GAD_SEL
        GAD = GAD_SEL.values[GAD_SEL.value[0]]
        IS_GAD = True if GAD == 'YES' else False
        GAD_RES_NAME = self.GAD_RES_NAME.value
        GAD_DEV_GRP_SEL = self.GAD_DEV_GRP_SEL
        GAD_DEV_GRP = GAD_DEV_GRP_SEL.values[GAD_DEV_GRP_SEL.value[0]]
        SER_PRI = self.SER_PRI.value
        SER_SEC = self.SER_SEC.value

        if len(LDEVS) != len(LDEVS_GB):
            nps.notify_wait("PLEASE, DOUBLE CHECK LDEVS VS THEIR SIZE", title='WARNING')
        elif not all([len(i) == 4 for i in LDEVS]):
            nps.notify_wait("LDEV ID MUST BE OF EXACTLY _4 DIGITS_, HEX (ex: 012F)", title='WARNING')
        elif not all([j for i in [[k in '0123456789abcdefABCDEF' for k in j] for j in LDEVS] for j in i]):
            nps.notify_wait("LDEV ID MUST BE _HEXADECIMAL_, 4-DIGITS (ex: 012F)", title='WARNING')
        elif not len(LDEVS) == len(set(LDEVS)):
            nps.notify_wait("THERE ARE _REPEATED_ LDEV IDs IN YOUR LIST", title='WARNING')
        else:
            write_yaml(ldev_prefix=LDEV_PREFIX,
                       ldevs_gb=LDEVS_GB,
                       is_gad=IS_GAD,
                       gad_res_name=GAD_RES_NAME,
                       gad_dev_grp=GAD_DEV_GRP,
                       pool_id=POOL_ID,
                       ser_pri=SER_PRI,
                       ser_sec=SER_SEC,
                       ldevs=LDEVS)
            write_output('create')

            nps.notify_wait("CONFIGURATION FILE CREATED.")

        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")


class App(nps.NPSAppManaged):
    def onStart(self):
        nps.setTheme(nps.Themes.ElegantTheme)
        self.addForm("HOST PROVISIONER", host_provisionerForm, name="HOST PROVISIONER")


if __name__ == "__main__":
    App().run()
    print(" *** I WANT PIZZA ***")

