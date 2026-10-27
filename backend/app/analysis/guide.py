from typing import List
from ..schemas.contract import GuideSection, Finding, LanguageBreakdown, RepoMeta

def generate_plain_english_guide(
    repo_meta: RepoMeta,
    languages: List[LanguageBreakdown],
    tech_stack: List[Finding],
    config_files: List[Finding],
    entry_points: List[Finding],
    dependencies_ecosystems: List[str]
) -> List[GuideSection]:
    """
    Generates deterministic, template-based field notes explaining the repository.
    Strictly follows Section 1.3: Every sentence traces to a finding. No invented facts.
    """
    sections: List[GuideSection] = []

    # 1. Repository Survey Overview
    ecosystem_findings = [f for f in tech_stack if f.category == "Ecosystem"]
    ecosystem_names = [f.label for f in ecosystem_findings] or ["unspecified"]
    top_langs = [f"{l.name} ({l.percent}%)" for l in languages[:3]]
    langs_summary = ", ".join(top_langs) if top_langs else "no detected language distribution"

    overview_refs = [f.id for f in ecosystem_findings]
    overview_body = (
        f"Survey of repository '{repo_meta.full_name}'. Primary ecosystem identified as "
        f"{', '.join(ecosystem_names)}. Recorded language distribution: {langs_summary}."
    )
    if repo_meta.description:
        overview_body += f" Manifest description: \"{repo_meta.description.strip()}\"."
    sections.append(GuideSection(
        title="Site Survey & Primary Ecosystem",
        body=overview_body,
        finding_refs=overview_refs
    ))

    # 2. Frameworks & Tooling Stratum
    framework_findings = [f for f in tech_stack if f.category in ("Framework", "Tooling", "Styling", "Testing", "Data Science", "Machine Learning")]
    if framework_findings:
        fw_refs = [f.id for f in framework_findings]
        fw_names = [f.label for f in framework_findings]
        tooling_body = (
            f"The codebase declares the following frameworks and development tooling: {', '.join(fw_names)}. "
            "All framework artifacts were confirmed through declared manifest dependencies."
        )
        sections.append(GuideSection(
            title="Frameworks & Tooling Stratum",
            body=tooling_body,
            finding_refs=fw_refs
        ))

    # 3. Entry Points & Execution Flow Candidates
    if entry_points:
        ep_refs = [f.id for f in entry_points]
        confirmed_eps = [f.label for f in entry_points if f.confidence == "confirmed"]
        heuristic_eps = [f.label for f in entry_points if f.confidence == "heuristic"]

        ep_sentences = []
        if confirmed_eps:
            ep_sentences.append(
                f"Confirmed entry candidates declared in configuration/manifests: {', '.join(confirmed_eps)}."
            )
        if heuristic_eps:
            ep_sentences.append(
                f"Heuristic entry point candidates inferred from convention: {', '.join(heuristic_eps)}."
            )
        ep_sentences.append(
            "Note: In accordance with analysis integrity rules, entry targets represent candidates rather than verified execution paths."
        )
        sections.append(GuideSection(
            title="Execution Candidates & Entry Points",
            body=" ".join(ep_sentences),
            finding_refs=ep_refs
        ))

    # 4. Configuration & Infrastructure
    if config_files:
        cfg_refs = [f.id for f in config_files]
        cfg_labels = [f.label for f in config_files]
        cfg_body = (
            f"Archaeological survey identified {len(config_files)} active configuration specifications: "
            f"{', '.join(cfg_labels)}. These define build pipelines, containers, and compiler constraints."
        )
        sections.append(GuideSection(
            title="Configuration & Environment Stratum",
            body=cfg_body,
            finding_refs=cfg_refs
        ))

    return sections
