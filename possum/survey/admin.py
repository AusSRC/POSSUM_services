from django.contrib import admin

from .models import Observation, AssociatedTile, FieldTile, Tile


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
                       'validated_state', 'mfs_update', 'mfs_state', 'cube_update', 'cube_state')

    model = FieldTile

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

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        qs = super(Band1FieldTileAdminInline, self).get_queryset(request)
        return qs.filter(name__name__istartswith = 'EMU')


class Band2FieldTileAdminInline(admin.TabularInline):
    readonly_fields = ('obs_start', 'sbid', 'processed_date', 'validated_date', 
                       'validated_state', 'mfs_update', 'mfs_state', 'cube_update', 'cube_state')

    model = FieldTile

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
        return qs.filter(name__name__istartswith = 'WALLABY')


class ObservationAdmin(admin.ModelAdmin):
    inlines = [AssociatedTileAdminInline,]

    list_display = ('name', 'ra_deg', 'dec_deg', 'band', 'obs_start', 'sbid', 'processed_date', 'validated_date', 
                    'validated_state', 'mfs_update', 'mfs_state', 'cube_update', 'cube_state')

    readonly_fields = ('name', 'ra_deg', 'dec_deg', 'gl', 'gb', 'rotation', 
                       'duration', 'centrefreq', 'bandwidth', 'footprint', 'band')

    fields = ('name', 'ra_deg', 'dec_deg', 'gl', 'gb', 'rotation', 'duration', 'centrefreq', 
              'bandwidth', 'footprint', 'band', 'obs_start', 'sbid', 'processed_date', 'validated_date', 
              'validated_state', 'mfs_update', 'mfs_state', 'cube_update', 'cube_state')

    search_fields = ('name', 
                     'ra_deg', 
                     'dec_deg', 
                     'band', 
                     'sbid',
                     'validated_state',
                     'mfs_state',
                     'cube_state',
                     'associatedtile__tile__tile')

    can_delete = False
    can_add = False
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False


class TileAdmin(admin.ModelAdmin):
    inlines = [Band1FieldTileAdminInline, Band2FieldTileAdminInline,]

    list_display = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'oned_pipeline_main_band1', 'oned_pipeline_borders_band1', 'threed_pipeline_band1',
                    'oned_pipeline_main_band2', 'oned_pipeline_borders_band2', 'threed_pipeline_band2')
    readonly_fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb')
    fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'oned_pipeline_main_band1', 'oned_pipeline_borders_band1', 'threed_pipeline_band1',
             'oned_pipeline_main_band2', 'oned_pipeline_borders_band2', 'threed_pipeline_band2')

    search_fields = ('tile', 
                     'ra_deg', 
                     'dec_deg',
                     'associatedtile__name__name')

    can_delete = False
    can_add = False
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Observation, ObservationAdmin)
admin.site.register(Tile, TileAdmin)