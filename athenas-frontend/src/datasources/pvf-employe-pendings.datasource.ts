import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfEmployePendingsService } from 'services/pvf-employe-pendings.service';

export class PvfEmployePendingsDataSource extends baseDatasourceFactory(
    pvfEmployePendingsService
) {}
