# Copyright (C) 2020 ditekshen
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

from lib.cuckoo.common.abstracts import Signature


class WarzoneRATRegkeys(Signature):
    name = "warzonerat_regkeys"
    description = "Creates WarzoneRAT registry keys"
    severity = 3
    categories = ["rat"]
    families = ["WarzoneRAT", "AveMaria"]
    authors = ["ditekshen"]
    minimum = "1.3"
    ttps = ["T1112", "T1219"]  # MITRE v6,7,8
    mbcs = ["B0022", "E1112"]
    mbcs += ["OC0008", "C0036"]  # micro-behaviour

    def run(self):
        indicators = (
            r"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\[A-Z0-9]{10}\\[a-z]{4}$",
            r"HKEY_CURRENT_USER\\Software\\_rptls\\Install$",
        )

        for indicator in indicators:
            match = self.check_key(pattern=indicator, regex=True)
            if match:
                self.data.append({"regkey": match})
                return True

        return False


class WarzoneRATFiles(Signature):
    name = "warzonerat_files"
    description = "Accesses or creates Warzone RAT directories and/or files"
    severity = 3
    categories = ["rat"]
    families = ["WarzoneRAT", "AveMaria"]
    authors = ["ditekshen"]
    minimum = "1.3"
    ttps = ["T1219"]  # MITRE v6,7,8
    mbcs = ["B0022"]
    mbcs += ["OC0001", "C0016"]  # micro-behaviour

    def run(self):
        indicators = [
            r".*\\Program Files\\Microsoft DN1.*",
            r".*\\AppData\\Local\\Microsoft Vision\\",
        ]

        for indicator in indicators:
            match = self.check_file(pattern=indicator, regex=True)
            if match:
                self.data.append({"file": match})
                return True

        return False
