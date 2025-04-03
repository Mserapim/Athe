import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfEmployeTeamService } from 'services/pvf-employe-team.service';
import { pvfEventTypesService } from 'services/pvf-event-types.service';

export class PvfEventTypesDataSource extends baseDatasourceFactory(
    pvfEventTypesService
) {}
