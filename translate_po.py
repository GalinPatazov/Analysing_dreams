import asyncio
from googletrans import Translator
import polib

po_file_path = 'locale/bg/LC_MESSAGES/django.po'

async def translate_entries(po):
    translator = Translator()
    for entry in po:
        if entry.msgid and not entry.msgstr:  # Only translate if empty
            result = await translator.translate(entry.msgid, src='en', dest='bg')
            entry.msgstr = result.text

def main():
    po = polib.pofile(po_file_path)
    asyncio.run(translate_entries(po))
    po.save()
    print("Translations auto-generated!")

if __name__ == "__main__":
    main()