def calculate_ats_score(findings, suggestions, company=None):
    base_score = 100
    
    # Deduct for weak phrases
    verb_issues = len([s for s in suggestions if s.get('type') == 'word_replacement'])
    base_score -= verb_issues * 5
    
    # Deduct for missing metrics
    metric_issues = len([s for s in suggestions if s.get('type') == 'metric_missing'])
    base_score -= metric_issues * 10
    
    # Bonus for keyword match (if company specified)
    if company and 'keyword_matches' in findings:
        match_ratio = len(findings['keyword_matches']) / len(company.keywords) if company.keywords else 0
        base_score += int(match_ratio * 20)
    
    return max(0, min(100, int(base_score)))