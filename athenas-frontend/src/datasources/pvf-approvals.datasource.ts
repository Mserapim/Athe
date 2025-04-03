import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhPvfApprovalsRequests } from 'api/rh/api-rh-pvf-approvals-requests.service';

export class PvfApprovalsDataSource extends baseDatasourceFactory(
    apiRhPvfApprovalsRequests
) {}
