# Copyright (C) 2016 Brad Spengler
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


class FortinetDetectFiles(Signature):
    name = "antisandbox_fortinet_files"
    description = "Attempts to detect Fortinet Sandbox through the presence of a file"
    severity = 3
    categories = ["anti-sandbox"]
    authors = ["Brad Spengler"]
    minimum = "0.5"
    ttps = ["T1057", "T1083", "T1497"]  # MITRE v6,7,8
    ttps += ["U1333"]  # Unprotect
    mbcs = ["OB0001", "B0007", "B0007.002", "OB0007", "E1083"]

    def run(self):
        indicators = [
            r"^C:\\tracer\\mdare32_0\.sys$",
            r"^C:\\tracer\\fortitracer\.exe$",
            r"^C:\\manual\\sunbox\.exe$",
        ]

        for indicator in indicators:
            if self.check_file(pattern=indicator, regex=True):
                return True

        return False
