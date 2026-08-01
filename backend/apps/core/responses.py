from rest_framework.response import Response


def success(data=None, *, status=200):
    return Response({"data": {} if data is None else data}, status=status)
