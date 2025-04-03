import { Injectable } from '@angular/core';
import { Observable, ReplaySubject, firstValueFrom, map } from 'rxjs';
import { Navigation } from 'core/navigation/navigation.types';
import { FuseNavigationItem } from '@fuse/components/navigation';
import { uniqueId } from 'lodash';
import { Grupo } from 'core/tipos/grupo';
import { Menu } from 'core/tipos/Menu';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { Modulo } from 'core/tipos/modulo';
import { Router } from '@angular/router';
import { Favorito } from 'core/tipos/Favorito';

@Injectable({
    providedIn: 'root',
})
export class LayoutNavegacaoService {
    private _navigation: ReplaySubject<Navigation> =
        new ReplaySubject<Navigation>(1);

    /**
     */
    constructor(
        private router: Router,
        private navegacaoAtualService: NavegacaoAtualService
    ) {
        this.observarNavegacaoAtual();
    }

    async observarNavegacaoAtual() {
        this.navegacaoAtualService.navegacaoAtual$.subscribe(async (grupos) => {
            const fuseNavegation = await this.construirFuseNavegation(grupos);
            this._navigation.next(fuseNavegation);
        });
    }

    /**
     * Construir navegação completa no padrão do fuse
     */
    async construirFuseNavegation(grupos: Grupo[]): Promise<Navigation> {
        const moduloAtual: Modulo = await firstValueFrom(
            this.navegacaoAtualService.moduloAtual$
        );

        const favoritosAtual: Favorito[] = await firstValueFrom(
            this.navegacaoAtualService.favoritosAtual$
        );

        const gruposBuilded = (grupos || []).flatMap((grupo) =>
            this.construirMenuGroup(moduloAtual, grupo)
        );

        if (favoritosAtual && favoritosAtual.length > 0) {
            const favoritoGroup = <FuseNavigationItem[]>[
                {
                    id: '' + uniqueId(),
                    title: 'Favoritos',
                    type: 'collapsable',
                    icon: 'star',
                    children: this.construirMenuItems(favoritosAtual),
                },
            ];
            gruposBuilded.unshift(...favoritoGroup);
        }

        let menus;
        if (gruposBuilded.length == 1) {
            menus = gruposBuilded[0].children;
        } else {
            menus = gruposBuilded;
        }

        return {
            default: menus,
            compact: menus,
            futuristic: menus,
            horizontal: menus,
        };
    }

    construirMenuGroup(modulo: Modulo, grupo: Grupo) {
        return <FuseNavigationItem[]>[
            {
                id: '' + uniqueId(),
                title: grupo.nome,
                type: 'collapsable',
                icon: grupo?.icone || 'home',
                children: this.construirMenuItems(grupo.menus),
            },
        ];
    }

    construirMenuItems(menus: Menu[] | Favorito[]) {
        return menus
            .filter((x) => x.situacao == 'ATIVO')
            .map((menu) => {
                return <FuseNavigationItem>{
                    id: '' + (menu?.pk || menu?.id),
                    title: menu.nome,
                    type: 'basic',
                    icon: menu?.icone || 'home',
                    meta: menu,
                    subtitle: menu.descricao,
                    link: menu.url,
                    function: (item: FuseNavigationItem) => {
                        let url = menu.url;
                        if (menu.url.startsWith('/')) url += '/' + menu.url;
                        this.router.navigate([menu.url]);
                    },
                };
            });
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Accessors
    // -----------------------------------------------------------------------------------------------------

    /**
     * Getter for navigation
     */
    get navigation$(): Observable<Navigation> {
        return this._navigation.asObservable();
    }
}
