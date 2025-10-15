from django.contrib import admin
from django.db.models import Case, When, Value, IntegerField
from django.utils.html import format_html
from .models import (ObservationStatesBand1, ObservationStatesBand2,
                     PartialTilePipelineRegionsBand1, PartialTilePipelineRegionsBand2,
                     TileStatesBand1, TileStatesBand2)

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

class PartialTile1DBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'observation', 'sbid', 'tile1', 'tile2', 'tile3',
                     'tile4', 'type', 'number_sources', '_1d_pipeline')
    search_fields = ('id', 'observation__name', 'observation__sbid', 'tile1__tile', 'tile2__tile', 'tile3__tile',
                     'tile4__tile', 'type', 'number_sources', '_1d_pipeline')
    readonly_fields = ('sbid',)

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super(PartialTile1DBaseAdmin, self).get_queryset(request)
        return qs.annotate(
            complete_first=Case(
                When(_1d_pipeline='Completed', then=Value(0)),
                When(_1d_pipeline='Running', then=Value(1)),
                When(_1d_pipeline='Failed', then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            )
        ).order_by('complete_first', '-_1d_pipeline')
        # default ordering: Completed, Running, Failed, NULL last

class ObservationStatesBaseAdmin(admin.ModelAdmin):
    # only comments can be edited
    readonly_fields = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'colour_mfs_state', 'mfs_update', 'colour_cube_state', 'cube_update')    
    search_fields = ('name__name', 'name__sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'mfs_state', 'mfs_update', 'cube_state', 'cube_update')
    fields = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'comments', 'colour_mfs_state', 'mfs_update', 'colour_cube_state', 'cube_update')
    list_display = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

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

    def get_queryset(self, request):
        qs = super(ObservationStatesBaseAdmin, self).get_queryset(request)
        return qs.annotate(
            complete_first=Case(
                When(_1d_pipeline_validation='Completed', then=Value(0)),
                When(_1d_pipeline_validation='Running', then=Value(1)),
                When(_1d_pipeline_validation='Failed', then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            )
        ).order_by('complete_first', '-single_SB_1D_pipeline', '-cube_state', '-mfs_state')
        # default ordering: Completed, Running, Failed, NULL last

class TileStatesBaseAdmin(admin.ModelAdmin):
    # Make sure 3d_val_comments can be updated
    readonly_fields = ('tile_id', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_url',
                       'colour_mfs_state', 'colour_cube_state')
    search_fields = ('tile_id__tile', '_3d_pipeline', '_3d_pipeline_val',
                     '_3d_pipeline_ingest', '_3d_pipeline_validator', '_3d_val_link',
                     '_3d_val_comments', 'mfs_state', 'cube_state')
    # Make sure 3d_val_link appears as links, and the colour coding works for mfs_state and cube_state
    fields = ('tile_id', '_3d_pipeline', '_3d_pipeline_val',
                     '_3d_pipeline_ingest', '_3d_pipeline_validator', '_3d_val_url',
                     '_3d_val_comments', 'colour_mfs_state', 'colour_cube_state')
    # ditto for the list view
    list_display = fields

    def _3d_val_url(self, obj):
        url = obj._3d_val_link
        if not url is None and url.startswith('http'):
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return url

    _3d_val_url.short_description = '3d val link'
    _3d_val_url.admin_order_field = '_3d_val_link'

    def colour_cube_state(self, obj):
        state = obj.cube_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.cube_state)

    colour_cube_state.admin_order_field = 'cube_state'
    colour_cube_state.short_description = 'cube tile state'

    def colour_mfs_state(self, obj):
        state = obj.mfs_state
        if state is None:
            return '-'
        colour = pipeline_state_colour(state)
        return format_html('<span style="color: {};">{}</span>',
                           colour,
                           obj.mfs_state)

    colour_mfs_state.admin_order_field = 'mfs_state'
    colour_mfs_state.short_description = 'mfs tile state'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            complete_first=Case(
                When(_3d_pipeline_val='Good', then=Value(0)),
                When(_3d_pipeline_val='Bad', then=Value(1)),
                When(_3d_pipeline_val='Running', then=Value(2)),
                When(_3d_pipeline_val='Failed', then=Value(3)),
                When(_3d_pipeline_val='WaitingForValidation', then=Value(4)),
                default=Value(5),
                output_field=IntegerField()
            )
        ).order_by('complete_first')
    # default ordering: WGood, Bad, Running, Failed, WaitingForValidation, NULL last

admin.site.register(PartialTilePipelineRegionsBand1, PartialTile1DBaseAdmin)
admin.site.register(PartialTilePipelineRegionsBand2, PartialTile1DBaseAdmin)
admin.site.register(ObservationStatesBand1, ObservationStatesBaseAdmin)
admin.site.register(ObservationStatesBand2, ObservationStatesBaseAdmin)
admin.site.register(TileStatesBand1, TileStatesBaseAdmin)
admin.site.register(TileStatesBand2, TileStatesBaseAdmin)
