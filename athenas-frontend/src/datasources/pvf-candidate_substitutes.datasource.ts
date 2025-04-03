import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfCandidatSubstitutesService } from 'services/pvf-candidate-substitutes.service';

export class pvfCandidateSubstitutesDataSource extends baseDatasourceFactory(
    pvfCandidatSubstitutesService
) {}
