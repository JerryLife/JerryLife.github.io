"""Check editable content and CMS schema compatibility without changing files."""
import copy
import unittest

import build_cv_content as content


class FacultyContentTests(unittest.TestCase):
    def setUp(self):
        self.home = content.load_yaml(content.CONTENT_DIRECTORY / "home.yml")
        self.supervision = content.load_yaml(content.CONTENT_DIRECTORY / "supervision.yml")
        self.pages = content.load_yaml(content.CONTENT_DIRECTORY / "pages.yml")
        self.publications = content.load_publications()

    def validate(self):
        content.validate_faculty_content(self.home, self.supervision, self.pages, self.publications)

    def test_current_content(self):
        self.validate()

    def test_publication_author_role_priority(self):
        aliases = {"Zhaomin Wu", "Z. Wu"}
        cases = [
            (["Zhaomin Wu", "Other Author"], 0),
            (["First Author*", "Zhaomin Wu*", "Last Author"], 0),
            (["First Author∗", "Z. Wu∗†", "Last Author"], 0),
            (["Zhaomin Wu†"], 0),
            (["First Author", "Zhaomin Wu†", "Last Author"], 1),
            (["First Author", "Z. Wu"], 1),
            (["First Author", "Zhaomin Wu", "Last Author"], 2),
            (["First Author*", "Zhaomin Wu", "Last Author†"], 2),
            (["Another Wu", "Other Author"], 2),
        ]
        for authors, expected in cases:
            with self.subTest(authors=authors):
                self.assertEqual(content.publication_role_priority({"author_names": authors}, aliases), expected)

    def test_website_publication_order_keeps_years_and_prioritizes_roles(self):
        scholar = {"first_name": ["Zhaomin", "Z."], "last_name": ["Wu"]}
        papers = [
            {"key": "a2026other", "year": "2026", "author_names": ["First Author", "Zhaomin Wu", "Last Author"]},
            {"key": "c2026last", "year": "2026", "author_names": ["First Author", "Zhaomin Wu"]},
            {"key": "z2026first", "year": "2026", "author_names": ["Zhaomin Wu", "Last Author"]},
            {"key": "a2025first", "year": "2025", "author_names": ["Zhaomin Wu", "Last Author"]},
            {"key": "b2026corresponding", "year": "2026", "author_names": ["First Author", "Zhaomin Wu†", "Last Author"]},
            {"key": "y2026cofirst", "year": "2026", "author_names": ["First Author*", "Z. Wu*†", "Last Author"]},
        ]
        original = copy.deepcopy(papers)
        ordered = content.sorted_website_publications(papers, scholar)
        self.assertEqual([paper["key"] for paper in ordered], [
            "y2026cofirst", "z2026first", "b2026corresponding", "c2026last", "a2026other", "a2025first",
        ])
        self.assertEqual(papers, original)

    def test_additional_research_direction_needs_no_template_change(self):
        direction = copy.deepcopy(self.home["directions"][0])
        direction.update(id="additional-direction", title="Additional research")
        self.home["directions"].append(direction)
        self.validate()

    def test_unknown_publication_fails_with_field_path(self):
        self.home["directions"][0]["subcategories"][0]["publications"].append("missing-paper")
        with self.assertRaisesRegex(content.ContentValidationError, r"home.directions\[0\].*missing-paper"):
            self.validate()

    def test_duplicate_direction_id_is_rejected(self):
        self.home["directions"].append(copy.deepcopy(self.home["directions"][0]))
        with self.assertRaisesRegex(content.ContentValidationError, "unique lowercase identifier"):
            self.validate()

    def test_missing_template_label_is_rejected(self):
        del self.pages["supervision"]["mentoring_heading"]
        with self.assertRaisesRegex(content.ContentValidationError, "pages.supervision.mentoring_heading"):
            self.validate()

    def test_email_propagates_to_legacy_social_data(self):
        profile = content.load_yaml(content.PROFILE_SOURCE)
        self.assertNotIn("email", profile["socials"])
        profile["basics"]["email"] = "example@example.org"
        result = content.validate_profile(profile)
        self.assertEqual(result["socials"]["email"], "example@example.org")

    def test_cms_covers_editable_page_content(self):
        cms = content.load_yaml(content.REPOSITORY_ROOT / "admin/config.yml")
        documents = {item["file"]: item for collection in cms["collections"] for item in collection.get("files", [])}

        def check_fields(value, fields, path):
            field_map = {field["name"]: field for field in fields}
            for key, item in value.items():
                self.assertIn(key, field_map, f"CMS field missing: {path}.{key}")
                field = field_map[key]
                if isinstance(item, dict):
                    check_fields(item, field.get("fields", []), f"{path}.{key}")
                elif isinstance(item, list):
                    for element in item:
                        if isinstance(element, dict):
                            check_fields(element, field.get("fields", []), f"{path}.{key}[]")

        for filename, data in (("home", self.home), ("supervision", self.supervision), ("pages", self.pages)):
            path = f"_data/content/{filename}.yml"
            check_fields(data, documents[path]["fields"], path)

        for _, filename in content.SERVICE_GROUP_DEFINITIONS:
            path = f"_data/content/service/{filename}"
            data = content.load_yaml(content.SERVICE_DIRECTORY / filename)
            check_fields(data, documents[path]["fields"], path)

    def test_cv_preserves_conference_and_journal_roles(self):
        service = {"groups": [
            {"id": "area-chairs", "title": "Area Chair", "entries": [
                {"year": 2027, "name": "ICLR", "role": "Area Chair"},
            ]},
            {"id": "conference-reviewers", "title": "Conference Reviewers", "entries": [
                {"year": 2026, "name": "ICLR", "role": "Reviewer"},
                {"year": 2026, "name": "Other Conference", "role": "Senior PC Member"},
            ]},
            {"id": "journal-reviewers", "title": "Journal Reviewers", "entries": [
                {"year": 2026, "name": "Example Journal", "role": "Associate Editor"},
            ]},
        ]}
        rendered = content.render_service(service)
        headings = [r"\yearSeparator{" + group["title"] + "}" for group in service["groups"]]
        for heading in headings:
            self.assertIn(heading, rendered)
        self.assertLess(rendered.index(headings[0]), rendered.index(headings[1]))
        self.assertLess(rendered.index(headings[1]), rendered.index(headings[2]))
        self.assertIn(r"\serviceLine{2027}{ICLR.}", rendered)
        self.assertIn("Other Conference (Senior PC Member)", rendered)
        self.assertIn("Example Journal (Associate Editor)", rendered)
        self.assertNotIn("(Reviewer)", rendered)
        self.assertNotIn("ICLR (Area Chair)", rendered)
        self.assertIn(r"\serviceLine{2026}", rendered)


if __name__ == "__main__":
    unittest.main()
