/**
 *
 **/
Ext._define('rh.employee.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.employee.Window',

    keywordFieldMessage: 'Palavra-chave',

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
                    name: 'member',
                    checked: false,
                    value: 'MBR',
                },
                {
                    name: 'member2',
                    checked: false,
                    value: 'MBR2',
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
                    name: 'memel',
                    checked: false,
                    value: 'MEL',
                },
                {
                    name: 'memel2',
                    checked: false,
                    value: 'MEL2',
                },
                {
                    name: 'memcm',
                    checked: false,
                    value: 'MCM',
                },
                {
                    name: 'memcm2',
                    checked: false,
                    value: 'MCM2',
                },
                {
                    name: 'reqcm',
                    checked: false,
                    value: 'RCM',
                },
                {
                    name: 'efefc',
                    checked: false,
                    value: 'EFC',
                },
                {
                    name: 'reqfc',
                    checked: false,
                    value: 'RFC',
                },
                {
                    name: 'memlcm',
                    checked: false,
                    value: 'MEC',
                },
                {
                    name: 'memlcm2',
                    checked: false,
                    value: 'MEC2',
                },
                {
                    name: 'trainee',
                    checked: false,
                    value: 'EST',
                },
                {
                    name: 'aprentice',
                    checked: false,
                    value: 'JCA',
                },
                {
                    name: 'outsourced',
                    checked: false,
                    value: 'TCR',
                },
                {
                    name: 'voluntare',
                    checked: false,
                    value: 'VOL',
                },
                {
                    name: 'contracted',
                    checked: false,
                    value: 'CTR',
                },
                {
                    name: 'extern',
                    checked: false,
                    value: 'EXT',
                },
                {
                    name: 'efretired',
                    checked: false,
                    value: 'SAP',
                },
                {
                    name: 'mretired',
                    checked: false,
                    value: 'MAP',
                },
                {
                    name: 'benefit',
                    checked: false,
                    value: 'BFP',
                },
                {
                    name: 'employeexxx',
                    checked: false,
                    value: 'XXX',
                },
                {
                    name: 'eventual_collaborator',
                    checked: false,
                    value: 'COE',
                },
                {
                    name: 'resident',
                    checked: false,
                    value: 'RES',
                },
            ]
        });

        this.departament = cfg.departament;
        this.situationMenuValue = cfg.situationMenuValue;
        this.typePossessionItems = cfg.typePossessionItems;

        rh.employee.Grid.superclass.constructor.call(this, cfg);

        this.__setFilterPropertyDefault(this.gridAutoLoad);
    },

    __setFilterPropertyDefault: function (gridAutoLoad) {
        var situationMenuValueToFilter = [];
        this.situationMenuValue.forEach(
            function (item) {

                if (item.checked) {
                    situationMenuValueToFilter.push(item.value);
                }
            }
        );

        var filterTypePossession = [];
        this.typePossessionItems.forEach(
            function (item) {
                if (item.checked)
                    filterTypePossession.push(item.value);
            }
        );

        if (filterTypePossession.length > 0) {
            this.setFilterProperty('type_by_possession__in', filterTypePossession, 1003, false);
        }
        if (situationMenuValueToFilter.length > 0) {
            this.setFilterProperty('ativo__in', situationMenuValueToFilter, 1001, false);
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
                    { header: 'Chave', dataIndex: 'pk', width: 55, hidden: true },
                    {
                        header: 'Ativo',
                        dataIndex: 'ativo',
                        width: 40,
                        renderer: toolkit.util.formatIconYesNo,
                    },
                    { header: 'Regime Previdenciário', dataIndex: 'icons', width: 70, menuDisabled: true, renderer: core.rendererIconGrid},
                    { header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function (value) { return '<div style="text-align:right">' + value + '</div>'; } },
                    { header: 'Nome Registral', dataIndex: 'pessoa_fisica_unicode', hidden: true, id: 'autoExpandColumn' },
                    { header: 'Nome', dataIndex: 'social_name', width: 250 },
                    { header: 'Tipo', dataIndex: 'type_by_possession_display', width: 180 },
                    { header: 'Cat. eSocial', dataIndex: 'category_esocial_display', width: 180, hidden: true },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 90, hidden: true },
                    { header: 'Criação', dataIndex: 'created_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: false, sortable: true },
                    { header: 'Alterado por', dataIndex: 'modified_by_unicode', width: 90, hidden: true },
                    { header: 'Alteração', dataIndex: 'modified_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                    { header: 'Posse', dataIndex: 'data_posse', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Exercício', dataIndex: 'data_exercicio', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Desligamento', dataIndex: 'data_desligamento', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Afastamento', dataIndex: 'departure_unicode', width: 200 },
                    { header: 'Cargo Efetivo', dataIndex: 'effective_unicode', width: 250 },
                    { header: 'Cargo Comissão', dataIndex: 'commission_unicode', width: 150 },
                    { header: 'Cargo Eletivo', dataIndex: 'elective_unicode', width: 150 },
                    { header: 'eSocial', dataIndex: 'event_esocial', width: 70, renderer: function (value) {
                            var tpl = new Ext.XTemplate(
                                '<tpl if="value != 0">' +
                                    '<div class="tk-grid-icon-cell icon-core icon-core-success" ext:qtip="Enviado" ext:qwidth="16";"></div>'+
                                '</tpl>'+
                                '<tpl if="value == 0 || value == undefined">' +
                                    '<div class="tk-grid-icon-cell icon-core icon-core-delete" ext:qtip="Não" ext:qwidth="16"></div>'+
                                '</tpl>'
                            );
                            return tpl.apply({'value': value});
                        }
                    },
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
                if (this.typePossessionItems[i].name == 'member') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'member',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MBR',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'member') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'member2',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO*',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MBR2',
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
                if (this.typePossessionItems[i].name == 'memel') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'memel',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO com EL',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MEL',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'memel2') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'memel2',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO com EL 2*',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MEL2',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'memcm') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'memcm',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO com CM',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MCM',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'memcm2') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'memcm2',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO com CM 2',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MCM2',
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
                if (this.typePossessionItems[i].name == 'efefc') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'efefc',
                            groupMenu: 'possession_type',
                            text: 'EFETIVO com FC',
                            checked: this.typePossessionItems[i].checked,
                            value: 'EFC',
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
                if (this.typePossessionItems[i].name == 'memlcm') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'memlcm',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO com EL e CM',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MEC',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'memlcm2') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'memlcm2',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO com EL e CM 2',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MEC2',
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
                if (this.typePossessionItems[i].name == 'aprentice') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'aprentice',
                            groupMenu: 'possession_type',
                            text: 'JOVEM CIDADÃO - APRENDIZ',
                            checked: this.typePossessionItems[i].checked,
                            value: 'JCA',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'outsourced') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'outsourced',
                            groupMenu: 'possession_type',
                            text: 'TERCEIRIZADO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'TCR',
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
                if (this.typePossessionItems[i].name == 'contracted') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'contracted',
                            groupMenu: 'possession_type',
                            text: 'CONTRATADO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'CTR',
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
                if (this.typePossessionItems[i].name == 'efretired') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'efretired',
                            groupMenu: 'possession_type',
                            text: 'SERVIDOR APOSENTADO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'SAP',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'mretired') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'mretired',
                            groupMenu: 'possession_type',
                            text: 'MEMBRO APOSENTADO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'MAP',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'benefit') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'benefit',
                            groupMenu: 'possession_type',
                            text: 'BENEFICIÁRIO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'BFP',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'employeexxx') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employeexxx',
                            groupMenu: 'possession_type',
                            text: 'SERVIDOR NÃO RECONHECIDO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'XXX',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'pensioner') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'pensioner',
                            groupMenu: 'possession_type',
                            text: 'BEN. DE PENSÃO',
                            checked: this.typePossessionItems[i].checked,
                            value: 'BFP',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'eventual_collaborator') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'eventual_collaborator',
                            groupMenu: 'possession_type',
                            text: 'COLABORADOR EVENTUAL',
                            checked: this.typePossessionItems[i].checked,
                            value: 'COE',
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterPossessionType(this.autoload);
                            }
                        })
                    );
                }
                if (this.typePossessionItems[i].name == 'resident') {
                    this._possessionType.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'resident',
                            groupMenu: 'possession_type',
                            text: 'RESIDENTE',
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

    getTypeItemsMenu: function () {
        if (this._typeItems == undefined) {
            this._typeItems = [];
            for (var i = 0; i < this.typeItemsValue.length; i++) {
                if (this.typeItemsValue[i].name == 'trainee')
                    this._typeItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employee_member',
                            groupMenu: 'type',
                            text: 'ESTAGIÁRIO',
                            checked: this.typeItemsValue[i].checked,
                            value: 'E',
                            scope: this,
                            handler: this.filterType
                        })
                    );
                if (this.typeItemsValue[i].name == 'member')
                    this._typeItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employee_member',
                            groupMenu: 'type',
                            text: 'MEMBRO',
                            checked: this.typeItemsValue[i].checked,
                            value: 'M',
                            scope: this,
                            handler: this.filterType
                        })
                    );
                if (this.typeItemsValue[i].name == 'military')
                    this._typeItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employee_member',
                            groupMenu: 'type',
                            text: 'MILITAR',
                            checked: this.typeItemsValue[i].checked,
                            value: 'P',
                            scope: this,
                            handler: this.filterType
                        })
                    );
                if (this.typeItemsValue[i].name == 'employee')
                    this._typeItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employee',
                            groupMenu: 'type',
                            text: 'SERVIDOR',
                            checked: this.typeItemsValue[i].checked,
                            value: 'S',
                            scope: this,
                            handler: this.filterType
                        })
                    );
                if (this.typeItemsValue[i].name == 'outsourced')
                    this._typeItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employee_member',
                            groupMenu: 'type',
                            text: 'TERCEIRIZADO',
                            checked: this.typeItemsValue[i].checked,
                            value: 'T',
                            scope: this,
                            handler: this.filterType
                        })
                    );
                if (this.typeItemsValue[i].name == 'voluntary')
                    this._typeItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'employee_member',
                            groupMenu: 'type',
                            text: 'VOLUNTÁRIO',
                            checked: this.typeItemsValue[i].checked,
                            value: 'V',
                            scope: this,
                            handler: this.filterType
                        })
                    );
            }
        }
        return this._typeItems;
    },

    getFilterMenu: function () {
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
        ];
    },

    getToolbar: function (cfg) {
        this._toolbar = rh.employee.Grid.superclass.getToolbar.call(this, cfg);
        this._toolbar.insertButton(10, {
            xtype: 'button',
            text: 'Limpar',
            iconCls: true,
            icon: '/' + global.Context + '/static/images/clean.png',
            handler: function () {
                for (var i = 0; i < this.situationMenuValue.length; i++) {
                    var situationMenuValue = this.situationMenuValue;
                    this.getSituationItemsMenu().forEach(
                        function (item) {
                            if (item.name == situationMenuValue[i].name)
                                item.setChecked(situationMenuValue[i].checked);
                        }
                    );
                }

                for (var i = 0; i < this.typePossessionItems.length; i++) {
                    var typePossessionItems = this.typePossessionItems;
                    this.getPossessionTypeItemsMenu().forEach(
                        function (item) {
                            if (item.name == typePossessionItems[i].name)
                                item.setChecked(typePossessionItems[i].checked);
                        }
                    );
                }

                this.__setFilterPropertyDefault(true);
            },
            scope: this
        });
        return this._toolbar;
    },

    filterSituation: function () {
        var values = [];
        this.getSituationItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('ativo__in', values, 1001);
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
        this.setFilterProperty('type_by_possession__in', values, 1003, autoload);
    },
});

core.RestfulGrid.register(
    'rh.employee.Restful',
    'rh.employee.Grid'
);
