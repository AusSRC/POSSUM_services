from django.contrib import admin
from django.utils.html import format_html
from django.db.models.aggregates import Count
from django.db.models import Q, Count

from .models import Observation, AssociatedTile, Tile, Validation

class AssociatedTileAdminInline(admin.TabularInline):
    model = AssociatedTile

    can_delete = False
    can_add = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class Band1FieldTileAdminInline(admin.TabularInline):
    readonly_fields = ('obs_start', 'sbid', 'processed_date', 'validated_date',
                       'validated_state')

    model = AssociatedTile

    can_delete = False
    can_add = False
    show_change_link = True

    verbose_name = "Band 1 Field Tile"

    def obs_start(self, obj):
        val = obj.name.obs_start
        if val is None:
            return '-'
        return val

    def sbid(self, obj):
        val = obj.name.sbid
        if val is None:
            return '-'
        return val

    def processed_date(self, obj):
        val = obj.name.processed_date
        if val is None:
            return '-'
        return val

    def validated_date(self, obj):
        val = obj.name.validated_date
        if val is None:
            return '-'
        return val

    def validated_state(self, obj):
        val = obj.name.validated_state
        if val is None:
            return '-'

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        qs = super(Band1FieldTileAdminInline, self).get_queryset(request)
        return qs.filter(name__band=1)


class Band2FieldTileAdminInline(admin.TabularInline):
    readonly_fields = ('obs_start', 'sbid', 'processed_date', 'validated_date',
                       'validated_state')

    model = AssociatedTile

    can_delete = False
    can_add = False
    show_change_link = True

    verbose_name = "Band 2 Field Tile"

    def obs_start(self, obj):
        val = obj.name.obs_start
        if val is None:
            return '-'
        return val

    def sbid(self, obj):
        val = obj.name.sbid
        if val is None:
            return '-'
        return val

    def processed_date(self, obj):
        val = obj.name.processed_date
        if val is None:
            return '-'
        return val

    def validated_date(self, obj):
        val = obj.name.validated_date
        if val is None:
            return '-'
        return val

    def validated_state(self, obj):
        val = obj.name.validated_state
        if val is None:
            return '-'
        return val

    def mfs_update(self, obj):
        val = obj.name.mfs_update
        if val is None:
            return '-'
        return val

    def mfs_state(self, obj):
        val = obj.name.mfs_state
        if val is None:
            return '-'
        return val

    def cube_update(self, obj):
        val = obj.name.cube_update
        if val is None:
            return '-'
        return val

    def cube_state(self, obj):
        val = obj.name.cube_state
        if val is None:
            return '-'
        return val

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(Band2FieldTileAdminInline, self).get_queryset(request)
        return qs.filter(name__band=2)


class ValidationAdminInline(admin.TabularInline):
    model = Validation

    readonly_fields = [field.name for field in Validation._meta.get_fields()]
    can_delete = False
    can_add = False

    def get_queryset(self, request):
        qs = super(ValidationAdminInline, self).get_queryset(request)
        return qs.filter()


class ValidationAdmin(admin.ModelAdmin):
    model = Validation
    list_display = [field.name for field in Validation._meta.get_fields()]

    can_delete = False
    can_add = False
    show_change_link = True

    def get_queryset(self, request):
        qs = super(ValidationAdmin, self).get_queryset(request)
        return qs.filter()


class ObservationAdmin(admin.ModelAdmin):
    inlines = [AssociatedTileAdminInline, ValidationAdminInline]

    list_display = ('name', 'ra_deg', 'dec_deg', 'band', 'obs_start', 'sbid', 'processed_date', 'validated_date',
                    'validated_state')

    readonly_fields = ('name', 'ra_deg', 'dec_deg', 'gl', 'gb', 'rotation',
                       'duration', 'centrefreq', 'bandwidth', 'footprint', 'band','obs_start', 'sbid', 'processed_date', 'validated_date',
                       'validated_state')

    fields = ('name', 'ra_deg', 'dec_deg', 'gl', 'gb', 'rotation', 'duration', 'centrefreq',
              'bandwidth', 'footprint', 'band', 'obs_start', 'sbid', 'processed_date', 'validated_date',
              'validated_state')

    search_fields = ('name',
                     'ra_deg',
                     'dec_deg',
                     'band',
                     'sbid',
                     'validated_state',
                     'associatedtile__tile__tile')

    can_delete = False
    can_add = False
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False


class TileAdmin(admin.ModelAdmin):
    inlines = [Band1FieldTileAdminInline, Band2FieldTileAdminInline,]
    list_display = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'band1_count', 'band2_count')
    readonly_fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb')
    fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb')

    search_fields = ('tile',
                     'ra_deg',
                     'dec_deg',
                     'associatedtile__name__name')

    can_delete = False
    can_add = False
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            band1_count=Count('associatedtile',
                              filter=Q(associatedtile__name__band=1))).order_by('band1_count')

        qs = qs.annotate(
            band2_count=Count('associatedtile',
                              filter=Q(associatedtile__name__band=2))).order_by('band2_count')

        return qs

    def band1_count(self, obj):
        return obj.band1_count

    band1_count.admin_order_field = 'band1_count'
    band1_count.short_description = 'Band 1'

    def band2_count(self, obj):
        return obj.band2_count

    band2_count.admin_order_field = 'band2_count'
    band2_count.short_description = 'Band 2'

admin.site.register(Observation, ObservationAdmin)
admin.site.register(Tile, TileAdmin)
admin.site.register(Validation, ValidationAdmin)
