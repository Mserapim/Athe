import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfCandidatSubstitutesService } from 'services/pvf-candidate-substitutes.service';
import { pvfEventsService } from 'services/pvf-events';

export class PvfEventsDataSource extends baseDatasourceFactory(
    pvfEventsService
) {}
