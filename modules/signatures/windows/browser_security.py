# Copyright (C) 2015 Kevin Ross, Optiv, Inc. (brad.spengler@optiv.com)
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


class BrowserSecurity(Signature):
    name = "browser_security"
    description = "Attempts to modify browser security settings"
    severity = 3
    categories = ["browser", "clickfraud", "banker"]
    authors = ["Kevin Ross", "Optiv"]
    minimum = "1.2"
    ttps = ["T1089", "T1112"]  # MITRE v6
    ttps += ["T1562", "T1562.001"]  # MITRE v7,8
    mbcs = ["OB0006", "E1112", "F0004"]
    mbcs += ["OC0008", "C0036", "C0036.001"]  # micro-behaviour

    def run(self):
        if self.results["info"]["package"] in ["pdf"]:
            return False

        safelist = ["zoom.exe"]

        reg_indicators = (
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Internet\\ Explorer\\Privacy\\EnableInPrivateMode$",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Internet\\ Explorer\\PhishingFilter\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Windows\\CurrentVersion\\Internet\\ Settings\\Zones\\[0-4]\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Windows\\CurrentVersion\\Internet\\ Settings\\ZoneMap\\Domains\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Windows\\CurrentVersion\\Internet\\ Settings\\ZoneMap\\EscDomains\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Windows\\CurrentVersion\\Internet\\ Settings\\ZoneMap\\EscRanges\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Windows\\CurrentVersion\\Internet\\ Settings\\ZoneMap\\IEHarden$",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Windows\\CurrentVersion\\Internet\\ Settings\\CertificateRevocation$",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Internet\\ Explorer\\Main\\NoUpdateCheck$",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Internet\\ Explorer\\Security\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Internet\\ Explorer\\Main\\FeatureControl\\.*",
        )

        for indicator in reg_indicators:
            regkeys = self.check_write_key(pattern=indicator, regex=True, all=True)
            if regkeys:
                for regkey in regkeys:
                    if not any(item in regkey.lower() for item in safelist):
                        self.data.append({"regkey": regkey})

        if len(self.data) > 0:
            return True
        else:
            return False
