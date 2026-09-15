"""Independent assertions shared by runtime cohorts and deterministic calibration."""
import re


def assert_pdf_cohort(text, labels, forbidden, title):
    for label in labels:
        if label not in text:
            raise AssertionError("WORKFLOW_INVOICE_LINE missing " + label)
    for label in forbidden:
        if label in text:
            raise AssertionError("WORKFLOW_INVOICE_LINE_TECHNICAL visible " + label)
    if not re.search(r"\b" + re.escape(title) + r"\b", text):
        raise AssertionError("WORKFLOW_INVOICE_LANGUAGE expected " + title)
    if "49" not in text:
        raise AssertionError("WORKFLOW_INVOICE_AMOUNT expected 49")


def accounting_write(query):
    code = getattr(query, "code", query)
    if not isinstance(code, str):
        return False
    return bool(re.search(
        r'\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+"?(?:account_move_line|account_move)"?(?:\s|\(|$)',
        code, re.IGNORECASE,
    ))
