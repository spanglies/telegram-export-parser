#!/usr/bin/env python3
"""Parses Telegram """
import argparse
from datetime import datetime
import json
from bs4 import BeautifulSoup
import glob


class TelegramMessage:
    """Class wrapping a telegram message"""
    def __init__(self, date: datetime, sender: str, message: str):
        self.date = date
        self.sender = sender
        self.message = message

    def to_text_string(self):
        """ returns Message as a full Text String"""
        return f"[{self.date.isoformat()}] {self.sender}: {self.message}"

    def to_object(self):
        """ return a dict"""
        return {"date": self.date.isoformat(),
                "sender": self.sender,
                "message": self.message}

    def to_plain_string(self):
        """ returns just the message """
        return f"{self.sender}: {self.message}"

    def to_html(self):
        """ return in html format"""
        return f"<b>{self.sender}</b>: {self.message}"

    def no_names_message(self):
        return f"{self.message}"


def main():
    """ main function of script """
    parser = argparse.ArgumentParser(description="python script to parse telegram html chat"
                                                 " logs exported by the desktop client")
    parser.add_argument("-i", "--input", nargs=1, required=True)
    parser.add_argument("-o", "--output", nargs=1, default="./output", type=argparse.FileType('a'))
    parser.add_argument("-f", "--format", nargs=1, choices=["text", "json", "plain", "html", "message"])
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("-r", "--replace", nargs="*")

    parsed = parser.parse_args()
    print(parsed)

    if parsed.replace is not None:
        if len(parsed.replace)%2 != 0:
            print("If you are using the replace tool, please use an even number")
            return

    objects = []
    for filename in glob.glob(parsed.input[0]):
        with open(filename, "r") as file:
            soup = BeautifulSoup(file, "html.parser")
            alldefaultmesssages = soup.select(".message.default")

            last_name = ""
            for mess in alldefaultmesssages:
                textselection = mess.select_one(".text")
                dateselection = mess.select_one(".date")
                date = datetime.strptime(dateselection["title"], "%d.%m.%Y %H:%M:%S")

                if "joined" in mess["class"]:
                    name = last_name
                else:
                    name = mess.select_one(".from_name").text.strip()
                    last_name = name

                if parsed.replace is not None:
                    if name in parsed.replace[::2]:
                        name = parsed.replace[parsed.replace.index(name)+1]
                        last_name = name

                if textselection is not None:
                    obj = TelegramMessage(date, name, textselection.text.strip())
                    objects.append(obj)
                    if parsed.verbose is True:
                        print(obj.to_text_string())
    if isinstance(parsed.output, list):
        outfile = parsed.output[0]
    else:
        outfile = parsed.output
    objects.sort(key=lambda x: x.date)

    if parsed.format is None or parsed.format[0] == "json":
        json.dump([x.to_object() for x in objects], outfile)
    elif parsed.format[0] == "text":
        for exs in objects:
            outfile.write(exs.to_text_string()+"\n")
    elif parsed.format[0] == "message":
        for exs in objects:
            outfile.write(exs.no_names_message()+"\n")
    elif parsed.format[0] == "plain":
        for exs in objects:
            outfile.write(exs.to_plain_string()+"\n")
    elif parsed.format[0] == "html":
        for exs in objects:
            outfile.write(exs.to_html()+"\n")


if __name__ == "__main__":
    main()
