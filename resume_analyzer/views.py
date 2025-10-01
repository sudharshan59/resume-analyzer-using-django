from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JobRole, CompanyProfile
from .nlp_engine.extractor import extract_text_from_file
from .nlp_engine.analyzer import analyze_resume

def index(request):
    roles = JobRole.objects.filter(active=True)
    companies = CompanyProfile.objects.filter(active=True)
    return render(request, 'resume_analyzer/index.html', {'roles': roles, 'companies': companies})

@csrf_exempt
def analyze_api(request):
    text = request.POST.get('text', '').strip()
    file = request.FILES.get('file')
    if file:
        text = extract_text_from_file(file)
    if not text:
        return JsonResponse({'error': 'No resume provided'}, status=400)

    role = request.POST.get('role')
    company_id = request.POST.get('company_id')
    if company_id:
        company_id = int(company_id)

    result = analyze_resume(text, role, company_id)
    return JsonResponse(result)