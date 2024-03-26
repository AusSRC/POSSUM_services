from django.contrib import admin
from django.utils.html import format_html
from django.db.models.aggregates import Count
from django.db.models import Q, Count, Case, When, BooleanField

from .models import Observation, AssociatedTile, FieldTile, Tile


def pipeline_state_colour(state):
    colour = 'DodgerBlue'
    if state == 'PENDING':
        colour = 'orange'
    elif state == 'RUNNING':
        colour = 'SlateBlue'
    elif state == 'COMPLETED':
        colour = 'limegreen'
    elif state == 'FAILED':
        colour = 'Tomato'
    return colour


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
        return qs.filter(name__band=1)


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
        return qs.filter(name__band=2)


class ObservationAdmin(admin.ModelAdmin):
    inlines = [AssociatedTileAdminInline,]
    ordering = ('mfs_state', 'cube_state', 'name')

    list_display = ('name', 'ra_deg', 'dec_deg', 'band', 'obs_start', 'sbid', 'processed_date', 'validated_date',
                    'validated_state', 'colour_mfs_state', 'mfs_update', 'colour_cube_state', 'cube_update',)

    readonly_fields = ('name', 'ra_deg', 'dec_deg', 'gl', 'gb', 'rotation',
                       'duration', 'centrefreq', 'bandwidth', 'footprint', 'band','obs_start', 'sbid', 'processed_date', 'validated_date',
                       'validated_state', 'mfs_update', 'mfs_state', 'cube_update', 'cube_state')

    fields = ('name', 'ra_deg', 'dec_deg', 'gl', 'gb', 'rotation', 'duration', 'centrefreq',
              'bandwidth', 'footprint', 'band', 'obs_start', 'sbid', 'processed_date', 'validated_date',
              'validated_state', 'mfs_state', 'mfs_update', 'cube_state', 'cube_update',)

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

    def colour_mfs_state(self, obj):
        state = obj.mfs_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.mfs_state)

    colour_mfs_state.admin_order_field = 'mfs_state'
    colour_mfs_state.short_description = 'mfs state'

    def colour_cube_state(self, obj):
        state = obj.cube_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.cube_state)

    colour_cube_state.admin_order_field = 'cube_state'
    colour_cube_state.short_description = 'cube state'

    def has_delete_permission(self, request, obj=None):
        return False


class TileAdmin(admin.ModelAdmin):
    inlines = [Band1FieldTileAdminInline, Band2FieldTileAdminInline,]

    #list_display = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'band1_count', 'band1_mfs_complete', 'band1_cube_complete',
    #                'oned_pipeline_main_band1', 'oned_pipeline_borders_band1', 'threed_pipeline_band1',
    #                'oned_pipeline_main_band2', 'oned_pipeline_borders_band2', 'threed_pipeline_band2')
    list_display = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb',
                    'band1_count', 'band1_mfs_complete', 'band1_cube_complete',
                    'band2_count', 'band2_mfs_complete', 'band2_cube_complete',
                    'colour_band1_mfs_state', 'colour_band1_cube_state',
                    'colour_band2_mfs_state', 'colour_band2_cube_state'
                   )

    readonly_fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'band1_mfs_state', 'band1_cube_state', 'band2_mfs_state', 'band2_cube_state',)
    #fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'oned_pipeline_main_band1', 'oned_pipeline_borders_band1', 'threed_pipeline_band1',
    #         'oned_pipeline_main_band2', 'oned_pipeline_borders_band2', 'threed_pipeline_band2')

    fields = ('tile', 'ra_deg', 'dec_deg', 'gl', 'gb', 'band1_mfs_state', 'band1_cube_state', 'band2_mfs_state', 'band2_cube_state',)

    search_fields = ('tile',
                     'ra_deg',
                     'dec_deg',
                     'associatedtile__name__name')

    can_delete = False
    can_add = False
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False

    def colour_band1_cube_state(self, obj):
        state = obj.band1_cube_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.band1_cube_state)

    colour_band1_cube_state.admin_order_field = 'band1_cube_state'
    colour_band1_cube_state.short_description = 'band 1 cube tile state'

    def colour_band1_mfs_state(self, obj):
        state = obj.band1_mfs_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.band1_mfs_state)

    colour_band1_mfs_state.admin_order_field = 'band1_mfs_state'
    colour_band1_mfs_state.short_description = 'band 1 mfs tile state'

    def colour_band2_cube_state(self, obj):
        state = obj.band2_cube_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.band2_cube_state)

    colour_band2_cube_state.admin_order_field = 'band2_cube_state'
    colour_band2_cube_state.short_description = 'band 2 cube tile state'


    def colour_band2_mfs_state(self, obj):
        state = obj.band2_mfs_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.band2_mfs_state)

    colour_band2_mfs_state.admin_order_field = 'band2_mfs_state'
    colour_band2_mfs_state.short_description = 'band 2 mfs tile state'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            band1_count=Count('fieldtile',
                              filter=Q(fieldtile__name__band=1))).order_by('band1_count')
        qs = qs.annotate(
            band1_mfs_complete=Case(
                When(band1_count=Count('fieldtile',
                                        filter=Q(fieldtile__name__band=1,
                                        fieldtile__name__mfs_state='COMPLETED')), then=True),
                default=False,
                output_field=BooleanField()
            )).order_by('-band1_mfs_complete')

        qs = qs.annotate(
            band1_cube_complete=Case(
                When(band1_count=Count('fieldtile',
                                        filter=Q(fieldtile__name__band=1,
                                        fieldtile__name__cube_state='COMPLETED')), then=True),
                default=False,
                output_field=BooleanField()
            )).order_by('-band1_cube_complete')


        qs = qs.annotate(
            band2_count=Count('fieldtile',
                              filter=Q(fieldtile__name__band=2))).order_by('band2_count')
        qs = qs.annotate(
            band2_mfs_complete=Case(
                When(band2_count=Count('fieldtile',
                                        filter=Q(fieldtile__name__band=2,
                                        fieldtile__name__mfs_state='COMPLETED')), then=True),
                default=False,
                output_field=BooleanField()
            )).order_by('-band2_mfs_complete')

        qs = qs.annotate(
            band2_cube_complete=Case(
                When(band1_count=Count('fieldtile',
                                        filter=Q(fieldtile__name__band=2,
                                        fieldtile__name__cube_state='COMPLETED')), then=True),
                default=False,
                output_field=BooleanField()
            )).order_by('-band2_cube_complete')


        return qs


    def band1_count(self, obj):
        return obj.band1_count

    band1_count.admin_order_field = 'band1_count'
    band1_count.short_description = 'Band 1'

    def band1_mfs_complete(self, obj):
        if obj.band1_count == 0:
            return False
        return obj.band1_mfs_complete

    band1_mfs_complete.admin_order_field = 'band1_mfs_complete'
    band1_mfs_complete.short_description = 'Band 1 mfs complete'
    band1_mfs_complete.boolean = True

    def band1_cube_complete(self, obj):
        if obj.band1_count == 0:
            return False
        return obj.band1_cube_complete

    band1_cube_complete.admin_order_field = 'band1_cube_complete'
    band1_cube_complete.short_description = 'Band 1 cube complete'
    band1_cube_complete.boolean = True

    def band2_count(self, obj):
        return obj.band2_count

    band2_count.admin_order_field = 'band2_count'
    band2_count.short_description = 'Band 2'

    def band2_mfs_complete(self, obj):
        if obj.band2_count == 0:
            return False
        return obj.band2_mfs_complete

    band2_mfs_complete.admin_order_field = 'band2_mfs_complete'
    band2_mfs_complete.short_description = 'Band 2 mfs complete'
    band2_mfs_complete.boolean = True

    def band2_cube_complete(self, obj):
        if obj.band2_count == 0:
            return False
        return obj.band2_cube_complete

    band2_cube_complete.admin_order_field = 'band2_cube_complete'
    band2_cube_complete.short_description = 'Band 2 cube complete'
    band2_cube_complete.boolean = True


admin.site.register(Observation, ObservationAdmin)
admin.site.register(Tile, TileAdmin)