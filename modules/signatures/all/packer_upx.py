# Copyright (C) 2012,2015 Michael Boman (@mboman), Optiv, Inc. (brad.spengler@optiv.com)
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


class UPXCompressed(Signature):
    name = "packer_upx"
    description = "The executable is compressed using UPX"
    severity = 2
    categories = ["packer"]
    authors = ["Michael Boman", "nex", "Optiv"]
    minimum = "1.3"
    ttps = ["T1045"]  # MITRE v6
    ttps += ["T1027"]  # MITRE v6,7,8
    ttps += ["T1027.002"]  # MITRE v7,8
    mbcs = ["OB0001", "OB0002", "OB0006", "F0001", "F0001.008"]

    def run(self):
        ret = False

        target = self.results.get("target", {})
        if target.get("category") in ("file", "static") and target.get("file"):
            pe = self.results["target"]["file"].get("pe", [])
            if pe:
                for section in pe["sections"]:
                    if section["name"].lower().startswith(".upx"):
                        self.data.append({"section": section})
                        ret = True

        return ret
