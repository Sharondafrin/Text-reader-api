import re
import logging
from dateutil.parser import parse
from scripts.date_utils import extract_date_with_monthname, get_date_format, str2datetime, datetime2str

expression_mapper = {
    'date': {
        'yy-mm-dd': r'([\d]{4}[ ,\/]{1,2}([\d]{1,2}|[A-Za-z]{3,9})[ \/]{1,2}[\d]{1,2})',
        'dd-mm-yy': r'([\d]{1,2}([ .\/]{1,2}[\d]{1,2}|[ .\/]{0,2}[A-Za-z]{3,9})[ .,\/]{1,2}[\d]{2,4})',
        'mm-dd-yy': r'(([\d]{1,2}[ .\/]{1,2}|[A-Za-z]{3,9}[ .\/]{0,2})[\d]{1,2}[ .,\/]{1,2}[\d]{4})',
    }}


def amount_extraction(text_segment):

    try:

        text_segment = re.sub(r'[$€£¥₣₹|]+', ' ', text_segment).strip()
        text_segment = re.sub(r' +', ' ', text_segment)
        text_segment = re.sub(r'[\[\]|]+', '', text_segment)

        text_segment = re.sub(r'—_', r'-', str(text_segment))
        text_segment = re.sub(r'[\'?]', '', text_segment)

        # consider the condition while updating the function
        # if text_segment.endswith(',-') or text_segment.endswith(',') or text_segment.endswith('-')

        if text_segment.endswith(',-'):
            text_segment = re.sub(r'(,|-|,-)$', '.00', text_segment)
        elif text_segment.endswith('-'):
            text_segment = text_segment[:-1]
        elif text_segment.endswith(',') or text_segment.endswith('.'):
            return None

        result = re.sub(r'[ ,]', '.', text_segment)
        # result = re.sub(r'-', '', result)

        specials = [item for item in result if not item.isnumeric() and item != '-']

        if specials:
            dot = specials[-1]

            if specials.count(dot) >= 2:

                result = [re.sub(r'\.', '', result[i]) if i < len(result) - 3 else result[i] for i, x in
                          enumerate(result)]
                result = ''.join(result)

            else:

                dot_idx = [i - len(result) for i, x in enumerate(result) if x == '.'][0]
                result = [result[dot_idx].replace('.', '')
                          if (i - len(result) == dot_idx) and (dot_idx < -3) else result[i] for i, x in
                          enumerate(result)]
                result = ''.join(result)

        return float(result)

    except Exception as error:
        logging.error(f'Failed Amount to Float for text segment {text_segment}: {error}')

    return None


def date_extraction(text_segment):

    # date = ''
    try:
        # Text cleaning
        text_segment = re.sub(r'(\d)(st|nd|rd|th|ST|ND|RD|TH)', r'\1', text_segment.lower())
        text_segment = re.sub(r'[ .,\-":|â\'—]+', r'/', text_segment)
        date_expressions = expression_mapper['date']
        extracted_dates = []
        for case, expression in date_expressions.items():
            if not any(extracted_dates):
                exp = re.compile(expression)

                detected_dates = [_date for _date, _ in exp.findall(text_segment)]
                # print('detected_dates', detected_dates)

                if any(detected_dates):
                    for _date in detected_dates:
                        if any(re.findall(r'[a-zA-Z]+', _date)):
                            _date = extract_date_with_monthname(_date)
                        extracted_dates.append(_date)
                    break

        # print('extracted_dates', extracted_dates)

        date = extracted_dates[0] if extracted_dates else ''

        if date:
            date_format = get_date_format([date])
            date_dt = str2datetime(date, date_format)
            date = str(datetime2str(date_dt))

    except Exception as error:
        parsed_date = parse(text_segment)
        date = parsed_date.strftime("%Y-%m-%d")
        logging.error('An error occurred during: %s' % error)

    return date


def validate_transcript(text_segment):

    try:
        text_segment = re.sub(r'[.,:;\s-]+', '', text_segment)

    except Exception as error:
        text_segment = text_segment
        logging.error('An error occurred during: %s' % error)

    return text_segment


if __name__ == '__main__':

    # text_segments = ['24.MAY2022']
    # text_segments = ['06-23-2023', '08-08-2021', '1-10 2022', '10-06-2021', '10/23/2022', '2.11.21',
    # '2022-10-05', '2022.09.29',
    #                  '21.08.22', '22.09.15', '24/2-2023', '25-09-2022', '30TH JUNE 2022']

    text_segments = [
        '05-Apr-22', '06-23-2023', '08-08-2021', '08-Aug-22', '1-10 2022', '10-06-2021', '10/23/2022',
        '10042021', '11-Mar-21', '11. November 2022', '1205', '121121', '13 06', '14.07', '15/09',
        '180621', '181216', '19082022', '2.11.21', '2022-10-05', '2022.09.29', '21.08.22', '22-Nov-22',
        '25-Aug-22', '27-Sep-22', '2nd may', '31/05—2020', 'Apr 14, 2022', 'Date 30TH JUNE 2022',
        'Dato 230206', 'Dato: man 13 mar. 2023 - 15.00', '16. oktober 2023',
        'March3,2021',  "25th dec '18", '1Sep 2022'
    ]

    _cls = 'invoiceDate'
    for segment in text_segments:
        print('Input segment', segment)
        print(date_extraction(segment))
