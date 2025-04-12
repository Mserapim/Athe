Ext._define('rh.gestorbatida.servidor.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gestorbatida.servidor.Window',

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
            situacaoMenuValue: [
                {
                    name: 'active',
                    checked: true,
                    value: true,
                },
                {
                    name: 'finished',
                    checked: false,
                    value: false,
                },
            ],
            typePossessionItems: [
                {
                    name: 'efective',
                    checked: true,
                    value: 'EFE',
                },
                {
                    name: 'efefc',
                    checked: true,
                    value: 'EFC',
                },
                {
                    name: 'comissioned',
                    checked: true,
                    value: 'CMS',
                },
                {
                    name: 'requested',
                    checked: true,
                    value: 'REQ',
                },
                {
                    name: 'requestedrex',
                    checked: true,
                    value: 'REX',
                },
                {
                    name: 'efecm',
                    checked: true,
                    value: 'ECM',
                },
                {
                    name: 'reqcm',
                    checked: true,
                    value: 'RCM',
                },
                {
                    name: 'reqfc',
                    checked: true,
                    value: 'RFC',
                },
                {
                    name: 'trainee',
                    checked: true,
                    value: 'EST',
                },
                {
                    name: 'voluntare',
                    checked: true,
                    value: 'VOL',
                },
                {
                    name: 'extern',
                    checked: true,
                    value: 'EXT',
                },
                {
                    name: 'residentes',
                    checked: true,
                    value: 'RES',
                },
            ],

        });

        this.departament = cfg.departament;
        this.situacaoMenuValue = cfg.situacaoMenuValue;
        this.typePossessionItems = cfg.typePossessionItems;

        rh.gestorbatida.servidor.Grid.superclass.constructor.call(this, cfg);

        this.__setFilterPropertyDefault(this.gridAutoLoad);
    },

    __setFilterPropertyDefault: function (gridAutoLoad) {
        var situacaoMenuValueToFilter = [];
        var filterTypePossession = [];

        this.situacaoMenuValue.forEach(
            function (item) {
                if (item.checked) {
                    situacaoMenuValueToFilter.push(item.value);
                }
            }
        );
        this.typePossessionItems.forEach(
            function (item) {
                if (item.checked)
                    filterTypePossession.push(item.value);
            }
        );
        
        if (situacaoMenuValueToFilter.length > 0) {
            this.setFilterProperty('ativo__in', situacaoMenuValueToFilter, 1, false);
        }
        if (filterTypePossession.length > 0) {
            this.setFilterProperty('type_by_possession__in', filterTypePossession, 2, false);
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
                    { header: 'Data Posse', dataIndex: 'dt_posse', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y') },                    
                    { header: 'Cargo Efetivo', dataIndex: 'effective_unicode', width: 250 },
                    { header: 'Cargo Comissão', dataIndex: 'commission_unicode', width: 150 },
                    { header: 'Criado por', dataIndex: 'servidor_created_by_unicode', width: 90, hidden: true },
                    { header: 'Criado em', dataIndex: 'servidor_created_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true, sortable: true },
                    { header: 'Alterado por', dataIndex: 'servidor_modified_by_unicode', width: 90, hidden: true },
                    { header: 'Alterado em', dataIndex: 'servidor_modified_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                ]
            );
        return this._columnModel;
    },

    getSituacaoItemsMenu: function () {
        if (this._situacaoItems == undefined) {
            this._situacaoItems = [];
            for (var i = 0; i < this.situacaoMenuValue.length; i++) {
                if (this.situacaoMenuValue[i].name == 'active') {
                    this._situacaoItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'active',
                            groupMenu: 'situacao',
                            text: 'ATIVO',
                            checked: this.situacaoMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filtroSituacao();
                            }
                        })
                    );
                }
                if (this.situacaoMenuValue[i].name == 'finished') {
                    this._situacaoItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'finished',
                            groupMenu: 'situacao',
                            text: 'ENCERRADO',
                            checked: this.situacaoMenuValue[i].checked,
                            value: false,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filtroSituacao();
                            }
                        })
                    );
                }

            }
        }
        return this._situacaoItems;
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
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
                                this.filtroTipoPosse(this.autoload);
                            }
                        })
                    );
                }
            }
        }
        return this._possessionType;
    },


    getFiltroMenu: function () {
        return [
            {
                name: 'situacao',
                groupMenu: '',
                text: 'Situação',
                scope: this,
                menu: this.getSituacaoItemsMenu()
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
                        checked: true,
                        hideOnClick: false,
                        handler: function (checked) {
                            this.getPossessionTypeItemsMenu().forEach(
                                function (item) {
                                    item.setChecked(!checked.checked, true);
                                }
                                );
                            this.filtroTipoPosse(true);
                        }
                    })
                    ]
                )
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

    atualizaSubAnotacaoGrid: function() {
        if (this.ownerCt && this.ownerCt._subAnotacaoGrid && this.ownerCt._subAnotacaoGrid.disabled == false) {
            this.ownerCt._subAnotacaoGrid.disable();
            this.ownerCt._subAnotacaoGrid.getStore().removeAll();
        }
        var store = this.getStore();
        store.load({});
    },

    getToolbar: function (cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            itensTollBar.splice(3, 0, '->');

            itensTollBar.splice(
                12,
                0,
                {
                    text: 'Filtros',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: this.getFiltroMenu()
                }
            );
            itensTollBar.splice(13, 0, '-');
                        
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

    filtroSituacao: function () {
        var values = [];
        this.getSituacaoItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('ativo__in', values, 1, true);
        this.atualizaSubAnotacaoGrid();
    },

    filtroTipoPosse: function (autoload) {
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
        this.setFilterProperty('type_by_possession__in', values, 2, autoload);
        this.atualizaSubAnotacaoGrid();
    },
    

});

core.RestfulGrid.register(
    'rh.gestorbatida.servidor.Restful',
    'rh.gestorbatida.servidor.Grid'
);

