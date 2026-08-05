import csv
from io import StringIO

from django.http import HttpResponse


def respuesta_csv(nombre_archivo, filas, columnas):
    """Genera respuesta CSV compatible con Excel (UTF-8 BOM)."""
    buffer = StringIO()
    buffer.write('\ufeff')
    writer = csv.writer(buffer)
    writer.writerow(columnas)
    for fila in filas:
        writer.writerow(fila)

    response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response
