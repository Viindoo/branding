from openupgradelib import openupgrade

del_xml_ids = [
    'to_backend_theme.menu',
    'to_backend_theme.webclient_bootstrap',
    ]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, del_xml_ids)
