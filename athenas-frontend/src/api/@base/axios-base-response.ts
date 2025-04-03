import { AxiosBaseResponseError } from './axios-base-response-error';
import axios, { AxiosError } from 'axios';

export class AxiosBaseResponse<M extends object | []> {
    data?: M;
    response?: any;
    headers?: any;
    errors?: any;
    loading?: boolean | undefined;

    constructor(response: any) {
        if (response instanceof AxiosError) {
            const errors = [response.message];
            throw new AxiosBaseResponseError(undefined, errors, false);
        } else {
            this.response = response;
            this.data = response.data;
            this.headers = response.headers;
        }
    }
}
