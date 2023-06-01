from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage


# Create your views here.
def get_data(request):
    data_list = ["test"]
    code = 200
    msg = ""
    data_count = 10
    json_dict = {"code": code, 'msg': msg, 'count': data_count, 'data': data_list}
    return JsonResponse(json_dict)


def upload(request):
    if request.method == 'POST' and request.FILES['']:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'upload.html', {'uploaded_file_url': uploaded_file_url})
    return render(request, 'upload.html')
