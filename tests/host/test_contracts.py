"""Pack contract tests adapted for Lab paths (SV0-01.02). Unchanged assertions."""
from pathlib import Path
import unittest, json, csv, importlib.util, yaml, re
from jsonschema import Draft202012Validator, FormatChecker

LAB = Path(__file__).resolve().parents[2]
PACK = LAB / "references/agent-pack/Svaraa_V0_Engineer_Agent_Pack"
CONTRACTS = LAB / "contracts"

spec = importlib.util.spec_from_file_location(
    "frame", CONTRACTS / "reference_frame.py"
)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


class Tests(unittest.TestCase):
    def setUp(self):
        self.e = json.loads((CONTRACTS / "example_event.json").read_text())
        self.v = Draft202012Validator(
            json.loads((CONTRACTS / "device_event.schema.json").read_text()),
            format_checker=FormatChecker(),
        )

    def test_example(self):
        self.v.validate(self.e)

    def test_live_drill_mismatch(self):
        self.e["mode"] = "live"
        self.assertTrue(list(self.v.iter_errors(self.e)))

    def test_latitude(self):
        self.e["payload"]["location"]["latitude"] = 100
        self.assertTrue(list(self.v.iter_errors(self.e)))

    def test_unknown_field(self):
        self.e["bypass"] = True
        self.assertTrue(list(self.v.iter_errors(self.e)))

    def test_id_format(self):
        self.e["event_id"] = "bad"
        self.assertTrue(list(self.v.iter_errors(self.e)))

    def test_jira_parent_integrity(self):
        with (PACK / "jira/svaraa_v0_jira_import.csv").open() as h:
            r = list(csv.DictReader(h))
        byid = {x["Work item ID"]: x for x in r}
        self.assertEqual(len(r), 87)
        self.assertEqual(len(byid), 87)
        self.assertEqual(sum(x["Work type"] == "Sub-task" for x in r), 72)
        for x in r:
            if x["Parent"]:
                self.assertIn(x["Parent"], byid)

    def test_api_refs(self):
        d = yaml.safe_load((CONTRACTS / "openapi.yaml").read_text())

        def visit(x):
            if isinstance(x, dict):
                if "$ref" in x:
                    y = d
                    for k in x["$ref"][2:].split("/"):
                        y = y[k]
                for v in x.values():
                    visit(v)
            elif isinstance(x, list):
                for v in x:
                    visit(v)

        visit(d)

    def test_path_parameters(self):
        d = yaml.safe_load((CONTRACTS / "openapi.yaml").read_text())
        for path, ops in d["paths"].items():
            for op in ops.values():
                self.assertEqual(
                    set(re.findall(r"\{([^}]+)\}", path)),
                    {p["name"] for p in op["parameters"] if p["in"] == "path"},
                )

    def test_drawings(self):
        self.assertEqual(len(list((PACK / "diagrams").glob("*.svg"))), 21)

    def test_crc_golden(self):
        self.assertEqual(f.crc16(b"123456789"), 0x29B1)

    def test_roundtrip(self):
        self.assertEqual(
            f.decode(f.imu_frame(65535, 123, (0, 0, 1000, -2, 3, 4))),
            (0, 0, 1000, -2, 3, 4),
        )

    def test_corruption(self):
        b = bytearray(f.imu_frame(1, 1, (1, 2, 3, 4, 5, 6)))
        b[16] ^= 1
        with self.assertRaises(ValueError):
            f.decode(b)

    def test_length(self):
        with self.assertRaises(ValueError):
            f.decode(b"123")

    def test_range(self):
        with self.assertRaises(Exception):
            f.imu_frame(1, 1, (40000, 0, 0, 0, 0, 0))

    def test_padding(self):
        self.assertEqual(f.imu_frame(1, 1, (0, 0, 0, 0, 0, 0))[23:30], bytes(7))


if __name__ == "__main__":
    unittest.main()
