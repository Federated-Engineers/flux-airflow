import logging

from plugins.utils.google_sheet import get_data_from_gsheet

logger = logging.getLogger(__name__)

GSHEET_ID = "1E-gheqe2TQAU5e0p7wwKllupEplJSdcPmm5M_mwrFrY"

GOOGLE_CREDS_SSM_PATH = (
    "/production/google-service-account/credentials"
)

HARVEST_SHEET = "vineyard_harvest_cycle"
EXPORT_SHEET = "export_consignments"


def extract_data():
    """
    Extract data from Google Sheets tabs into pandas DataFrames.
    """

    logger.info("Starting Google Sheets extraction")

    harvest_df = get_data_from_gsheet(
        gsheet_id=GSHEET_ID,
        ssm_path=GOOGLE_CREDS_SSM_PATH,
        sheet_name=HARVEST_SHEET,
    )

    export_df = get_data_from_gsheet(
        gsheet_id=GSHEET_ID,
        ssm_path=GOOGLE_CREDS_SSM_PATH,
        sheet_name=EXPORT_SHEET,
    )

    logger.info(
        "Harvest rows: %s | Export rows: %s",
        len(harvest_df),
        len(export_df),
    )

    return {
        "vineyard_harvest_cycle": harvest_df,
        "export_consignment": export_df,
    }


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    datasets = extract_data()

    print("\nHarvest Data")
    print(datasets["vineyard_harvest_cycle"].head())

    print("\nExport Data")
    print(datasets["export_consignment"].head())

