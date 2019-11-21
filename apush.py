import argparse
import docx

import scraper

parser = argparse.ArgumentParser()
parser.add_argument('outline', help='Outline Document')
parser.add_argument('-u', '--username', help='Username', required=True)
parser.add_argument('-p', '--password', help='Password', required=True)
parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true')  # TODO: Implement proper logging
args = parser.parse_args()

scraper = scraper.Scraper(args.username, args.password)
outline_doc = docx.Document(args.outline)

sectionNumber = 1
# output_doc = docx.Document()
# Outline content begins at index 13
for para in outline_doc.paragraphs[13:-1]:
    section = para.text.strip()
    if para.runs[0].bold:
        print("**", para.text, "**")
    else:
        summary = scraper.summary(section)
        print(sectionNumber, para.text, "-", summary)
        sectionNumber += 1

scraper.close()
