import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Menu } from 'core/tipos/Menu';
import { Title } from '@angular/platform-browser';
import { NavigationEnd, Router } from '@angular/router';
import { apiPainelControleControleAcessoMenuUsuario } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-usuario.service';
import { Modulo } from 'core/tipos/modulo';
import { Grupo } from 'core/tipos/grupo';
import { Favorito } from 'core/tipos/Favorito';
import { FuseLoadingService } from '@fuse/services/loading';

@Injectable({
    providedIn: 'root',
})
export class NavegacaoAtualService {
    /** Modulos do usuário */
    public modulosSubject = new BehaviorSubject<Modulo[]>([]);
    /** Modulo Atual */
    public moduloAtualSubject = new BehaviorSubject<Modulo>(null);
    /** Menus do modulo atual */
    public navegacaoAtualSubject = new BehaviorSubject<Grupo[]>([]);
    /** Favoritos */
    public favoritosAtualSubject = new BehaviorSubject<Favorito[]>([]);
    /** Pagina atual */
    public paginaAtualSubject = new BehaviorSubject<Menu | undefined>(
        undefined
    );
    /** Rota atual */
    public urlAtualSubject = new BehaviorSubject<string>(undefined);

    /** Permissão atual */
    public acoesSubject = new BehaviorSubject<string[]>(undefined);

    public permissoesPaginaAtual: string[] = [];

    constructor(
        private router: Router,
        private fuseLoadingService: FuseLoadingService,
        private titleService: Title
    ) {
        this.recarregar();
        this.manterUrlAtualAtualizado();
        this.manterPaginaAtualAtualizado();
        this.manterNavegacaoAtualAtualizado();
        this.manterModuloAtualAtualizado();
    }

    /**  */
    private manterUrlAtualAtualizado() {
        this.router.events.subscribe(async (data: any) => {
            if (data instanceof NavigationEnd) {
                const urlOriginal = data.url;
                if (!urlOriginal) return;

                let url = urlOriginal;
                if (urlOriginal.startsWith('/')) {
                    url = urlOriginal?.substring(1, 1000);
                }
                if (url == '') url = 'vdf/home';
                this.urlAtualSubject.next(url);
            }
        });
    }

    /**  */
    private manterNavegacaoAtualAtualizado() {
        this.moduloAtual$.subscribe(async (modulo) => {
            if (!modulo) return;
            const navegacaoCompleta = this.modulosSubject.value;
            const navegacao = navegacaoCompleta.find(
                ({ pk }) => pk == modulo?.pk
            );
            if (!navegacao)
                return console.warn(
                    'MODULO NÃO TEM MENU',
                    modulo,
                    navegacaoCompleta
                );
            this.navegacaoAtualSubject.next(navegacao.grupos);
        });
    }

    /**
     */
    private async manterModuloAtualAtualizado() {
        this.paginaAtualSubject.asObservable().subscribe(async (pagina) => {
            this.moduloAtualSubject.next(pagina?.modulo);
        });
    }

    /**
     */
    private async manterPaginaAtualAtualizado() {
        this.urlAtualSubject.asObservable().subscribe(async (url) => {
            if (!url) return;
            if (
                !this.modulosSubject.value ||
                this.modulosSubject.value.length <= 0
            )
                return;

            const pagina = await this.modulosSubject.value
                .flatMap((x) => x.grupos)
                .flatMap((x) => x.menus)
                .find((x) => {
                    return url
                        ?.toUpperCase()
                        ?.trim()
                        .startsWith(x.url?.toUpperCase()?.trim());
                });

            /** fix - 25/05/2024 - permitir acessar o registro de ponto mesmo fora do menu*/
            if (url == 'vdf/registro-ponto') return;

            if (!pagina) {
                return this.router.navigate(['base/pagina-nao-encontrada']);
            }

            this.atualizarTituloPagina(pagina);
            this.atualizarPermissoesPagina(pagina);
            this.paginaAtualSubject.next(pagina);
            this.acoesSubject.next(pagina.acoes);
        });
    }

    private atualizarTituloPagina(pagina: Menu) {
        const title = [pagina?.nome, 'Suíte Athenas']
            .filter((x) => x)
            .join(' - ');
        this.titleService.setTitle(title);
    }

    /**  */
    public async trocarModulo(modulo: Modulo) {
        if (!modulo) return;
        const grupos = modulo.grupos;
        if (!grupos || grupos.length <= 0) return;
        const menus = grupos[0].menus;
        if (!menus || menus.length <= 0) return;

        this.router.navigate([menus[0].url]);
    }
    /**
     * */
    public async recarregar() {
        this.fuseLoadingService.show();

        const { results } = await apiPainelControleControleAcessoMenuUsuario({
            situacao: 'ATIVO',
            retornar_favoritos: true,
        });

        const mapped = [];

        const modulos = results.filter((x) => !x.menus_favoritos);

        const menuMapped = modulos
            .flatMap((x) => {
                return x.grupos.flatMap((y) => {
                    return y.menus.flatMap((z) => z);
                });
            })
            .reduce((obj, menu) => {
                obj[menu.pk] = menu;
                return obj;
            }, <Record<number, Menu>>{});

        const favoritos = (
            results.find((x) => x.menus_favoritos)?.menus_favoritos || []
        ).map((x) => {
            const menu = menuMapped[x.id];
            return <Menu>{
                id: x.id,
                nome: x.nome,
                acoes: menu?.acoes || [],
                ordem: 1,
                situacao: 'ATIVO',
                url: x.url,
                favorito: false,
                descricao: menu?.descricao,
                icone: menu?.icone || 'home',
            };
        });

        /** Normalizar a informação **/
        for await (const modulo of modulos) {
            const grupos = modulo.grupos;

            for await (const grupo of grupos) {
                const menus = grupo.menus;

                for await (const menu of menus) {
                    menu.favorito = favoritos.some((x) => x.id == menu.pk);
                    menu.modulo = {
                        pk: modulo.pk,
                        sigla: modulo.sigla,
                        nome: modulo.nome,
                        icone: modulo.icone,
                        codigo: modulo.sigla,
                    };
                }
            }

            mapped.push(modulo);
        }

        this.modulosSubject.next(<Modulo[]>(<unknown>mapped));
        this.favoritosAtualSubject.next(favoritos);

        this.fuseLoadingService.hide();

        if (!this.urlAtualSubject.value) return;
        this.urlAtualSubject.next(this.urlAtualSubject.value);
    }

    public get modulos$(): Observable<Modulo[]> {
        return this.modulosSubject.asObservable();
    }

    public get moduloAtual$(): Observable<Modulo> {
        return this.moduloAtualSubject.asObservable();
    }

    public get navegacaoAtual$(): Observable<Grupo[]> {
        return this.navegacaoAtualSubject.asObservable();
    }

    public get favoritosAtual$(): Observable<Favorito[]> {
        return this.favoritosAtualSubject.asObservable();
    }

    public get paginaAtual$(): Observable<Menu> {
        return this.paginaAtualSubject.asObservable();
    }

    public get acoes$(): Observable<string[]> {
        return this.acoesSubject.asObservable();
    }

    public obterAcoesPaginaAtual(): string[] | [] {
        const paginaAtual = this.paginaAtualSubject.value;
        return paginaAtual?.acoes;
    }

    private atualizarPermissoesPagina(pagina: Menu) {
        this.permissoesPaginaAtual = pagina?.acoes;
    }

    public possuiPermissao(permissao: string): boolean {
        if (this.permissoesPaginaAtual?.includes(permissao)) {
            return true;
        }
        return false;
    }
}
