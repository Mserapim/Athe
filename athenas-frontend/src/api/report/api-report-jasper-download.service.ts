import { useGet } from 'api/@base/use-get';

interface Payload {
    uuid: string;
}

class Response {}

export async function apiReportJasperDownload(payload: Payload) {
    const { data } = await useGet<Response>('report/jasper/download/', payload);
    return data;
}
