import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhConfigWorkplaces } from 'api/rh/api-rh-config-worksplaces.service';

export class PvfConfigServerShiftsWorkplacesDataSource extends baseDatasourceFactory(
    apiRhConfigWorkplaces
) {}
