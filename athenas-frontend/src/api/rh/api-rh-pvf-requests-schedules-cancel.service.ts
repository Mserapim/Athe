import { usePost } from 'api/@base/use-post';

interface Payload {
    usufruct_id: number;
    observation: string;
}

export class ApiRhPvfRequestsSchedulesCancelResponseItem {}

export async function apiRhPvfRequestsSchedulesCancel(payload: Payload) {
    const { data } = await usePost<ApiRhPvfRequestsSchedulesCancelResponseItem>(
        '/rh/pvf/requests/schedules/cancel/',
        payload
    );
    return data;
}
