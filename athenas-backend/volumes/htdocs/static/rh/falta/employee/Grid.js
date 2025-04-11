/**
 *
 **/
Ext._define('rh.falta.employee.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.falta.employee.Window',

    keywordFieldMessage: 'Palavra-chave',

    hideItemsToolbar: ['add', 'edit', 'remove'],

    configOrderToolBar: ['-', 'search', '->'],

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        var departament = cfg.departament;
        if (departament == undefined || departament == 'expediente')
            departament = 'rh';
        Ext.applyIf(cfg, {
            departament: departament,
            gridAutoLoad: true,
            situationMenuValue: [
                {
                    name: 'active',
                    checked: true,
                    value: true,
                },
                {
                    name: 'finished',
                    checked: true,
                    value: false,
                },
            ],
            typePossessionItems: [
                {
                    name: 'efective',
                    checked: false,
                    value: 'EFE',
                },
                {
                    name: 'comissioned',
                    checked: false,
                    value: 'CMS',
                },
                {
                    name: 'requested',
                    checked: false,
                    value: 'REQ',
                },
                {
                    name: 'requestedrex',
                    checked: false,
                    value: 'REX',
                },
                {
                    name: 'efecm',
                    checked: false,
                    value: 'ECM',
                },
                {
                    name: 'reqcm',
                    checked: false,
                    value: 'RCM',
                },
                {
                    name: 'reqfc',
                    checked: false,
                    value: 'RFC',
                },
                {
                    name: 'trainee',
                    checked: false,
                    value: 'EST',
                },
                {
                    name: 'voluntare',
                    checked: false,
                    value: 'VOL',
                },
                {
                    name: 'extern',
                    checked: false,
                    value: 'EXT',
                },
                {
                    name: 'residentes',
                    checked: false,
                    value: 'RES',
                },
            ],
            tipoFaltaMenuValue: [
                {
                    name: 'justificada',
                    checked: true,
                    value: true,
                },
                {
                    name: 'injustificada',
                    checked: true,
                    value: false,
                },
            ],
            situacaoFaltaMenuValue: [
                {
                    name: 'aguardando_processar',
                    checked: true,
                    value: 1,
                },
                {
                    name: 'processada',
                    checked: false,
                    value: 2,
                },
                {
                    name: 'removida',
                    checked: false,
                    value: 3,
                },
            ],
            impactoFinanceiroMenuValue: [
                {
                    name: 'com_impacto',
                    checked: true,
                    value: true,
                },
                {
                    name: 'sem_impacto',
                    checked: true,
                    value: false,
                },
            ],
            verTodosMenuValue: [
                {
                    name: 'active',
                    checked: false,
                    value: true,
                },
            ],
            trabalhoRemotoMenuValue: [
                {
                    name: 'sim',
                    checked: false,
                    value: true,
                },                
            ],
        });

        this.departament = cfg.departament;
        this.situationMenuValue = cfg.situationMenuValue;
        this.typePossessionItems = cfg.typePossessionItems;
        this.tipoFaltaMenuValue = cfg.tipoFaltaMenuValue;
        this.situacaoFaltaMenuValue = cfg.situacaoFaltaMenuValue;
        this.impactoFinanceiroMenuValue = cfg.impactoFinanceiroMenuValue;
        this.verTodosMenuValue = cfg.verTodosMenuValue;
        this.trabalhoRemotoMenuValue = cfg.trabalhoRemotoMenuValue;

        rh.falta.employee.Grid.superclass.constructor.call(this, cfg);

        this.__setFilterPropertyDefault(this.gridAutoLoad);
    },

    __setFilterPropertyDefault: function (gridAutoLoad, ano, mes) {
        var situationMenuValueToFilter = [];
        var filterTypePossession = [];
        var tipoFaltaMenuValueToFilter = [];
        var situacaoFaltaMenuValueToFilter = [];
        var impactoFinanceiroMenuValueToFilter = [];
        var verTodosMenuValueToFilter = [];
        var trabalhoRemotoMenuValueToFilter = [];

        this._situationItems.forEach(
            function (item) {
                if (item.checked)
                    situationMenuValueToFilter.push(item.value);
            }
        );
        this._possessionType.forEach(
            function (item) {
                if (item.checked)
                    filterTypePossession.push(item.value);
            }
        );
        this._tipoFaltaItems.forEach(
            function (item) {
                if (item.checked)
                    tipoFaltaMenuValueToFilter.push(item.value);
            }
        );
        this._situacaoFaltaItems.forEach(
            function (item) {
                if (item.checked)
                    situacaoFaltaMenuValueToFilter.push(item.value);
            }
        );
        this._impactoFinanceiroItems.forEach(
            function (item) {
                if (item.checked)
                    impactoFinanceiroMenuValueToFilter.push(item.value);
            }
        );
        this._verTodosItems.forEach(
            function (item) {
                if (item.checked)
                    verTodosMenuValueToFilter.push(item.value);
            }
        );
        this._trabalhoRemotoItems.forEach(
            function (item) {
                if (item.checked)
                    trabalhoRemotoMenuValueToFilter.push(item.value);
            }
        );

        if (situationMenuValueToFilter.length > 0) {
            this.setFilterProperty('servidor__ativo__in', situationMenuValueToFilter, 1, false);
        }
        if (filterTypePossession.length > 0) {
            this.setFilterProperty('servidor__type_by_possession__in', filterTypePossession, 2, false);
        }
        if (tipoFaltaMenuValueToFilter.length > 0) {
            this.setFilterProperty('justificado__in', tipoFaltaMenuValueToFilter, 5, false);
        }
        if (situacaoFaltaMenuValueToFilter.length > 0) {
            this.setFilterProperty('situacao__in', situacaoFaltaMenuValueToFilter, 6, false);
        }
        if (impactoFinanceiroMenuValueToFilter.length > 0) {
            this.setFilterProperty('payroll__in', impactoFinanceiroMenuValueToFilter, 7, false);
        }
        if (verTodosMenuValueToFilter.length > 0) {
            this.setFilterProperty('ver_todos', verTodosMenuValueToFilter, 8, false);
        }
        if (trabalhoRemotoMenuValueToFilter.length > 0) {
            this.setFilterProperty('servidor__movimentacaopessoal__movimentacaoteletrabalho__ativo__in', trabalhoRemotoMenuValueToFilter, 9, gridAutoLoad);
        }

        if (ano && mes) {
            this.filtrarAnoMes(ano, mes);
        } else {
            this.filtrarAnoMes(ano);
        }

        if (gridAutoLoad) {
            var store = this.getStore();
            store.load({});
        }
    },
    
    showBoolean: function (value) {
        return value ? 'SIM' : 'NÃO';
    },

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Chave', dataIndex: 'servidor_pk', width: 55, hidden: true },
                    { header: 'Ativo', dataIndex: 'ativo', width: 40, renderer: toolkit.util.formatIconYesNo },
                    { header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function (value) { return '<div style="text-align:right">' + value + '</div>'; } },
                    { header: 'Nome', dataIndex: 'pessoa_fisica_unicode', id: 'autoExpandColumn' },
                    { header: 'Tipo', dataIndex: 'type_by_possession_display', width: 180 },
                    { header: 'Afastamento', dataIndex: 'departure_unicode', width: 150 },
                    { header: 'Data Posse', dataIndex: 'dt_posse', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y') },                    
                    { header: 'Cargo Efetivo', dataIndex: 'effective_unicode', width: 250 },
                    { header: 'Cargo Comissão', dataIndex: 'commission_unicode', width: 150 },
                    { header: 'Última Folha Ponto', dataIndex: 'last_sendindg_time_sheet', width: 150},
                    { header: 'Situação da Ultima Folha Ponto', dataIndex: 'status', width: 150},
                    { header: 'Teletrabalho', dataIndex: 'in_telework', width: 150},
                    { header: 'Criado por', dataIndex: 'servidor_created_by_unicode', width: 90, hidden: true },
                    { header: 'Criado em', dataIndex: 'servidor_created_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true, sortable: true },
                    { header: 'Alterado por', dataIndex: 'servidor_modified_by_unicode', width: 90, hidden: true },
                    { header: 'Alterado em', dataIndex: 'servidor_modified_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                ]
            );
        return this._columnModel;
    },

    getSituationItemsMenu: function () {
        if (this._situationItems == undefined) {
            this._situationItems = [];
            for (var i = 0; i < this.situationMenuValue.length; i++) {
                if (this.situationMenuValue[i].name == 'active') {
                    this._situationItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'active',
                            groupMenu: 'situation',
                            text: 'ATIVO',
                            checked: this.situationMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterSituation();
                            }
                        })
                    );
                }
                if (this.situationMenuValue[i].name == 'finished') {
                    this._situationItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'finished',
                            groupMenu: 'situation',
                            text: 'ENCERRADO',
                            checked: this.situationMenuValue[i].checked,
                            value: false,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterSituation();
                            }
                        })
                    );
                }

            }
        }
        return this._situationItems;
    },

    getPossessionTypeItemsMenu: function (autoload) {
        this.autoload = autoload;
        if (this._possessionType == undefined) {
            this._possessionType = [];
            for (var i = 0; i < this.typePossessionItems.length; i++) {
                if (this.typePossessionItems[i].name == 'efective') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'efective',
                            groupMenu: 'possession_type',
                            text: 'EFETIVO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'EFE',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'comissioned') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'comissioned',
                            groupMenu: 'possession_type',
                            text: 'COMISSIONADO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'CMS',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'requested') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'requested',
                            groupMenu: 'possession_type',
                            text: 'REQUISITADO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'REQ',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'requestedrex') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'requestedrex',
                            groupMenu: 'possession_type',
                            text: 'REQUISITADO EXTERNO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'REX',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'efecm') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'efecm',
                            groupMenu: 'possession_type',
                            text: 'EFETIVO com CM',
                            checked: this.typePossessionItems[i].checked,
                            value: 'ECM',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'reqcm') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'reqcm',
                            groupMenu: 'possession_type',
                            text: 'REQUISITADO com CM',
                            checked: this.typePossessionItems[i].checked,
                            value: 'RCM',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'reqfc') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'reqfc',
                            groupMenu: 'possession_type',
                            text: 'REQUISITADO com FC',
                            checked: this.typePossessionItems[i].checked,
                            value: 'RFC',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'trainee') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'trainee',
                            groupMenu: 'possession_type',
                            text: 'ESTAGIÁRIO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'EST',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'voluntare') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'voluntare',
                            groupMenu: 'possession_type',
                            text: 'VOLUNTÁRIO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'VOL',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'extern') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'extern',
                            groupMenu: 'possession_type',
                            text: 'EXTERNO SEM VÍNCULO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'EXT',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'residentes') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'extern',
                            groupMenu: 'possession_type',
                            text: 'RESIDENTES',
                            checked: this.typePossessionItems[i].checked,
                            value: 'RES',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
            }
        }
        return this._possessionType;
    },

    getTrabalhoRemotoItemsMenu: function () {
        if (this._trabalhoRemotoItems == undefined) {
            this._trabalhoRemotoItems = [];
            for (var i = 0; i < this.trabalhoRemotoMenuValue.length; i++) {
                if (this.trabalhoRemotoMenuValue[i].name == 'sim') {
                    this._trabalhoRemotoItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'sim',
                            groupMenu: 'trabalho_remoto',
                            text: 'SIM',
                            checked: this.trabalhoRemotoMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterTrabalhoRemoto();
                            }
                        })
                    );
                }
            }
        }
        return this._trabalhoRemotoItems;
    },

    getVerTodosItemsMenu: function () {
        if (this._verTodosItems == undefined) {
            this._verTodosItems = [];
            for (var i = 0; i < this.verTodosMenuValue.length; i++) {
                if (this.verTodosMenuValue[i].name == 'active') {
                    this._verTodosItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'active',
                            groupMenu: 'ver_todos',
                            text: 'ATIVO',
                            checked: this.verTodosMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterVerTodos();        
                            }
                        })
                    );
                }
            }
        }
        return this._verTodosItems;
    },

    getServidorFilterMenu: function () {
        return [
            {
                name: 'situation',
                groupMenu: '',
                text: 'Situação',
                scope: this,
                menu: this.getSituationItemsMenu()
            },
            {
                name: 'possession_type',
                groupMenu: '',
                text: 'Tipo de posse',
                scope: this,
                menu: this.getPossessionTypeItemsMenu().concat(
                    [
                        '-',
                        new Ext.menu.CheckItem({
                        text: 'Marcar todos os filtros',
                        name: 'uncheck_possession_type',
                        scope: this,
                        checked: false,
                        hideOnClick: false,
                        handler: function (checked) {
                            this.getPossessionTypeItemsMenu().forEach(
                                function (item) {
                                    item.setChecked(!checked.checked, true);
                                }
                                );
                            this.filterPossessionType(true);
                        }
                    })
                    ]
                )
            },
            {
                name: 'trabalho_remoto',
                groupMenu: '',
                text: 'Trabalho Remoto',
                scope: this,
                menu: this.getTrabalhoRemotoItemsMenu()
            },
        ];
    },

    getTipoFaltaItemsMenu: function () {
        if (this._tipoFaltaItems == undefined) {
            this._tipoFaltaItems = [];
            for (var i = 0; i < this.tipoFaltaMenuValue.length; i++) {
                if (this.tipoFaltaMenuValue[i].name == 'justificada') {
                    this._tipoFaltaItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'justificada',
                            groupMenu: 'justificado',
                            text: 'JUSTIFICADA',
                            checked: this.tipoFaltaMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterTipoFalta();
                            }
                        })
                    );
                }
                if (this.tipoFaltaMenuValue[i].name == 'injustificada') {
                    this._tipoFaltaItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'injustificada',
                            groupMenu: 'justificado',
                            text: 'INJUSTIFICADA',
                            checked: this.tipoFaltaMenuValue[i].checked,
                            value: false,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterTipoFalta();
                            }
                        })
                    );
                }

            }
        }
        return this._tipoFaltaItems;
    },

    getSituacaoFaltaItemsMenu: function () {
        if (this._situacaoFaltaItems == undefined) {
            this._situacaoFaltaItems = [];
            for (var i = 0; i < this.situacaoFaltaMenuValue.length; i++) {
                if (this.situacaoFaltaMenuValue[i].name == 'aguardando_processar') {
                    this._situacaoFaltaItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'aguardando_processar',
                            groupMenu: 'situacao_falta',
                            text: 'AGUARDANDO ANÁLISE',
                            checked: this.situacaoFaltaMenuValue[i].checked,
                            value: 1,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterSituacaoFalta();
                            }
                        })
                    );
                }
                if (this.situacaoFaltaMenuValue[i].name == 'processada') {
                    this._situacaoFaltaItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'processada',
                            groupMenu: 'situacao_falta',
                            text: 'PROCESSADA',
                            checked: this.situacaoFaltaMenuValue[i].checked,
                            value: 2,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterSituacaoFalta();
                            }
                        })
                    );
                }
                if (this.situacaoFaltaMenuValue[i].name == 'removida') {
                    this._situacaoFaltaItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'removida',
                            groupMenu: 'situacao_falta',
                            text: 'REMOVIDA',
                            checked: this.situacaoFaltaMenuValue[i].checked,
                            value: 3,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterSituacaoFalta();
                            }
                        })
                    );
                }
            }
        }
        return this._situacaoFaltaItems;
    },

    getImpactoFinanceiroItemsMenu: function () {
        if (this._impactoFinanceiroItems == undefined) {
            this._impactoFinanceiroItems = [];
            for (var i = 0; i < this.impactoFinanceiroMenuValue.length; i++) {
                if (this.impactoFinanceiroMenuValue[i].name == 'com_impacto') {
                    this._impactoFinanceiroItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'com_impacto',
                            groupMenu: 'impacto_financeiro',
                            text: 'COM IMPACTO',
                            checked: this.impactoFinanceiroMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterImpactoFinanceiro();
                            }
                        })
                    );
                }
                if (this.impactoFinanceiroMenuValue[i].name == 'sem_impacto') {
                    this._impactoFinanceiroItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'sem_impacto',
                            groupMenu: 'impacto_financeiro',
                            text: 'SEM IMPACTO',
                            checked: this.impactoFinanceiroMenuValue[i].checked,
                            value: false,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterImpactoFinanceiro();
                            }
                        })
                    );
                }
            }
        }
        return this._impactoFinanceiroItems;
    },

    getFaltaFilterMenu: function () {
        return [
            {
                name: 'justificado',
                groupMenu: '',
                text: 'Tipo de Falta',
                scope: this,
                menu: this.getTipoFaltaItemsMenu()
            },
            {
                name: 'situacao_falta',
                groupMenu: '',
                text: 'Situação',
                scope: this,
                menu: this.getSituacaoFaltaItemsMenu()
            },
            {
                name: 'impacto_financeiro',
                groupMenu: '',
                text: 'Impacto Financeiro',
                scope: this,
                menu: this.getImpactoFinanceiroItemsMenu()
            },
        ];
    },

    getVerTodosFilterMenu: function () {
        return [
            {
                name: 'ver_todos',
                groupMenu: '',
                text: 'Ver Todos',
                scope: this,
                menu: this.getVerTodosItemsMenu()
            },
        ];
    },

    exibirMsgErro: function(msg){
        Ext.Msg.show({
            minWidth: 400,
            title: this.title,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
            msg: msg
        });
    },

    atualizaSubFaltaGrid: function() {
        if (this.ownerCt && this.ownerCt._subfaltaGrid && this.ownerCt._subfaltaGrid.disabled == false) {
            this.ownerCt._subfaltaGrid.disable();
            this.ownerCt._subfaltaGrid.getStore().removeAll();
        }
        var store = this.getStore();
        store.load({});
    },

    acoesGestorFaltas: function(nome_metodo, tipo_processamento){
        var msg_erro = '';
        var msg_pergunta = '';
        var params = '';

        var filtro_ano = '';
        var filtro_mes = '';
        var filtro_txt = '';
        var filtro_situacao = [];
        var filtro_tipo = [];
        var filtro_tipo_falta = [];
        var filtro_situacao_falta = [];
        var filtro_impacto_financeiro = [];

        this._toolbar.items.items.forEach(function(item, i){
            if(item.emptyText == 'Ano para filtro'){ filtro_ano = item.getValue(); }
            if(item.emptyText == 'Mês para filtro'){ filtro_mes = item.getValue(); }
            if(item.emptyText == 'Palavra-chave'){ filtro_txt = item.getValue(); }
            
            if(item.text == 'Filtro Servidor'){
                item.menu.items.items.forEach(function(sub_item){
                    if(sub_item.text == 'Situação')
                        sub_item.menu.items.items.forEach(function(item_filtro){
                            if(item_filtro.id != 'todos' && item_filtro.checked == true){ filtro_situacao.push(item_filtro.value); }
                        });
                    if(sub_item.text == 'Tipo de posse'){
                        sub_item.menu.items.items.forEach(function(item_filtro){
                            if(item_filtro.id != '0' && item_filtro.checked == true){ filtro_tipo.push(item_filtro.value); }
                        });
                    }
                });
            }
            if(item.text == 'Filtro Falta'){
                item.menu.items.items.forEach(function(sub_item){
                    if(sub_item.text == 'Tipo de Falta')
                        sub_item.menu.items.items.forEach(function(item_filtro){
                            if(item_filtro.id != 'todos' && item_filtro.checked == true){ filtro_tipo_falta.push(item_filtro.value); }
                        });
                    if(sub_item.text == 'Situação')
                        sub_item.menu.items.items.forEach(function(item_filtro){
                            if(item_filtro.id != '0' && item_filtro.checked == true){ filtro_situacao_falta.push(item_filtro.value); }
                        });
                    if(sub_item.text == 'Impacto Financeiro'){
                        sub_item.menu.items.items.forEach(function(item_filtro){
                            if(item_filtro.id != 'todos' && item_filtro.checked == true){ filtro_impacto_financeiro.push(item_filtro.value); }
                        });
                    }
                });
            }
        });

        if(tipo_processamento == 'selecionados'){
            var selecionados = this.getSelectionModel().getSelections().map(function(a){ return a.data.servidor_pk; });

            if(selecionados.length == 0){
                msg_erro = 'Escolha pelo menos um registro para '+nome_metodo.split('_')[0]+'.';
            }else{
                params = { servidor_ids: selecionados };
                msg_pergunta = 'ATENÇÃO! Só serão processadas as Faltas que possuírem Competência de Desconto informada. <br>Tem certeza que deseja '+nome_metodo.split('_')[0]+' o(s) registro(s) selecionado(s)?';
            }
        }else if(tipo_processamento == 'todos'){
            params = {
                servidor_ids: 'todos',
            };
            msg_pergunta = 'ATENÇÃO! Só serão processadas as Faltas que possuírem Competência de Desconto informada. <br>Tem certeza que deseja '+nome_metodo.split('_')[0]+' todos os registros?';
        }

        params['filtro_ano'] = filtro_ano;
        params['filtro_mes'] = filtro_mes;
        params['filtro_txt'] = filtro_txt;
        params['filtro_situacao'] = filtro_situacao;
        params['filtro_tipo'] = filtro_tipo;
        params['filtro_tipo_falta'] = filtro_tipo_falta;
        params['filtro_situacao_falta'] = filtro_situacao_falta;
        params['filtro_impacto_financeiro'] = filtro_impacto_financeiro;

        if(filtro_mes == 0 && tipo_processamento == 'todos'){
            msg_erro = 'A ação '+nome_metodo.split('_')[0]+' todos filtrados não pode ser executada quando o filtro de Meses está com o valor Todos Selecionado'; 
        }

        if(msg_erro != ''){
            this.exibirMsgErro(msg_erro);
        }else if(nome_metodo == 'processar_faltas'){
            Ext.Msg.show({
                msg: msg_pergunta,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (b) {
                    if (b == 'no') return;

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('PONTFalta', nome_metodo),
                        params: params,
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success == true){
                                this.getStore().reload();
                                this.atualizaSubFaltaGrid();
                                this.getSelectionModel().clearSelections();
                                Ext.Msg.show({
                                    msg: 'Processamento iniciado com sucesso. Acompanhe o processamento através do botão: Relatórios, no canto esquerdo superior da tela!',
                                    icon: Ext.Msg.QUESTION,
                                    buttons: Ext.Msg.OK,
                                    scope: this,
                                })
                            }
                            else{ this.exibirMsgErro(obj.message); }
                        },
                        scope: this
                    });
                }
            })
        }else{
            new rh.falta.employee.AtribuirCompDescWindow({
                params: params,
                nome_metodo: nome_metodo,
                msg_pergunta: msg_pergunta,
                success: {
                    scope: this,
                    callback: function() { 
                        this.getStore().reload();
                        this.atualizaSubFaltaGrid();
                    }
                }
            }).show();
        }
    },

    acoesItem: function(texto, icone, nome_metodo, tipo_processamento){
        return {
            text: texto,
            iconCls: 'icon-16px '+icone,
            scope: this,
            handler: function(){ this.acoesGestorFaltas(nome_metodo,tipo_processamento) },
        }
    },

    menuAcoes: function(){
        this._menuAcoes = [
            this.acoesItem('Processar Selecionados', 'icon-core icon-core-run', 'processar_faltas', 'selecionados'),
            this.acoesItem('Processar Todos Filtrados', 'icon-core icon-core-run', 'processar_faltas', 'todos'),
            this.acoesItem('Atribuir Comp. Desc. Selecionados', 'icon-core icon-core-calendar-plus', 'atribuir_comp_desc', 'selecionados'),
            this.acoesItem('Atribuir Comp. Desc. Todos Filtrados', 'icon-core icon-core-calendar-plus', 'atribuir_comp_desc', 'todos'),
        ];

        return this._menuAcoes
    },

    
    getReport: function(cfg){
        var servidor_pk = ''
        if (this.getSelectionModel().getSelections().length > 0) {
            servidor_pk = this.getSelectionModel().getSelections()[0].data.servidor_pk
        }
        var wnd = Ext._create('rh.falta.RelatorioWindow', {
            modal: true,
            params: {'servidor': servidor_pk},
        });

        wnd.show()
    },

    getOpenRelatorioAction: function(){
        if(!this._openRelatorio)
            this._openRelatorio = Ext._create('Ext.Button', {
                text: 'Relatório',
                iconCls: 'icon-estagio icon-archive-pdf',
                scope: this,
                handler: this.getReport
            });
    
        return this._openRelatorio;
    },

    getToolbar: function (cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            var menuAcoes = this.menuAcoes();
            itensTollBar.splice(
                0,
                0,
                {
                    text: 'Ações',
                    iconCls: 'icon-16px icon-fopag icon-node-select',
                    menu: menuAcoes,
                }
            )
            itensTollBar.splice(1, 0, '-');
            itensTollBar.splice(2, 0, this.getOpenRelatorioAction());
            itensTollBar.splice(3, 0, '->');
            itensTollBar.splice(4, 0, 'Ano: ');
            itensTollBar.splice(5, 0, this.comboAno());
            itensTollBar.splice(6, 0, '-');
            itensTollBar.splice(7, 0, 'Mês: ');
            itensTollBar.splice(8, 0, this.comboMes());

            itensTollBar.splice(
                12,
                0,
                {
                    text: 'Filtro Servidor',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: this.getServidorFilterMenu()
                }
            );
            itensTollBar.splice(13, 0, '-');
            itensTollBar.splice(
                14,
                0,
                {
                    text: 'Filtro Falta',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: this.getFaltaFilterMenu()
                }
            );
            itensTollBar.splice(
                15,
                0,
                {
                    text: 'Ver Todos Servidores',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    // menu: this.getVerTodosFilterMenu()
                    menu: this.getVerTodosItemsMenu()
                }
            );
                        
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: itensTollBar,
            });

            if((this.toolbarHideLabel || cfg.toolbarHideLabel))
                this._toolbar.items.each(
                    function(item) {
                        item.tooltip = (item.tooltip || item.text);

                        if(item.text && core.nullValue(item.hideLabel, true))
                            item.text = null;
                    }
                );
        }

        return this._toolbar;
    },

    doKeywordFilter: function(keyword) {
        var store = this.getStore();
        if(keyword !== '')
            store.baseParams.keyword = keyword;
        else {
            store.baseParams.keyword = null;
            delete store.baseParams.keyword;
        }
        this._toolbar.items.items.forEach(function(item, i){
            if(item.emptyText == 'Ano para filtro'){ ano = item.getValue(); }
        });
        this._toolbar.items.items.forEach(function(item, i){
            if(item.emptyText == 'Mês para filtro'){ mes = item.getValue(); }
        });
        this.__setFilterPropertyDefault(true, ano, mes);
    },

    filterSituation: function () {
        var values = [];
        this.getSituationItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('servidor__ativo__in', values, 1, true);
        this.atualizaSubFaltaGrid();
    },

    filterPossessionType: function (autoload) {
        var values = [];
        if (autoload === undefined) {
            autoload = true
        }
        this.getPossessionTypeItemsMenu(autoload).forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('servidor__type_by_possession__in', values, 2, autoload);
        this.atualizaSubFaltaGrid();
    },

    filterTipoFalta: function () {
        var values = [];
        this.getTipoFaltaItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('justificado__in', values, 5, true);
        this.atualizaSubFaltaGrid();
    },
    
    filterSituacaoFalta: function () {
        var values = [];
        this.getSituacaoFaltaItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('situacao__in', values, 6, true);
        this.atualizaSubFaltaGrid();
    },
    
    filterImpactoFinanceiro: function () {
        var values = [];
        this.getImpactoFinanceiroItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('payroll__in', values, 7, true);
        this.atualizaSubFaltaGrid();
    },

    filterVerTodos: function () {
        var values = [];
        this.getVerTodosItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
            
        );
        this.setFilterProperty('ver_todos', values, 8, true);
        this.atualizaSubFaltaGrid();
    },

    filterTrabalhoRemoto: function () {
        var values = [];
        
        menuItens=this.getTrabalhoRemotoItemsMenu();

        if (menuItens[0].checked == true){
            values.push(true)
            this.setFilterProperty('servidor__movimentacaopessoal__movimentacaoteletrabalho__ativo__in', values, 9, true);
        }else{
            this.removeFilterProperty('servidor__movimentacaopessoal__movimentacaoteletrabalho__ativo__in', 9, true);
        }        
        this.atualizaSubFaltaGrid();
    },

    comboAno: function(){
        const timeElapsed = Date.now();
        var hoje = new Date(timeElapsed);

        var storeComboAno = new Ext.data.JsonStore({
            proxy: new Ext.data.HttpProxy({
                url: toolkit.util.Normalize.controller_action('PONTFalta', 'anos_falta', ['only']),
                disableCaching: true,
                method: 'GET',
            }),
            root: 'root',
            fields: ['pk', 'description']
        });

        return {
            xtype: 'combo',
            store: storeComboAno,
            displayField: 'description',
            valueFeild: 'pk',
            emptyText: 'Ano para filtro',
            width: 140,
            triggerAction: 'all',
            value: hoje.getMonth() == 0 ? hoje.getFullYear() - 1 : hoje.getFullYear() ,
            listeners: {
                scope: this,
                select: function (combo, record) {
                    var ano = record.json.pk;

                    var mes = 0;
                    this._toolbar.items.items.forEach(function(item, i){
                        if(item.emptyText == 'Mês para filtro'){ mes = item.getValue(); }
                    });

                    this.filtrarAnoMes(ano, mes);
                }
            }
        }
    },

    comboMes: function(){
        const timeElapsed = Date.now();
        var hoje = new Date(timeElapsed);

        console.log(hoje.getMonth())

        return {
            xtype: 'combo',
            store: [
                [0, 'TODOS'],
                [1, 'JANEIRO'],
                [2, 'FEVEREIRO'],
                [3, 'MARÇO'],
                [4, 'ABRIL'],
                [5, 'MAIO'],
                [6, 'JUNHO'],
                [7, 'JULHO'],
                [8, 'AGOSTO'],
                [9, 'SETEMBRO'],
                [10, 'OUTUBRO'],
                [11, 'NOVEMBRO'],
                [12, 'DEZEMBRO'],
            ],
            emptyText: 'Mês para filtro',
            width: 140,
            triggerAction: 'all',
            value: hoje.getMonth() == 0 ? 11 : hoje.getMonth() - 1,
            listeners: {
                scope: this,
                select: function (combo, record) {
                    var mes = record.json[0]

                    var ano = 0;
                    this._toolbar.items.items.forEach(function(item, i){
                        if(item.emptyText == 'Ano para filtro'){ ano = item.getValue(); }
                    });

                    this.filtrarAnoMes(ano, mes);
                }
            },
        }
    },

    filtrarAnoMes: function (ano='', mes='') {
        if((ano === 0 || ano === 'TODOS') && mes === 0){
            this.removeFilterProperty('data__lte', 3, false);
            this.removeFilterProperty('data_fim__gte', 4, false);
            this.removeFilterProperty('data_fim__isnull', 4, true);
        }else{
            const timeElapsed = Date.now();
            hoje = new Date(timeElapsed);

            if(ano === '' && mes === ''){
                ano_filtro = hoje.getMonth() == 0 ? hoje.getFullYear() - 1 : hoje.getFullYear();
                mes = hoje.getMonth() == 0 ? 11 : hoje.getMonth() - 1;
                
                var d_inicio = new Date(ano_filtro, mes).toISOString().substring(0, 10);
                var d_fim = new Date(ano_filtro, mes+1);

            }else if((ano === 0 || ano === 'TODOS') && mes != ''){
                this._toolbar.items.items.forEach(function(item, i){
                    if(item.emptyText == 'Ano para filtro'){
                        ano_filtro = item.initialConfig.store.data.items.slice(-1)[0].data.pk;
                    }
                });

                var d_inicio = new Date(ano_filtro, 0).toISOString().substring(0, 10);
                var d_fim = new Date(hoje.getFullYear(), mes);
            }else{
                if(mes == 0){
                    var d_inicio = new Date(ano, 0).toISOString().substring(0, 10);
                    var d_fim = new Date(ano, 12);
                }else{
                    var d_inicio = new Date(ano, mes-1).toISOString().substring(0, 10);
                    var d_fim = new Date(ano, mes);
                }
            }


            d_fim.setDate(d_fim.getDate() - 1);
            d_fim = d_fim.toISOString().substring(0, 10);

            this.setFilterProperty('data__lte', d_fim, 3, false);
            this.setFilterProperty('data_fim__gte', d_inicio, 4, false);
            this.setFilterProperty('data_fim__isnull', true, 4, true);
        }
        this.atualizaSubFaltaGrid();
    },
});

core.RestfulGrid.register(
    'rh.falta.employee.Restful',
    'rh.falta.employee.Grid'
);


Ext._define('rh.falta.employee.AtribuirCompDescWindow', {
    extend: 'Ext.Window',
    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = new Ext.form.FormPanel({
                border: false,
                frame: true,
                scope: this,
                items: [
                    {
                        
                        allowBlank: true,
                        fieldLabel: "Competência de Desconto (mm/aaaa)",
                        name: "competencia_desconto",
                        xtype: 'datefield',
                        format: 'm/Y',
                        width: 200,
                    },
                ],
                buttons: [
                    {
                        text: 'Atribuir',
                        scope: this,
                        handler: this.doSubmit
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]                

            });
    
        return this._formPanel;
    },

    doSubmit: function(){
        var form = this.getFormPanel().getForm();
        var competencia_desconto_Field = this.getFormPanel().getForm().findField('competencia_desconto');

        if (!competencia_desconto_Field.value) {
            Ext.Msg.show({
                minWidth: 320,
                title: 'Competência de Desconto',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Informe a Competência de Desconto!'
            });
        } else {
            form.waitMsgTarget = this.getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action('PONTFalta', this.nome_metodo),
                scope: this,
                params: this.params,
                waitMsg: 'Atribuindo...',
                success: function(request,form, action) {
                    var fn = this.success;
                    var rst = Ext.decode(request.responseText);
                    fn && fn.callback.call(fn.scope ? fn.scope : window);
                    Ext.Msg.show({
                        title: 'Competência de Desconto',
                        msg: 'Atribuição realizada com sucesso!',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.destroy();
                },
                failure: function(form, action) {
                    if(action.failureType == 'client')
                        message = 'Erro de comunicação com servidor, tente novamente mais tarde.'
                    else
                        message = action.result.message;
    
                    Ext.Msg.show({
                        title: this.title,
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
    
                    this.failure && this.failure.callback.call(this.failure.scope ? this.failure.scope : window);
                }
            });
        }
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(cfg, {
            title: 'Atribuir Competência de Desconto',
            modal: true,
            resizable: false,
            width: 400,
            items: this.getFormPanel(cfg)
        });

        rh.falta.employee.AtribuirCompDescWindow.superclass.constructor.call(this, cfg);
    }
});