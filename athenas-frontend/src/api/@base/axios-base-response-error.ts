export class AxiosBaseResponseError<M extends object | [] | undefined> extends Error {

    data?: M
    errors?: any
    loading?: boolean | undefined

    constructor(data: M, errors: any, loading: boolean) {
        super(errors)
        this.data = data
        this.errors = errors
        this.loading = loading
    }

    toString() {
        console.log('BaseResponseError', 'toString', this.errors)
        if (this.errors && this.errors.length > 0) {
            return this.errors[0]['message']
        }
        return super.toString()
    }

    get message() {
        console.log(this.errors)
        if (this.errors && this.errors.length > 0) {
            return this.errors[0]['message']
        }
        return super.toString()
    }
}
