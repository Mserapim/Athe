import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfConfigRequestsAbsencesTypesService } from 'services/pvf-config-requests-absences-types.service';

export class PvfConfigRequestsAbsencesTypesDataSource extends baseDatasourceFactory(
    pvfConfigRequestsAbsencesTypesService
) {}
