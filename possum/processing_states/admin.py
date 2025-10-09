from django.contrib import admin
from .models import (ObservationBand1_1DPipelineValidation, ObservationBand2_1DPipelineValidation,
                     PartialTilePipelineRegionsBand1, PartialTilePipelineRegionsBand2,
                     SurveyTiles_3DPipelineBand1,  SurveyTiles_3DPipelineBand2)

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

class Observation1DBand1Admin(admin.ModelAdmin):
    readonly_fields = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline')
    list_display = [field.name for field in ObservationBand1_1DPipelineValidation._meta.get_fields()]
    search_fields = ['name__name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline', 'comments']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(Observation1DBand1Admin, self).get_queryset(request)
        return qs.filter()

class Observation1DBand2Admin(admin.ModelAdmin):
    readonly_fields = ('name', 'sbid', '_1d_pipeline_validation', 'single_SB_1D_pipeline')
    list_display = [field.name for field in ObservationBand2_1DPipelineValidation._meta.get_fields()]
    search_fields = [field.name for field in ObservationBand2_1DPipelineValidation._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(Observation1DBand2Admin, self).get_queryset(request)
        return qs.filter()

class SurveyTiles3DPipelineBand1Admin(admin.ModelAdmin):
    readonly_fields = ('tile_id', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_link')
    list_display = [field.name for field in SurveyTiles_3DPipelineBand1._meta.get_fields()]
    search_fields = ('tile_id__tile', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_comments',
                     '_3d_pipeline_val', '_3d_pipeline_validator', '_3d_val_link')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(SurveyTiles3DPipelineBand1Admin, self).get_queryset(request)
        return qs.filter()

class SurveyTiles3DPipelineBand2Admin(admin.ModelAdmin):
    readonly_fields = ('tile_id', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_link')
    list_display = [field.name for field in SurveyTiles_3DPipelineBand2._meta.get_fields()]
    search_fields = ('tile_id__tile', '_3d_pipeline', '_3d_pipeline_ingest', '_3d_val_comments',
                     '_3d_pipeline_val', '_3d_pipeline_validator', '_3d_val_link')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(SurveyTiles3DPipelineBand2Admin, self).get_queryset(request)
        return qs.filter()

admin.site.register(PartialTilePipelineRegionsBand1, PartialTile1DBand1Admin)
admin.site.register(PartialTilePipelineRegionsBand2, PartialTile1DBand2Admin)
admin.site.register(ObservationBand1_1DPipelineValidation, Observation1DBand1Admin)
admin.site.register(ObservationBand2_1DPipelineValidation, Observation1DBand2Admin)
admin.site.register(SurveyTiles_3DPipelineBand1, SurveyTiles3DPipelineBand1Admin)
admin.site.register(SurveyTiles_3DPipelineBand2, SurveyTiles3DPipelineBand2Admin)
