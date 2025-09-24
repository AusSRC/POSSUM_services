from django.db import models


VALIDATED_STATE = (
        ('Good', 'Good'),
        ('Bad', 'Bad'),)

PIPELINE_STATE = (
        ('Completed', 'Completed'),
        ('Running', 'Running'),
        ('Failed', 'Failed'),
        ('WaitingForValidation', 'WaitingForValidation'),)

class PartialTilePipelineRegionsBand1(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    observation = models.ForeignKey('survey.Observation', models.DO_NOTHING, db_column='observation', blank=True, null=True)
    sbid = models.BigIntegerField(blank=True, null=True, db_column='sbid')
    tile1 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile1', to_field='tile', related_name='band1_tile1')
    tile2 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile2', to_field='tile', related_name='band1_tile2')
    tile3 = models.ForeignKey('survey.Tile', models.DO_NOTHING,db_column='tile3', to_field='tile', related_name='band1_tile3')
    tile4 = models.ForeignKey('survey.Tile', models.DO_NOTHING,db_column='tile4', to_field='tile', related_name='band1_tile4')
    type = models.TextField(blank=True, null=True, db_column='type')
    number_sources = models.PositiveIntegerField(blank=True, null=True, db_column='number_sources')
    _1d_pipeline = models.CharField(choices=PIPELINE_STATE, db_column='1d_pipeline')
  
    class Meta:
        managed = False
        db_table = 'partial_tile_1d_pipeline_band1'
        unique_together = (('observation', 'sbid', 'tile1', 'tile2', 'tile3', 'tile4', 'type'),)

class PartialTilePipelineRegionsBand2(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    observation = models.ForeignKey('survey.Observation', models.DO_NOTHING, db_column='observation', to_field='name', blank=True, null=True)
    sbid = models.BigIntegerField(blank=True, null=True, db_column='sbid')
    tile1 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile1', related_name='band2_tile1')
    tile2 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile2', related_name='band2_tile2')
    tile3 = models.ForeignKey('survey.Tile', models.DO_NOTHING,db_column='tile3', related_name='band2_tile3')
    tile4 = models.ForeignKey('survey.Tile', models.DO_NOTHING,db_column='tile4', related_name='band2_tile4')
    type = models.TextField(blank=True, null=True, db_column='type')
    number_sources = models.PositiveIntegerField(blank=True, null=True, db_column='number_sources')
    _1d_pipeline = models.CharField(choices=PIPELINE_STATE, db_column='1d_pipeline')
    
    class Meta:
        managed = False
        db_table = 'partial_tile_1d_pipeline_band2'
        unique_together = (('observation', 'sbid', 'tile1', 'tile2', 'tile3', 'tile4', 'type'),)
    
class ObservationBand1_1DPipelineValidation(models.Model):
    name = models.OneToOneField('survey.Observation', models.DO_NOTHING, db_column='name', to_field='name', primary_key=True)
    sbid = models.BigIntegerField(blank=True, null=True, db_column='sbid')
    _1d_pipeline_validation = models.TextField(blank=True, null=True, db_column='1d_pipeline_validation')
    single_SB_1D_pipeline = models.TextField(blank=True, null=True, db_column='single_sb_1d_pipeline')
    comments = models.TextField(blank=True, null=True, db_column='comments')
    
    class Meta:
        managed = False
        db_table = 'observation_1d_pipeline_band1'
    
class ObservationBand2_1DPipelineValidation(models.Model):
    name = models.OneToOneField('survey.Observation', models.DO_NOTHING, db_column='name', to_field='name', primary_key=True)
    sbid = models.BigIntegerField(blank=True, null=True, db_column='sbid')
    _1d_pipeline_validation = models.TextField(blank=True, null=True, db_column='1d_pipeline_validation')
    single_SB_1D_pipeline = models.TextField(blank=True, null=True, db_column='single_sb_1d_pipeline')
    comments = models.TextField(blank=True, null=True, db_column='comments')
    
    class Meta:
        managed = False
        db_table = 'observation_1d_pipeline_band2'
        
class SurveyTiles_3DPipeline(models.Model):
    tile_id = models.OneToOneField('survey.Tile', models.DO_NOTHING, db_column='tile_id', to_field='tile', primary_key=True)
    _3d_pipeline_band1 = models.TextField(blank=True, null=True, db_column='3d_pipeline_band1')
    _3d_pipeline_band2 = models.TextField(blank=True, null=True, db_column='3d_pipeline_band2')
    _3d_pipeline_val_band1 = models.CharField(choices=VALIDATED_STATE, db_column='3d_pipeline_val_band1')
    _3d_pipeline_val_band2 = models.CharField(choices=VALIDATED_STATE, db_column='3d_pipeline_val_band2')
    _3d_pipeline_ingest_band1 = models.TextField(blank=True, null=True, db_column='3d_pipeline_ingest_band1')
    _3d_pipeline_ingest_band2 = models.TextField(blank=True, null=True, db_column='3d_pipeline_ingest_band2')
	
    class Meta:
        managed = False
        db_table = 'tile_3d_pipeline'
