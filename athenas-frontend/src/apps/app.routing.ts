import { Route } from '@angular/router';
import { LayoutComponent } from 'layout/layout.component';
import { InitialDataResolver } from 'apps/app.resolvers';
import { BasePaginaNaoEncontradaComponent } from './base/base-pagina-nao-encontrada/base-pagina-nao-encontrada.component';

// @formatter:off
/* eslint-disable max-len */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
export const appRoutes: Route[] = [
    { path: '', pathMatch: 'full', redirectTo: 'vdf/home' },

    {
        path: 'vdf',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'VDF',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/vdf/vdf.module').then((m) => m.VdfModule),
            },
        ],
    },
    {
        path: 'gestao-pessoas',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'gestao-pessoas',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/gestao-pessoas/gestao-pessoas.module').then(
                        (m) => m.GestaoPessoasModule
                    ),
            },
        ],
    },
    {
        path: 'painel-controle',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'painel-controle',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/painel-controle/painel-controle.module').then(
                        (m) => m.PainelControleModule
                    ),
            },
        ],
    },
    {
        path: 'movimentacao-carreira',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'movimentacao-carreira',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import(
                        'apps/movimentacao-carreira/movimentacao-carreira.module'
                    ).then((m) => m.MovimentacaoCarreiraModule),
            },
        ],
    },
    {
        path: 'anotacoes-pessoais',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'anotacoes-pessoais',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import(
                        'apps/anotacoes-pessoais/anotacoes-pessoais.module'
                    ).then((m) => m.AnotacoesPessoaisModule),
            },
        ],
    },
    {
        path: 'diarias',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'diarias',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/diarias/diarias.module').then(
                        (m) => m.DiariasModule
                    ),
            },
        ],
    },
    {
        path: 'defin',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'defin',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/defin/defin.module').then(
                        (m) => m.DefinModule
                    ),
            },
        ],
    },
    {
        path: 'e-social',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'e-social',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/e-social/e-social.module').then(
                        (m) => m.ESocialModule
                    ),
            },
        ],
    },
    {
        path: 'folha-ponto',
        canMatch: [],
        component: LayoutComponent,
        resolve: {
            initialData: InitialDataResolver,
        },
        data: {
            modulo: 'folha-ponto',
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/folha-ponto/folha-ponto.module').then(
                        (m) => m.FolhaPontoModule
                    ),
            },
        ],
    },
    {
        path: 'base',
        canMatch: [],
        resolve: {
            initialData: InitialDataResolver,
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/base/base.module').then((m) => m.BaseModule),
            },
        ],
    },
    {
        path: 'core',
        canMatch: [],
        resolve: {
            initialData: InitialDataResolver,
        },
        children: [
            {
                path: '',
                loadChildren: () =>
                    import('apps/core/core.module').then((m) => m.CoreModule),
            },
        ],
    },
    {
        path: '**',
        pathMatch: 'full',
        redirectTo: 'base/pagina-nao-encontrada',
    },
];
