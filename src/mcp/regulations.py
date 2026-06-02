"""
GovAgent — Regulatory Clause Corpus
=====================================
Hardcoded corpus of key EU AI Act and GDPR regulation clauses.
Each clause is a dict with id, regulation, article, title, and text.

This is used to build the FAISS vector store for semantic retrieval.
"""

from __future__ import annotations

REGULATION_CLAUSES: list[dict[str, str]] = [
    # =====================================================================
    # EU AI ACT
    # =====================================================================
    {
        "id": "eu-ai-act-art5",
        "regulation": "EU AI Act",
        "article": "Article 5",
        "title": "Prohibited Artificial Intelligence Practices",
        "text": (
            "The following AI practices shall be prohibited: (a) AI systems that deploy "
            "subliminal techniques beyond a person's consciousness to materially distort "
            "behaviour causing physical or psychological harm; (b) AI systems that exploit "
            "vulnerabilities of specific groups (age, disability) to distort behaviour; "
            "(c) AI systems for social scoring by public authorities leading to detrimental "
            "treatment; (d) Real-time remote biometric identification systems in publicly "
            "accessible spaces for law enforcement, subject to exceptions."
        ),
    },
    {
        "id": "eu-ai-act-art6",
        "regulation": "EU AI Act",
        "article": "Article 6",
        "title": "Classification Rules for High-Risk AI Systems",
        "text": (
            "An AI system is considered high-risk if: (a) it is intended to be used as a "
            "safety component of a product covered by Union harmonisation legislation, or "
            "is itself such a product; (b) the product or AI system is required to undergo "
            "a third-party conformity assessment. AI systems in Annex III areas (biometric "
            "identification, critical infrastructure, education, employment, essential "
            "services, law enforcement, migration, justice) are also high-risk."
        ),
    },
    {
        "id": "eu-ai-act-art9",
        "regulation": "EU AI Act",
        "article": "Article 9",
        "title": "Risk Management System",
        "text": (
            "A risk management system shall be established, implemented, documented, and "
            "maintained for high-risk AI systems. It shall consist of a continuous iterative "
            "process running throughout the entire lifecycle. It shall comprise: identification "
            "and analysis of known and foreseeable risks; estimation and evaluation of risks "
            "that may emerge; adoption of appropriate risk management measures; and testing "
            "to ensure the system performs consistently for its intended purpose."
        ),
    },
    {
        "id": "eu-ai-act-art10",
        "regulation": "EU AI Act",
        "article": "Article 10",
        "title": "Data and Data Governance",
        "text": (
            "High-risk AI systems using data-driven training shall be developed on the "
            "basis of training, validation, and testing datasets that meet quality criteria. "
            "Data governance shall include: examination of data for possible biases; "
            "identification of data gaps or shortcomings; appropriate measures to address "
            "those; relevant representation of persons in datasets; and ensuring data is "
            "relevant, representative, free of errors, and complete."
        ),
    },
    {
        "id": "eu-ai-act-art13",
        "regulation": "EU AI Act",
        "article": "Article 13",
        "title": "Transparency and Provision of Information to Users",
        "text": (
            "High-risk AI systems shall be designed and developed to ensure that their "
            "operation is sufficiently transparent to enable users to interpret the system's "
            "output and use it appropriately. Instructions for use shall include: identity "
            "and contact details of the provider; characteristics and limitations of the "
            "system; its intended purpose; level of accuracy, robustness, and cybersecurity; "
            "any known circumstance that may lead to risks; and human oversight measures."
        ),
    },
    {
        "id": "eu-ai-act-art14",
        "regulation": "EU AI Act",
        "article": "Article 14",
        "title": "Human Oversight",
        "text": (
            "High-risk AI systems shall be designed and developed to be effectively overseen "
            "by natural persons during the period of use. Human oversight shall aim to prevent "
            "or minimise risks to health, safety, or fundamental rights. Oversight measures "
            "shall enable the individual overseeing the system to: fully understand its "
            "capacities and limitations; monitor operation for anomalies; be able to decide "
            "not to use the system or to disregard, override, or reverse its output; and "
            "intervene in or interrupt the operation of the system."
        ),
    },
    {
        "id": "eu-ai-act-art15",
        "regulation": "EU AI Act",
        "article": "Article 15",
        "title": "Accuracy, Robustness, and Cybersecurity",
        "text": (
            "High-risk AI systems shall be designed and developed to achieve an appropriate "
            "level of accuracy, robustness, and cybersecurity, and perform consistently in "
            "those respects throughout their lifecycle. The levels of accuracy and relevant "
            "accuracy metrics shall be declared in the instructions of use. High-risk AI "
            "systems shall be resilient against errors, faults, or inconsistencies, and "
            "against attempts by unauthorised third parties to alter their use or performance "
            "by exploiting system vulnerabilities (adversarial attacks)."
        ),
    },
    {
        "id": "eu-ai-act-art52",
        "regulation": "EU AI Act",
        "article": "Article 52",
        "title": "Transparency Obligations for Certain AI Systems",
        "text": (
            "Providers shall ensure that AI systems intended to interact with natural persons "
            "are designed and developed so that natural persons are informed that they are "
            "interacting with an AI system, unless obvious from the circumstances. AI systems "
            "generating synthetic audio, image, video, or text content shall disclose that "
            "the content has been artificially generated or manipulated. This applies to "
            "deep fakes and AI-generated text published to inform the public on matters of "
            "public interest."
        ),
    },
    {
        "id": "eu-ai-act-art71",
        "regulation": "EU AI Act",
        "article": "Article 71",
        "title": "Penalties",
        "text": (
            "Member States shall lay down rules on penalties applicable to infringements. "
            "For prohibited AI practices (Art. 5): fines up to EUR 35 million or 7% of "
            "total worldwide annual turnover. For non-compliance with high-risk requirements: "
            "fines up to EUR 15 million or 3% of turnover. For supplying incorrect, "
            "incomplete, or misleading information: fines up to EUR 7.5 million or 1% "
            "of turnover."
        ),
    },
    {
        "id": "eu-ai-act-art-annex3",
        "regulation": "EU AI Act",
        "article": "Annex III",
        "title": "High-Risk AI Systems (Specific Areas)",
        "text": (
            "The following areas contain high-risk AI systems: (1) Biometric identification "
            "and categorisation of natural persons; (2) Management and operation of critical "
            "infrastructure (road traffic, water, gas, heating, electricity); (3) Education "
            "and vocational training (determining access, assigning students); (4) Employment, "
            "worker management, and access to self-employment (recruitment, screening, "
            "evaluation); (5) Access to essential private and public services (credit scoring, "
            "insurance, emergency services); (6) Law enforcement (risk assessment, polygraphs, "
            "profiling); (7) Migration, asylum, and border control; (8) Administration of "
            "justice and democratic processes."
        ),
    },

    # =====================================================================
    # GDPR
    # =====================================================================
    {
        "id": "gdpr-art5",
        "regulation": "GDPR",
        "article": "Article 5",
        "title": "Principles Relating to Processing of Personal Data",
        "text": (
            "Personal data shall be: (a) processed lawfully, fairly, and in a transparent "
            "manner (lawfulness, fairness, transparency); (b) collected for specified, "
            "explicit, and legitimate purposes and not further processed incompatibly "
            "(purpose limitation); (c) adequate, relevant, and limited to what is necessary "
            "(data minimisation); (d) accurate and kept up to date (accuracy); (e) kept in "
            "a form permitting identification for no longer than necessary (storage limitation); "
            "(f) processed with appropriate security (integrity and confidentiality)."
        ),
    },
    {
        "id": "gdpr-art6",
        "regulation": "GDPR",
        "article": "Article 6",
        "title": "Lawfulness of Processing",
        "text": (
            "Processing shall be lawful only if: (a) the data subject has given consent; "
            "(b) processing is necessary for performance of a contract; (c) compliance with "
            "a legal obligation; (d) protection of vital interests; (e) performance of a "
            "task in the public interest; or (f) legitimate interests pursued by the "
            "controller, except where overridden by the data subject's interests or rights. "
            "Consent must be freely given, specific, informed, and unambiguous."
        ),
    },
    {
        "id": "gdpr-art13",
        "regulation": "GDPR",
        "article": "Article 13",
        "title": "Information to be Provided Where Data is Collected from the Data Subject",
        "text": (
            "The controller shall provide the data subject with: identity and contact details "
            "of the controller; contact details of the DPO; purposes and legal basis for "
            "processing; legitimate interests pursued; recipients of personal data; "
            "information on transfers to third countries; period of storage; right to access, "
            "rectification, erasure, restriction, portability, and objection; right to "
            "withdraw consent; right to lodge a complaint; whether provision of data is "
            "statutory or contractual requirement; existence of automated decision-making "
            "including profiling."
        ),
    },
    {
        "id": "gdpr-art14",
        "regulation": "GDPR",
        "article": "Article 14",
        "title": "Information Where Data Has Not Been Obtained from the Data Subject",
        "text": (
            "Where personal data has not been obtained from the data subject, the controller "
            "shall provide the data subject with: categories of data concerned; identity of "
            "the controller; purposes and legal basis; recipients; transfers to third countries; "
            "period of storage; legitimate interests; right to access, rectification, and "
            "erasure; right to lodge a complaint; the source of the data; existence of "
            "automated decision-making. This information shall be provided within a "
            "reasonable period but at the latest within one month."
        ),
    },
    {
        "id": "gdpr-art17",
        "regulation": "GDPR",
        "article": "Article 17",
        "title": "Right to Erasure ('Right to be Forgotten')",
        "text": (
            "The data subject shall have the right to obtain from the controller the erasure "
            "of personal data without undue delay where: the data is no longer necessary; "
            "consent is withdrawn; the data subject objects to processing; the data has been "
            "unlawfully processed; erasure is required by law; or the data was collected in "
            "relation to offering information society services to a child. The controller "
            "shall take reasonable steps to inform other controllers processing the data."
        ),
    },
    {
        "id": "gdpr-art22",
        "regulation": "GDPR",
        "article": "Article 22",
        "title": "Automated Individual Decision-Making, Including Profiling",
        "text": (
            "The data subject shall have the right not to be subject to a decision based "
            "solely on automated processing, including profiling, which produces legal effects "
            "or similarly significantly affects them. This does not apply if the decision is: "
            "necessary for entering or performing a contract; authorised by Union or Member "
            "State law; or based on the data subject's explicit consent. In those cases, the "
            "controller shall implement suitable measures to safeguard the data subject's "
            "rights and freedoms, at least the right to obtain human intervention, to express "
            "their point of view, and to contest the decision."
        ),
    },
    {
        "id": "gdpr-art25",
        "regulation": "GDPR",
        "article": "Article 25",
        "title": "Data Protection by Design and by Default",
        "text": (
            "The controller shall implement appropriate technical and organisational measures "
            "designed to implement data-protection principles (such as data minimisation) "
            "effectively, both at the time of determining the means for processing and at the "
            "time of the processing itself. The controller shall implement measures for "
            "ensuring that, by default, only personal data which are necessary for each "
            "specific purpose of the processing are processed. This applies to the amount "
            "of data collected, the extent of processing, the period of storage, and "
            "accessibility."
        ),
    },
    {
        "id": "gdpr-art32",
        "regulation": "GDPR",
        "article": "Article 32",
        "title": "Security of Processing",
        "text": (
            "The controller and processor shall implement appropriate technical and "
            "organisational measures to ensure a level of security appropriate to the risk, "
            "including: pseudonymisation and encryption of personal data; ability to ensure "
            "ongoing confidentiality, integrity, availability, and resilience of processing "
            "systems; ability to restore availability and access to data in a timely manner; "
            "and a process for regularly testing, assessing, and evaluating the effectiveness "
            "of security measures."
        ),
    },
    {
        "id": "gdpr-art35",
        "regulation": "GDPR",
        "article": "Article 35",
        "title": "Data Protection Impact Assessment",
        "text": (
            "Where processing is likely to result in a high risk to the rights and freedoms "
            "of natural persons, the controller shall carry out a data protection impact "
            "assessment (DPIA) prior to the processing. A DPIA is required when: using new "
            "technologies; systematically and extensively evaluating personal aspects "
            "(profiling); processing special categories of data on a large scale; or "
            "systematically monitoring a publicly accessible area on a large scale. The DPIA "
            "shall contain: a systematic description of processing operations and purposes; "
            "an assessment of necessity and proportionality; an assessment of risks to rights "
            "and freedoms; and measures to address those risks."
        ),
    },
    {
        "id": "gdpr-art83",
        "regulation": "GDPR",
        "article": "Article 83",
        "title": "General Conditions for Imposing Administrative Fines",
        "text": (
            "Infringements of the basic principles for processing (Art. 5, 6, 7, 9) and "
            "data subjects' rights (Art. 12-22) shall be subject to fines up to EUR 20 million "
            "or 4% of total worldwide annual turnover, whichever is higher. Infringements of "
            "obligations of the controller and processor (Art. 8, 11, 25-39, 42, 43) shall be "
            "subject to fines up to EUR 10 million or 2% of turnover. Supervisory authorities "
            "shall ensure that fines are effective, proportionate, and dissuasive."
        ),
    },
    {
        "id": "gdpr-art37",
        "regulation": "GDPR",
        "article": "Article 37",
        "title": "Designation of the Data Protection Officer",
        "text": (
            "The controller and processor shall designate a data protection officer (DPO) "
            "where: the processing is carried out by a public authority or body; the core "
            "activities consist of processing operations requiring regular and systematic "
            "monitoring of data subjects on a large scale; or the core activities consist "
            "of processing on a large scale of special categories of data. The DPO shall "
            "be designated on the basis of professional qualities, expert knowledge of data "
            "protection law and practices, and the ability to fulfil their tasks."
        ),
    },
]
