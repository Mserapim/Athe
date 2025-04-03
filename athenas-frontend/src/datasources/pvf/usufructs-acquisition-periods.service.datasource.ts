import { baseDatasourceFactory } from '../base.datasource.factory';
import { pvfConfigRequestsAcquisitionPeriods } from '../../services/pvf-config-requests-acquisition-periods.service';

export class PvfUsufructsAcquisitionPeriodsDataSource extends baseDatasourceFactory(
    pvfConfigRequestsAcquisitionPeriods
) {}
