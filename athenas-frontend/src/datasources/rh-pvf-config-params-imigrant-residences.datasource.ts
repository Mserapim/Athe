import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhConfigParamsImigrantResidencesService } from 'api/rh/api-rh-config-params-imigrant-residences.service';

export class RhConfigParamsImigrantResidencesDataSource extends baseDatasourceFactory(
    apiRhConfigParamsImigrantResidencesService
) {}
