from PyPDF4 import PdfFileReader
import requests, re

def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
    
    try:
        stamp1 = information.getText("/CreationDate").split('-')
        stamp2 = information.getText("/ModDate").split('-')

        readable1 = extract_date(stamp1)
        readable2 = extract_date(stamp2)
    except:
        readable1 = None
        readable2 = None

    txt = f"""
    Information about: {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Creation Date: {readable1}
    Modification Date: {readable2}
    Number of pages: {number_of_pages}
    """

    print(txt)
    return information

def extract_date(stamp):
    switch = ''
    try:
        front, back = stamp[0], stamp[1]; factor = int(re.findall("[1-9]", back)[0])
    except: 
        front = stamp[0]; factor = 0

    seconds = front[-2::]
    minutes = front[-4:-2]
    hours = int(front[-6:-4])-5+factor

    if hours >= 23: hours=(hours%12); switch = "AM"
    elif hours > 12: hours=(hours%12); switch = "PM"
    else: switch = "AM"

    raw_date = ''.join(re.findall('[0-9]', front[:-6]))

    time = f"{hours}:{minutes}:{seconds}"
    date = f"{raw_date[4:6]}/{raw_date[6:8]}/{raw_date[0:4]}"

    return f"{date} - {time} {switch}"

def pdf_scrape():
    url = "https://ioactive.com/pdfs/Hacking-Robots-Before-Skynet.pdf"
    expected_name = url.split('/')[-1]
    req = requests.get(url)
    if req.status_code and req.url == url:
        with open(expected_name, 'wb+')as data:
            data.write(req.content)
        extract_information(expected_name)
    else:
        print('bad status')

if __name__ == '__main__':
    pdf_scrape()
    # path = 'How-to-Dispose-of-Unused-Medicines-(PDF).pdf'
    # extract_information(path)
