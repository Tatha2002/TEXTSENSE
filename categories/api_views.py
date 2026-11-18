
from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
)

from .models import Category
from .serializers import CategorySerializer
from .permissions import IsTextSenseAdmin


class CategoryListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated(), IsTextSenseAdmin()]

    # GET: Retrieve categories
    def get(self, request):
        if IsTextSenseAdmin().has_permission(request, self):
            categories = Category.objects.all().order_by("name")
        else:
            categories = Category.objects.filter(active=True).order_by("name")

        serializer = CategorySerializer(categories, many=True)

        return Response(
            {
                "message": "Categories retrieved successfully.",
                "categories": serializer.data
            },
            status=HTTP_200_OK
        )

    # POST: Create category (Admin only)
    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Category created successfully.",
                    "category": serializer.data
                },
                status=HTTP_201_CREATED
            )

        return Response(
            {"errors": serializer.errors},
            status=HTTP_400_BAD_REQUEST
        )


class CategoryDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated(), IsTextSenseAdmin()]

    # GET: Retrieve category details
    def get(self, request, pk):
        if IsTextSenseAdmin().has_permission(request, self):
            category = get_object_or_404(Category, pk=pk)
        else:
            category = get_object_or_404(Category, pk=pk, active=True)

        serializer = CategorySerializer(category)

        return Response(
            {"category": serializer.data},
            status=HTTP_200_OK
        )

    # PUT: Update complete category
    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Category updated successfully.",
                    "category": serializer.data
                },
                status=HTTP_200_OK
            )

        return Response(
            {"errors": serializer.errors},
            status=HTTP_400_BAD_REQUEST
        )

    # PATCH: Update selected fields or deactivate category
    def patch(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Category updated successfully.",
                    "category": serializer.data
                },
                status=HTTP_200_OK
            )

        return Response(
            {"errors": serializer.errors},
            status=HTTP_400_BAD_REQUEST
        )

    # DELETE: Delete category if no feedback exists
    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)

        if category.feedbacks.exists():
            return Response(
                {
                    "message": "Category cannot be deleted because feedback is associated with it."
                },
                status=HTTP_409_CONFLICT
            )

        try:
            category.delete()
        except ProtectedError:
            return Response(
                {
                    "message": "Category cannot be deleted because feedback is associated with it."
                },
                status=HTTP_409_CONFLICT
            )

        return Response(
            {"message": "Category deleted successfully."},
            status=HTTP_200_OK
        )
