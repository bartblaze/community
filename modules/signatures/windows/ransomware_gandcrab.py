# Copyright (C) 2019 ditekshen
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


class GandCrabMutexes(Signature):
    name = "gandcrab_mutexes"
    description = "Creates known GandCrab ransomware mutexes"
    severity = 3
    categories = ["ransomware"]
    families = ["GandCrab"]
    authors = ["ditekshen"]
    minimum = "0.5"
    ttps = ["T1486"]  # MITRE v6,7,8
    mbcs = ["OC0003", "C0042"]  # micro-behaviour

    def run(self):
        indicators = [
            "AversSucksForever$",
            r"\\Sessions\\1\\BaseNamedObjects\\AversSucksForever$",
        ]

        for indicator in indicators:
            match_mutex = self.check_mutex(pattern=indicator, regex=True)
            if match_mutex:
                self.data.append({"mutex": match_mutex})
                return True

        return False
