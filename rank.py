Python 3.10.7 (tags/v3.10.7:6cc6b13, Sep  5 2022, 14:08:36) [MSC v.1933 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> !pip install sentence-transformers
... import json
... import csv
... import torch
... from datetime import datetime
... from sentence_transformers import SentenceTransformer, util
... from google.colab import files
... 
... print("Please upload your JSONL file:")
... uploaded = files.upload()
... DATA_PATH = next(iter(uploaded))
... CSV_OUTPUT_NAME = 'team_final_submission.csv'
... 
... # Reference date based on the dataset timeline
... REFERENCE_DATE = datetime(2026, 6, 19)
... 
... # ==========================================
... # SETUP: LOAD THE AI MODEL
... # ==========================================
... print("Loading AI Embedding Model...")
... model = SentenceTransformer('all-MiniLM-L6-v2')
... 
... IDEAL_PROFILE_TEXT = """
... Senior AI Engineer ML systems embeddings retrieval ranking LLMs fine-tuning product-engineering scalable backend.
... Built recommendation systems, deployed language models, strong technical depth combined with scrappy product focus.
... """
... ideal_embedding = model.encode(IDEAL_PROFILE_TEXT, convert_to_tensor=True)
... 
... # ==========================================
... # PHASE 1: THE HONEYPOT CATCHER
... # ==========================================
... def is_honeypot(candidate):
...     yoe = candidate.get('profile', {}).get('years_of_experience', 0)
...     if yoe is None: yoe = 0
...     career_history = candidate.get('career_history', [])
    skills = candidate.get('skills', [])

    for role in career_history:
        duration = role.get('duration_months', 0)
        if duration and duration > (yoe * 12) + 24: return True

    total_career_months = sum([role.get('duration_months', 0) for role in career_history if role.get('duration_months')])
    if total_career_months > (yoe * 12 * 2.5) and total_career_months > 60: return True

    for skill in skills:
        if skill.get('proficiency', '').lower() == 'expert' and skill.get('duration_months', 0) == 0: return True

    return False

# ==========================================
# PHASE 3: THE BEHAVIORAL MULTIPLIER (V2)
# ==========================================
def calculate_behavioral_multiplier(candidate):
    multiplier = 1.0
    profile = candidate.get('profile', {})
    signals = candidate.get('redrob_signals', {})

    # 1. Location Penalty (The Unhirables)
    location = profile.get('location', '').lower()
    willing_to_relocate = signals.get('willing_to_relocate', False)
    in_target_city = 'noida' in location or 'pune' in location

    if not in_target_city and not willing_to_relocate:
        multiplier *= 0.1  # 90% penalty

    # 2. The Ghost Penalty (>6 months inactive)
    last_active = signals.get('last_active_date')
    if last_active:
        try:
            active_date = datetime.strptime(last_active, "%Y-%m-%d")
            days_inactive = (REFERENCE_DATE - active_date).days
            if days_inactive > 180:
                multiplier *= 0.5  # 50% penalty
        except: pass

    # 3. Flake Penalties (Statistically validated to hit bottom 25%)
    response_rate = signals.get('recruiter_response_rate', 1.0)
    if response_rate < 0.25:
        multiplier *= 0.5
    else:
        multiplier *= (0.5 + (response_rate * 0.5))

    interview_rate = signals.get('interview_completion_rate', 1.0)
    if interview_rate < 0.50:
        multiplier *= 0.7

    # 4. The Builder Boost (Adjusted for actual distribution)
    github = signals.get('github_activity_score', -1)
    if github > 40:
        multiplier *= 1.25  # Top ~5%: Massive 25% boost
    elif github > 18:
        multiplier *= 1.10  # Top 25%: Solid 10% boost

    # 5. The Immediate Joiner Premium
    notice_period = signals.get('notice_period_days', 90)
    if notice_period <= 30:
        multiplier *= 1.15  # 15% boost for being ready immediately
    elif notice_period > 90:
        multiplier *= 0.90  # 10% penalty for taking 4+ months

    # 6. Market Demand (Wisdom of the Crowd)
    saves = signals.get('saved_by_recruiters_30d', 0)
    if saves >= 15:
        multiplier *= 1.10  # 10% boost if highly sought after

    # 7. Identity Verification (Anti-bot / Anti-spam)
    if signals.get('verified_email', False):
        multiplier *= 1.02
    if signals.get('verified_phone', False):
        multiplier *= 1.02
    if signals.get('linkedin_connected', False):
        multiplier *= 1.02

    return multiplier

# ==========================================
# MASTER PIPELINE EXECUTION
# ==========================================
print("1. Reading, filtering, scoring, and penalizing candidates...")
candidates_scored = []
honeypots_caught = 0

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        candidate = json.loads(line)

        # --- PHASE 1 ---
        if is_honeypot(candidate):
            honeypots_caught += 1
            continue

        # --- PHASE 2 ---
        cid = candidate.get('candidate_id')
        profile = candidate.get('profile', {})
        title = profile.get('current_title', '')
        summary = profile.get('summary', '')
        yoe = profile.get('years_of_experience', 0)

        career_history = candidate.get('career_history', [])
        job_descriptions = " ".join([role.get('description', '') for role in career_history[:2] if role.get('description')])
        candidate_text = f"{title}. {summary} {job_descriptions}"

        if len(candidate_text.strip()) > 10:
            cand_embedding = model.encode(candidate_text, convert_to_tensor=True)
            semantic_score = util.cos_sim(ideal_embedding, cand_embedding).item()
        else:
            semantic_score = 0.0

        # --- PHASE 3 ---
        behavioral_multiplier = calculate_behavioral_multiplier(candidate)

        # Combine everything and round to 4 decimal places to prevent Validator tie bugs!
        final_score = round(semantic_score * behavioral_multiplier, 4)

        # Craft a compelling reasoning string for the judges
        location_str = profile.get('location', 'Unknown')
        reasoning = f"{title} ({yoe}y in {location_str}). Base Match: {round(semantic_score*100)}%. Adjusted for behavior multiplier: {round(behavioral_multiplier, 2)}x."

        candidates_scored.append((final_score, cid, reasoning))

print(f"Processed valid candidates. Caught {honeypots_caught} honeypots.")

# TIE-BREAKER SORTING: Sort by score descending, then by candidate_id ascending
candidates_scored.sort(key=lambda x: (-x[0], x[1]))
top_100 = candidates_scored[:100]

print(f"2. Writing Top 100 to {CSV_OUTPUT_NAME}...")
with open(CSV_OUTPUT_NAME, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])
    for rank, (score, cid, reasoning) in enumerate(top_100, start=1):
        writer.writerow([cid, rank, score, reasoning])

print("Done! Master pipeline execution complete.")

