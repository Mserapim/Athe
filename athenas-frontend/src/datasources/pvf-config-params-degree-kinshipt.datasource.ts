import { baseDatasourceFactory } from './base.datasource.factory';
import { pvfConfigParamsDegreeKinshiptService } from 'services/pvf-config-params-degree-kinshipt.service';

export class pvfConfigParamsDegreeKinshiptDataSource extends baseDatasourceFactory(
    pvfConfigParamsDegreeKinshiptService
) {}
