# RYPE — Explainable Operational Risk Intelligence

> From risk scoring to explainable, intervention-oriented decision support.

**RYPE — Risk Yield Propagation Engine** is a research prototype for explainable geopolitical and operational supply-chain risk intelligence.

Rather than treating supply-chain risk as a single prediction score, RYPE investigates how externally grounded risk signals can enter an operational system, propagate across interconnected decision nodes, and change under alternative interventions.

The prototype integrates geopolitical risk grounding, mechanism-driven D1–D4 risk propagation, explainable risk decomposition, counterfactual scenario analysis, resilience evaluation, and human-in-the-loop decision support within a unified research interface.

---

## Research Motivation

A high risk score alone does not answer the questions a decision-maker actually faces:

- Where does the risk originate?
- How does it propagate through the operational chain?
- Which node concentrates the exposure?
- What changes under an alternative route or intervention?
- Can a human decision improve the system state?
- Is the model explaining operational mechanisms or merely reproducing information already embedded in the data?

RYPE was developed around these questions.

The research process also includes a methodological investigation of data leakage and apparently near-perfect predictive performance. Instead of accepting unusually strong model results at face value, the project examines whether target-related information is structurally embedded in the feature space and distinguishes predictive performance from genuine operational realism.

This methodological inquiry forms an important part of the project's research context.

---

## System Architecture

RYPE represents operational risk through four mechanism-oriented propagation nodes:

| Node | Operational interpretation |
|---|---|
| **D1 — Supplier** | Supplier and upstream operational exposure |
| **D2 — Port** | Port, customs, handling, and logistics-process exposure |
| **D3 — Route** | Transportation and route-level propagation |
| **D4 — Last-mile** | Downstream delivery and final operational exposure |

External geopolitical pressure is grounded using country-level risk indicators and connected to operational states through a route-level risk inference layer.

The system then evaluates how risk propagates across D1 → D2 → D3 → D4.

---

## External Risk Grounding

The current research layer incorporates signals derived from:

- ACLED political violence and conflict indicators
- World Bank Worldwide Governance Indicators
- Sanctions and trade-restriction risk variables
- UN/LOCODE port and location entities
- Logistics, delivery, and e-commerce operational datasets

These signals are used to construct an externally grounded geopolitical risk layer.

The current MVP contains:

- **17,517 country-month geopolitical risk observations**
- **17,597 UN/LOCODE-based port and location entities**
- Country-level temporal risk signals extending from **1996 to 2026**
- A port-to-country bridge for route-level risk grounding

The existence of an external geopolitical signal does not automatically imply operational realism. RYPE explicitly treats this distinction as a methodological concern:

> **External Risk Realism ≠ Operational Realism**

---

## Core Research Components

### 1. Geopolitical Risk Grounding

Conflict, governance fragility, sanctions, and trade-restriction signals are integrated into an external geopolitical pressure layer.

### 2. Mechanism-Driven D1–D4 Risk Propagation

Risk is represented as a sequential operational mechanism rather than a single isolated score.

The interface exposes supplier, port, route, and last-mile risk states to show where exposure accumulates across the chain.

### 3. Explainable Risk Decomposition

RYPE decomposes the active route-risk structure into interpretable contributors.

The objective is not only to identify a high-risk route, but to expose the factors and propagation states associated with the resulting risk estimate.

### 4. Counterfactual Intervention Analysis

Alternative origin nodes can be compared against the active route.

The system quantifies changes in:

- geopolitical pressure
- D1–D4 propagation states
- edge risk
- propagation-adjusted success probability

This allows RYPE to answer a decision-oriented question:

> **What changes if the operational decision changes?**

### 5. Scenario Stress Laboratory

Precomputed research scenarios evaluate the sensitivity of the propagation structure under:

- geopolitical escalation
- cyber escalation
- supplier financial stress
- port congestion shock
- last-mile disruption
- compound crisis conditions

Risk amplification and success-probability deterioration are treated as related but distinct response dimensions.

### 6. Temporal Propagation and Resilience

RYPE visualizes how instability propagates across operational nodes over sequential steps.

A separate resilience trajectory evaluates whether staged intervention reduces downstream exposure and improves the propagation-adjusted probability of operational success.

### 7. Human-in-the-Loop Decision Support

RYPE includes a Human-in-the-Loop decision layer for comparing expert intervention scenarios.

Human overrides are not assumed to improve the system automatically.

Instead, interventions are compared against a baseline using changes in chain risk and success probability.

This supports an auditable decision-support perspective:

> **Human intervention is evaluated, not automatically trusted.**

---

## Decision Intelligence Interface

The Streamlit MVP translates the research architecture into an interactive decision-support environment.

The current interface includes:

- Executive Overview
- Maritime Route Map
- D1–D4 Propagation Intelligence
- Counterfactual Intervention Analysis
- Scenario Stress Laboratory
- Temporal and Resilience Intelligence
- Human-in-the-Loop Decision Space
- Methodological Disclosure

The interface is designed to communicate three layers simultaneously:

1. **Risk state**
2. **Risk mechanism**
3. **Decision consequence**

---

## Maritime Route Visualization

The current route layer visualizes estimated maritime corridors using known sea-waypoints for selected major shipping lanes.

The visualization is intended as a route-context layer and **must not be interpreted as a live vessel track**.

Current route paths are estimated maritime corridors.

### Planned AIS Extension

A future AIS integration layer may introduce:

- live vessel position
- vessel speed anomaly
- ETA drift
- route deviation
- port approach behavior
- dynamic maritime congestion signals

AIS is intentionally presented as a planned extension rather than as an existing capability of the current MVP.

---

## Methodological Positioning

RYPE does not claim novelty from the first use of machine learning, SHAP, scenario analysis, or human-in-the-loop methods individually.

Its contribution lies in integrating:

- a data-leakage-driven methodological inquiry
- externally grounded geopolitical risk indicators
- mechanism-driven D1–D4 operational risk propagation
- explainable risk decomposition
- counterfactual intervention analysis
- resilience evaluation
- human-in-the-loop decision support

within a single research prototype.

The central research perspective is that operational risk intelligence should move beyond predictive accuracy toward **mechanism understanding, uncertainty-aware interpretation, and intervention-oriented decision support**.

---

## Scope and Limitations

RYPE is a **research MVP and decision-support demonstrator**.

It is not currently:

- a live shipment monitoring platform
- an AIS vessel-tracking system
- an autonomous route optimizer
- an industrial ERP or TMS integration
- a production-grade operational command system

The dynamic route engine currently uses origin-node geopolitical pressure as the primary external trigger.

The destination port provides route context and visualization.

Scenario, temporal, resilience, and HITL panels use precomputed research experiment outputs.

These boundaries are disclosed intentionally to preserve methodological transparency.

---

## Planned Research Extensions

Future development directions include:

- AIS vessel-position integration
- live ETA drift and route-deviation signals
- real-time port congestion feeds
- ERP and shipment-event integration
- temporal event grounding
- observed disruption outcomes
- uncertainty quantification
- probabilistic calibration
- survival-based disruption modeling
- dynamic Bayesian risk propagation
- advanced network-based risk diffusion
- operational Human-in-the-Loop governance

---

## Technology Stack

- Python
- Streamlit
- pandas
- NumPy
- Plotly

Research workflow components include statistical modeling, machine learning, explainability, scenario analysis, and decision-support design.

---

## Repository Structure

```text
rype-risk-intelligence/
├── app.py
├── README.md
├── requirements.txt
└── data/
    ├── real_external_geo_risk_table.csv
    ├── real_port_country_bridge.csv
    ├── propagation_df.csv
    ├── scenario_df.csv
    ├── temporal_df.csv
    ├── resilience_df.csv
    ├── hitl_df.csv
    └── metadata.json
```

---

## Run Locally

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

---

## Research Status

**Current version:** RYPE MVP v0.5 — Feature Freeze Decision Intelligence Interface

The current release represents a deployable research demonstrator built from the RYPE experimental workflow.

The project remains under active methodological and research development.

---

## Author

**Meriç Özcan**

Statistics Student  
Risk Modeling & Decision Science  
Explainable AI & Quantitative Research

---

## Disclaimer

RYPE is an academic research prototype.

Outputs are intended for research, methodological demonstration, and decision-support experimentation.

They should not be interpreted as autonomous operational, financial, compliance, sanctions, or maritime navigation decisions.
