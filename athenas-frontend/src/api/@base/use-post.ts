import { AxiosBaseResponse } from './axios-base-response';
import axios from 'axios';
import { environment } from 'environments/environment';

const API_URL = environment.api_endpoint || 'http://localhost:1231';

const url = (target: string) => {
    if (target.charAt(0) == '/') target = target.substring(1, 10000);
    return `${API_URL}/${target}`;
};

export const usePost = async <M extends object | [] = any>(
    target: string,
    params: any,
    headers: any = undefined
): Promise<AxiosBaseResponse<M>> => {
    return await axios
        .post(url(target), params, {
            headers: { ...headers, remote: environment.remote },
        })
        .catch((error) => {
            // console.log('error', error);
            throw error;
            // new AxiosBaseResponse<M>(error);
        })
        .then((response) => {
            return new AxiosBaseResponse<M>(response);
        });
};
