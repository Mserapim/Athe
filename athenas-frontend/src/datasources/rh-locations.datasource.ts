import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhLocations } from 'api/rh/api-rh-locations.service';

export class RhLocationsDataSource extends baseDatasourceFactory(
    apiRhLocations
) {}
