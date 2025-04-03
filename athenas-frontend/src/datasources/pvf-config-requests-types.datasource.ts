import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfEmployeTeamService } from 'services/pvf-employe-team.service';
import { pvfConfigRequestsTypesService } from 'services/pvf-config-requests-types.service';

export class PvfConfigRequestTypesDataSource extends baseDatasourceFactory(
    pvfConfigRequestsTypesService
) {}
