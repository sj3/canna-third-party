from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        cr,
        """
        select id, date_stop from account_period where state='done' ORDER BY 
        date_stop DESC LIMIT 1;
        """,
    )
    period_id, date_stop = cr.fetchall()
    openupgrade.logged_query(
        cr,
        """
        select journal_id from account_journal_period where period_id=%s;
        """,
        (journal_id,),
    )
    rows = cr.fetchall()
    for (journal_id,) in rows:
        openupgrade.logged_query(
            cr,
            """
            UPDATE account_journal SET journal_lock_date = %s WHERE 
            id = %s;
            """,
            (date_stop, journal_id,),
        )
