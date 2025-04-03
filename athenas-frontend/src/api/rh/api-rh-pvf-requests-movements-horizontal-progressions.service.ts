import { usePost } from 'api/@base/use-post';

export interface Payload {
    progression: number;
    config: number;
    documents: {
        name: string;
        attachment_id: number;
    }[];
    termo_aceite: boolean;
}

export class ApiRhPvfRequestsMovementsHorizontalProgressions {
    id: number;
    request_type: number;
    date: Date;
    status: number;
    step_current: number;
    portal_request_type: number;
    request: number;
    employee: number;
    approver: number;
    progression: number;
    config: number;
    publication: number;
}

export async function apiRhPvfRequestsMovementsHorizontalProgressions(
    payload: Payload
) {
    try {
        const { data } =
            await usePost<ApiRhPvfRequestsMovementsHorizontalProgressions>(
                `/athenas/api/v2/rh/pvf/requests/movements/horizontal-progressions/`,
                payload
            );
        return { success: true, data };
    } catch (e) {
        return { success: false, message: e.response.data.message };
    }
}
