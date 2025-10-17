from django.db import models


VALIDATED_STATE = (
        ('Good', 'Good'),
        ('Bad', 'Bad'),
        ('Running', 'Running'),
        ('Failed', 'Failed'),
        ('WaitingForValidation', 'WaitingForValidation'))

PIPELINE_STATE = (
        ('Completed', 'Completed'),
        ('Running', 'Running'),
        ('Failed', 'Failed'),
        ('WaitingForValidation', 'WaitingForValidation'),)

PARTIAL_TILES_TYPE = (
        ('center', 'center'),
        ('edge', 'edge'),
        ('corner', 'corner'),
        ('edge - crosses projection boundary!', 'edge - crosses projection boundary!'),
        ('corner - crosses projection boundary!', 'corner - crosses projection boundary!'),)

class PartialTilePipelineRegionsBand1(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    observation = models.ForeignKey('survey.Observation', models.CASCADE, db_column='observation')
    tile1 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile1', to_field='tile', related_name='band1_tile1')
    tile2 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile2', to_field='tile', related_name='band1_tile2')
    tile3 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile3', to_field='tile', related_name='band1_tile3')
    tile4 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile4', to_field='tile', related_name='band1_tile4')
    type = models.CharField(choices=PARTIAL_TILES_TYPE, db_column='type')
    number_sources = models.PositiveIntegerField(blank=True, null=True, db_column='number_sources')
    _1d_pipeline = models.CharField(choices=PIPELINE_STATE, db_column='1d_pipeline', blank=True, null=True)

    @property
    def sbid(self):
        return self.observation.sbid if self.observation else None

    class Meta:
        verbose_name = "Band 1 - Partial Tile 1D Pipeline"
        managed = False
        db_table = 'partial_tile_1d_pipeline_band1'
        unique_together = (('observation', 'tile1', 'tile2', 'tile3', 'tile4', 'type'),)

class PartialTilePipelineRegionsBand2(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    observation = models.ForeignKey('survey.Observation', models.CASCADE, db_column='observation', to_field='name')
    tile1 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile1', related_name='band2_tile1')
    tile2 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile2', related_name='band2_tile2')
    tile3 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile3', related_name='band2_tile3')
    tile4 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile4', related_name='band2_tile4')
    type = models.CharField(choices=PARTIAL_TILES_TYPE, db_column='type')
    number_sources = models.PositiveIntegerField(blank=True, null=True, db_column='number_sources')
    _1d_pipeline = models.CharField(choices=PIPELINE_STATE, db_column='1d_pipeline', blank=True, null=True)

    @property
    def sbid(self):
        return self.observation.sbid if self.observation else None

    class Meta:
        verbose_name = "Band 2 - Partial Tile 1D Pipeline"
        managed = False
        db_table = 'partial_tile_1d_pipeline_band2'
        unique_together = (('observation', 'tile1', 'tile2', 'tile3', 'tile4', 'type'),)

class ObservationStatesBand1(models.Model):
    name = models.OneToOneField('survey.Observation', models.CASCADE, db_column='name', to_field='name', primary_key=True)
    _1d_pipeline_validation = models.CharField(blank=True, null=True, db_column='1d_pipeline_validation')
    single_SB_1D_pipeline = models.CharField(blank=True, null=True, db_column='single_sb_1d_pipeline')
    comments = models.TextField(blank=True, null=True, db_column='comments')
    mfs_update = models.DateTimeField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    cube_update = models.DateTimeField(blank=True, null=True)
    cube_state = models.TextField(blank=True, null=True)

    @property
    def sbid(self):
        return self.name.sbid if self.name else None

    class Meta:
        verbose_name = "Band 1 - Observation State"
        managed = False
        db_table = 'observation_state_band1'

class ObservationStatesBand2(models.Model):
    name = models.OneToOneField('survey.Observation', models.CASCADE, db_column='name', to_field='name', primary_key=True)
    _1d_pipeline_validation = models.CharField(blank=True, null=True, db_column='1d_pipeline_validation')
    single_SB_1D_pipeline = models.CharField(blank=True, null=True, db_column='single_sb_1d_pipeline')
    comments = models.TextField(blank=True, null=True, db_column='comments')
    mfs_update = models.DateTimeField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    cube_update = models.DateTimeField(blank=True, null=True)
    cube_state = models.TextField(blank=True, null=True)

    @property
    def sbid(self):
        return self.name.sbid if self.name else None

    class Meta:
        verbose_name = "Band 2 - Observation State"
        managed = False
        db_table = 'observation_state_band2'

class TileStatesBand1(models.Model):
    tile = models.OneToOneField('survey.Tile', models.DO_NOTHING, db_column='tile', to_field='tile', primary_key=True)
    _3d_pipeline = models.DateTimeField(blank=True, null=True, db_column='3d_pipeline')
    _3d_pipeline_val = models.CharField( blank=True, null=True, choices=VALIDATED_STATE, db_column='3d_pipeline_val')
    _3d_pipeline_ingest = models.CharField(blank=True, null=True, db_column='3d_pipeline_ingest')
    _3d_pipeline_validator = models.CharField(blank=True, null=True, db_column='3d_pipeline_validator')
    _3d_val_link = models.CharField(blank=True, null=True, db_column='3d_val_link')
    _3d_val_comments = models.TextField(blank=True, null=True, db_column='3d_val_comments')
    cube_state = models.TextField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Band 1 - Tile State"
        managed = False
        db_table = 'tile_state_band1'

class TileStatesBand2(models.Model):
    tile = models.OneToOneField('survey.Tile', models.DO_NOTHING, db_column='tile', to_field='tile', primary_key=True)
    _3d_pipeline = models.CharField(blank=True, null=True, db_column='3d_pipeline')
    _3d_pipeline_val = models.CharField( blank=True, null=True, choices=VALIDATED_STATE, db_column='3d_pipeline_val')
    _3d_pipeline_ingest = models.CharField(blank=True, null=True, db_column='3d_pipeline_ingest')
    _3d_pipeline_validator = models.CharField(blank=True, null=True, db_column='3d_pipeline_validator')
    _3d_val_link = models.CharField(blank=True, null=True, db_column='3d_val_link')
    _3d_val_comments = models.TextField(blank=True, null=True, db_column='3d_val_comments')
    cube_state = models.TextField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Band 2 - Tile State"
        managed = False
        db_table = 'tile_state_band2'
