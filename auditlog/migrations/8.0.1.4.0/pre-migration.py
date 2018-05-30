# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info("Creating columns: auditlog_log (model_name, model_model) "
                "and auditlog_log_line (field_description).")
    cr.execute("""
    ALTER TABLE auditlog_log
    ADD COLUMN IF NOT EXISTS model_name VARCHAR,
    ADD COLUMN IF NOT EXISTS model_model VARCHAR;
    ALTER TABLE auditlog_log_line
    ADD COLUMN IF NOT EXISTS field_description VARCHAR
    """)
    logger.info("Creating indexes on auditlog_log column 'model_id' and "
                "auditlog_log_line column 'field_id'.")
    cr.execute("""
    CREATE INDEX auditlog_log_model_id_index ON auditlog_log (model_id);
    CREATE INDEX auditlog_log_line_field_id_index
        ON auditlog_log_line (field_id)
    """)
    logger.info("Preemptive fill auditlog_log columns: 'model_name' and "
                "'model_model'.")
    cr.execute("""
    UPDATE auditlog_log al
    SET model_name = (
      SELECT im.name
      FROM ir_model im
      WHERE im.id = al.model_id
    );
    UPDATE auditlog_log al
    SET model_model = (
      SELECT im.model
      FROM ir_model im
      WHERE im.id = al.model_id
    )
    """)
    logger.info("Preemtive fill of auditlog_log_line columns: 'field_name' and"
                " 'field_description'.")
    cr.execute("""
    UPDATE auditlog_log_line al
    SET field_name = (
      SELECT imf.name
      FROM ir_model_fields imf
      WHERE imf.id = al.field_id
    );
    UPDATE auditlog_log_line al
    SET field_description = (
      SELECT imf.field_description
      FROM ir_model_fields imf
      WHERE imf.id = al.field_id
    )
    """)
    logger.info("Successfully updated auditlog_log and auditlog_log_line "
                "tables.")
