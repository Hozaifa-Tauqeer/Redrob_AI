Redrob Hackathon v4: Pipeline Optimization Engine

This repository contains our team's submission for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

🧠 Architecture Overview (The 3-Phase Ranker)

To effectively identify the absolute best candidates for the Senior AI Engineer role while filtering out noise and impossible profiles, we engineered a unified 3-Phase ranking pipeline:

Phase 1: The Honeypot Catcher (Rule-Based)

Eliminates mathematically impossible candidates immediately.

Catches edge cases like single-job durations exceeding total years of experience, or "Expert" proficiency claims with 0 months of actual duration.

Phase 2: Semantic Matching (AI Embeddings)

Uses the lightweight all-MiniLM-L6-v2 transformer model to embed the candidate's actual career history and summary.

Computes cosine similarity against the provided Job Description to penalize applicants from entirely different fields (e.g., Accountants, HR Managers).

Phase 3: Behavioral Multipliers (Business Logic)

Statistically weights the redrob_signals to measure actual hireability and intent.

Penalties: 0.1x for strict location mismatches, 0.5x for ghosting/inactive users.

Bonuses: 1.25x for top 5% GitHub builders, 1.15x for immediate joiners (≤30 day notice periods).

Trust: Cumulative 1.02x Trust & Safety boosts for verified IDs to downrank bots.

🚀 How to Run Locally (Stage 3 Reproduction)

Prerequisites:
Ensure you have Python 3.10+ installed and install the required dependencies:

pip install sentence-transformers torch

Ranking Execution:
Place the candidates.jsonl file in the root directory. Run the master pipeline to process the candidates, apply the 3-phase logic, and generate the final ranked CSV:

python rank.py


(Note: Edit the DATA_PATH and CSV_OUTPUT_NAME variables inside rank.py if your file names or paths differ).

🧪 Interactive Sandbox (Stage 1 Requirement)

To meet the Hackathon requirement for a ≤100 candidate sandbox, we have provided an interactive Google Colab notebook.

This notebook dynamically clones this GitHub repository (https://github.com/Hozaifa-Tauqeer/Redrob_AI), installs dependencies, reads a sample of the dataset, and runs the ranking pipeline end-to-end to instantly download the results CSV.

👉 [Open our Colab Sandbox](https://colab.research.google.com/drive/1SRj2Z-JAq2MOz3lHDnKjFymLTSyYoVKj?usp=sharing)

📂 Repository Structure

rank.py: The master pipeline script containing the Honeypot logic, AI embedding generator, and Behavioral Multiplier logic. Outputs the ranked top 100 CSV.


submission_metadata.yaml: Team and environment details for the portal submission.
