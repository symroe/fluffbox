import json
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from models import Fluff

def home(request):
    f = open("%s/index.html" % settings.PROJECT_PATH)
    return HttpResponse(f.read())


def all_fluffs(request):
    
    all_fluffs = []
    # json.dumps(F.as_json()) for F in Fluff.objects.all()
    for fluff in Fluff.objects.all():
        all_fluffs.append(fluff.as_json())
        
    
    return HttpResponse(json.dumps({'fluff' : all_fluffs}))
#     return render_to_response(
#         'download.html', 
#         {
#             'street_files' : street_files,
#             'neighbourhood_files' : neighbourhood_files,
#         },
#         context_instance=RequestContext(request)
#     )  
#     
