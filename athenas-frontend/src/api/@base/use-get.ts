import { AxiosBaseResponse } from './axios-base-response';
import axios, { ResponseType } from 'axios';
import { environment } from 'environments/environment';

const API_URL = environment.api_endpoint || 'http://localhost:1231';
const url = (target: string) => {
    if (target.charAt(0) == '/') target = target.substring(1, 10000);
    return `${API_URL}/${target}`;
};
export const useGet = async <M extends object | [] = any>(
    target: string,
    payload: any = {},
    headers: any = {},
    responseType: ResponseType = undefined
): Promise<AxiosBaseResponse<M>> => {
    return await axios
        .get(url(target), {
            headers: { ...headers, remote: environment.remote },
            params: payload,
            data: payload,
            responseType: responseType,
        })
        .catch((error) => {
            throw new AxiosBaseResponse<M>(error?.response || error);
        })
        .then((response) => {
            return new AxiosBaseResponse<M>(response);
        });
};
