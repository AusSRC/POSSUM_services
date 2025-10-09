from django.contrib import admin
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
class PartialTile1DBand1Admin(admin.ModelAdmin):
    list_display = [field.name for field in PartialTilePipelineRegionsBand1._meta.get_fields()]
    search_fields = ('id', 'observation__name', 'sbid', 'tile1__tile', 'tile2__tile', 'tile3__tile',
                     'tile4__tile', 'type', 'number_sources', '_1d_pipeline')
    can_delete = False
    can_add = False
    show_change_link = True

    def get_queryset(self, request):
        qs = super(PartialTile1DBand1Admin, self).get_queryset(request)
        return qs.filter()

class PartialTile1DBand2Admin(admin.ModelAdmin):
    list_display = [field.name for field in PartialTilePipelineRegionsBand2._meta.get_fields()]
    search_fields = ('id', 'observation__name', 'sbid', 'tile1__tile', 'tile2__tile', 'tile3__tile',
                     'tile4__tile', 'type', 'number_sources', '_1d_pipeline')

    can_delete = False
    can_add = False
    show_change_link = True

    def get_queryset(self, request):
        qs = super(PartialTile1DBand2Admin, self).get_queryset(request)
        return qs.filter()

class ObservationStatesBand1Admin(admin.ModelAdmin):
    # only comments can be edited
    readonly_fields = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'mfs_state', 'mfs_update', 'cube_state', 'cube_update')
    list_display = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'comments',
                    'colour_mfs_state', 'mfs_update', 'colour_cube_state', 'cube_update',)
    search_fields = [field.name for field in ObservationStatesBand1._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(ObservationStatesBand1Admin, self).get_queryset(request)
        return qs.filter()
    
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

class ObservationStatesBand2Admin(admin.ModelAdmin):
    # only comments can be edited
    readonly_fields = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'mfs_state', 'mfs_update', 'cube_state', 'cube_update')
    list_display = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'comments',
                    'colour_mfs_state', 'mfs_update', 'colour_cube_state', 'cube_update',)
    search_fields = [field.name for field in ObservationStatesBand2._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(ObservationStatesBand2Admin, self).get_queryset(request)
        return qs.filter()
    
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

class TileStatesBand1Admin(admin.ModelAdmin):
    # Make sure 3d_val_comments can be updated
    readonly_fields = ('tile_id', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_link', 
                       'mfs_complete', 'cube_complete', 'colour_mfs_state', 'colour_cube_state')
    list_display = [field.name for field in TileStatesBand1._meta.get_fields()]
    search_fields = [field.name for field in TileStatesBand1._meta.get_fields()]
          
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
        qs = super(TileStatesBand1Admin, self).get_queryset(request)
        return qs.filter()

class TileStatesBand2Admin(admin.ModelAdmin):
    # Make sure 3d_val_comments can be updated
    readonly_fields = ('tile_id', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_link',
                       'mfs_complete', 'cube_complete', 'colour_mfs_state', 'colour_cube_state')
    list_display = [field.name for field in TileStatesBand2._meta.get_fields()]
    search_fields = [field.name for field in TileStatesBand2._meta.get_fields()]
    
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
        qs = super(TileStatesBand2Admin, self).get_queryset(request)
        return qs.filter()

admin.site.register(PartialTilePipelineRegionsBand1, PartialTile1DBand1Admin)
admin.site.register(PartialTilePipelineRegionsBand2, PartialTile1DBand2Admin)
admin.site.register(ObservationStatesBand1Admin, ObservationStatesBand1Admin)
admin.site.register(ObservationStatesBand2Admin, ObservationStatesBand2Admin)
admin.site.register(TileStatesBand1Admin, TileStatesBand1Admin)
admin.site.register(TileStatesBand2Admin, TileStatesBand2Admin)
