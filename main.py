import logging
import os
import time
import argparse
from contextlib import contextmanager

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


@contextmanager
def chrome_driver():
    driver = webdriver.Chrome()
    try:
        yield driver
    finally:
        driver.quit()


class ZkFlowParser:
    def __init__(self):
        self.logger = self.setup_logger()
        self.amount_of_addresses = 0
        self.errors = 0

    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('zkFlowParser')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger

    def load_addresses(self, file_name: str) -> list[str]:
        with open(file_name, 'r') as f:
            addresses = (line.rstrip('\n') for line in f)
            return list(addresses)

    def append_to_xlsx(self, file_name: str, data: pd.DataFrame) -> None:
        if os.path.exists(file_name):
            with pd.ExcelWriter(
                path=file_name,
                mode='a',
                engine='openpyxl',
                if_sheet_exists='overlay'
            ) as writer:
                data.to_excel(
                    excel_writer=writer,
                    sheet_name='Results',
                    header=None,
                    startrow=writer.sheets['Results'].max_row,
                    index=False
                )
        else:
            self.logger.info(
                msg=f'File {file_name} does not exist. Creating a new one...'
            )
            data.to_excel(
                file_name,
                index=False,
                header=True,
                sheet_name='Results'
            )

    def process_address(self, id: int, address: str, file_name: str) -> None:
        try:
            with chrome_driver() as driver:
                driver.get(
                    url=f'https://byfishh.github.io/zk-flow/?address={address}'
                )
                time.sleep(4)

                account_data = driver.find_elements(
                    by=By.CSS_SELECTOR,
                    value='h3.text-blue-600'
                )
                activity_last = driver.find_element(
                    by=By.XPATH,
                    value='/html/body/div[1]/main/div/div/div[2]/div[2]/div'
                          '/ul/li[1]/div/div[2]'
                )
                activity_day = driver.find_element(
                    by=By.XPATH,
                    value='/html/body/div[1]/main/div/div/div[2]/div[2]/div'
                          '/ul/li[2]/div/div[2]'
                )
                activity_week = driver.find_element(
                    by=By.XPATH,
                    value='/html/body/div[1]/main/div/div/div[2]/div[2]/div'
                          '/ul/li[3]/div/div[2]'
                )
                activity_month = driver.find_element(
                    by=By.XPATH,
                    value='/html/body/div[1]/main/div/div/div[2]/div[2]/div'
                          '/ul/li[4]/div/div[2]'
                )

                data = pd.DataFrame({
                    'id': [id],
                    'address': [address],
                    'interactions': [account_data[0].text],
                    'volume': [account_data[1].text.split('$')[1]],
                    'fee_spent': [account_data[2].text.split('$')[1]],
                    'last_activity': [activity_last.text],
                    'activity_day': [activity_day.text],
                    'activity_week': [activity_week.text],
                    'activity_month': [activity_month.text],
                })

                self.append_to_xlsx(file_name, data)
                self.logger.info(
                    f'Address: {address} with volume: {account_data[1].text} '
                    'has been parsed and added to the results file.'
                )
        except (NoSuchElementException, TimeoutException) as e:
            self.errors += 1
            self.logger.error(
                msg=f'Error occured while proccessing address {address}:'
                    f'{str(e)}'
            )

    def run(self, input_file: str, output_file: str) -> None:
        self.logger.info('Started.')

        if not os.path.exists(input_file):
            self.logger.error(
                f'The {input_file} file does not exist. Please provide '
                'a valid input file.'
            )
            return

        addresses = self.load_addresses(input_file)
        self.amount_of_addresses = len(addresses)

        for address_id, address in enumerate(addresses, start=1):
            self.process_address(address_id, address, output_file)

        if self.errors != 0:
            self.logger.info(
                msg=f'{self.errors}/{self.amount_of_addresses} '
                'addresses was checked with errors!'
            )
        else:
            self.logger.info('All addresses are successfully checked.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZkFlowParser')
    parser.add_argument(
        'input_file',
        nargs='?',
        default='input.txt',
        help='Path to input .txt file (default: input.txt)'
    )
    parser.add_argument(
        'output_file',
        nargs='?',
        default='output.xlsx',
        help='Path to output .xlsx file (default: output.xlsx)'
    )

    args = parser.parse_args()

    parser = ZkFlowParser()
    parser.run(args.input_file, args.output_file)
