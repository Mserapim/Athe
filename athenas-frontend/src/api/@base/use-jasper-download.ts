import { apiReportDownloadService } from 'api/report/api-report-download';
import { apiReportStatus } from 'api/report/api-report-status.service';
import axios from 'axios';
import { environment } from 'environments/environment';
import { useGet } from './use-get';

const API_URL = environment.api_endpoint || 'http://localhost:1231';
const url = (target: string) => {
    if (target.charAt(0) == '/') target = target.substring(1, 10000);
    return `${API_URL}/${target}`;
};

// const maxAttemps = 30;

async function waitReady(
    uuid: string,
    attempts: number = 0,
    maxAttemps: number = 30
) {
    try {
        const { status } = await apiReportStatus({
            uuid,
        });

        if (status == 'processing') {
            return await new Promise((res, rej) => {
                setTimeout(async () => {
                    const status = await waitReady(
                        uuid,
                        attempts + 1,
                        maxAttemps
                    );
                    res(status);
                }, 1000);
            });
        }

        if (status == 'fail') {
            throw 'Erro inesperado ao baixar o arquivo, favor, tente novamente';
        }
        return status;
    } catch (e) {
        throw e;
    }
}
export async function useJasperDownload<T>(
    uuid: string,
    attempts: number = 0,
    maxAttemps: number = 30,
    options: {
        automaticDownload: boolean;
    } = {
        automaticDownload: true,
    }
) {
    try {
        const status = await waitReady(uuid, attempts, maxAttemps);
        const link = url('/report/jasper/download/?uuid=' + uuid);
        if (options.automaticDownload) {
            window.open(link, '_blank');
        } else {
            const response = await useGet(
                `${link}&download=false`,
                {},
                {},
                'arraybuffer'
            );

            const contentType = response.headers['content-type'] as string;
            const blob = new Blob([response.data], { type: contentType });
            const url = URL.createObjectURL(blob);

            return url;
        }
    } catch (e) {
        alert(e);
    }

    return;
}
