import argparse
import logging

import docx

import scraper

from summa.summarizer import summarize

parser = argparse.ArgumentParser()
parser.add_argument('outline', help='Outline Document')
parser.add_argument('-u', '--username', help="Username", required=True)
parser.add_argument('-p', '--password', help="Password", required=True)
parser.add_argument('-f', '--full', help="Do not summarize the section body", action='store_true')
parser.add_argument('-d', '--debug', help="Display debug logs", action='store_true')
args = parser.parse_args()

outline_doc = docx.Document(args.outline)
scraper = scraper.Scraper(args.username, args.password)
if args.debug:
    logging.basicConfig(level=logging.DEBUG)

section_number = 1
output_doc = docx.Document()

# Outline content begins at paragraph 13
for para in outline_doc.paragraphs[13:-1]:
    section = para.text.strip()
    if para.runs[0].bold:
        logging.debug("Read heading", section)
        output_doc.add_heading(section, 2)
    else:
        logging.debug("Read section", section)
        content = scraper.section_body(section)
        if not args.full:
            content = summarize(content, words=100, split=True)
        output_doc.add_paragraph(str(section_number) + ". " + section + ": " + ' '.join(content))
        section_number += 1

scraper.close()
output_doc.save(args.outline[:-5] + "_Complete.docx")
