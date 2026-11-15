from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,HTTP_204_NO_CONTENT)

from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategorySerializer
from .permissions import IsTextSenseAdmin


class CategoryListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated(), IsTextSenseAdmin()]


    # GET: Retrieve all active categories
    def get(self, request):
        categories = Category.objects.filter(active=True).order_by("name")
        serializer = CategorySerializer(categories, many=True)

        return Response(
            {
                "message": "Categories retrieved successfully.",
                "categories": serializer.data
            },
            status=HTTP_200_OK
        )


    # POST: Create a category (Admin only)
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
    permission_classes = [IsAuthenticated, IsTextSenseAdmin]

    # GET: Retrieve a particular category
    def get(self, request, pk):
        category = get_object_or_404(Category,pk=pk)
        serializer = CategorySerializer(category)
        return Response({"category": serializer.data}, status=HTTP_200_OK)

    # PUT: Update complete category
    def put(self, request, pk):
        category = get_object_or_404(Category,pk=pk)
        serializer = CategorySerializer(category,data=request.data)

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


    # PATCH: Update selected fields
    def patch(self, request, pk):
        category = get_object_or_404(Category,pk=pk)
        serializer = CategorySerializer(category,data=request.data,partial=True)

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


    # DELETE: Delete category
    def delete(self, request, pk):
        category = get_object_or_404(Category,pk=pk)
        category.delete()
        return Response(
            {
                "message": "Category deleted successfully."
            },
            status=HTTP_204_NO_CONTENT
        )