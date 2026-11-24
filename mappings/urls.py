from django.urls import path
from .views import (
    MappingListCreateView,
    MappingDetailOrPatientDoctorsView,
    PatientDoctorsExplicitView
)

app_name = 'mappings'

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('patient/<int:patient_id>/', PatientDoctorsExplicitView.as_view(), name='mapping-by-patient'),
    path('<int:identifier>/', MappingDetailOrPatientDoctorsView.as_view(), name='mapping-detail-or-patient'),
]
