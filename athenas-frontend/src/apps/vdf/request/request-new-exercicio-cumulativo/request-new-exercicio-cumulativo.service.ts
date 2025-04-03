import { Injectable } from '@angular/core';
import { apiRhPvfRequestsUsufructsIndividualVacationsService } from 'api/rh/api-rh-pvf-requests-usufructs-individual-vacations.service';
import { apiRhPvfRequestsUsufructsRegularVacations } from 'api/rh/api-rh-pvf-requests-usufructs-regular-vacations.service';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfRequestsUsufructsElectoralSlackService } from 'api/rh/api-rh-pvf-requests-usufructs-electoral-slack.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { addDay } from 'utils/add-day';
import { CurrentUserService } from 'core/current-user/current-user.service';
import {
    ApiRhPvfConfigRequestsAcquisitionPeriodsItem,
    apiRhPvfConfigRequestsAcquisitionPeriods,
} from 'api/rh/api-rh-pvf-config-requests-acquisition-periods.service';

@Injectable({
    providedIn: 'root',
})
export class RequestNewExercicioCumulativoService {
    title = 'Dispensa eleitoral';
    path = 'dispensa-eleitoral';
    type_usufruct = TypeUsufructEnum.FOLGA_ELEITORAL;
}
