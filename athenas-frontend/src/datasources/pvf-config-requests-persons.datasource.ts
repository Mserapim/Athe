import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfConfigRequestsAbsencesTypesService } from 'services/pvf-config-requests-absences-types.service';
import { pvfConfigRequestsPersonsService } from 'services/pvf-config-requests-persons.service';

export class PvfConfigRequestsPersonsDataSource extends baseDatasourceFactory(
    pvfConfigRequestsPersonsService
) {}
