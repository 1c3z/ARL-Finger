import json

from enum import Enum

import yaml


class Method(Enum):
    KEYWORD = "keyword"
    FAVICON_HASH = "faviconhash"


class Location(Enum):
    BODY = "body"
    TITLE = "title"
    HEADER = "header"


def validate_keyword(keyword):
    if not isinstance(keyword, list):
        raise ValueError("keyword must be a list")
    if len(keyword) == 0:
        raise ValueError("empty keyword")


# ARL 支持的字段， body, title, header，icon_hash


class FingerPrint:
    def __init__(self, cms, method, location, keyword):
        validate_keyword(keyword)

        self.cms = cms
        self.method = Method(method)
        self.location = Location(location)
        self.keyword = keyword

    def __str__(self):
        return self.cms

    def transfer_rule(self) -> str:
        items = []
        if self.method == Method.KEYWORD:
            for keyword in self.keyword:
                msg = f'{self.location.value}="{self.quote_keyword(keyword)}"'
                items.append(msg)

            return " && ".join(items)

        if self.method == Method.FAVICON_HASH:
            return f'icon_hash="{self.keyword[0]}"'

    @staticmethod
    def quote_keyword(keyword):
        keyword = keyword.replace('\\', r'\\')
        return keyword.replace('"', r'\"')

    def transfer(self) -> dict:
        item = {
            "name": self.cms,
            "rule": self.transfer_rule()
        }
        return item


def load_fingers() -> [FingerPrint]:
    items = []
    with open("ehole-finger.json", encoding="utf-8") as f:
        for item in json.load(f)["fingerprint"]:
            items.append(FingerPrint(**item))
    return items


def main():
    transferred_fingers = []
    loaded_fingers = load_fingers()
    print(f"Loaded fingers: {len(loaded_fingers)}")

    unique_rules = set()
    for finger in loaded_fingers:
        rule = finger.transfer()
        if rule["rule"] in unique_rules:
            print("Repeated rule", rule)
            continue

        unique_rules.add(rule["rule"])

        transferred_fingers.append(rule)

    print(f"Transferred fingers: {len(transferred_fingers)}")

    finger_data = yaml.dump(transferred_fingers, default_flow_style=False, sort_keys=False, allow_unicode=True)

    with open("finger.yml", "w", encoding="utf-8") as file:
        file.write(finger_data)

    print("Done")


if __name__ == "__main__":
    main()
