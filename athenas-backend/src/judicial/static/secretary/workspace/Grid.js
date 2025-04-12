Ext._define('judicial.secretary.workspace.Grid', {
    extend: 'judicial.OutCourtLawsuitGrid',

    restWindow: 'judicial.secretary.workspace.Window',

    configOrderToolBar: ['openDocument', '-', 'search', '->', 'download'],

    filterExecutionOrgan: function() {
        Ext._create(
            'judicial.outcourtlawsuit.FilterExecutionOrganWindow',
            {grid: this}
        ).show();
    },

    filterTypeLawsuit: function() {
        Ext._create(
            'judicial.outcourtlawsuit.FilterLawsuitTypeWindow',
            {grid: this}
        ).show();
    },

    filterInterested: function() {
        Ext._create(
            'judicial.outcourtlawsuit.FilterInterestedWindow',
            {grid: this}
        ).show();
    },

    filterBloke: function() {
        Ext._create(
            'judicial.outcourtlawsuit.FilterBlokeWindow',
            {grid: this}
        ).show();
    },

    getFields: function(param){
        if (param == 1)
            return {
                name: "bloke",
                xtype: "rest-autocompletefield",
                fieldLabel: "Associação",
                allowBlank: false,
                rest: "rh.person.legalperson.Restful",
            };
        else if (param == 2)
            return {
                name: "bloke",
                xtype: "rest-autocompletefield",
                fieldLabel: "Pessoa Jurídica",
                allowBlank: false,
                rest: "rh.person.legalperson.Restful",
            };
        else if (param == 3)
            return {
                name: "bloke",
                xtype: "rest-autocompletefield",
                fieldLabel: "Autoridade",
                allowBlank: false,
                rest: "rh.person.naturalperson.Restful",
            };
        else if (param == 4)
            return {
                name: "bloke",
                xtype: "rest-autocompletefield",
                fieldLabel: "Pessoa Fisica",
                allowBlank: false,
                rest: "rh.person.naturalperson.Restful",
            };
    },

    filterShowRemoved: function(item, checked) {
        if(!checked)
            this.setFilterProperty('removed_by', null, 3000);
        else
            this.removeFilterProperty('removed_by', 3000);
    },

    filterShowArchived: function(item, checked) {
        if(!checked)
            this.setFilterProperty('closed_by', null, 3002);
        else
            this.removeFilterProperty('closed_by', 3002);
    },

    filterWithoutActingZone: function(item, checked) {
        if(checked)
            this.setFilterProperty('acting_zone', null, 3001);
        else
            this.removeFilterProperty('acting_zone', 3001);
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = judicial.secretary.workspace.Grid.superclass.getFilterMenu.call(this, {}).concat([
                '-',
                {
                    text: 'Por Órgão de Execução',
                    scope: this,
                    handler: this.filterExecutionOrgan
                },
                {
                    text: 'Por Tipo de Procedimento',
                    scope: this,
                    handler: this.filterTypeLawsuit
                },
                '-',
                {
                    text: 'Por Interessado',
                    scope: this,
                    handler: this.filterInterested
                },
                {
                    text: 'Por Investigado/Apontado',
                    scope: this,
                    handler: this.filterBloke
                },
                '-',
                {
                    text: 'Mostrar também os removidos',
                    hideOnClick: false,
                    checked: false,
                    listeners: {
                        scope: this,
                        checkchange: this.filterShowRemoved
                    }
                },
                {
                    text: 'Mostrar também os arquivados',
                    hideOnClick: false,
                    checked: false,
                    listeners: {
                        scope: this,
                        checkchange: this.filterShowArchived
                    }
                }
            ]);

        return this._filterMenu;
    },

    openDocument: function() {
        var selected = this.getSelectionModel().getSelected();
        var width, height, left, top;

        width = (Ext.getBody().getBox().width * 0.9);
        height = (Ext.getBody().getBox().height * 0.9);
        left = screenX + (screen.width / 2) - (width / 2);
        top = (screen.height / 2) - (height / 2);

        var spec = [
            'width=' + width,
            'height=' + height,
            'top=' + top,
            'left=' + left,
            'scrollbars',
            'resizable',
            'status',
            'titlebar'
        ];

        if (this._wndP) this._wndP.close();

        this._wndP = window.open(
            '/athenas/EJudOutCourtLawsuit/viewer/#secretary/0/' + this.documentPath(selected),
            'ejud-proccess',
            spec.join(', ')
        );

        if (!this._wndP)
            Ext.Msg.show({
                title: 'Abrindo procedimento!',
                msg: 'O bloqueador de popup interceptou a abertura do procedimento!',
                buttons: Ext.Msg.OK,
                icons: Ext.Msg.ERROR
            });

        this._wndP.config = function () {
            return selected.data;
        };

        this._wndP.MainRemoteObserver = core.RemoteObserver;
        this._wndP.getRemoteObserver = function () { return core.RemoteObserver; };
    },

    openReminderWindow: function () {
        var selections = this.getSelectionModel().getSelections();
        if (selections.length > 0) {
            lawsuit = selections.map(function (data) { return data.get('pk'); })[0];
            is_received = selections.map(function (data) { return data.get('is_received'); })[0];
        }
        if (is_received)
            Ext._create('judicial.reminder.lawsuit.WindowManage', {
                modal: true,
                params: {
                    lawsuit: lawsuit
                }
            }).show();
        else
            Ext.Msg.show({
                title: 'Ação não permitida',
                msg: 'Não é possivel adicionar um lembrete para um procedimento que ainda não foi recebido.' +
                    'Receba o procedimento para adicionar o lembrete',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK
            });
    },

    classLawsuitGrid: function() {
        return 'judicial.secretary.workspace.Grid';
    },

    classLawsuitRest: function() {
        return 'judicial.secretary.workspace.Restful';
    },

    getDefaultItemsContextMenu: function () {
        var menu = [
            {
                text: 'Abrir Procedimento',
                iconCls: 'icon-judicial icon-ejud-open-proccess',
                scope: this,
                handler: this.validateOpenDocument
            },
            {
                text: 'Lembretes',
                iconCls: 'icon-core icon-core-balloons',
                scope: this,
                handler: this.openReminderWindow,
            },
            {
                text: 'Enviar para promotoria',
                iconCls: 'icon-judicial icon-judicial icon-ejud-give-back-diligence',
                scope: this,
                handler: this.giveBackExecutionOrgan,
            }
        ];

        return menu;

    },

    getRowContextMenu: function (toAppend) {
        this._rowContextMenu = Ext._create('Ext.menu.Menu', {
            items: this.getDefaultItemsContextMenu().concat(toAppend),
        });

        return this._rowContextMenu;
    },

    buildContextMenu: function (selection, xy) {
        if (selection.length >= 1) {
            this.getRowContextMenu([]).showAt(xy);
            return true;
        }

        return false;
    },

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 90,
                        menuDisabled: true,
                        renderer: core.rendererIconGrid,
                        hidden: true
                    },
                    { sortable: true, header: 'Código', dataIndex: 'origin_codigo', width: 120, hidden: true },
                    { sortable: true, header: 'Data Envio para Secretaria', dataIndex: 'date_send_secretary', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { sortable: false, header: 'Interessado', dataIndex: 'origin_interessado_unicode', width: 200 },
                    { sortable: true, header: 'Procedimento', renderer: this.formatCacheNumberUrgent, dataIndex: 'cache_number', width: 150 },
                    { sortable: true, header: 'Título', dataIndex: 'title', id: 'autoExpandColumn' },
                    { sortable: false, header: 'Fim do Prazo', dataIndex: 'deadline', width: 125, renderer: this.deadlineRenderer },
                    { sortable: true, header: 'Tipo do Procedimento', dataIndex: 'type_lawsuit_display', width: 165 },
                    { sortable: true, header: 'Localização', dataIndex: 'current_location_unicode', width: 325, hidden: false },
                    { sortable: true, header: 'Área de atuação', dataIndex: 'acting_zone_unicode', width: 165, hidden: true },
                    { sortable: false, header: 'Último Movimento', dataIndex: 'last_document_signed', width: 300, hidden: true },
                    { sortable: true, header: 'Data do Movimento', dataIndex: 'date_last_document_signed', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { sortable: true, header: 'Na Casa', dataIndex: 'location_unicode', width: 325, hidden: true },
                    { sortable: true, header: 'Ano', dataIndex: 'year', width: 90, hidden: true },
                    { sortable: true, header: 'Número', dataIndex: 'number_lawsuit', width: 90, hidden: true }
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false,
            }
        );

        judicial.secretary.workspace.Grid.superclass.constructor.call(this, cfg);

        
        this.on({
            scope: this,
            rowcontextmenu: function (me, index, evt) {
                var selections = this.getSelectionModel().getSelections();

                if (this.buildContextMenu(selections, evt.getXY())) {
                    evt.stopEvent();
                }
            }
        });
        
    }
});

core.RestfulGrid.register(
    'judicial.secretary.workspace.Restful',
    'judicial.secretary.workspace.Grid'
);
