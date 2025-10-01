import re
from django.apps import apps

def analyze_resume(text: str, target_role: str = None, company_id: int = None):
    if not text or not text.strip():
        return {
            'ats_score': 0,
            'breakdown': {'formatting': 0, 'skills': 0, 'action_verbs': 0, 'metrics': 0},
            'suggestions': [{'type': 'error', 'suggestion': 'Resume text is empty.'}],
            'feedback': {
                'formatting': {'score': 0, 'issues': ['No resume provided'], 'fixes': ['Upload or paste your resume']},
                'skills': {'score': 0, 'missing': [], 'found': [], 'fixes': []},
                'action_verbs': {'score': 0, 'weak': [], 'fixes': []},
                'metrics': {'score': 0, 'has_metrics': False, 'fixes': []}
            }
        }

    text_lower = text.lower()
    suggestions = []

    # ✅ FULLY INITIALIZED findings dict (fixes KeyError)
    findings = {
        'formatting': {'score': 100, 'issues': [], 'fixes': []},
        'skills': {'score': 100, 'missing': [], 'found': [], 'fixes': []},  # ← 'fixes' now present
        'action_verbs': {'score': 100, 'weak': [], 'fixes': []},
        'metrics': {'score': 100, 'has_metrics': False, 'fixes': []}
    }

    # 1. Formatting Check (Weekday-style)
    if re.search(r'<table|<img|<div|<span|<style', text, re.IGNORECASE):
        findings['formatting']['score'] = 60
        findings['formatting']['issues'].append("Avoid tables, images, or HTML tags — ATS can't parse them")
        findings['formatting']['fixes'].append("Use plain text with standard headings like 'Work Experience', 'Education'")
    elif len([line for line in text.split('\n') if line.strip()]) < 5:
        findings['formatting']['score'] = 70
        findings['formatting']['issues'].append("Resume is too short — missing key sections")
        findings['formatting']['fixes'].append("Add sections: Work Experience, Education, Skills, Projects")

    # 2. Skill Matching (Keywords)
    JobRole = apps.get_model('resume_analyzer', 'JobRole')
    CompanyProfile = apps.get_model('resume_analyzer', 'CompanyProfile')
    
    expected_keywords = []
    if company_id:
        try:
            company = CompanyProfile.objects.get(id=company_id, active=True)
            expected_keywords = company.keywords or []
        except CompanyProfile.DoesNotExist:
            expected_keywords = []
    elif target_role:
        try:
            role = JobRole.objects.get(title__iexact=target_role.strip(), active=True)
            expected_keywords = role.keywords or []
        except JobRole.DoesNotExist:
            expected_keywords = ['Python', 'SQL', 'Git', 'REST API', 'Agile']

    found = [kw for kw in expected_keywords if kw.lower() in text_lower]
    missing = [kw for kw in expected_keywords if kw not in found]
    findings['skills']['missing'] = missing
    findings['skills']['found'] = found
    findings['skills']['score'] = max(30, 100 - len(missing) * 10)

    if missing:
        suggestions.append({
            'type': 'missing_keywords',
            'suggestion': f"Missing key ATS keywords: {', '.join(missing[:5])}"
        })
        findings['skills']['fixes'].append(f"Add these naturally: {', '.join(missing[:3])}")

    # 3. Action Verb Detection
    weak_phrases = ["responsible for", "helped with", "worked on", "was involved in", "assisted in"]
    strong_alternatives = {
        "responsible for": ["Led", "Directed", "Spearheaded"],
        "helped with": ["Collaborated on", "Supported", "Co-developed"],
        "worked on": ["Engineered", "Built", "Developed"],
        "was involved in": ["Contributed to", "Played key role in"],
        "assisted in": ["Supported", "Enabled", "Facilitated"]
    }
    for weak in weak_phrases:
        if weak in text_lower:
            findings['action_verbs']['weak'].append(weak)
            suggestions.append({
                'type': 'word_replacement',
                'original': weak,
                'suggestions': strong_alternatives[weak]
            })
            findings['action_verbs']['fixes'].append(f"Replace '{weak}' with '{strong_alternatives[weak][0]}'")
    findings['action_verbs']['score'] = max(30, 100 - len(findings['action_verbs']['weak']) * 15)

    # 4. Metric Detection (Quantifiable Achievements)
    if re.search(r'\b\d+[%$]?\b', text):
        findings['metrics']['has_metrics'] = True
        findings['metrics']['score'] = 100
    else:
        findings['metrics']['score'] = 40
        suggestions.append({
            'type': 'metric_missing',
            'suggestion': 'Add quantifiable metrics (e.g., “Improved sales by 32%”, “Reduced latency by 200ms”)'
        })
        findings['metrics']['fixes'].append("Include numbers: e.g., 'Managed team of 5', 'Cut costs by $10K'")

    # Final ATS Score (Weighted)
    ats_score = (
        findings['formatting']['score'] * 0.2 +
        findings['skills']['score'] * 0.3 +
        findings['action_verbs']['score'] * 0.25 +
        findings['metrics']['score'] * 0.25
    )

    return {
        'ats_score': max(0, min(100, int(ats_score))),
        'breakdown': {
            'formatting': findings['formatting']['score'],
            'skills': findings['skills']['score'],
            'action_verbs': findings['action_verbs']['score'],
            'metrics': findings['metrics']['score']
        },
        'suggestions': suggestions,
        'feedback': findings  # ← Now safe to use in frontend
    }