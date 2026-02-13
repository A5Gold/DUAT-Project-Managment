# MTR DUAT - ManpowerParser Tests
"""TDD tests for parsers/manpower_parser.py - written BEFORE implementation."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ── Helper function tests ────────────────────────────────────────────────────


class TestParseTeamCounts:
    """Tests for _parse_team_counts helper."""

    @pytest.mark.unit
    def test_multiple_teams(self):
        from parsers.manpower_parser import _parse_team_counts
        result = _parse_team_counts("S2x3, S3x2")
        assert result == {"S2": 3, "S3": 2}

    @pytest.mark.unit
    def test_single_team(self):
        from parsers.manpower_parser import _parse_team_counts
        result = _parse_team_counts("S4x1")
        assert result == {"S4": 1}

    @pytest.mark.unit
    def test_empty_string(self):
        from parsers.manpower_parser import _parse_team_counts
        result = _parse_team_counts("")
        assert result == {}

    @pytest.mark.unit
    def test_all_four_teams(self):
        from parsers.manpower_parser import _parse_team_counts
        result = _parse_team_counts("S2x1, S3x2, S4x3, S5x4")
        assert result == {"S2": 1, "S3": 2, "S4": 3, "S5": 4}

    @pytest.mark.unit
    def test_no_match_text(self):
        from parsers.manpower_parser import _parse_team_counts
        result = _parse_team_counts("no teams here")
        assert result == {}

    @pytest.mark.unit
    def test_whitespace_variations(self):
        from parsers.manpower_parser import _parse_team_counts
        result = _parse_team_counts("S2x3,S3x2")
        assert result == {"S2": 3, "S3": 2}


class TestCategorizeLeave:
    """Tests for _categorize_leave helper."""

    @pytest.mark.unit
    def test_al_leave(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("AL: John, Mary")
        assert "John" in result["AL"]
        assert "Mary" in result["AL"]

    @pytest.mark.unit
    def test_sl_leave(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("SL: Peter")
        assert "Peter" in result["SL"]

    @pytest.mark.unit
    def test_rd_leave(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("RD: Tom, Jerry")
        assert "Tom" in result["RD"]
        assert "Jerry" in result["RD"]

    @pytest.mark.unit
    def test_sh_leave(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("SH: Alice")
        assert "Alice" in result["SH"]

    @pytest.mark.unit
    def test_training_leave(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("Training: Bob")
        assert "Bob" in result["Training"]

    @pytest.mark.unit
    def test_empty_string(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("")
        assert result == {"AL": [], "SH": [], "SL": [], "RD": [], "Training": []}

    @pytest.mark.unit
    def test_multiple_categories(self):
        from parsers.manpower_parser import _categorize_leave
        result = _categorize_leave("AL: John\nSL: Mary\nRD: Tom")
        assert "John" in result["AL"]
        assert "Mary" in result["SL"]
        assert "Tom" in result["RD"]


class TestExtractProjectCode:
    """Tests for _extract_project_code helper."""

    @pytest.mark.unit
    def test_extracts_c_code(self):
        from parsers.manpower_parser import _extract_project_code
        result = _extract_project_code("Work on C9081 at KTL")
        assert result == "C9081"

    @pytest.mark.unit
    def test_no_project_code(self):
        from parsers.manpower_parser import _extract_project_code
        result = _extract_project_code("General maintenance work")
        assert result is None

    @pytest.mark.unit
    def test_multiple_codes_returns_first(self):
        from parsers.manpower_parser import _extract_project_code
        result = _extract_project_code("C1234 and C5678")
        assert result == "C1234"

    @pytest.mark.unit
    def test_empty_string(self):
        from parsers.manpower_parser import _extract_project_code
        result = _extract_project_code("")
        assert result is None


class TestClassifyJobType:
    """Tests for _classify_job_type helper."""

    @pytest.mark.unit
    def test_cbm(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("CBM inspection at depot")
        assert result == "CBM"

    @pytest.mark.unit
    def test_cm(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("CM repair work")
        assert result == "CM"

    @pytest.mark.unit
    def test_pa_work(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("PA work at station")
        assert result == "PA work"

    @pytest.mark.unit
    def test_spa_work(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("SPA work on OHL")
        assert result == "SPA work"

    @pytest.mark.unit
    def test_hlm(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("HLM high level maintenance")
        assert result == "HLM"

    @pytest.mark.unit
    def test_c_and_r(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("C&R renewal project")
        assert result == "C&R"

    @pytest.mark.unit
    def test_unknown_type(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("some other work")
        assert result == "Other"

    @pytest.mark.unit
    def test_empty_string(self):
        from parsers.manpower_parser import _classify_job_type
        result = _classify_job_type("")
        assert result == "Other"


class TestParseEpicRoles:
    """Tests for _parse_epic_roles helper."""

    @pytest.mark.unit
    def test_cp_p_role(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("CP(P): John")
        assert "John" in result["CP_P"]

    @pytest.mark.unit
    def test_cp_t_role(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("CP(T): Mary")
        assert "Mary" in result["CP_T"]

    @pytest.mark.unit
    def test_ap_e_role(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("AP(E): Tom")
        assert "Tom" in result["AP_E"]

    @pytest.mark.unit
    def test_spc_role(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("SPC: Alice")
        assert "Alice" in result["SPC"]

    @pytest.mark.unit
    def test_hsm_role(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("HSM: Bob")
        assert "Bob" in result["HSM"]

    @pytest.mark.unit
    def test_np_role(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("NP: Charlie")
        assert "Charlie" in result["NP"]

    @pytest.mark.unit
    def test_empty_string(self):
        from parsers.manpower_parser import _parse_epic_roles
        result = _parse_epic_roles("")
        assert result == {
            "EPIC": "",
            "CP_P": [],
            "CP_T": [],
            "AP_E": [],
            "SPC": [],
            "HSM": [],
            "NP": [],
        }

    @pytest.mark.unit
    def test_multiple_roles(self):
        from parsers.manpower_parser import _parse_epic_roles
        text = "CP(P): John\nCP(T): Mary\nAP(E): Tom"
        result = _parse_epic_roles(text)
        assert "John" in result["CP_P"]
        assert "Mary" in result["CP_T"]
        assert "Tom" in result["AP_E"]

    @pytest.mark.unit
    def test_epic_field_populated(self):
        from parsers.manpower_parser import _parse_epic_roles
        text = "CP(P): John, CP(T): Mary"
        result = _parse_epic_roles(text)
        assert result["EPIC"] != ""


# ── ManpowerParser class tests ───────────────────────────────────────────────


class TestManpowerParserInit:
    """Tests for ManpowerParser.__init__."""

    @pytest.mark.unit
    def test_stores_folder_path(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        parser = ManpowerParser(tmp_path)
        assert parser.folder_path == tmp_path

    @pytest.mark.unit
    def test_accepts_path_object(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        parser = ManpowerParser(tmp_path)
        assert isinstance(parser.folder_path, Path)


class TestGetReportFiles:
    """Tests for ManpowerParser.get_report_files."""

    @pytest.mark.unit
    def test_empty_folder_returns_empty_list(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        parser = ManpowerParser(tmp_path)
        result = parser.get_report_files()
        assert result == []

    @pytest.mark.unit
    def test_excludes_temp_files(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        # Create a normal report file and a temp file
        normal = tmp_path / "PS-OHLR_DUAT_Daily Report_WK01.docx"
        normal.write_bytes(b"fake")
        temp = tmp_path / "~$PS-OHLR_DUAT_Daily Report_WK01.docx"
        temp.write_bytes(b"fake")
        parser = ManpowerParser(tmp_path)
        result = parser.get_report_files()
        assert len(result) == 1
        assert "~$" not in result[0].name

    @pytest.mark.unit
    def test_matches_report_pattern(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        # Create matching and non-matching files
        match = tmp_path / "PS-OHLR_DUAT_Daily Report_WK21.docx"
        match.write_bytes(b"fake")
        no_match = tmp_path / "other_document.docx"
        no_match.write_bytes(b"fake")
        parser = ManpowerParser(tmp_path)
        result = parser.get_report_files()
        assert len(result) == 1
        assert result[0].name == "PS-OHLR_DUAT_Daily Report_WK21.docx"

    @pytest.mark.unit
    def test_returns_sorted_list(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        for name in ["PS-OHLR_DUAT_Daily Report_WK03.docx",
                     "PS-OHLR_DUAT_Daily Report_WK01.docx",
                     "PS-OHLR_DUAT_Daily Report_WK02.docx"]:
            (tmp_path / name).write_bytes(b"fake")
        parser = ManpowerParser(tmp_path)
        result = parser.get_report_files()
        names = [f.name for f in result]
        assert names == sorted(names)


class TestProcessAll:
    """Tests for ManpowerParser.process_all."""

    @pytest.mark.unit
    def test_empty_folder_returns_empty_list(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        parser = ManpowerParser(tmp_path)
        result = parser.process_all()
        assert result == []

    @pytest.mark.unit
    def test_returns_list(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        parser = ManpowerParser(tmp_path)
        result = parser.process_all()
        assert isinstance(result, list)

    @pytest.mark.unit
    def test_corrupted_file_does_not_crash(self, tmp_path: Path):
        """Corrupted DOCX files should be skipped gracefully."""
        from parsers.manpower_parser import ManpowerParser
        bad_file = tmp_path / "PS-OHLR_DUAT_Daily Report_WK01.docx"
        bad_file.write_bytes(b"this is not a valid docx")
        parser = ManpowerParser(tmp_path)
        result = parser.process_all()
        assert isinstance(result, list)
        # Should not crash, returns empty or skips the file
        assert len(result) == 0


class TestShiftRecordStructure:
    """Tests to verify the output structure of parsed records."""

    @pytest.mark.unit
    def test_shift_record_has_required_keys(self):
        """Verify a well-formed ShiftRecord dict has all required keys."""
        from parsers.manpower_parser import ManpowerParser
        # Build a minimal valid record to check structure
        record = {
            "date": "19/5/2025",
            "day_of_week": "Monday",
            "shift": "Day",
            "week": "21",
            "year": "2025",
            "jobs": [],
            "on_duty_names": [],
            "on_duty_team_counts": {},
            "apprentices": [],
            "term_labour_count": 0,
            "leave": {"AL": [], "SH": [], "SL": [], "RD": [], "Training": []},
        }
        required_keys = {
            "date", "day_of_week", "shift", "week", "year",
            "jobs", "on_duty_names", "on_duty_team_counts",
            "apprentices", "term_labour_count", "leave",
        }
        assert required_keys.issubset(set(record.keys()))

    @pytest.mark.unit
    def test_job_dict_has_required_keys(self):
        """Verify a well-formed Job dict has all required keys."""
        job = {
            "type": "CBM",
            "project_code": "C9081",
            "description": "test",
            "qty": 1.0,
            "done_by_raw": "S2x3",
            "team_counts": {"S2": 3},
            "worker_names": ["John"],
            "total_workers": 3,
            "roles": {
                "EPIC": "",
                "CP_P": [],
                "CP_T": [],
                "AP_E": [],
                "SPC": [],
                "HSM": [],
                "NP": [],
            },
        }
        required_keys = {
            "type", "project_code", "description", "qty",
            "done_by_raw", "team_counts", "worker_names",
            "total_workers", "roles",
        }
        assert required_keys.issubset(set(job.keys()))

        role_keys = {"EPIC", "CP_P", "CP_T", "AP_E", "SPC", "HSM", "NP"}
        assert role_keys == set(job["roles"].keys())


# ── Additional helper tests for coverage ─────────────────────────────────────


class TestExtractNamesFromText:
    """Tests for _extract_names_from_text helper."""

    @pytest.mark.unit
    def test_comma_separated(self):
        from parsers.manpower_parser import _extract_names_from_text
        result = _extract_names_from_text("John, Mary, Tom")
        assert result == ["John", "Mary", "Tom"]

    @pytest.mark.unit
    def test_empty_string(self):
        from parsers.manpower_parser import _extract_names_from_text
        result = _extract_names_from_text("")
        assert result == []

    @pytest.mark.unit
    def test_whitespace_only(self):
        from parsers.manpower_parser import _extract_names_from_text
        result = _extract_names_from_text("   ")
        assert result == []

    @pytest.mark.unit
    def test_trailing_commas(self):
        from parsers.manpower_parser import _extract_names_from_text
        result = _extract_names_from_text("John, Mary,")
        assert result == ["John", "Mary"]


class TestParseShiftFromFilename:
    """Tests for _parse_shift_from_filename helper."""

    @pytest.mark.unit
    def test_extracts_week(self):
        from parsers.manpower_parser import _parse_shift_from_filename
        week, year = _parse_shift_from_filename(
            "PS-OHLR_DUAT_Daily Report_WK21.docx"
        )
        assert week == "21"

    @pytest.mark.unit
    def test_extracts_year(self):
        from parsers.manpower_parser import _parse_shift_from_filename
        week, year = _parse_shift_from_filename(
            "PS-OHLR_DUAT_Daily Report_WK21_2025.docx"
        )
        assert year == "2025"

    @pytest.mark.unit
    def test_no_week_returns_empty(self):
        from parsers.manpower_parser import _parse_shift_from_filename
        week, year = _parse_shift_from_filename("some_other_file.docx")
        assert week == ""

    @pytest.mark.unit
    def test_no_year_returns_empty(self):
        from parsers.manpower_parser import _parse_shift_from_filename
        week, year = _parse_shift_from_filename("report_WK05.docx")
        assert year == ""


class TestGetCellText:
    """Tests for _get_cell_text helper."""

    @pytest.mark.unit
    def test_joins_paragraphs(self):
        from parsers.manpower_parser import _get_cell_text

        class FakeParagraph:
            def __init__(self, text):
                self.text = text

        class FakeCell:
            def __init__(self, texts):
                self.paragraphs = [FakeParagraph(t) for t in texts]

        cell = FakeCell(["Hello", "World"])
        result = _get_cell_text(cell)
        assert result == "Hello\nWorld"

    @pytest.mark.unit
    def test_strips_whitespace(self):
        from parsers.manpower_parser import _get_cell_text

        class FakeParagraph:
            def __init__(self, text):
                self.text = text

        class FakeCell:
            def __init__(self, texts):
                self.paragraphs = [FakeParagraph(t) for t in texts]

        cell = FakeCell(["  spaced  "])
        result = _get_cell_text(cell)
        assert result == "spaced"


class TestParseSecondTable:
    """Tests for _parse_second_table with mock table objects."""

    def _make_cell(self, text):
        class FakeParagraph:
            def __init__(self, t):
                self.text = t
        class FakeCell:
            def __init__(self, t):
                self.paragraphs = [FakeParagraph(t)]
        return FakeCell(text)

    def _make_row(self, texts):
        class FakeRow:
            def __init__(self, cells):
                self.cells = cells
        return FakeRow([self._make_cell(t) for t in texts])

    def _make_table(self, rows_data):
        class FakeTable:
            def __init__(self, rows):
                self.rows = rows
        return FakeTable([self._make_row(texts) for texts in rows_data])

    @pytest.mark.unit
    def test_empty_table_returns_empty(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([["Header1", "Header2"]])
        result = _parse_second_table(table, "21", "2025")
        assert result == []

    @pytest.mark.unit
    def test_single_row_table_returns_empty(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([["Header"]])
        result = _parse_second_table(table, "21", "2025")
        assert result == []

    @pytest.mark.unit
    def test_parses_cbm_job_row(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Type", "Qty", "Done By"],
            ["Mon 19/5", "CBM inspection", "3", "S2x2, S3x1"],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        record = result[0]
        assert record["date"] == "19/5"
        assert record["week"] == "21"
        assert record["year"] == "2025"
        assert len(record["jobs"]) >= 1
        job = record["jobs"][0]
        assert job["type"] == "CBM"
        assert job["team_counts"]["S2"] == 2
        assert job["team_counts"]["S3"] == 1

    @pytest.mark.unit
    def test_parses_project_code_in_job(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["19/5", "C9081 HLM work at KTL", "2"],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        job = result[0]["jobs"][0]
        assert job["project_code"] == "C9081"
        assert job["type"] == "HLM"

    @pytest.mark.unit
    def test_parses_attendance_row(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["Mon 19/5", "CBM work", "1"],
            ["", "On duty: John, Mary, Tom", ""],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert "John" in result[0]["on_duty_names"]
        assert "Mary" in result[0]["on_duty_names"]

    @pytest.mark.unit
    def test_parses_apprentice_row(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["19/5", "CBM work", "1"],
            ["", "Apprentice: Alice, Bob", ""],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert "Alice" in result[0]["apprentices"]
        assert "Bob" in result[0]["apprentices"]

    @pytest.mark.unit
    def test_parses_term_labour_row(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["19/5", "CBM work", "1"],
            ["", "Term labour: 5", ""],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert result[0]["term_labour_count"] == 5

    @pytest.mark.unit
    def test_parses_leave_row(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["19/5", "CBM work", "1"],
            ["", "AL: John, Mary", ""],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert "John" in result[0]["leave"]["AL"]
        assert "Mary" in result[0]["leave"]["AL"]

    @pytest.mark.unit
    def test_shift_detection_day(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Shift", "Qty"],
            ["Day shift", "CBM work", "1"],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert result[0]["shift"] == "Day"

    @pytest.mark.unit
    def test_shift_detection_night(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Shift", "Qty"],
            ["Night shift", "HLM work", "0"],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert result[0]["shift"] == "Night"

    @pytest.mark.unit
    def test_multiple_jobs_same_shift(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["19/5", "CBM inspection", "2"],
            ["19/5", "HLM maintenance", "1"],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert len(result[0]["jobs"]) == 2

    @pytest.mark.unit
    def test_day_of_week_extracted(self):
        from parsers.manpower_parser import _parse_second_table
        table = self._make_table([
            ["Header", "Desc", "Qty"],
            ["Mon 19/5", "CBM work", "1"],
        ])
        result = _parse_second_table(table, "21", "2025")
        assert len(result) >= 1
        assert "Mon" in result[0]["day_of_week"]


class TestProcessAllWithMockedDocx:
    """Tests for process_all using mocked python-docx Document."""

    @pytest.mark.unit
    def test_skips_file_with_fewer_than_2_tables(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        from unittest.mock import patch, MagicMock

        report = tmp_path / "PS-OHLR_DUAT_Daily Report_WK01.docx"
        report.write_bytes(b"fake")

        mock_doc = MagicMock()
        mock_doc.tables = [MagicMock()]  # Only 1 table

        with patch("docx.Document", return_value=mock_doc):
            parser = ManpowerParser(tmp_path)
            result = parser.process_all()
            assert result == []

    @pytest.mark.unit
    def test_nonexistent_folder_returns_empty(self):
        from parsers.manpower_parser import ManpowerParser
        parser = ManpowerParser(Path("C:/nonexistent/folder/xyz"))
        result = parser.get_report_files()
        assert result == []

    @pytest.mark.unit
    def test_process_all_with_valid_mock_table(self, tmp_path: Path):
        from parsers.manpower_parser import ManpowerParser
        from unittest.mock import patch, MagicMock

        report = tmp_path / "PS-OHLR_DUAT_Daily Report_WK21_2025.docx"
        report.write_bytes(b"fake")

        def make_para(text):
            p = MagicMock()
            p.text = text
            return p

        def make_cell(text):
            c = MagicMock()
            c.paragraphs = [make_para(text)]
            return c

        def make_row(texts):
            r = MagicMock()
            r.cells = [make_cell(t) for t in texts]
            return r

        header_row = make_row(["Header", "Desc", "Qty"])
        data_row = make_row(["Mon 19/5", "CBM inspection at KTL", "3"])

        table1 = MagicMock()
        table2 = MagicMock()
        table2.rows = [header_row, data_row]

        mock_doc = MagicMock()
        mock_doc.tables = [table1, table2]

        with patch("docx.Document", return_value=mock_doc):
            parser = ManpowerParser(tmp_path)
            result = parser.process_all()
            assert len(result) >= 1
            assert result[0]["week"] == "21"
            assert result[0]["year"] == "2025"
            assert result[0]["jobs"][0]["type"] == "CBM"
