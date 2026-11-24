from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Doctor
from .serializers import DoctorSerializer, DoctorDetailSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    """
    POST /api/doctors/ - Add a new doctor (Authenticated users only)
    GET /api/doctors/ - Retrieve all doctors
    """
    permission_classes = [IsAuthenticated]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    @extend_schema(
        summary="Retrieve all doctors",
        description="Returns a list of all registered doctors.",
        responses={200: DoctorSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Add a new doctor",
        description="Creates a new doctor record.",
        request=DoctorSerializer,
        responses={
            201: DoctorSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response({
                'success': True,
                'message': 'Doctor record created successfully.',
                'data': self.get_serializer(doctor).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to create doctor record.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/ - Get details of a specific doctor
    PUT /api/doctors/<id>/ - Update doctor details
    DELETE /api/doctors/<id>/ - Delete a doctor record
    """
    permission_classes = [IsAuthenticated]
    queryset = Doctor.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DoctorDetailSerializer
        return DoctorSerializer

    @extend_schema(
        summary="Get details of a specific doctor",
        description="Retrieves details and assigned patients for a specific doctor.",
        responses={200: DoctorDetailSerializer, 404: OpenApiResponse(description="Doctor not found")}
    )
    def get(self, request, *args, **kwargs):
        doctor = self.get_object()
        serializer = self.get_serializer(doctor)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update doctor details",
        description="Updates full details of a doctor record.",
        request=DoctorSerializer,
        responses={200: DoctorSerializer, 400: OpenApiResponse(description="Validation error"), 404: OpenApiResponse(description="Doctor not found")}
    )
    def put(self, request, *args, **kwargs):
        doctor = self.get_object()
        serializer = self.get_serializer(doctor, data=request.data)
        if serializer.is_valid():
            updated_doctor = serializer.save()
            return Response({
                'success': True,
                'message': 'Doctor details updated successfully.',
                'data': self.get_serializer(updated_doctor).data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Validation failed while updating doctor.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partial update doctor details",
        description="Partially updates doctor details.",
        request=DoctorSerializer,
        responses={200: DoctorSerializer, 400: OpenApiResponse(description="Validation error")}
    )
    def patch(self, request, *args, **kwargs):
        doctor = self.get_object()
        serializer = self.get_serializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            updated_doctor = serializer.save()
            return Response({
                'success': True,
                'message': 'Doctor details updated successfully.',
                'data': self.get_serializer(updated_doctor).data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Validation failed while updating doctor.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a doctor record",
        description="Deletes a doctor record by ID.",
        responses={200: OpenApiResponse(description="Doctor deleted successfully"), 404: OpenApiResponse(description="Doctor not found")}
    )
    def delete(self, request, *args, **kwargs):
        doctor = self.get_object()
        doctor_id = doctor.id
        doctor.delete()
        return Response({
            'success': True,
            'message': f'Doctor with ID {doctor_id} has been deleted successfully.'
        }, status=status.HTTP_200_OK)
