import logging

_logger = logging.getLogger(__name__)

SHELLS = ('viin_brand_web', 'viin_brand_base_setup')


def migrate(cr, version):
    """Give the views of viin_brand_web and viin_brand_base_setup to viin_brand.

    Every view keeps its record id, so the customer views that inherit it still point at
    the same record. A shell keeps an external id for each of its records, flagged
    noupdate so the update cleanup leaves it alone: a customer module that still depends
    on the shell resolves them, and a view id points at the record viin_brand owns. The
    shell removal drops these ids and keeps the records. A view that viin_brand holds
    under the same name replaces the copy of the shell: the views inheriting the copy
    move to it and the copy is deleted.
    """
    cr.execute(
        """
        UPDATE ir_ui_view child
           SET inherit_id = brand.res_id
          FROM ir_model_data shell
          JOIN ir_model_data brand
            ON brand.module = 'viin_brand'
           AND brand.model = 'ir.ui.view'
           AND brand.name = shell.name
         WHERE shell.model = 'ir.ui.view'
           AND shell.module IN %s
           AND child.inherit_id = shell.res_id
           AND brand.res_id != shell.res_id
        """,
        (SHELLS,),
    )
    _logger.info("%d views re-pointed to the viin_brand copy of their parent", cr.rowcount)
    cr.execute(
        """
        SELECT shell.res_id
          FROM ir_model_data shell
          JOIN ir_model_data brand
            ON brand.module = 'viin_brand'
           AND brand.model = 'ir.ui.view'
           AND brand.name = shell.name
         WHERE shell.model = 'ir.ui.view'
           AND shell.module IN %s
           AND brand.res_id != shell.res_id
        """,
        (SHELLS,),
    )
    replaced_view_ids = [row[0] for row in cr.fetchall()]
    cr.execute(
        """
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
        SELECT 'viin_brand', shell.name, 'ir.ui.view', shell.res_id, FALSE
          FROM ir_model_data shell
         WHERE shell.model = 'ir.ui.view'
           AND shell.module IN %s
           AND NOT EXISTS (
                SELECT 1
                  FROM ir_model_data brand
                 WHERE brand.module = 'viin_brand'
                   AND brand.model = 'ir.ui.view'
                   AND brand.name = shell.name)
        """,
        (SHELLS,),
    )
    _logger.info("%d view external ids given to viin_brand", cr.rowcount)
    cr.execute(
        """
        UPDATE ir_model_data shell
           SET res_id = brand.res_id,
               noupdate = TRUE
          FROM ir_model_data brand
         WHERE shell.model = 'ir.ui.view'
           AND shell.module IN %s
           AND brand.module = 'viin_brand'
           AND brand.model = 'ir.ui.view'
           AND brand.name = shell.name
        """,
        (SHELLS,),
    )
    cr.execute(
        "UPDATE ir_model_data SET noupdate = TRUE WHERE module IN %s AND model != 'ir.ui.view'",
        (SHELLS,),
    )
    if replaced_view_ids:
        cr.execute("DELETE FROM ir_ui_view WHERE id IN %s", (tuple(replaced_view_ids),))
    _logger.info("%d view copies of the shells replaced by the viin_brand view", len(replaced_view_ids))
