from cape_parsers.CAPE.core.RedLine import extract_config
from maco.extractor import Extractor
from maco.model import ExtractorModel as MACOModel

from modules.parsers.utils import get_YARA_rule


def convert_to_MACO(raw_config: dict):
    if not (raw_config and isinstance(raw_config, dict)):
        return None

    parsed_result = MACOModel(family="RedLine", other=raw_config)

    if "C2" in raw_config:
        host, port = raw_config["C2"].split(":")
        parsed_result.http.append(MACOModel.Http(hostname=host, port=port, usage="c2"))

    return parsed_result


class RedLine(Extractor):
    author = "kevoreilly"
    family = "RedLine"
    last_modified = "2024-10-26"
    sharing = "TLP:CLEAR"
    yara_rule = get_YARA_rule(family)

    def run(self, stream, matches):
        return convert_to_MACO(extract_config(stream.read()))
