
import re, htmlentitydefs

#
# Remove entities (html or xml) form the input
# based on http://effbot.org/zone/re-sub.htm#unescape-html
#
def unescapeEntities(xmlText):
    def replaceEntities(matchObject):
        text = matchObject.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub(r'&#?\w+;', replaceEntities, xmlText)
