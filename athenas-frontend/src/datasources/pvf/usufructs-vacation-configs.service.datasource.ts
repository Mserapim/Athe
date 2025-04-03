import { baseDatasourceFactory } from '../base.datasource.factory';
import { apiRhPvfConfigRequestsVacationConfigs } from 'api/rh/api-rh-pvf-config-requests-vacation-configs.service';

export class pvfUsufructsVacationConfigsDataSource extends baseDatasourceFactory(
    apiRhPvfConfigRequestsVacationConfigs
) {}
