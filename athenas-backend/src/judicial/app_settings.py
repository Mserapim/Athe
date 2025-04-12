# -*- coding:utf-8 -*-
from contrib.config import config

JUDICIAL_CONVERT_LIMIT_MEMORY = config("JUDICIAL_CONVERT_LIMIT_MEMORY", default="256MB")
JUDICIAL_CONVERT_LIMIT_MAP = config("JUDICIAL_CONVERT_LIMIT_MAP", default="512MB")
JUDICIAL_CONVERT_DENSITY = config("JUDICIAL_CONVERT_DENSITY", default="120")
JUDICIAL_CONVERT_QUALITY = config("JUDICIAL_CONVERT_QUALITY", default="0.75")


JUDICIAL_URL_CACHE = config(
    "JUDICIAL_URL_CACHE", default="/EJudOutCourtLawsuit/printer"
)
JUDICIAL_URL_PDF = config("JUDICIAL_URL_CACHE", default="/EJudPartLawsuit/read_pdf")
JUDICIAL_URL_PDF_LAWSUIT = config(
    "JUDICIAL_URL_CACHE_LAWSUIT", default="/EJudOutCourtLawsuit/read_pdf"
)
JUDICIAL_DESTINATION_CACHE = config("JUDICIAL_DESTINATION_CACHE", default="lawsuit")

JUDICIAL_WKHTML_CMD = config(
    "JUDICIAL_WKHTML_CMD",
    default=["/usr/bin/xvfb-run", "-a", "/usr/local/bin/wkhtmltopdf"],
)

JUDICIAL_WKHTML_STATIC_PARAMS = config(
    "JUDICIAL_WKHTML_STATIC_PARAMS",
    default=["--disable-smart-shrinking", "--zoom", "0.75", "--enable-internal-links"],
)

JUDICIAL_PDF_ERROR = config(
    "JUDICIAL_PDF_ERROR", default="/app/root/judicial/static/pdf/error"
)
JUDICIAL_PDF_ACCESS_DENIED = config(
    "JUDICIAL_PDF_ACCESS_DENIED", default="/app/root/judicial/static/pdf/access_denied"
)
JUDICIAL_PDF_PROCESSING = config(
    "JUDICIAL_PDF_PROCESSING",
    default="/app/root/judicial/static/pdf/processing_document",
)
