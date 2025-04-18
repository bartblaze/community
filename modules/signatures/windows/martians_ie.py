# Copyright (C) 2015 Will Metcalf (william.metcalf@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    import re2 as re
except ImportError:
    import re

from lib.cuckoo.common.abstracts import Signature

ie_paths_re = re.compile(r"^c:\\program files(?:\s\(x86\))?\\internet explorer\\iexplore.exe$", re.I)
# run through re.escape()
white_list_re = [
    r"^C\\:\\Program Files(?:\s\\(x86\\))?\\Adobe\\Reader\\ \\d+\\.\\d+\\Reader\\AcroRd32\\.exe$",
    r"^C\\:\\Program Files(?:\s\\(x86\\))?\\Java\\jre\\d+\\bin\\j(?:avaw?|p2launcher)\\.exe$",
    r"^C\\:\\Program Files(?:\s\\(x86\\))?\\Microsoft SilverLight\\(?:\\d+\\.)+\\d\\agcp.exe$",
    r"^C\\:\\Windows\\System32\\ntvdm\\.exe$",
    r"^C\\:\\Windows\\system32\\rundll32\\.exe$",
    r"^C\\:\\Windows\\syswow64\\rundll32\\.exe$",
    r"^C\\:\\Windows\\system32\\drwtsn32\\.exe$",
    r"^C\\:\\Windows\\syswow64\\drwtsn32\\.exe$",
    r"^C\\:\\Windows\\system32\\dwwin\\.exe$",
    r"^C\\:\\Windows\\system32\\WerFault\\.exe$",
    r"^C\\:\\Windows\\syswow64\\WerFault\\.exe$",
]
# means we can be evaded but also means we can have relatively tight paths between 32-bit and 64-bit
white_list_re_compiled = []
for entry in white_list_re:
    white_list_re_compiled.append(re.compile(entry, re.I))
white_list_re_compiled.append(ie_paths_re)


class MartiansIE(Signature):
    name = "ie_martian_children"
    description = "Martian Subprocess Started By IE"
    severity = 3
    categories = ["martians"]
    authors = ["Will Metcalf"]
    minimum = "0.5"
    ttps = ["T1059"]  # MITRE v6,7,8
    mbcs = ["OB0009", "E1059"]

    def go_deeper(self, pdict, result=None):
        if result is None:
            result = []
        result.append(pdict["module_path"].lower())
        for e in pdict["children"]:
            self.go_deeper(e, result)
        return result

    def find_martians(self, ptree, pwlist):
        result = []
        if ptree["children"]:
            children = self.go_deeper(ptree)
            for child in children:
                match_found = False
                for entry in pwlist:
                    if entry.match(child):
                        match_found = True
                if not match_found:
                    result.append(child)
        return result

    def run(self):
        if self.results.get("target", {}).get("category", "") == "file":
            return False

        # Sometimes if we get a service loaded we get out of order processes in tree need iterate over IE processes get the path of the initial monitored executable
        self.initialpath = None
        processes = self.results.get("behavior", {}).get("processtree", [])
        for p in processes or []:
            initialpath = p["module_path"].lower()
            if initialpath and ie_paths_re.match(initialpath) and "children" in p:
                self.martians = self.find_martians(p, white_list_re_compiled)
                if len(self.martians) > 0:
                    for martian in self.martians:
                        self.data.append({"ie_martian": martian})
                    return True
        return False
