import { apiRhConfigParamsImigrantConditionsService } from 'api/rh/api-rh-config-params-imigrant-conditions.service';
import { baseDatasourceFactory } from './base.datasource.factory';

export class RhConfigParamsImigrantConditionsDataSource extends baseDatasourceFactory(
    apiRhConfigParamsImigrantConditionsService
) {}
