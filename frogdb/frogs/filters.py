import django_filters

class PermitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Permit
        fields = ['aqis', 'qen','arrival_date']