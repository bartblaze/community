# Copyright (C) 2014,2015 Robby Zeitfuchs (@robbyFux), Optiv, Inc. (brad.spengler@optiv.com)
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


class PackerEntropy(Signature):
    name = "packer_entropy"
    description = "The binary likely contains encrypted or compressed data"
    severity = 2
    categories = ["packer"]
    authors = ["Robby Zeitfuchs", "nex", "Optiv"]
    minimum = "1.3"
    ttps = ["T1045"]  # MITRE v6
    ttps += ["T1027"]  # MITRE v6,7,8
    ttps += ["T1027.002"]  # MITRE v7,8
    mbcs = ["OB0001", "OB0002", "OB0006", "F0001"]
    references = [
        "http://www.forensickb.com/2013/03/file-entropy-explained.html",
        "http://virii.es/U/Using%20Entropy%20Analysis%20to%20Find%20Encrypted%20and%20Packed%20Malware.pdf",
    ]

    def run(self):
        ret = False

        target = self.results.get("target", {})
        if target.get("category") in ("file", "static") and target.get("file"):
            pe = self.results["target"]["file"].get("pe", [])
            if pe:
                total_compressed = 0
                total_pe_data = 0

                for section in pe["sections"]:
                    total_pe_data += int(section["size_of_data"], 16)

                    if float(section["entropy"]) > 6.8:
                        self.data.append({"section": section})
                        total_compressed += int(section["size_of_data"], 16)

                if total_pe_data and ((1.0 * total_compressed) / total_pe_data) > 0.2:
                    ret = True

        return ret
