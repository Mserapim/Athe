import { usePost } from 'api/@base/use-post';

interface RetificationPayload {
    requestId: number;
    observation: string;
}

interface ApiRhPvfObservationRetificationResponse {
    pk: number;
    success: boolean;
    message: string;
}

export async function apiRetificateObservation(
    payload: RetificationPayload
): Promise<ApiRhPvfObservationRetificationResponse> {
    const { data } = await usePost<ApiRhPvfObservationRetificationResponse>(
        `/rh/pvf/requests/${payload.requestId}/observation-retification/`,
        payload
    );
    return data;
}
