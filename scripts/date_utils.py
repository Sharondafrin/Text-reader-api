import re
from datetime import datetime
import logging
import numpy as np


'''Languages include
English, French, German, Dutch, Danish, Hungarian, Norwegian, Polish, Swedish'''

months_name2int = {
    1: ("january", "janvier", "januar", "januari", "januar", "január", "januar", "styczeń", "januari"),
    2: ("february", "février", "februar", "februari", "februar", "február", "februar", "luty", "februari"),
    3: ("march", "mars", "märz", "maart", "marts", "március", "mars", "marzec", "mars", "mrt"),
    4: ("april", "avril", "april", "april", "april", "április", "april", "kwiecień", "april"),
    5: ("may", "mai", "mai", "mei", "maj", "május", "mai", "maj", "maj"),
    6: ("june", "juin", "juni", "juni", "juni", "június", "juni", "czerwiec", "juni"),
    7: ("july", "juillet", "juli", "juli", "juli", "július", "juli", "lipiec", "juli"),
    8: ("august", "août", "august", "augustus", "august", "augusztus", "august", "sierpień", "augusti"),
    9: ("september", "septembre", "september", "september", "september", "szeptember", "september", "wrzesień",
        "september"),
    10: ("october", "octobre", "oktober", "oktober", "oktober", "október", "oktober", "październik", "oktober"),
    11: ("november", "novembre", "november", "november", "november", "november", "november", "listopad", "november"),
    12: ("december", "décembre", "dezember", "december", "december", "december", "desember", "grudzień", "december")
}


def str2datetime(date, date_format='%d/%m/%Y', valid_year=None, year_index=None):
    try:
        if valid_year and year_index:
            current_year = datetime.now().year
            year = date.split('/')[year_index]
            date = date.replace(year, valid_year) \
                if len(year) not in (2, 4) and current_year-10 > int(year) > current_year+1 \
                else date

        return datetime.strptime(date, date_format).date()

    except Exception as err:
        logging.error('Failed! String to datetime: %s' % err)
        return None


def datetime2str(date):

    try:
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        return '{}-{}-{}'.format(date.year, month, day)
    except Exception as err:
        logging.error('datetime to string failed: {}'.format(err))

    return ''


def get_date_format(dates):

    current_year = int(datetime.now().year)

    year_indices = [index for date in dates for index, value in enumerate(date.split('/')) if len(value) == 4
                    and current_year-10 <= int(value) <= current_year+2]
    date_format = '%d/%m/%Y' if any(year_indices) else '%d/%m/%y'

    year_index = max(np.unique(year_indices), key=year_indices.count) if year_indices else 2

    try:
        if year_index == 0:
            for date in dates:
                year, month, day = date.split('/')
                if 0 < int(month) <= 12 and 0 < int(day) <= 31:
                    date_format = '%Y/%m/%d'
                    break

        elif year_index == 2:
            for date in dates:
                day, month, year = date.split('/')
                # print('day: {}, month: {}, year:{}'.format(day, month, year))
                if int(month) > 12 >= int(day) >= 1:
                    date_format = '%m/%d/%Y' if len(year) == 4 else '%m/%d/%y'
                    break

    except Exception as error:
        logging.error(error)

    return date_format


def extract_date_with_monthname(text_segment):
    formatted_date = ''

    try:
        extracted_month = find_month(text_segment)
        if extracted_month:
            extracted_numbers = re.findall(r'\d+', text_segment)
            day = extracted_numbers[0]
            month = extracted_month[0]
            year = extracted_numbers[1] if 2 <= len(extracted_numbers) <= 4 \
                else datetime.now().year

            if len(day) == 4:
                day, year = year, day
            formatted_date = f'{day}/{month}/{year}'
    except Exception as error:
        logging.error('Extraction failed for %s: %s' % (text_segment, str(error)))

    return formatted_date


def find_month(text_segment):
    month_segment = ''.join(re.findall(r'[a-zA-Z]', text_segment)).lower()
    month_int = [key for key, months in months_name2int.items()
                 if month_segment and any(month_segment in month for month in months)]

    return month_int


if __name__ == '__main__':
    # text_segments = ['24.MAY2022']
    text_segments = [
        '05-Apr-22', '06-23-2023', '08-08-2021', '08-Aug-22', '1-10 2022', '10-06-2021', '10/23/2022',
        '10042021', '11-Mar-21', '11. November 2022', '1205', '121121', '13 06', '14.07', '15/09',
        '180621', '181216', '19082022', '2.11.21', '2022-10-05', '2022.09.29', '21.08.22', '22-Nov-22',
        '22.09.15', '22.NOV.2022', '24.MAY2022', '24.jan2022', '24/2-2023.', '25-09-2022',
        '25-Aug-22', '27-Sep-22', '2nd may', '31/05—2020', 'Apr 14, 2022', 'Date 30TH JUNE 2022',
        'Dato 230206', 'Dato: man 13 mar. 2023 - 15.00', 'March3,2021', "25th dec '18", '1Sep 2022']

    _cls = 'invoiceDate'
    for segment in text_segments:
        print('Input segment', segment)
        print(extract_date_with_monthname(segment))
