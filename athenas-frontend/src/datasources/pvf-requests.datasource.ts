import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfEmployeTeamService } from 'services/pvf-employe-team.service';
import { pvfRequestsService } from 'services/pvf-requests.service';

export class PvfRequestsDataSource extends baseDatasourceFactory(
    pvfRequestsService
) {}
