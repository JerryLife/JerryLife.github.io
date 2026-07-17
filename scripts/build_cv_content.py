#!/usr/bin/env python3
"""Build the website and PDF CV from a single semantic content model.

Editable sources:
  * `_data/content/profile.yml`
  * `_data/content/site.yml`
  * `_data/content/cv/*.yml`
  * `_data/content/service/*.yml`
  * `_data/content/teaching.yml`
  * `_data/content/mentoring.yml`
  * `_data/content/talks.yml`
  * `_data/content/publications/*.bib`

The generated JSON Resume, Jekyll view model, merged bibliography, LaTeX
fragments, and PDF are outputs. They must not be edited by hand.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import yaml
    from pybtex.database import parse_string
    from pybtex.errors import set_strict_mode
except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
    sys.stderr.write(
        f"{error.name} is required. Install project dependencies with "
        "`python3 -m pip install -r requirements.txt`.\n"
    )
    raise SystemExit(2)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIRECTORY = REPOSITORY_ROOT / "_data" / "content"
PROFILE_SOURCE = CONTENT_DIRECTORY / "profile.yml"
SITE_SOURCE = CONTENT_DIRECTORY / "site.yml"
CV_DIRECTORY = CONTENT_DIRECTORY / "cv"
CV_PROFILE_SOURCE = CV_DIRECTORY / "profile.yml"
CV_WORK_SOURCE = CV_DIRECTORY / "work.yml"
CV_EDUCATION_SOURCE = CV_DIRECTORY / "education.yml"
CV_AWARDS_SOURCE = CV_DIRECTORY / "awards.yml"
CV_SKILLS_SOURCE = CV_DIRECTORY / "skills.yml"
CV_LANGUAGES_SOURCE = CV_DIRECTORY / "languages.yml"
CV_VOLUNTEER_SOURCE = CV_DIRECTORY / "volunteer.yml"
CV_PUBLICATION_DISPLAY_SOURCE = CV_DIRECTORY / "publication-display.yml"
CV_RESEARCH_IMPACT_SOURCE = CV_DIRECTORY / "research-impact.yml"
CV_SECTIONS_SOURCE = CV_DIRECTORY / "sections.yml"
SERVICE_DIRECTORY = CONTENT_DIRECTORY / "service"
TEACHING_SOURCE = CONTENT_DIRECTORY / "teaching.yml"
MENTORING_SOURCE = CONTENT_DIRECTORY / "mentoring.yml"
TALKS_SOURCE = CONTENT_DIRECTORY / "talks.yml"
PUBLICATION_SOURCE_DIRECTORY = CONTENT_DIRECTORY / "publications"

RESUME_JSON_OUTPUT = REPOSITORY_ROOT / "assets" / "json" / "resume.json"
SITE_VIEW_OUTPUT = REPOSITORY_ROOT / "_data" / "generated" / "content.yml"
MERGED_BIBLIOGRAPHY_OUTPUT = REPOSITORY_ROOT / "_bibliography" / "papers.bib"
PUBLICATIONS_BIBLIOGRAPHY_OUTPUT = REPOSITORY_ROOT / "_bibliography" / "publications.bib"
PREPRINTS_BIBLIOGRAPHY_OUTPUT = REPOSITORY_ROOT / "_bibliography" / "preprints.bib"
LATEX_OUTPUT_DIRECTORY = REPOSITORY_ROOT / "assets" / "latex" / "generated"

LATEX_ESCAPE_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

MONTH_NAMES = {
    "01": "Jan.",
    "02": "Feb.",
    "03": "Mar.",
    "04": "Apr.",
    "05": "May",
    "06": "Jun.",
    "07": "Jul.",
    "08": "Aug.",
    "09": "Sep.",
    "10": "Oct.",
    "11": "Nov.",
    "12": "Dec.",
}

INLINE_MARKDOWN = re.compile(
    r"(?P<link>\[(?P<link_text>[^\[\]\n]+)\]\((?P<link_url>[^()\s]+)\))"
    r"|(?P<bold>\*\*(?P<bold_text>[^*\n]+)\*\*)"
    r"|(?P<italic>(?<!\*)\*(?P<italic_text>[^*\n]+)\*(?!\*))"
    r"|(?P<code>`(?P<code_text>[^`\n]+)`)")

# Keep BibTeX keys portable and predictable across Jekyll Scholar, LaTeX, and
# the CMS filesystem. The convention is first-author + year + short title.
CITATION_KEY_PATTERN = re.compile(r"^[a-z]+(?:19|20)\d{2}[a-z][a-z0-9]*$")

SERVICE_GROUP_DEFINITIONS = (
    ("conference-reviewers", "conference-reviewers.yml"),
    ("journal-reviewers", "journal-reviewers.yml"),
    ("recognition", "recognition.yml"),
    ("tutorial", "tutorial.yml"),
)


class NoAliasSafeDumper(yaml.SafeDumper):
    """Keep generated YAML readable and independent of YAML anchor support."""

    def ignore_aliases(self, data: Any) -> bool:  # type: ignore[override]
        return True


class ContentValidationError(ValueError):
    """Raised when editable content cannot be rendered safely."""


def validation_error(path: str, message: str) -> None:
    raise ContentValidationError(f"{path}: {message}")


def mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        validation_error(path, "must be an object")
    return value


def list_value(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        validation_error(path, "must be a list")
    return value


def text(value: Any, path: str, *, required: bool = False) -> str:
    if value is None:
        if required:
            validation_error(path, "is required")
        return ""
    if isinstance(value, bool) or not isinstance(value, (str, int, float, date)):
        validation_error(path, "must be text")
    result = str(value).strip()
    if required and not result:
        validation_error(path, "must not be empty")
    return result


def optional_list(value: Any, path: str) -> list[Any]:
    if value is None:
        return []
    return list_value(value, path)


def validate_url(value: Any, path: str, *, allow_empty: bool = True) -> str:
    value = text(value, path, required=not allow_empty)
    if not value:
        return ""
    if any(character in value for character in "\\{}\r\n\t"):
        validation_error(path, "contains characters that cannot be used in a URL")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https", "mailto"}:
        validation_error(path, "must use http, https, or mailto")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        validation_error(path, "must include a host")
    if parsed.scheme == "mailto" and not parsed.path:
        validation_error(path, "must include an email address")
    return value


def validate_email(value: Any, path: str) -> str:
    value = text(value, path)
    if not value:
        return ""
    if not re.fullmatch(r"[^@\s{}\\]+@[^@\s{}\\]+\.[^@\s{}\\]+", value):
        validation_error(path, "must be a valid email address")
    return value


def validate_string_list(value: Any, path: str) -> list[str]:
    return [text(item, f"{path}[{index}]", required=True) for index, item in enumerate(optional_list(value, path))]


def load_yaml(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError:
        raise ContentValidationError(f"{path.relative_to(REPOSITORY_ROOT)}: file does not exist") from None
    except yaml.YAMLError as error:
        raise ContentValidationError(f"{path.relative_to(REPOSITORY_ROOT)}: invalid YAML: {error}") from None


def require_schema(value: dict[str, Any], path: str, version: int) -> None:
    if value.get("schema_version") != version:
        validation_error(f"{path}.schema_version", f"must be {version}")


def validate_profile(data: Any) -> dict[str, Any]:
    profile = mapping(data, "profile")
    require_schema(profile, "profile", 1)
    basics = mapping(profile.get("basics"), "profile.basics")
    text(basics.get("name"), "profile.basics.name", required=True)
    for field in ("label", "position", "image", "summary", "phone", "location"):
        text(basics.get(field), f"profile.basics.{field}")
    validate_email(basics.get("email"), "profile.basics.email")
    if basics.get("url"):
        validate_url(basics["url"], "profile.basics.url")
    for index, item in enumerate(optional_list(basics.get("profiles"), "profile.basics.profiles")):
        item = mapping(item, f"profile.basics.profiles[{index}]")
        text(item.get("network"), f"profile.basics.profiles[{index}].network", required=True)
        if item.get("url"):
            validate_url(item["url"], f"profile.basics.profiles[{index}].url")
        if "username" in item:
            text(item["username"], f"profile.basics.profiles[{index}].username")

    web_about = mapping(profile.get("web_about"), "profile.web_about")
    for field in ("subtitle", "body", "image", "align"):
        text(web_about.get(field), f"profile.web_about.{field}", required=field in {"body", "image"})
    if not isinstance(web_about.get("image_circular", False), bool):
        validation_error("profile.web_about.image_circular", "must be true or false")

    mapping(profile.get("socials", {}), "profile.socials")
    return profile


def validate_cv_profile(data: Any) -> dict[str, Any]:
    profile = mapping(data, "cv_profile")
    require_schema(profile, "cv_profile", 1)
    text(profile.get("title"), "cv_profile.title", required=True)
    text(profile.get("body"), "cv_profile.body", required=True)
    return profile


def validate_schema_document(data: Any, path: str) -> dict[str, Any]:
    document = mapping(data, path)
    require_schema(document, path, 1)
    return document


def validate_cv_entries(entries: list[Any], name: str, required: set[str], url_fields: set[str]) -> None:
    for index, value in enumerate(entries):
        path = f"cv.{name}[{index}]"
        entry = mapping(value, path)
        for field in required:
            text(entry.get(field), f"{path}.{field}", required=True)
        for field in url_fields:
            if entry.get(field):
                validate_url(entry[field], f"{path}.{field}")
        for field in ("highlights", "courses", "keywords"):
            if field in entry:
                validate_string_list(entry[field], f"{path}.{field}")


def validate_work_entries(entries: list[Any], path: str) -> None:
    for index, value in enumerate(entries):
        entry_path = f"{path}[{index}]"
        entry = mapping(value, entry_path)
        main_job = mapping(entry.get("main_job"), f"{entry_path}.main_job")
        text(main_job.get("name"), f"{entry_path}.main_job.name", required=True)
        text(main_job.get("location"), f"{entry_path}.main_job.location")
        if main_job.get("url"):
            validate_url(main_job["url"], f"{entry_path}.main_job.url")

        subjobs = optional_list(entry.get("subjobs"), f"{entry_path}.subjobs")
        if not subjobs:
            validation_error(f"{entry_path}.subjobs", "must contain at least one job")
        for subjob_index, subjob_value in enumerate(subjobs):
            subjob_path = f"{entry_path}.subjobs[{subjob_index}]"
            subjob = mapping(subjob_value, subjob_path)
            text(subjob.get("position"), f"{subjob_path}.position", required=True)
            for field in ("start_date", "end_date", "summary"):
                text(subjob.get(field), f"{subjob_path}.{field}")
            validate_string_list(subjob.get("highlights"), f"{subjob_path}.highlights")


def validate_work_document(data: Any) -> dict[str, Any]:
    work = mapping(data, "cv.work")
    require_schema(work, "cv.work", 2)
    validate_work_entries(optional_list(work.get("entries"), "cv.work.entries"), "cv.work.entries")
    return work


def validate_award_config(value: Any, path: str) -> dict[str, Any]:
    config = mapping(value, path)
    text(config.get("title"), f"{path}.title", required=True)
    validate_string_list(config.get("include_titles"), f"{path}.include_titles")
    return config


def validate_research_impact(value: Any) -> dict[str, Any]:
    impact = mapping(value, "cv.research_impact")
    text(impact.get("title"), "cv.research_impact.title", required=True)
    text(impact.get("supplemental"), "cv.research_impact.supplemental")
    for index, group in enumerate(optional_list(impact.get("groups"), "cv.research_impact.groups")):
        group = mapping(group, f"cv.research_impact.groups[{index}]")
        text(group.get("title"), f"cv.research_impact.groups[{index}].title", required=True)
        for item_index, item in enumerate(optional_list(group.get("items"), f"cv.research_impact.groups[{index}].items")):
            item = mapping(item, f"cv.research_impact.groups[{index}].items[{item_index}]")
            text(item.get("name"), f"cv.research_impact.groups[{index}].items[{item_index}].name", required=True)
            if item.get("url"):
                validate_url(item["url"], f"cv.research_impact.groups[{index}].items[{item_index}].url")
            text(item.get("venue"), f"cv.research_impact.groups[{index}].items[{item_index}].venue")
            text(item.get("description"), f"cv.research_impact.groups[{index}].items[{item_index}].description")
    validate_string_list(impact.get("paragraphs"), "cv.research_impact.paragraphs")
    return impact


def validate_cv(data: Any) -> dict[str, Any]:
    cv = mapping(data, "cv")
    require_schema(cv, "cv", 1)
    validate_work_entries(optional_list(cv.get("work"), "cv.work"), "cv.work")
    validate_cv_entries(optional_list(cv.get("education"), "cv.education"), "education", {"institution", "study_type"}, {"url"})
    validate_cv_entries(optional_list(cv.get("awards"), "cv.awards"), "awards", {"title"}, {"url"})
    validate_cv_entries(optional_list(cv.get("skills"), "cv.skills"), "skills", {"name"}, set())
    validate_cv_entries(optional_list(cv.get("languages"), "cv.languages"), "languages", {"language"}, set())
    validate_cv_entries(optional_list(cv.get("volunteer"), "cv.volunteer",), "volunteer", {"organization", "position"}, {"url"})

    for index, section in enumerate(optional_list(cv.get("sections"), "cv.sections")):
        section = mapping(section, f"cv.sections[{index}]")
        text(section.get("title"), f"cv.sections[{index}].title", required=True)
        text(section.get("body"), f"cv.sections[{index}].body", required=True)
        if "id" in section:
            identifier = text(section["id"], f"cv.sections[{index}].id", required=True)
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", identifier):
                validation_error(f"cv.sections[{index}].id", "must use lowercase letters, digits, hyphens, or underscores")
        if "enabled" in section and not isinstance(section["enabled"], bool):
            validation_error(f"cv.sections[{index}].enabled", "must be true or false")

    display = mapping(cv.get("display"), "cv.display")
    for name in ("grants", "honors", "undergraduate_honors"):
        validate_award_config(display.get(name), f"cv.display.{name}")
    for name in ("selected_publications", "publications", "preprints"):
        config = mapping(display.get(name), f"cv.display.{name}")
        text(config.get("title"), f"cv.display.{name}.title", required=True)
        text(config.get("supplemental"), f"cv.display.{name}.supplemental")
    validate_research_impact(cv.get("research_impact"))
    return cv


def validate_service_group(data: Any, group_id: str) -> dict[str, Any]:
    path = f"service.{group_id}"
    group = mapping(data, path)
    require_schema(group, path, 1)
    text(group.get("title"), f"{path}.title", required=True)
    for index, item_value in enumerate(optional_list(group.get("entries"), f"{path}.entries")):
        item_path = f"{path}.entries[{index}]"
        item = mapping(item_value, item_path)
        year = text(item.get("year"), f"{item_path}.year", required=True)
        if not re.fullmatch(r"\d{4}", year):
            validation_error(f"{item_path}.year", "must be a four-digit year")
        text(item.get("name"), f"{item_path}.name", required=True)
        text(item.get("role"), f"{item_path}.role")
        if item.get("url"):
            validate_url(item["url"], f"{item_path}.url")
    return {**group, "id": group_id}


def load_service() -> dict[str, Any]:
    if not SERVICE_DIRECTORY.is_dir():
        validation_error("_data/content/service", "directory does not exist")
    expected_files = {filename for _, filename in SERVICE_GROUP_DEFINITIONS}
    unknown_files = sorted(path.name for path in SERVICE_DIRECTORY.glob("*.yml") if path.name not in expected_files)
    if unknown_files:
        validation_error("_data/content/service", f"has unknown category files: {', '.join(unknown_files)}")
    return {
        "groups": [
            validate_service_group(load_yaml(SERVICE_DIRECTORY / filename), group_id)
            for group_id, filename in SERVICE_GROUP_DEFINITIONS
        ]
    }


def validate_teaching(data: Any) -> dict[str, Any]:
    teaching = mapping(data, "teaching")
    require_schema(teaching, "teaching", 1)
    text(teaching.get("cv_section_title"), "teaching.cv_section_title", required=True)
    teaching_kinds = {"teaching_assistant", "instructor", "guest_lecture", "other"}
    for section_index, section_value in enumerate(optional_list(teaching.get("sections"), "teaching.sections")):
        section_path = f"teaching.sections[{section_index}]"
        section = mapping(section_value, section_path)
        kind = text(section.get("kind"), f"{section_path}.kind", required=True)
        if kind not in teaching_kinds:
            validation_error(f"{section_path}.kind", f"must be one of {', '.join(sorted(teaching_kinds))}")
        text(section.get("title"), f"{section_path}.title", required=True)
        for entry_index, entry_value in enumerate(optional_list(section.get("entries"), f"{section_path}.entries")):
            path = f"{section_path}.entries[{entry_index}]"
            item = mapping(entry_value, path)
            if kind == "other":
                text(item.get("title"), f"{path}.title", required=True)
                text(item.get("period"), f"{path}.period", required=True)
            else:
                for field in ("course", "term"):
                    text(item.get(field), f"{path}.{field}", required=True)
                text(item.get("code"), f"{path}.code")
            for field in ("institution", "role"):
                text(item.get(field), f"{path}.{field}")
            validate_string_list(item.get("notes"), f"{path}.notes")
            if item.get("url"):
                validate_url(item["url"], f"{path}.url")

    return teaching


def validate_mentoring(data: Any) -> dict[str, Any]:
    mentoring = mapping(data, "mentoring")
    require_schema(mentoring, "mentoring", 1)
    text(mentoring.get("title"), "mentoring.title", required=True)
    text(mentoring.get("intro"), "mentoring.intro")
    text(mentoring.get("cv_title"), "mentoring.cv_title")
    for index, group_value in enumerate(optional_list(mentoring.get("cv_groups"), "mentoring.cv_groups")):
        path = f"mentoring.cv_groups[{index}]"
        group = mapping(group_value, path)
        for field in ("title", "detail", "period", "representative"):
            text(group.get(field), f"{path}.{field}", required=True)
    for index, item_value in enumerate(optional_list(mentoring.get("entries"), "mentoring.entries")):
        path = f"mentoring.entries[{index}]"
        item = mapping(item_value, path)
        for field in ("name", "role", "institution", "period"):
            text(item.get(field), f"{path}.{field}", required=True)
        validate_string_list(item.get("notes"), f"{path}.notes")
        text(item.get("outcome"), f"{path}.outcome")
        if item.get("url"):
            validate_url(item["url"], f"{path}.url")
    return mentoring


def validate_talks(data: Any) -> dict[str, Any]:
    talks = mapping(data, "talks")
    require_schema(talks, "talks", 1)
    cv = mapping(talks.get("cv"), "talks.cv")
    text(cv.get("title"), "talks.cv.title", required=True)
    for index, item in enumerate(optional_list(talks.get("entries"), "talks.entries")):
        path = f"talks.entries[{index}]"
        item = mapping(item, path)
        for field in ("date", "type", "venue", "title"):
            text(item.get(field), f"{path}.{field}", required=True)
        if item.get("url"):
            validate_url(item["url"], f"{path}.url")
        text(item.get("note"), f"{path}.note")
    return talks


def validate_site(data: Any) -> dict[str, Any]:
    settings = mapping(data, "site")
    require_schema(settings, "site", 1)

    seo = mapping(settings.get("seo"), "site.seo")
    text(seo.get("description"), "site.seo.description", required=True)
    text(seo.get("keywords"), "site.seo.keywords")
    text(settings.get("footer_text"), "site.footer_text")

    repositories = mapping(settings.get("repositories"), "site.repositories")
    for field in ("github_users", "github_repos"):
        for index, value in enumerate(optional_list(repositories.get(field), f"site.repositories.{field}")):
            text(value, f"site.repositories.{field}[{index}]", required=True)
    lines_max = repositories.get("repo_description_lines_max")
    if lines_max is not None and (isinstance(lines_max, bool) or not isinstance(lines_max, int) or lines_max < 1):
        validation_error("site.repositories.repo_description_lines_max", "must be a positive integer")

    seen_venues: set[str] = set()
    for index, entry_value in enumerate(list_value(settings.get("venues"), "site.venues")):
        path = f"site.venues[{index}]"
        entry = mapping(entry_value, path)
        abbreviation = text(entry.get("abbreviation"), f"{path}.abbreviation", required=True)
        if abbreviation in seen_venues:
            validation_error(f"{path}.abbreviation", f"duplicate venue abbreviation '{abbreviation}'")
        seen_venues.add(abbreviation)
        if entry.get("url"):
            validate_url(entry["url"], f"{path}.url")
        color = text(entry.get("color"), f"{path}.color")
        if color and not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            validation_error(f"{path}.color", "must be a six-digit hex color such as #2563eb")
    return settings


def extract_single_bibtex_entry(source: str, path: Path) -> str:
    """Ensure a CMS publication file contains exactly one real BibTeX record."""
    start = source.find("@")
    if start < 0:
        validation_error(str(path.relative_to(REPOSITORY_ROOT)), "must contain a BibTeX entry")
    match = re.match(r"@\s*([A-Za-z]+)\s*([\{(])", source[start:])
    if not match:
        validation_error(str(path.relative_to(REPOSITORY_ROOT)), "has an invalid BibTeX entry header")
    entry_type = match.group(1).lower()
    if entry_type in {"comment", "preamble", "string"}:
        validation_error(str(path.relative_to(REPOSITORY_ROOT)), "must contain a publication entry, not a BibTeX macro")
    opener = match.group(2)
    closer = "}" if opener == "{" else ")"
    cursor = start + match.end() - 1
    depth = 0
    quoted = False
    escaped = False
    while cursor < len(source):
        character = source[cursor]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
        else:
            if character == '"' and depth == 1:
                quoted = True
            elif character == opener:
                depth += 1
            elif character == closer:
                depth -= 1
                if depth == 0:
                    break
        cursor += 1
    if cursor >= len(source):
        validation_error(str(path.relative_to(REPOSITORY_ROOT)), "has an unclosed BibTeX entry")
    trailing = re.sub(r"(?m)^\s*%.*$", "", source[cursor + 1 :]).strip()
    if trailing:
        validation_error(str(path.relative_to(REPOSITORY_ROOT)), "must contain exactly one BibTeX entry")
    return source[start : cursor + 1].strip() + "\n"


def bibtex_text(value: Any) -> str:
    result = str(value or "")
    result = result.replace("&amp;", "&")
    result = result.replace(r"\_", "_").replace(r"\%", "%").replace(r"\&", "&")
    result = result.replace(r"\#", "#").replace(r"\$", "$")
    result = result.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", result).strip()


def bibtex_bool(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def bibtex_order(value: Any, default: int = 9999) -> int:
    rendered = bibtex_text(value)
    return int(rendered) if re.fullmatch(r"[1-9]\d*", rendered) else default


def person_name(person: Any, *, abbreviated: bool) -> str:
    first_names = [bibtex_text(value) for value in person.first_names + person.middle_names]
    family_names = [bibtex_text(value) for value in person.prelast_names + person.last_names + person.lineage_names]
    if abbreviated:
        initials: list[str] = []
        for value in first_names:
            initials.append("-".join(f"{part[0]}." for part in value.split("-") if part))
        first_names = initials
    return " ".join(first_names + family_names).strip()


def publication_url(fields: dict[str, Any]) -> str:
    for name in ("cv_url", "url", "pdf"):
        value = bibtex_text(fields.get(name))
        if value:
            return value
    doi = bibtex_text(fields.get("doi"))
    return f"https://doi.org/{doi}" if doi else ""


def publication_details(entry_type: str, fields: dict[str, Any]) -> str:
    venue = bibtex_text(fields.get("booktitle") or fields.get("journal"))
    if not venue:
        return ""
    return f"In {venue}" if entry_type.lower() in {"inproceedings", "incollection", "conference"} else venue


def is_arxiv_preprint(fields: dict[str, Any]) -> bool:
    """Classify only records whose publication venue is arXiv, not papers with an arXiv PDF."""
    venue_fields = ("abbr", "booktitle", "journal", "archiveprefix", "eprinttype")
    return any("arxiv" in bibtex_text(fields.get(field)).lower() for field in venue_fields)


def load_publications() -> list[dict[str, Any]]:
    if not PUBLICATION_SOURCE_DIRECTORY.is_dir():
        validation_error("_data/content/publications", "directory does not exist")
    paths = sorted(PUBLICATION_SOURCE_DIRECTORY.glob("*.bib"), key=lambda path: path.name.lower())
    if not paths:
        validation_error("_data/content/publications", "must contain at least one .bib file")
    records: list[dict[str, Any]] = []
    keys: set[str] = set()
    set_strict_mode(True)
    for path in paths:
        raw = extract_single_bibtex_entry(path.read_text(encoding="utf-8"), path)
        try:
            bibliography = parse_string(raw, "bibtex")
        except Exception as error:  # Pybtex errors do not share a stable base class.
            validation_error(str(path.relative_to(REPOSITORY_ROOT)), f"cannot parse BibTeX: {error}")
        if len(bibliography.entries) != 1:
            validation_error(str(path.relative_to(REPOSITORY_ROOT)), "must contain exactly one publication")
        key, entry = next(iter(bibliography.entries.items()))
        if not CITATION_KEY_PATTERN.fullmatch(key):
            validation_error(
                str(path.relative_to(REPOSITORY_ROOT)),
                "citation key must use lowercase firstauthorYYYYshorttitle format without underscores or punctuation "
                "(for example, 'wu2026llmdna')",
            )
        if path.name != f"{key}.bib":
            validation_error(
                str(path.relative_to(REPOSITORY_ROOT)),
                f"filename must exactly match its citation key: expected '{key}.bib'",
            )
        if key in keys:
            validation_error(str(path.relative_to(REPOSITORY_ROOT)), f"duplicate citation key '{key}'")
        keys.add(key)
        fields = dict(entry.fields)
        for field in ("title", "year"):
            if not bibtex_text(fields.get(field)):
                validation_error(str(path.relative_to(REPOSITORY_ROOT)), f"BibTeX field '{field}' is required")
        if not entry.persons.get("author"):
            validation_error(str(path.relative_to(REPOSITORY_ROOT)), "BibTeX field 'author' is required")
        if not bibtex_text(fields.get("booktitle") or fields.get("journal")):
            validation_error(str(path.relative_to(REPOSITORY_ROOT)), "requires either 'booktitle' or 'journal'")
        year = bibtex_text(fields.get("year"))
        if not re.fullmatch(r"\d{4}", year):
            validation_error(str(path.relative_to(REPOSITORY_ROOT)), "BibTeX field 'year' must be a four-digit year")
        authors = [person_name(person, abbreviated=False) for person in entry.persons["author"]]
        short_authors = [person_name(person, abbreviated=True) for person in entry.persons["author"]]
        record = {
            "key": key,
            "source_path": str(path.relative_to(REPOSITORY_ROOT)),
            "source": raw,
            "entry_type": entry.type,
            "fields": fields,
            "year": year,
            "title": bibtex_text(fields["title"]),
            "author_names": authors,
            "short_author_names": short_authors,
            "authors": ", ".join(author for author in authors if author),
            "short_authors": ", ".join(author for author in short_authors if author),
            "abbr": bibtex_text(fields.get("abbr")),
            "venue": bibtex_text(fields.get("abbr") or fields.get("booktitle") or fields.get("journal")),
            "details": publication_details(entry.type, fields),
            "url": publication_url(fields),
            "highlight": bibtex_text(fields.get("cvselectedhighlight") or fields.get("cv_highlight") or fields.get("award")),
            "summary": bibtex_text(fields.get("cvselectedsummary") or fields.get("cv_summary")),
            "selected": bibtex_bool(fields.get("selected")),
            "cv_selected": bibtex_bool(fields.get("cv_selected")),
            "cv_order": int(bibtex_text(fields.get("cv_order")) or "9999"),
            "cv_full_order": bibtex_order(fields.get("cvfullorder") or fields.get("cv_full_order")),
            "cv_full_visible": (
                bibtex_bool(fields.get("cvfullvisible") or fields.get("cv_full_visible"))
                if fields.get("cvfullvisible") or fields.get("cv_full_visible")
                else True
            ),
            "cv_full_details": bibtex_text(fields.get("cvdetails") or fields.get("cv_full_venue")),
            "cv_full_highlight": bibtex_text(fields.get("cvfullhighlight") or fields.get("cv_full_highlight")),
            "is_preprint": is_arxiv_preprint(fields),
        }
        records.append(record)
    return records


def latex_escape(value: Any) -> str:
    return "".join(LATEX_ESCAPE_MAP.get(character, character) for character in str(value))


def latex_url(url: str) -> str:
    return url.replace("%", r"\%").replace("#", r"\#").replace("&", r"\&").replace("_", r"\_").replace("~", r"\string~")


def latex_author_text(value: Any) -> str:
    """Render BibTeX authors literally; contribution markers are not Markdown."""
    return latex_escape(value).replace("†", r"\textsuperscript{\ensuremath{\dagger}}").replace("*", r"\textsuperscript{*}")


def safe_href(url: str, label: str) -> str:
    try:
        validate_url(url, "URL", allow_empty=False)
    except ContentValidationError:
        return latex_escape(label)
    return rf"\href{{{latex_url(url)}}}{{{label}}}"


def render_inline_markdown(value: Any) -> str:
    source = str(value or "")
    rendered: list[str] = []
    cursor = 0
    for match in INLINE_MARKDOWN.finditer(source):
        rendered.append(latex_escape(source[cursor : match.start()]))
        if match.group("link"):
            rendered.append(safe_href(match.group("link_url"), render_inline_markdown(match.group("link_text"))))
        elif match.group("bold"):
            rendered.append(rf"\textbf{{{render_inline_markdown(match.group('bold_text'))}}}")
        elif match.group("italic"):
            rendered.append(rf"\textit{{{render_inline_markdown(match.group('italic_text'))}}}")
        else:
            rendered.append(rf"\texttt{{{latex_escape(match.group('code_text'))}}}")
        cursor = match.end()
    rendered.append(latex_escape(source[cursor:]))
    return "".join(rendered)


def render_markdown_blocks(value: str) -> str:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", value.strip()) if block.strip()]
    rendered: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        bullets = [re.match(r"^[-*]\s+(.+)$", line) for line in lines]
        if lines and all(bullets):
            rendered.append(r"\begin{itemize}")
            for match in bullets:
                assert match is not None
                rendered.append(rf"  \item {render_inline_markdown(match.group(1))}")
            rendered.append(r"\end{itemize}")
        else:
            rendered.append(rf"\noindent {render_inline_markdown(' '.join(lines))}\par")
    return "\n".join(rendered)


def pdf_date(value: Any) -> str:
    value = str(value or "").strip()
    if not value:
        return "Present"
    match = re.fullmatch(r"(\d{4})-(\d{2})(?:-\d{2})?", value)
    return f"{match.group(2)}/{match.group(1)}" if match else latex_escape(value)


def json_date(value: Any) -> str:
    value = str(value or "").strip()
    return f"{value}-01" if re.fullmatch(r"\d{4}-\d{2}", value) else value


def date_range(start_date: Any, end_date: Any) -> str:
    start = pdf_date(start_date) if start_date else ""
    end = pdf_date(end_date)
    return f"{start} -- {end}" if start else end


def markdown_link_or_text(label: str, url: str | None) -> str:
    safe_label = render_inline_markdown(label)
    return safe_href(url, safe_label) if url else safe_label


def year_sort_key(value: Any) -> tuple[int, str]:
    rendered = str(value)
    match = re.search(r"\d{4}", rendered)
    return (int(match.group()) if match else -1, rendered)


def render_header(basics: dict[str, Any]) -> str:
    fields: list[str] = []
    email = text(basics.get("email"), "profile.basics.email")
    if email:
        fields.append(rf"\faIcon{{envelope}}\ \cvheaderplainlink{{mailto:{latex_url(email)}}}{{{latex_escape(email)}}}")
    website = text(basics.get("url"), "profile.basics.url")
    if website:
        parsed = urlparse(website)
        label = (parsed.netloc or website).removeprefix("www.")
        fields.append(rf"\faIcon{{globe}}\ \cvheaderlink{{{latex_url(website)}}}{{{latex_escape(label)}}}")
    icon_by_network = {"google scholar": "graduation-cap", "github": "github", "linkedin": "linkedin", "orcid": "id-badge"}
    for profile in optional_list(basics.get("profiles"), "profile.basics.profiles"):
        if not profile.get("url"):
            continue
        network = text(profile["network"], "profile.basics.profiles.network", required=True)
        icon = icon_by_network.get(network.lower(), "link")
        fields.append(rf"\faIcon{{{icon}}}\ \cvheaderlink{{{latex_url(profile['url'])}}}{{{latex_escape(network)}}}")
    header_fields = r" \hspace{0.8em}".join(fields)
    return "\n".join(
        [
            "% Generated by scripts/build_cv_content.py. Do not edit.",
            rf"\name{{{latex_escape(basics['name'])}}}",
            rf"\address{{{{\footnotesize {header_fields}}}}}",
            "",
        ]
    )


def render_bio(config: dict[str, Any]) -> str:
    return "\n".join(
        [
            "% Generated by scripts/build_cv_content.py. Do not edit.",
            rf"\begin{{rSection}}{{{latex_escape(config['title'])}}}",
            latex_escape(text(config["body"], "cv_profile.body", required=True)),
            r"\end{rSection}",
            "",
        ]
    )


def render_cv_inline_markdown(value: Any, *, code_as_quoted_text: bool = False) -> str:
    """Render the legacy CV's inline Markdown with blue underlined links."""
    source = str(value or "")
    rendered: list[str] = []
    cursor = 0
    for match in INLINE_MARKDOWN.finditer(source):
        rendered.append(latex_escape(source[cursor : match.start()]))
        if match.group("link"):
            label = render_cv_inline_markdown(match.group("link_text"))
            try:
                validate_url(match.group("link_url"), "CV link", allow_empty=False)
            except ContentValidationError:
                rendered.append(label)
            else:
                rendered.append(rf"\cvlink{{{latex_url(match.group('link_url'))}}}{{{label}}}")
        elif match.group("bold"):
            rendered.append(rf"\textbf{{{render_cv_inline_markdown(match.group('bold_text'))}}}")
        elif match.group("italic"):
            rendered.append(rf"\textit{{{render_cv_inline_markdown(match.group('italic_text'))}}}")
        else:
            code = latex_escape(match.group("code_text"))
            rendered.append(chr(96) + code + "'" if code_as_quoted_text else code)
        cursor = match.end()
    rendered.append(latex_escape(source[cursor:]))
    return "".join(rendered)


def render_red_markdown(value: Any) -> str:
    """Use bold Markdown only where the legacy CV used its red emphasis macro."""
    source = str(value or "")
    rendered: list[str] = []
    cursor = 0
    for match in re.finditer(r"\*\*([^*\n]+)\*\*", source):
        rendered.append(render_cv_inline_markdown(source[cursor : match.start()]))
        rendered.append(rf"\red{{{render_cv_inline_markdown(match.group(1))}}}")
        cursor = match.end()
    rendered.append(render_cv_inline_markdown(source[cursor:]))
    return "".join(rendered)


def render_employment_markdown(value: Any) -> str:
    """Match the historical bold red emphasis used by the employment section."""
    source = str(value or "")
    rendered: list[str] = []
    cursor = 0
    for match in re.finditer(r"\*\*([^*\n]+)\*\*", source):
        rendered.append(render_cv_inline_markdown(source[cursor : match.start()]))
        rendered.append(rf"\textcolor{{red}}{{\textbf{{{render_cv_inline_markdown(match.group(1))}}}}}")
        cursor = match.end()
    rendered.append(render_cv_inline_markdown(source[cursor:]))
    return "".join(rendered)


def legacy_number_format(value: str) -> str:
    """Preserve the historical TeX spacing for thousands separators."""
    return re.sub(r"(?<=\d),(?=\d{3}\b)", r"{,}", value)


def legacy_publication_text(value: Any) -> str:
    return legacy_number_format(latex_escape(value)).replace(r"\textasciitilde{}", r"\(\sim\)")


def render_legacy_prose(value: Any) -> str:
    """Render the old CV's quote and inline-code conventions."""
    rendered = render_cv_inline_markdown(value, code_as_quoted_text=True)
    rendered = re.sub(
        r'"([^"]*)"',
        lambda match: chr(96) + chr(96) + match.group(1) + "''",
        rendered,
    )
    return legacy_number_format(rendered)


def legacy_venue(value: Any) -> str:
    """Convert an al-folio venue abbreviation to the established CV notation."""
    rendered = latex_escape(value)
    match = re.fullmatch(r"(.+?)\s+(?:19|20)(\d{2})(?:\s+(.+))?", rendered)
    if not match:
        return rendered
    suffix = f" {match.group(3)}" if match.group(3) else ""
    return f"{match.group(1)}'{match.group(2)}{suffix}"


def legacy_metric(value: Any) -> str:
    return legacy_number_format(latex_escape(value)).replace(r"\textasciitilde{}", r"$\sim$")


def legacy_author_name(value: str) -> str:
    """Underline Zhaomin Wu and retain the legacy equal/corresponding markers."""
    name = value.strip()
    markers = ""
    while name and name[-1] in {"*", "†"}:
        marker = name[-1]
        name = name[:-1].rstrip()
        markers = (r"\(^{*}\)" if marker == "*" else r"\(^\dagger\)") + markers
    rendered = latex_escape(name)
    if name in {"Zhaomin Wu", "Z. Wu"}:
        rendered = rf"\underline{{{rendered}}}"
    return rendered + markers


def legacy_authors(publication: dict[str, Any], *, abbreviated: bool) -> str:
    field = "short_author_names" if abbreviated else "author_names"
    return ", ".join(legacy_author_name(name) for name in publication[field] if name)


def render_employment(work: list[dict[str, Any]]) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit.", r"\begin{rSection}{Employment}", r"  {\small"]
    for work_group in work:
        main_job = mapping(work_group["main_job"], "cv.work.main_job")
        subjobs = optional_list(work_group.get("subjobs"), "cv.work.subjobs")
        organization = text(main_job.get("name"), "cv.work.main_job.name", required=True)
        location = text(main_job.get("location"), "cv.work.main_job.location")
        starts = [text(entry.get("start_date"), "cv.work.subjob.start_date") for entry in subjobs if entry.get("start_date")]
        end_dates = [text(entry.get("end_date"), "cv.work.subjob.end_date") for entry in subjobs]
        group_end = "" if any(not value for value in end_dates) else max(end_dates, default="")
        heading = latex_escape(organization)
        if location:
            heading += f", {latex_escape(location)}"
        lines.extend(
            [
                rf"    {{\bf {heading}}} \hfill {{{date_range(min(starts, default=''), group_end)}}}",
                r"    \vspace{-0.5em}",
                r"    \begin{list}{\textbullet}{\setlength{\leftmargin}{1.5em}\setlength{\labelwidth}{0.8em}\setlength{\labelsep}{0.4em}\setlength{\itemsep}{0.4em}\setlength{\parsep}{0pt}\setlength{\topsep}{0pt}\setlength{\partopsep}{0pt}}",
            ]
        )
        for entry in sorted(subjobs, key=lambda item: text(item.get("start_date"), "cv.work.subjob.start_date"), reverse=True):
            body_parts = [text(entry.get("summary"), "cv.work.subjob.summary")]
            body_parts.extend(text(item, "cv.work.highlight") for item in entry.get("highlights", []))
            body = " ".join(part for part in body_parts if part)
            lines.append(
                rf"      \item {{\em {latex_escape(entry['position'])}}} ({date_range(entry.get('start_date'), entry.get('end_date'))}), {render_employment_markdown(body)}"
            )
        lines.append(r"    \end{list}")
    lines.extend([r"  }", r"\end{rSection}", ""])
    return "\n".join(lines)


def render_education(education: list[dict[str, Any]]) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit.", r"\begin{rSection}{Education}"]
    for entry in education:
        institution = latex_escape(entry["institution"])
        location = latex_escape(entry.get("location", ""))
        heading = f"{institution}, {location}" if location else institution
        degree = latex_escape(entry["study_type"])
        area = latex_escape(entry.get("area", ""))
        detail = f"{degree} in {area}" if area else degree
        credential_note = latex_escape(entry.get("credential_note", ""))
        if credential_note:
            detail += f", {credential_note}"
        score = latex_escape(entry.get("score", ""))
        advisor = latex_escape(entry.get("advisor", ""))
        detail_left = detail
        if score and advisor:
            detail_left += rf", \;\textit{{{score}}}"
        if advisor:
            detail_line = detail_left + rf" \hfill {{Advisor: {advisor}}}"
        elif score:
            detail_line = detail_left + rf"\hfill {score}"
        else:
            detail_line = detail_left
        lines.extend(
            [
                rf"{{\bf {heading}}} \hfill {{{date_range(entry.get('start_date'), entry.get('end_date'))}}}\\",
                detail_line,
                "",
            ]
        )
    lines.extend([r"\end{rSection}", ""])
    return "\n".join(lines)


def select_awards(awards: list[dict[str, Any]], config: dict[str, Any], category: str) -> list[dict[str, Any]]:
    include_titles = config.get("include_titles") or []
    by_title = {entry["title"]: entry for entry in awards}
    return [by_title[title] for title in include_titles if title in by_title] if include_titles else [entry for entry in awards if entry.get("category") == category]


def render_awards(config: dict[str, Any], awards: list[dict[str, Any]], category: str) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit.", rf"\begin{{rSection}}{{{latex_escape(config['title'])}}}"]
    selected = select_awards(awards, config, category)
    for index, award in enumerate(selected):
        heading = rf"\noindent \textbf{{{latex_escape(award['title'])}}}"
        if award.get("date"):
            heading += f" ({latex_escape(award['date'])})"
        if award.get("awarder"):
            heading += f", {legacy_metric(award['awarder'])}"
        summary = text(award.get("summary"), "cv.award.summary")
        if category == "grant":
            lines.append(heading + r"\\")
            if summary:
                suffix = r"\par\vspace{0.2em}" if index < len(selected) - 1 else r"\par"
                lines.append(legacy_number_format(render_red_markdown(summary)) + suffix)
        elif category == "earlier_honor":
            line = r"\noindent$\bullet$ " + heading[len(r"\noindent ") :]
            if summary:
                line += f" --- {render_cv_inline_markdown(summary)}"
            lines.append(line + r"\par")
        else:
            lines.append(heading + r".\par")
    lines.extend([r"\end{rSection}", ""])
    return "\n".join(lines)


def legacy_contribution_note(value: Any) -> str:
    rendered = latex_escape(value)
    return rendered.replace("*", r"\(^*\)").replace("†", r"\(^\dagger\)")


def legacy_publication_details(publication: dict[str, Any]) -> str:
    if publication["cv_full_details"]:
        return latex_escape(publication["cv_full_details"])
    fields = publication["fields"]
    venue = bibtex_text(fields.get("booktitle") or fields.get("journal"))
    if not venue:
        return publication["year"]
    prefix = "In " if publication["entry_type"].lower() in {"inproceedings", "incollection", "conference"} else ""
    return f"{prefix}{latex_escape(venue)}, {publication['year']}"


def sorted_publications(publications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(publications, key=lambda item: (-int(item["year"]), item["key"].lower()))


def render_selected_publications(config: dict[str, Any], publications: list[dict[str, Any]]) -> str:
    selected = sorted((item for item in publications if item["cv_selected"]), key=lambda item: (item["cv_order"], -int(item["year"]), item["key"].lower()))
    lines = [
        "% Generated by scripts/build_cv_content.py. Do not edit.",
        rf"\begin{{rSectionTiny}}{{{latex_escape(config['title'])}}}{{{legacy_contribution_note(config.get('supplemental', ''))}}}",
        r"{\small",
    ]
    for publication in selected:
        title = safe_href(publication["url"], latex_escape(publication["title"]))
        line = (
            rf"\noindent {legacy_authors(publication, abbreviated=True)}. "
            rf"{{\bf {title}}}. ({{\bf {legacy_venue(publication['abbr'] or publication['venue'])}}})."
        )
        if publication["highlight"]:
            line += rf" \red{{{legacy_publication_text(publication['highlight'])}}}"
        if publication["summary"]:
            line += rf" \textit{{{legacy_number_format(render_cv_inline_markdown(publication['summary']))}}}"
        lines.extend([line, ""])
    lines.extend(["}", r"\end{rSectionTiny}", ""])
    return "\n".join(lines)


def render_publications(config: dict[str, Any], publications: list[dict[str, Any]], *, preprints: bool) -> str:
    lines = [
        "% Generated by scripts/build_cv_content.py. Do not edit.",
        rf"\begin{{rSectionTiny}}{{{latex_escape(config['title'])}}}{{{legacy_contribution_note(config.get('supplemental', ''))}}}",
    ]
    current_year = ""
    visible = (item for item in publications if item["cv_full_visible"] and item["is_preprint"] == preprints)
    ordered = sorted(visible, key=lambda item: (-int(item["year"]), item["cv_full_order"], item["key"].lower()))
    for publication in ordered:
        if publication["year"] != current_year:
            current_year = publication["year"]
            lines.append(rf"\publicationYear{{{latex_escape(current_year)}}}")
        title = safe_href(publication["url"], latex_escape(publication["title"]))
        line = (
            rf"{{\bf [{legacy_venue(publication['abbr'] or publication['venue'])}]}} "
            rf"{legacy_authors(publication, abbreviated=False)}. {title}. {legacy_publication_details(publication)}."
        )
        if publication["cv_full_highlight"]:
            line += rf" \red{{{legacy_publication_text(publication['cv_full_highlight'])}}}"
        lines.extend([line, ""])
    lines.extend([r"\end{rSectionTiny}", ""])
    return "\n".join(lines)


def ascii_latex_fallback(value: Any) -> str:
    """Keep a PDF build usable when the local TeX install lacks CJK support."""
    source = str(value or "")
    source = re.sub(r"\([^()]*[^\x00-\x7f][^()]*\)", "", source)
    source = re.sub(r"[^\x00-\x7f]+", "", source)
    return re.sub(r"\s{2,}", " ", source).strip()


def render_research_impact(config: dict[str, Any], *, ascii_only: bool = False) -> str:
    lines = [
        "% Generated by scripts/build_cv_content.py. Do not edit.",
        rf"\begin{{rSectionTiny}}{{{latex_escape(config['title'])}}}{{{render_cv_inline_markdown(config.get('supplemental', ''))}}}",
        r"{\small",
    ]
    for group in config.get("groups", []):
        lines.append(rf"\cvSubheading{{{latex_escape(group['title'])}}}")
        items = group.get("items", [])
        if group["title"] == "Publicity and Public Outreach":
            for index, item in enumerate(items):
                description = ascii_latex_fallback(item["description"]) if ascii_only else item.get("description", "")
                prefix = rf"\textbf{{\textit{{{latex_escape(item['name'])}}}}}"
                if item.get("venue"):
                    prefix += f" ({latex_escape(item['venue'])})"
                suffix = r"\par\vspace{0.1em}" if index < len(items) - 1 else ""
                lines.append(rf"\noindent {prefix}. {render_legacy_prose(description)}{suffix}")
                if suffix:
                    lines.append("")
        else:
            lines.append(r"\begin{list}{\textbullet}{\setlength{\leftmargin}{1.2em}\setlength{\labelwidth}{0.7em}\setlength{\labelsep}{0.35em}\setlength{\itemsep}{0.12em}\setlength{\parsep}{0pt}\setlength{\topsep}{0.1em}}")
            for item in items:
                name = latex_escape(item["name"])
                if item.get("url"):
                    name = rf"\cvlink{{{latex_url(item['url'])}}}{{{name}}}"
                prefix = rf"\textbf{{{name}}}"
                if item.get("venue"):
                    prefix += f" ({latex_escape(item['venue'])})"
                description = ascii_latex_fallback(item["description"]) if ascii_only else item.get("description", "")
                suffix = f": {render_legacy_prose(description)}" if description else ""
                lines.append(rf"      \item {prefix}{suffix}")
            lines.append(r"    \end{list}")
    for paragraph in config.get("paragraphs", []):
        lines.append(render_markdown_blocks(ascii_latex_fallback(paragraph) if ascii_only else paragraph))
        lines.append(r"\vspace{0.1em}")
    lines.extend(["}", r"\end{rSectionTiny}", ""])
    return "\n".join(lines)


def human_talk_date(value: Any) -> str:
    rendered = text(value, "talk.date", required=True)
    try:
        parsed = date.fromisoformat(rendered)
    except ValueError:
        return rendered
    return f"{MONTH_NAMES[parsed.strftime('%m')]} {parsed.year}"


def render_talks(talks: dict[str, Any]) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit.", rf"\begin{{rSection}}{{{latex_escape(talks['cv']['title'])}}}"]
    entries = sorted(talks.get("entries", []), key=lambda item: text(item["date"], "talk.date"), reverse=True)
    for item in entries:
        venue = latex_escape(item["venue"])
        if item.get("url"):
            venue = safe_href(item["url"], venue)
        description = rf"{latex_escape(item['type'])} at \textbf{{{venue}}}"
        note = text(item.get("note"), "talk.note")
        if note:
            description += render_cv_inline_markdown(note) if note.startswith(",") else f". {render_cv_inline_markdown(note)}"
        else:
            description += "."
        description += " " + chr(96) + chr(96) + latex_escape(item["title"]) + ".''"
        lines.append(rf"\talkOneLine{{{description}}}{{{latex_escape(human_talk_date(item['date']))}}}")
        lines.append("")
    lines.extend([r"\end{rSection}", ""])
    return "\n".join(lines)


def teaching_sections(teaching: dict[str, Any], mentoring: dict[str, Any]) -> list[dict[str, Any]]:
    sections = [section for section in teaching.get("sections", []) if section.get("entries")]
    if mentoring.get("entries"):
        sections.append(
            {
                "kind": "mentoring",
                "title": mentoring["title"],
                "intro": mentoring.get("intro", ""),
                "entries": mentoring["entries"],
            }
        )
    return sections


def render_teaching(teaching: dict[str, Any], mentoring: dict[str, Any]) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit.", rf"\begin{{rSection}}{{{latex_escape(teaching['cv_section_title'])}}}"]
    course_sections = [section for section in teaching.get("sections", []) if section.get("entries")]
    for section in course_sections:
        lines.extend([rf"\teachingGroup{{{latex_escape(section['title'])}}}", r"\vspace{-0.4em}"])
        courses: list[str] = []
        for item in reversed(section["entries"]):
            course = latex_escape(item["course"])
            code = latex_escape(item.get("code", ""))
            term = latex_escape(item["term"])
            courses.append(f"{course} ({code}, {term})" if code else f"{course} ({term})")
        lines.extend([rf"\noindent {'; '.join(courses)}.", ""])
    groups = mentoring.get("cv_groups", [])
    if groups:
        lines.extend([r"\smallskip", rf"\teachingGroup{{{latex_escape(mentoring.get('cv_title') or mentoring['title'])}}}", ""])
        for group in groups:
            heading = rf"\textbf{{{latex_escape(group['title'])}}} ({latex_escape(group['detail'])})"
            lines.append(
                rf"\mentoredGroupEntry{{{heading}}}{{{latex_escape(group['period'])}}}{{{latex_escape(group['representative'])}}}"
            )
    lines.extend([r"\end{rSection}", ""])
    return "\n".join(lines)


def service_item_text(item: dict[str, Any]) -> str:
    name = item.get("venue") or item.get("title") or ""
    rendered = markdown_link_or_text(str(name), item.get("url"))
    role = text(item.get("role"), "service.role")
    return f"{rendered} ({latex_escape(role)})" if role and role.lower() != "reviewer" else rendered


def render_service(service: dict[str, Any]) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit.", r"\begin{rSection}{Professional Service \& Recognition}"]
    reviews: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"conference": [], "journal": []})
    service_by_id = {group["id"]: group for group in service.get("groups", [])}
    conference_entries = service_by_id.get("conference-reviewers", {}).get("entries", [])
    journal_entries = service_by_id.get("journal-reviewers", {}).get("entries", [])
    recognition_entries = service_by_id.get("recognition", {}).get("entries", [])
    tutorial_group = service_by_id.get("tutorial", {})

    for item in conference_entries:
        reviews[text(item["year"], "service.year")]["conference"].append(latex_escape(item["name"]))
    for item in journal_entries:
        reviews[text(item["year"], "service.year")]["journal"].append(latex_escape(item["name"]))
    for item in recognition_entries:
        lines.append(rf"\noindent\textbf{{{latex_escape(item['name'])}:}} {latex_escape(item.get('role', ''))}\par\vspace{{0.4em}}")
    if reviews:
        lines.append(r"\noindent\textbf{Reviewer for conferences and journals:}\par\vspace{0.15em}")
        years = sorted(reviews, key=year_sort_key, reverse=True)
        for index, year in enumerate(years):
            parts: list[str] = []
            if reviews[year]["conference"]:
                parts.append(rf"\textit{{Conf.}} {', '.join(reviews[year]['conference'])}")
            if reviews[year]["journal"]:
                parts.append(rf"\textit{{Journals}} {', '.join(reviews[year]['journal'])}")
            spacing = r"\vspace{0.15em}" if index == len(years) - 1 else r"\vspace{-0.35em}"
            lines.append(rf"\noindent\textbf{{{latex_escape(year)}:}} {'. '.join(parts)}.\par{spacing}")
    for item in tutorial_group.get("entries", []):
        lines.append(rf"\noindent\textbf{{{latex_escape(tutorial_group['title'])}:}} {latex_escape(item['name'])}.\par")
    lines.extend([r"\end{rSection}", ""])
    return "\n".join(lines)


def slugify(value: Any) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug or "section"


def render_generic_sections(sections: list[dict[str, Any]]) -> str:
    lines = ["% Generated by scripts/build_cv_content.py. Do not edit."]
    identifiers: set[str] = set()
    for section in sections:
        if not section.get("enabled", True):
            continue
        base = str(section.get("id") or slugify(section["title"]))
        identifier = base
        suffix = 2
        while identifier in identifiers:
            identifier = f"{base}-{suffix}"
            suffix += 1
        identifiers.add(identifier)
        lines.extend([f"% CMS section id: {identifier}", rf"\begin{{rSection}}{{{latex_escape(section['title'])}}}", render_markdown_blocks(section["body"]), r"\end{rSection}", ""])
    return "\n".join(lines) + "\n"


def publication_for_web(publication: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": publication["key"],
        "title": publication["title"],
        "authors": publication["authors"],
        "short_authors": publication["short_authors"],
        "year": publication["year"],
        "venue": publication["venue"],
        "details": publication["details"],
        "url": publication["url"],
        "highlight": publication["highlight"],
        "summary": publication["summary"],
        "selected": publication["selected"],
        "cv_selected": publication["cv_selected"],
        "is_preprint": publication["is_preprint"],
    }


def service_groups(service: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    def group_years(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_year: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in entries:
            item = {"name": entry["name"], "role": entry.get("role", ""), "url": entry.get("url", "")}
            by_year[text(entry["year"], "service.year")].append(item)
        return [
            {"year": year, "items": sorted(items, key=lambda item: item["name"].lower())}
            for year, items in sorted(by_year.items(), key=lambda item: year_sort_key(item[0]), reverse=True)
        ]

    for group in service.get("groups", []):
        years = group_years(group.get("entries", []))
        if years:
            groups.append({"title": group["title"], "kind": group["id"], "years": years})
    return groups


def site_view(settings: dict[str, Any]) -> dict[str, Any]:
    venues = {
        item["abbreviation"]: {"url": item.get("url", ""), "color": item.get("color", "")}
        for item in settings["venues"]
    }
    return {
        "seo": settings["seo"],
        "footer_text": settings.get("footer_text", ""),
        "repositories": settings["repositories"],
        "venues": venues,
    }


def build_site_view(profile: dict[str, Any], settings: dict[str, Any], cv_profile: dict[str, Any], cv: dict[str, Any], service: dict[str, Any], teaching: dict[str, Any], mentoring: dict[str, Any], talks: dict[str, Any], publications: list[dict[str, Any]]) -> dict[str, Any]:
    publication_view = [publication_for_web(item) for item in sorted_publications(publications)]
    publication_entries = [item for item in publication_view if not item["is_preprint"]]
    preprint_entries = [item for item in publication_view if item["is_preprint"]]
    selected_publications = [item for item in publication_view if item["cv_selected"]]
    selected_publications.sort(key=lambda item: next(record["cv_order"] for record in publications if record["key"] == item["key"]))
    talk_entries = sorted(
        [{**entry, "date": text(entry["date"], "talk.date")} for entry in talks.get("entries", [])],
        key=lambda entry: entry["date"],
        reverse=True,
    )
    return {
        "profile": profile,
        "site": site_view(settings),
        "service": {"groups": service_groups(service)},
        "teaching": {"sections": teaching_sections(teaching, mentoring)},
        "talks": {"entries": talk_entries},
        "cv": {
            "profile": cv_profile,
            "research_impact": cv["research_impact"],
            "selected_publications": {"title": cv["display"]["selected_publications"]["title"], "entries": selected_publications},
            "publications": {"title": cv["display"]["publications"]["title"], "entries": publication_entries},
            "preprints": {"title": cv["display"]["preprints"]["title"], "entries": preprint_entries},
            "talks": {"title": talks["cv"]["title"], "entries": talk_entries},
            "teaching": {"title": teaching["cv_section_title"], "sections": teaching_sections(teaching, mentoring)},
            "service": {"title": "Professional Service & Recognition", "groups": service_groups(service)},
            "sections": cv.get("sections", []),
        },
    }


def to_json_resume(profile: dict[str, Any], cv: dict[str, Any], publications: list[dict[str, Any]]) -> dict[str, Any]:
    basics = profile["basics"]
    json_basics: dict[str, Any] = {
        "name": basics["name"],
        "position": basics.get("position") or basics.get("label", ""),
        "image": basics.get("image", ""),
        "email": basics.get("email", ""),
        "url": basics.get("url", ""),
    }
    for field in ("summary", "phone", "location"):
        if basics.get(field):
            json_basics[field] = basics[field]
    if basics.get("profiles"):
        json_basics["profiles"] = [
            {"network": item["network"], "url": item.get("url", ""), **({"username": item["username"]} if item.get("username") else {})}
            for item in basics["profiles"]
        ]

    def convert(entries: list[dict[str, Any]], field_map: dict[str, str]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for entry in entries:
            output.append({target: (json_date(entry.get(source, "")) if source in {"start_date", "end_date"} else entry.get(source, "")) for source, target in field_map.items()})
        return output

    def work_for_resume(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for group in groups:
            main_job = mapping(group["main_job"], "cv.work.main_job")
            subjobs = optional_list(group.get("subjobs"), "cv.work.subjobs")
            starts = [text(item.get("start_date"), "cv.work.subjob.start_date") for item in subjobs if item.get("start_date")]
            end_dates = [text(item.get("end_date"), "cv.work.subjob.end_date") for item in subjobs]
            group_end = "" if any(not value for value in end_dates) else max(end_dates, default="")
            output.append(
                {
                    "name": main_job["name"],
                    "location": main_job.get("location", ""),
                    "url": main_job.get("url", ""),
                    "startDate": json_date(min(starts, default="")),
                    "endDate": json_date(group_end),
                    "subjobs": convert(
                        subjobs,
                        {
                            "position": "position",
                            "start_date": "startDate",
                            "end_date": "endDate",
                            "summary": "summary",
                            "highlights": "highlights",
                        },
                    ),
                }
            )
        return output

    def publication_for_resume(publication: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": publication["title"],
            "publisher": publication["venue"],
            "releaseDate": f"{publication['year']}-01-01",
            "url": publication["url"],
            "summary": ". ".join(part for part in (publication["authors"], publication["details"], publication["highlight"]) if part),
        }

    ordered_publications = sorted_publications(publications)
    return {
        "basics": json_basics,
        "work": work_for_resume(cv.get("work", [])),
        "education": convert(cv.get("education", []), {"institution": "institution", "location": "location", "url": "url", "area": "area", "study_type": "studyType", "start_date": "startDate", "end_date": "endDate", "score": "score", "advisor": "advisor", "credential_note": "credentialNote", "courses": "courses"}),
        "awards": convert(cv.get("awards", []), {"title": "title", "date": "date", "awarder": "awarder", "url": "url", "summary": "summary", "category": "category"}),
        "skills": [{"name": item["name"], "keywords": item.get("keywords", []), "level": item.get("level", ""), "icon": item.get("icon", "")} for item in cv.get("skills", [])],
        "languages": [{"language": item["language"], "fluency": item.get("fluency", ""), "icon": item.get("icon", "")} for item in cv.get("languages", [])],
        "volunteer": convert(cv.get("volunteer", []), {"organization": "organization", "location": "location", "url": "url", "position": "position", "start_date": "startDate", "end_date": "endDate", "summary": "summary", "highlights": "highlights"}),
        "publications": [publication_for_resume(item) for item in ordered_publications if not item["is_preprint"]],
        "preprints": [publication_for_resume(item) for item in ordered_publications if item["is_preprint"]],
    }


def generated_latex(profile: dict[str, Any], cv_profile: dict[str, Any], cv: dict[str, Any], service: dict[str, Any], teaching: dict[str, Any], mentoring: dict[str, Any], talks: dict[str, Any], publications: list[dict[str, Any]]) -> dict[str, str]:
    display = cv["display"]
    awards = cv.get("awards", [])
    return {
        "header.tex": render_header(profile["basics"]),
        "bio.tex": render_bio(cv_profile),
        "employment.tex": render_employment(cv.get("work", [])),
        "education.tex": render_education(cv.get("education", [])),
        "grants.tex": render_awards(display["grants"], awards, "grant"),
        "honors.tex": render_awards(display["honors"], awards, "honor"),
        "selected_publications.tex": render_selected_publications(display["selected_publications"], publications),
        "research_impact.tex": render_research_impact(cv["research_impact"], ascii_only=True),
        "research_impact_cjk.tex": render_research_impact(cv["research_impact"]),
        "talks.tex": render_talks(talks),
        "teaching.tex": render_teaching(teaching, mentoring),
        "publications.tex": render_publications(display["publications"], publications, preprints=False),
        "preprints.tex": render_publications(display["preprints"], publications, preprints=True),
        "undergraduate_honors.tex": render_awards(display["undergraduate_honors"], awards, "earlier_honor"),
        "service.tex": render_service(service),
        "sections.tex": render_generic_sections(cv.get("sections", [])),
    }


def merged_bibliography(publications: list[dict[str, Any]]) -> str:
    return "---\n---\n\n" + "\n".join(item["source"].rstrip() for item in publications) + "\n"


def write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, prefix=f".{path.name}.", delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)
    return True


def build(profile: dict[str, Any], settings: dict[str, Any], cv_profile: dict[str, Any], cv: dict[str, Any], service: dict[str, Any], teaching: dict[str, Any], mentoring: dict[str, Any], talks: dict[str, Any], publications: list[dict[str, Any]]) -> list[Path]:
    changed: list[Path] = []
    outputs = {
        RESUME_JSON_OUTPUT: json.dumps(to_json_resume(profile, cv, publications), indent=2, ensure_ascii=False) + "\n",
        SITE_VIEW_OUTPUT: yaml.dump(
            build_site_view(profile, settings, cv_profile, cv, service, teaching, mentoring, talks, publications),
            Dumper=NoAliasSafeDumper,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        ),
        MERGED_BIBLIOGRAPHY_OUTPUT: merged_bibliography(publications),
        PUBLICATIONS_BIBLIOGRAPHY_OUTPUT: merged_bibliography([item for item in publications if not item["is_preprint"]]),
        PREPRINTS_BIBLIOGRAPHY_OUTPUT: merged_bibliography([item for item in publications if item["is_preprint"]]),
    }
    for path, content in outputs.items():
        if write_if_changed(path, content):
            changed.append(path)
    for filename, content in generated_latex(profile, cv_profile, cv, service, teaching, mentoring, talks, publications).items():
        output = LATEX_OUTPUT_DIRECTORY / filename
        if write_if_changed(output, content):
            changed.append(output)
    return changed


def load_cv_content() -> tuple[dict[str, Any], dict[str, Any]]:
    cv_profile = validate_cv_profile(load_yaml(CV_PROFILE_SOURCE))
    documents = {
        "work": validate_work_document(load_yaml(CV_WORK_SOURCE)),
        "education": validate_schema_document(load_yaml(CV_EDUCATION_SOURCE), "cv.education"),
        "awards": validate_schema_document(load_yaml(CV_AWARDS_SOURCE), "cv.awards"),
        "skills": validate_schema_document(load_yaml(CV_SKILLS_SOURCE), "cv.skills"),
        "languages": validate_schema_document(load_yaml(CV_LANGUAGES_SOURCE), "cv.languages"),
        "volunteer": validate_schema_document(load_yaml(CV_VOLUNTEER_SOURCE), "cv.volunteer"),
        "publication_display": validate_schema_document(load_yaml(CV_PUBLICATION_DISPLAY_SOURCE), "cv.publication_display"),
        "research_impact": validate_schema_document(load_yaml(CV_RESEARCH_IMPACT_SOURCE), "cv.research_impact"),
        "sections": validate_schema_document(load_yaml(CV_SECTIONS_SOURCE), "cv.sections"),
    }
    award_display = mapping(documents["awards"].get("display"), "cv.awards.display")
    publication_display = mapping(documents["publication_display"].get("display"), "cv.publication_display.display")
    cv = {
        "schema_version": 1,
        "work": optional_list(documents["work"].get("entries"), "cv.work.entries"),
        "education": optional_list(documents["education"].get("entries"), "cv.education.entries"),
        "awards": optional_list(documents["awards"].get("entries"), "cv.awards.entries"),
        "skills": optional_list(documents["skills"].get("entries"), "cv.skills.entries"),
        "languages": optional_list(documents["languages"].get("entries"), "cv.languages.entries"),
        "volunteer": optional_list(documents["volunteer"].get("entries"), "cv.volunteer.entries"),
        "display": {
            "grants": award_display.get("grants"),
            "honors": award_display.get("honors"),
            "undergraduate_honors": award_display.get("undergraduate_honors"),
            "selected_publications": publication_display.get("selected_publications"),
            "publications": publication_display.get("publications"),
            "preprints": publication_display.get("preprints"),
        },
        "research_impact": documents["research_impact"],
        "sections": optional_list(documents["sections"].get("entries"), "cv.sections.entries"),
    }
    return cv_profile, validate_cv(cv)


def load_and_validate() -> tuple[Any, ...]:
    cv_profile, cv = load_cv_content()
    return (
        validate_profile(load_yaml(PROFILE_SOURCE)),
        validate_site(load_yaml(SITE_SOURCE)),
        cv_profile,
        cv,
        load_service(),
        validate_teaching(load_yaml(TEACHING_SOURCE)),
        validate_mentoring(load_yaml(MENTORING_SOURCE)),
        validate_talks(load_yaml(TALKS_SOURCE)),
        load_publications(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "build"), help="validate content or write derived files")
    arguments = parser.parse_args()
    try:
        content = load_and_validate()
        if arguments.command == "validate":
            print("Content is valid.")
            return 0
        changed = build(*content)
    except ContentValidationError as error:
        print(f"Content validation failed: {error}", file=sys.stderr)
        return 1
    if changed:
        print("Generated:")
        for path in changed:
            print(f"  {path.relative_to(REPOSITORY_ROOT)}")
    else:
        print("Generated content is already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
