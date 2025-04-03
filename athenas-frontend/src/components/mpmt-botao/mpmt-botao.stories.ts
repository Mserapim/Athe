import { Meta, StoryFn } from '@storybook/angular';
import { MpmtBotaoComponent } from './mpmt-botao.component';
import { moduleMetadata } from '@storybook/angular';
import { MpmtBotaoModule } from './mpmt-botao.module';

export default {
    title: 'Components/MpmtBotao', // Nome para identificar o componente no Storybook
    component: MpmtBotaoComponent,
    decorators: [
        moduleMetadata({
            imports: [MpmtBotaoModule],
        }),
    ],
    argTypes: {
        cor: {
            control: {
                type: 'select',
                options: [
                    'primario',
                    'secondario',
                    'terciario',
                    'branco',
                    'sucesso',
                    'critico',
                ], // Opções para o controle no Storybook
            },
        },
        tipo: {
            control: {
                type: 'select',
                options: ['preenchido', 'borda'], // Opções para o controle no Storybook
            },
        },
        isLoading: {
            control: 'boolean',
        },
        desabilitado: {
            control: 'boolean',
        },
        click: { action: 'clicked' }, // Usar a API de ações do Storybook para o evento de clique
    },
} as Meta<MpmtBotaoComponent>;

// Template de história
const Template: StoryFn<MpmtBotaoComponent> = (args) => ({
    component: MpmtBotaoComponent,
    props: {
        ...args, // Passa os argumentos como propriedades para o componente
        click: args.click ? args.click : () => {},
    },
    template: `<mpmt-botao [cor]="cor" [tipo]="tipo" [isLoading]="isLoading" [desabilitado]="desabilitado" (click)="click">{{ textoBotao }}</mpmt-botao>`, // Definindo o conteúdo como texto
});

// Define as histórias
export const Default = Template.bind({});
Default.args = {
    cor: 'primario',
    tipo: 'preenchido',
    isLoading: false,
    desabilitado: false,
    textoBotao: 'Botão padrão',
};

export const Disabled = Template.bind({});
Disabled.args = {
    cor: 'primario',
    tipo: 'preenchido',
    desabilitado: true,
    textoBotao: 'Botão desabilitado',
};

export const Loading = Template.bind({});
Loading.args = {
    cor: 'primario',
    tipo: 'preenchido',
    isLoading: true,
    textoBotao: 'Carregando...',
};
