# Glossary

Medical device regulation and software engineering each have their own jargon. Threadline sits between them, so
here are both. Terms in **bold** inside a definition have their own entry.

| Term | Meaning |
|---|---|
| **Approval** | A record that a named person approved a specific revision of a **document** or **baseline**, with a stated meaning. In Threadline it's an item committed in an SSH-signed commit. |
| **Approved Body** | A UK organisation designated to assess medical device conformity (the UK counterpart of an EU Notified Body). |
| **AU Model Law** | The African Union Model Law on Medical Products Regulation (2016), which member states adapt into national law. |
| **Baseline** | A frozen snapshot of the **design file** for one release, identified by a hash. Its `released` approval is the release decision. |
| **Benefit-risk** | The justification for accepting a **residual risk** that is not acceptable on its own, because the medical benefit outweighs it (ISO 14971 7.4). |
| **CAPA** | Corrective and preventive action: the process for finding and fixing the root cause of a problem (ISO 13485 8.5). |
| **Clause** | A numbered section of a standard or regulation, such as ISO 14971 7.2. Every Threadline rule cites the clauses it enforces. |
| **CycloneDX** | A standard format for an **SBOM**. Threadline reads CycloneDX JSON. |
| **DCB0129** | NHS England's clinical risk management standard for manufacturers of health IT. Threadline exports a hazard log in its structure. |
| **Design file / DHF** | Design history file: the records showing how the device was designed and verified. In Threadline, the items under `dhf/`. |
| **Digital thread** | The unbroken chain of links from **user need** to requirement, risk control, passing test and signed release. |
| **Effective** | The status of an item or document that is approved and in force. |
| **Essential requirements / principles** | The safety and performance requirements a device must meet to be placed on a market (UK MDR 2002 Annex I; WHO and AU Model Law equivalents). |
| **Hazard** | A potential source of harm (ISO 14971). Threadline records the chain: hazard → sequence of events → **hazardous situation** → harm. |
| **Hazardous situation** | A circumstance in which people are exposed to a hazard. |
| **IEC 62304** | The international standard for medical device software lifecycle processes. Edition 1 uses **software safety classes** A, B, C; the draft Edition 2 uses **PRL** I and II. |
| **IEC 62366-1** | The standard for usability engineering of medical devices. |
| **IEC 81001-5-1** | The standard for security activities in the health software lifecycle. |
| **IMCI** | Integrated Management of Childhood Illness, the WHO guideline the fictional example device implements. |
| **ISO 13485** | The quality management system standard for medical devices. |
| **ISO 14971** | The risk management standard for medical devices. |
| **Item** | One record in Threadline: one YAML file whose name is its ID. |
| **JUnit XML** | A test result format almost every test framework can write. Threadline reads the `verifies` property from it. |
| **MHRA** | Medicines and Healthcare products Regulatory Agency, the UK regulator. |
| **OSV** | OSV.dev, an open database of security advisories, queried by `--osv`. |
| **P1, P2** | ISO 14971's split of probability of harm: P1 is the chance the **hazardous situation** occurs; P2 the chance it leads to harm. |
| **Part 11** | US 21 CFR Part 11, the FDA rule on electronic records and signatures. Not required in Threadline's markets; used as a design benchmark. |
| **PCCP** | Predetermined change control plan: an agreed plan for how an ML model may change after release. |
| **PRL** | Process rigour level, the draft IEC 62304 Edition 2 replacement for software safety classes. |
| **Residual risk** | The risk left after **risk controls** are applied. |
| **Risk control** | A measure that reduces risk: by design, by a protective measure, or by information for safety. |
| **RTM** | Requirements traceability matrix: the table linking requirements to their sources and tests. `threadline rtm` prints it. |
| **SaMD** | Software as a Medical Device: software that is itself a medical device, not part of hardware. |
| **SBOM** | Software bill of materials: a list of every third-party component in the software. |
| **SOP** | Standard operating procedure: a controlled document describing how a process is done. |
| **Software safety class** | IEC 62304 Edition 1's A (no injury possible), B (non-serious injury) or C (death or serious injury). It decides which activities are required. |
| **SOUP** | Software of unknown provenance: third-party software not developed under your medical device process (IEC 62304). |
| **Summative evaluation** | The final usability test showing the user interface can be used safely (IEC 62366-1). Formative evaluations come earlier, to shape the design. |
| **Technical file** | The documentation a manufacturer keeps to show a device meets its requirements. `threadline build` produces it as a PDF. |
| **Trust root** | The commit whose signer registry Threadline trusts without checking; everything after it is verified. Set by an admin as `THREADLINE_TRUST_ROOT`. |
| **UK MDR 2002** | The Medical Devices Regulations 2002, the UK's device law. |
| **User need** | What a user needs the device to do, in their terms. The start of the thread. |
| **WHO GMRF** | The WHO Global Model Regulatory Framework for medical devices, which African harmonisation builds on. |
