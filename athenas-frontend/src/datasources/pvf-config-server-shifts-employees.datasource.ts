import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhPvfConfigEmployeesService } from 'api/rh/api-rh-pvf-config-employees.service';

export class PvfConfigServerShiftsEmployeesDataSource extends baseDatasourceFactory(
    apiRhPvfConfigEmployeesService
) {}
