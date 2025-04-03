import { pvfUsufructsAcquisitionPeriods } from 'services/pvf/usufructs-acquisition-periods.service';
import { pvfConfigRequestsAcquisitionPeriods } from 'services/pvf-config-requests-acquisition-periods.service';
import { baseDatasourceFactory } from './base.datasource.factory';

export class PvfConfigRequestsAcquisitionPeriodsDataSource extends baseDatasourceFactory(
    pvfConfigRequestsAcquisitionPeriods
) {}
