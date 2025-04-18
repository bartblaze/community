# Copyright (C) 2018 Kevin Ross
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


class LsassCredentialDumping(Signature):
    name = "lsass_credential_dumping"
    description = "Requests access to read memory contents of lsass.exe potentially indicative of credential dumping"
    severity = 3
    categories = ["persistence", "lateral", "credential_dumping"]
    authors = ["Kevin Ross"]
    minimum = "1.3"
    evented = True
    ttps = ["T1003"]  # MITRE v6,7,8
    ttps += ["T1003.001"]  # MITRE v7,8
    mbcs = ["OB0005"]
    references = [
        "cyberwardog.blogspot.co.uk/2017/03/chronicles-of-threat-hunter-hunting-for_22.html",
        "cyberwardog.blogspot.co.uk/2017/04/chronicles-of-threat-hunter-hunting-for.html",
    ]

    filter_apinames = set(["NtOpenProcess", "Process32NextW", "ReadProcessMemory"])

    def __init__(self, *args, **kwargs):
        Signature.__init__(self, *args, **kwargs)
        self.lsasspid = []
        self.lsasshandle = []
        self.readaccessprocs = []
        self.creddumpprocs = []
        self.ret = False

    def on_call(self, call, process):
        if call["api"] == "Process32NextW":
            if self.get_argument(call, "ProcessName") == "lsass.exe":
                self.lsasspid.append(self.get_argument(call, "ProcessId"))

        if call["api"] == "NtOpenProcess":
            if self.get_argument(call, "ProcessIdentifier") in self.lsasspid and self.get_argument(call, "DesiredAccess") in [
                "0x00001010",
                "0x00001038",
            ]:
                pname = process["process_name"].lower()
                if pname not in self.readaccessprocs:
                    self.data.append(
                        {"lsass read access": "The process %s requested read access to the lsass.exe process" % (pname)}
                    )
                    self.lsasshandle.append(self.get_argument(call, "ProcessHandle"))
                    self.readaccessprocs.append(pname)
                    if self.pid:
                        self.mark_call()
                    self.ret = True

        if call["api"] == "ReadProcessMemory":
            if self.get_argument(call, "ProcessHandle") in self.lsasshandle:
                pname = process["process_name"].lower()
                if pname not in self.creddumpprocs:
                    self.description = "Locates and dumps memory from the lsass.exe process indicative of credential dumping"
                    self.data.append(
                        {"lsass credential dumping": "The process %s is reading memory from the lsass.exe process" % (pname)}
                    )
                    self.creddumpprocs.append(pname)
                    if self.pid:
                        self.mark_call()
                    self.ret = True

    def on_complete(self):
        return self.ret


class RegistryCredentialDumping(Signature):
    name = "registry_credential_dumping"
    description = "Dumps credentials from the registry using the Windows reg utility"
    severity = 3
    categories = ["persistence", "lateral", "credential_dumping"]
    authors = ["Kevin Ross"]
    minimum = "1.3"
    evented = True
    ttps = ["T1003"]  # MITRE v6,7,8
    ttps += ["T1003.002"]  # MITRE v7,8
    mbcs = ["OB0005"]

    def run(self):
        ret = False
        cmdlines = self.results.get("behavior", {}).get("summary", {}).get("executed_commands", [])
        for cmdline in cmdlines:
            lower = cmdline.lower()
            if "reg" in lower and "save" in lower and ("hklm\\system" in lower or "hklm\\sam" in lower):
                ret = True
                self.data.append({"command": cmdline})

        return ret


class RegistryCredentialStoreAccess(Signature):
    name = "registry_credential_store_access"
    description = "Accessed credential storage registry keys"
    severity = 3
    categories = ["persistence", "lateral", "credential_dumping"]
    authors = ["Kevin Ross"]
    minimum = "1.3"
    evented = True
    ttps = ["T1003"]  # MITRE v6,7,8
    ttps += ["T1003.002"]  # MITRE v7,8
    mbcs = ["OB0005"]

    def run(self):
        ret = False
        reg_indicators = (
            r"HKEY_LOCAL_MACHINE\\SAM$",
            r"HKEY_LOCAL_MACHINE\\SYSTEM$",
        )

        for indicator in reg_indicators:
            match = self.check_key(pattern=indicator, regex=True)
            if match:
                self.data.append({"regkey": match})
                ret = True
        # Tweak
        if "PDF" in self.results["target"]["file"].get("type", ""):
            self.severity = 1
        return ret


class RegistryLSASecretsAccess(Signature):
    name = "registry_lsa_secrets_access"
    description = "Accesses LSA Secrets that are stored in registry"
    severity = 3
    categories = ["credential_dumping"]
    authors = ["bartblaze"]
    minimum = "1.3"
    evented = True
    ttps = ["T1003"]  # MITRE v6,7,8
    ttps += ["T1003.004"]  # MITRE v7,8
    mbcs = ["OB0005"]

    def run(self):
        indicators = (r"HKEY_LOCAL_MACHINE\\SECURITY\\Policy\\Secrets$",)

        for indicator in indicators:
            match = self.check_key(pattern=indicator, regex=True)
            if match:
                self.data.append({"regkey": match})
                return True

        return False


class FileCredentialStoreAccess(Signature):
    name = "file_credential_store_access"
    description = "Accessed credential storage files"
    severity = 3
    categories = ["credential_access", "credential_dumping"]
    authors = ["bartblaze"]
    minimum = "1.3"
    evented = True
    ttps = ["T1003"]  # MITRE v6,7,8
    ttps += ["T1003.002"]  # MITRE v7,8
    mbcs = ["OB0005"]

    def run(self):
        indicators = (
            r".*\\Windows\\repair\\sam",
            r".*\\Windows\\System32\\config\\RegBack\\SAM",
            r".*\\Windows\\system32\\config\\SAM",
        )

        for indicator in indicators:
            match = self.check_file(pattern=indicator, regex=True)
            if match:
                self.data.append({"file": match})
                return True

        return False


class FileCredentialStoreWrite(Signature):
    name = "file_credential_store_write"
    description = "Writes to or from credential storage files"
    severity = 3
    categories = ["credential_access", "credential_dumping"]
    authors = ["bartblaze"]
    minimum = "1.3"
    evented = True
    ttps = ["T1003"]  # MITRE v6,7,8
    ttps += ["T1003.002"]  # MITRE v7,8
    mbcs = ["OB0005"]

    def run(self):
        indicators = (
            r".*\\Windows\\repair\\sam",
            r".*\\Windows\\System32\\config\\RegBack\\SAM",
            r".*\\Windows\\system32\\config\\SAM",
        )

        for indicator in indicators:
            match = self.check_write_file(pattern=indicator, regex=True)
            if match:
                self.data.append({"file": match})
                return True

        return False


class DumpLSAViaWindowsErrorReporting(Signature):
    name = "dump_lsa_via_windows_error_reporting"
    description = "Attempts to create LSASS crash dump via Windows Error Reporting process"
    severity = 3
    categories = ["credential_access", "credential_dumping"]
    authors = ["@para0x0dise"]
    minimum = "0.5"
    evented = True
    ttps = ["T1003"]
    references = [
        "https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/windows/credential_access_lsa_dump_via_windows_error_reporting.toml"
    ]

    filter_apinames = set(["NtCreateFile"])

    def on_call(self, call, process):
        # Checking parent process for false positives.
        if process["process_name"].lower() in ("WerFaultSecure.exe", "WerFault.exe") and call["api"] == "NtCreateFile":
            filename = self.get_argument(call, "FileName")
            if filename.endswith(".dmp") and "lsass_" in filename:
                return True


class KerberosCredentialAccessViaRubeus(Signature):
    name = "kerberos_credential_access_via_rubeus"
    description = "Attempts to manipulate/abuse Kerberos Ticketing System via Rubeus toolset"
    severity = 3
    categories = ["credential_access", "credential_dumping"]
    authors = ["@para0x0dise"]
    minimum = "0.5"
    evented = True
    ttps = ["T1003"]
    references = [
        "https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/windows/credential_access_potential_credential_access_via_rubeus.toml"
    ]

    def run(self):
        for cmdline in self.results.get("behavior", {}).get("summary", {}).get("executed_commands", []):
            lower = cmdline.lower()
            if "rebeus" in lower and any(
                arg in lower
                for arg in (
                    "asreproast",
                    "dump /service:krbtgt",
                    "dump /luid",
                    "kerberoast",
                    "createnetonly /program",
                    "ptt /ticket",
                    "/impersonateuser",
                    "renew /ticket",
                    "asktgt /user",
                    "asktgs /ticket",
                    "harvest /interval",
                    "s4u /user",
                    "s4u /ticket",
                    "hash /password",
                    "tgtdeleg",
                    "tgtdeleg /target",
                    "golden /des",
                    "golden /rc4",
                    "golden /aes128",
                    "golden /aes256",
                    "changpw /ticket",
                )
            ):
                return True
        return False
