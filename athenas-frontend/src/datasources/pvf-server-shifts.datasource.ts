import { apiRhPvfScalesServerShiftsService } from 'api/rh/api-rh-pvf-scales-server-shifts.service';
import { baseDatasourceFactory } from './base.datasource.factory';

export class PvfServerShiftsDataSource extends baseDatasourceFactory(
    apiRhPvfScalesServerShiftsService
) {}
