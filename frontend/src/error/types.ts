export type NoError = {
    type: 'no-error'
}

export type RedBar = {
    type: 'red-bar'
    message: string;
}

export type ErrorState = NoError | RedBar

