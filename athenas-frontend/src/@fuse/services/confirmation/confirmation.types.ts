export interface FuseConfirmationConfig
{
    title?: string;
    message?: string;
    icon?: {
        show?: boolean;
        name?: string;
        color?: 'primary' | 'accent' | 'warn' | 'basic' | 'info' | 'success' | 'warning' | 'error';
    };
    actions?: {
        confirm?: {
            show?: boolean;
            label?: string;
            style?: { 'background-color': string };
            class?: string;
            useStyle?: boolean;
            useClass?: boolean;
        };
        cancel?: {
            show?: boolean;
            label?: string;
            style?: { 'background-color': string };
            class?: string;
            useStyle?: boolean;
            useClass?: boolean;
        };
    };
    dismissible?: boolean;
}
