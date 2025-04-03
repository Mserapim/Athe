import { usePut } from 'api/@base/use-put';
import { ApiRhPvfRequestsMovementsHorizontalProgressions } from './api-rh-pvf-requests-movements-horizontal-progressions.service';

export async function apiUpdateRhPvfRequestMovementsHorizontalProgression(
    id,
    payload
) {
    try {
        const { data } =
            await usePut<ApiRhPvfRequestsMovementsHorizontalProgressions>(
                `/athenas/api/v2/rh/pvf/requests/movements/horizontal-progressions/${id}/`,
                payload
            );
        return { success: true, data };
    } catch (e) {
        return { success: false, message: e.response.data.message };
    }
}
