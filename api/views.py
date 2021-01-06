import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import FileSerializer
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re
from .models import Invoice

class FileUploadView(APIView):
    permission_classes = []
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
      file_serializer = FileSerializer(data=request.data)
      invoice_file = request.data['file']
      if file_serializer.is_valid():
        path = default_storage.save('tmp/invoice.pdf', ContentFile(invoice_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        output_string = StringIO()
        with open(tmp_file, 'rb') as in_file:
          parser = PDFParser(in_file)
          doc = PDFDocument(parser)
          rsrcmgr = PDFResourceManager()
          device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
          interpreter = PDFPageInterpreter(rsrcmgr, device)
          for page in PDFPage.create_pages(doc):
              interpreter.process_page(page)
          
          invoice_re = re.compile(r'\d\d\d-\d\d\d\d-\d\d\d\d') 
          date_re = re.compile(r'\d\d-\d\d-\d\d\d\d')

          ire = invoice_re.search(output_string.getvalue())
          dt = date_re.search(output_string.getvalue())
          
          f_obj = file_serializer.save()
          invoice_obj = Invoice(file=f_obj,num = ire.group(0), dt = dt.group(0))
          invoice_obj.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)