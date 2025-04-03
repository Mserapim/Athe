import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfConfigRequestStatusService } from 'services/pvf-config-requests-status.service';

export class PvfConfigRequestStatusDataSource extends baseDatasourceFactory(
    pvfConfigRequestStatusService
) {}
