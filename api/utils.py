from rest_framework.response import Response
from rest_framework.views import exception_handler


def success_response(data=None, message="Success", status_code=200):
    return Response({
        "status": True,
        "message": message,
        "data": data
    }, status=status_code)

def error_response(errors=None, message="Something went wrong", status_code=400):
    return Response({
        "status": False,
        "message": message,
        "errors": errors
    }, status=status_code)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return error_response(
            errors=str(exc),
            message="Internal server error",
            status_code=500,
        )

    message = "Something went wrong"
    if isinstance(response.data, dict) and "detail" in response.data:
        message = response.data["detail"]

    return error_response(
        errors=response.data,
        message=message,
        status_code=response.status_code,
    )


class StandardResponseMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return success_response(serializer.data, "Data fetched successfully")

        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, "Data fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data, "Data fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(serializer.data, "Data created successfully", 201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return success_response(serializer.data, "Data updated successfully")

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(None, "Data deleted successfully")
