"""Script to download daily and monthly ESACCI-CLOUD data."""
import logging
from datetime import datetime

from dateutil import relativedelta

from esmvaltool.cmorizers.data.downloaders.wget import WGetDownloader

logger = logging.getLogger(__name__)


def download_dataset(config, dataset, dataset_info, start_date, end_date,
                     overwrite):
    """Download dataset.

    Parameters
    ----------
    config : dict
        ESMValTool's user configuration
    dataset : str
        Name of the dataset
    dataset_info : dict
         Dataset information from the datasets.yml file
    start_date : datetime
        Start of the interval to download
    end_date : datetime
        End of the interval to download
    overwrite : bool
        Overwrite already downloaded files
    """
    if start_date is None:
        start_date = datetime(2000, 1, 1)
    if end_date is None:
        end_date = datetime(2007, 12, 31)
    loop_date = start_date

    downloader = WGetDownloader(
        config=config,
        dataset=dataset,
        dataset_info=dataset_info,
        overwrite=overwrite,
    )

    # Base paths for L3U (daily data) and L3C (monthly data)
    base_path_l3u = ('https://public.satproj.klima.dwd.de/data/ESA_Cloud_CCI/'
                     'CLD_PRODUCTS/v3.0/L3U/')
    base_path_l3c = ('https://public.satproj.klima.dwd.de/data/ESA_Cloud_CCI/'
                     'CLD_PRODUCTS/v3.0/L3C/')

    # File patterns for daily (L3U) and monthly (L3C) data
    files_l3u = [
        "*-ESACCI-L3U_CLOUD-CLD_MASKTYPE-AVHRR_*-fv3.0.nc",
        "*-ESACCI-L3U_CLOUD-CLD_PRODUCTS-AVHRR_*-fv3.0.nc"
    ]
    files_l3c = ["*-ESACCI-L3C_CLOUD-CLD_PRODUCTS-AVHRR_*-fv3.0.nc"]

    wget_options = [
        '-r',
        '-nH',  # Disable the creation of directory structure
        '-e',
        'robots=off',  # Ignore robots.txt
        '--cut-dirs=9',
        '--no-parent',  # Don't ascend to the parent directory
        '--reject="index.html"',  # Reject any HTML files
        '--accept=*.nc'  # Accept only .nc files
    ]

    while loop_date <= end_date:
        year = loop_date.year
        month = loop_date.month
        date = f'{year}{month:02}'

        if int(date) in range(198201, 198601):
            sat_am = 'AVHRR-PM/AVHRR_NOAA-7/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-9/'
        elif int(date) in range(198601, 198901):
            sat_am = 'AVHRR-PM/AVHRR_NOAA-9/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-11/'
        elif int(date) in range(198901, 199501):
            sat_am = 'AVHRR-PM/AVHRR_NOAA-11/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-14/'
        elif int(date) in range(199501, 200101):
            sat_am = 'AVHRR-PM/AVHRR_NOAA-14/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-16/'
        elif int(date) in range(200101, 200501):
            sat_am = 'AVHRR-AM/AVHRR_NOAA-17/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-16/'
        elif int(date) in range(200501, 200701):
            sat_am = 'AVHRR-AM/AVHRR_NOAA-17/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-18/'
        elif int(date) in range(200701, 200901):
            sat_am = 'AVHRR-AM/AVHRR_METOPA/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-18/'
        elif int(date) in range(200901, 201701):
            sat_am = 'AVHRR-AM/AVHRR_METOPA/'
            sat_pm = 'AVHRR-PM/AVHRR_NOAA-19/'
        else:
            logger.error("Number of instrument is not defined for date %s",
                         date)

        # Download daily data from L3U
        for sat in (sat_am, sat_pm):
            logger.info("Downloading daily data (L3U) for sat = %s", sat)
            if sat != '':
                folder_l3u = base_path_l3u + sat + f'{year}/{month:02}'
                logger.info("Download folder for daily data (L3U): %s",
                            folder_l3u)
                try:
                    downloader.download_file(folder_l3u, wget_options)
                except Exception as e:
                    logger.error("Failed to download daily data from %s: %s",
                                 folder_l3u, str(e))

        # Download monthly data from L3C
        for sat in (sat_am, sat_pm):
            logger.info("Downloading monthly data (L3C) for sat = %s", sat)
            if sat != '':
                folder_l3c = base_path_l3c + sat + f'{year}/'
                logger.info("Download folder for monthly data (L3C): %s",
                            folder_l3c)
                try:
                    downloader.download_file(folder_l3c, wget_options)
                except Exception as e:
                    logger.error("Failed to download monthly data from %s: %s",
                                 folder_l3c, str(e))

        # Increment the loop_date by one month
        loop_date += relativedelta.relativedelta(months=1)
