from rest_framework.response import Response


def response_api_view(data, page=1):
    """Retorna um response padronizado para api.

    :param data
    :returns: Response
    """

    return Response(
        {
            "total": len(data),
            "page": page,
            "per_page": len(data),
            # "navigation": {"next": None,"previous": None},
            "results": data,
        }
    )


def get_titulo_campo(serializer_class, campo):
    """
    Retorna o titulo do campo mapeado no serializer
    Args:
        - serializer_class: classe do serializer
        - campo: str field do serializer
    returns:
        - título/campo(str)
    """
    if hasattr(serializer_class, "titulo_campo"):
        return serializer_class.titulo_campo.get(campo, campo)
    return campo
