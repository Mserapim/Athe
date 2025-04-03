import { baseDatasourceFactory } from './base.datasource.factory';
import { apiPvfRhPvfConfigRequestsCandidateSubstitutesService } from 'api/rh/api-rh-pvf-config-requests-candidate-substitutes.service';

export class PvfConfigRequestsCandidateSubstitutesDataSource extends baseDatasourceFactory(
    apiPvfRhPvfConfigRequestsCandidateSubstitutesService
) {}
