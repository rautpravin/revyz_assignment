import os
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template

from xhtml2pdf import pisa


def render_to_pdf(template_src, filename, context_dict={}):
    template = get_template(template_src)

    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        base_media_path = str(settings.MEDIA_ROOT).replace('\\', '/')
        if not os.path.exists(base_media_path):
            os.mkdir(base_media_path)
        with open(base_media_path+f'/{filename}.pdf', 'wb') as f:
            f.write(result.getvalue())
            return True
        # return HttpResponse(result.getvalue(), content_type='application/pdf')
    return False


