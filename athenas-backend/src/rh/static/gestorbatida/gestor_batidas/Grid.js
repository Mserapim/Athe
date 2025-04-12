Ext._define('rh.gestorbatida.gestor_batidas.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gestorbatida.gestor_batidas.Window',

    configOrderToolBar: ['-', 'startdatefilter', '-', 'enddatefilter', '-', 'cleandate'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: 'Marcação Válida',
                        dataIndex: 'marcacao_valida',
                        width: 100,
                        renderer: function(value) {
                            if (value) {
                                return '<div class="tk-grid-icon-cell icon-core icon-core-success" ext:qtip="Válida" ext:qwidth="50"></div>';
                            } else {
                                return '<div class="tk-grid-icon-cell icon-core icon-core-delete" ext:qtip="Não válida" ext:qwidth="55"></div>';
                            }
                        }
                    },
                    {header: 'Ponto - Data e Hora', dataIndex: 'date_time', width: 200},
                    {header: 'Tipo de Justificativa', dataIndex: 'tipo_justificativa_label',  id: 'autoExpandColumn'},
                    {header: 'Observação', dataIndex: 'justificativa', width: 100},
                    {header: 'IP', dataIndex: 'ip', width: 120, hidden: true},
                    {header: 'Lotação', dataIndex: 'workplace', width: 200, hidden: true},
                    {header: 'Tabela de Importação', dataIndex: 'tabela_import', width: 150, hidden: true},
                    {header: 'Código de Importação', dataIndex: 'codigo_import', width: 150, hidden: true},           
                ]

            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if (!this._toolbar) {
            var filterByDateLabel = {
                xtype: 'tbtext',
                text: 'Filtrar por data:',
                style: {
                    marginRight: '10px',
                    fontWeight: 'bold',
                    fontSize: '11px'
                }
            };

            var menuFiltroMarcacaoValida = this.menuFiltroMarcacaoValida();
    
            var toolbarItems = [
                {
                    text: 'Justificativa por data',
                    iconCls: 'icon-core icon-core-add',
                    scope: this,
                    handler: this.JustificarPorData
                },
                '-',
                {
                    text: 'Justificativa por período',
                    iconCls: 'icon-core icon-core-calendar-plus',
                    scope: this,
                    handler: this.JustificarPorPeriodo
                },
                '-',
                {
                    text: 'Invalidar Marcações',
                    iconCls: 'icon-core icon-core-delete',
                    scope: this,
                    handler: this.invalidarMarcacoesSelecionadas
                },
                '-',
                '->',
                '-',
                {
                    text: 'Filtrar Marcação',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroMarcacaoValida
                },
                '-',
                filterByDateLabel,
                this.getStartdatefilterAction(),
                '-',
                this.getEnddatefilterAction(),
                '-',
                this.getCleandateAction()
            ];
    
    
            this._toolbar = Ext._create('Ext.Toolbar', {
                items: toolbarItems,
                style: cfg.toolbarStyle
            });
        }
    
        return this._toolbar;
    },

    getCleandateAction: function () {
        if (!this._cleanDate) {
            this._cleanDate = Ext._create('Ext.Button', {
                text: 'Limpar',
                iconCls: 'icon-usefulday icon-usefulday-calendar-remove-button',
                scope: this,
                handler: function () {
                    this.getStartdatefilterAction().setValue();
                    this.getEnddatefilterAction().setValue();
                    this.removeFilterProperty('marcacao__date__gte', 1003, false);
                    this.removeFilterProperty('marcacao__date__lte', 1004, true);
                }
            });
        }

        return this._cleanDate;
    },

    getStartdatefilterAction: function () {
        if (!this._startDateFilter) {
            var now = new Date();
            var firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

            this._startDateFilter = Ext._create('Ext.form.DateField', {
                emptyText: 'Data Início',
                format: 'd/m/Y',
                width: 90,
                value: firstDayOfMonth
            });

            this._startDateFilter.on({
                scope: this,
                select: function (me, value) {
                    if (value !== "") {
                        var formattedDate = Ext.util.Format.date(value, 'Y-m-d');
                        _day = this.getEnddatefilterAction().getValue();
                        if (_day && _day < value)
                            Ext.Msg.show({
                                title: 'Alterando estado de conservação',
                                msg: 'A data de inicial deve ser menor que a data final',
                                icon: Ext.Msg.WARNING,
                                buttons: Ext.Msg.OK
                            });
                        else {
                            this.removeFilterProperty('marcacao__date__year', 1003, false);
                            this.removeFilterProperty('marcacao__date__year', 1004, false);
                            this.setFilterProperty('marcacao__date__gte', formattedDate, 1003, true);

                        }
                    } else {
                        this.removeFilterProperty('marcacao__date__gte', 1003, false);
                        this.setFilterProperty('marcacao__date__year', new Date().format('Y'), 1004, true);
                    }
                }
            });
        }

        return this._startDateFilter;
    },

    getEnddatefilterAction: function () {
        if (!this._endDateFilter) {
            var now = new Date();
            var lastDayOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
            this._endDateFilter = Ext._create('Ext.form.DateField', {
                emptyText: 'Data Fim',
                format: 'd/m/Y',
                width: 90,
                value: lastDayOfMonth
            });

            this._endDateFilter.on({
                scope: this,
                select: function (me, value) {
                    if (value !== "") {
                        var formattedDate = Ext.util.Format.date(value, 'Y-m-d');
                        _day = this.getStartdatefilterAction().getValue();
                        if (_day > value)
                            Ext.Msg.show({
                                title: 'Alterando estado de conservação',
                                msg: 'A data de final deve ser maior que a data inicial',
                                icon: Ext.Msg.WARNING,
                                buttons: Ext.Msg.OK
                            });
                        else
                            this.setFilterProperty('marcacao__date__lte', formattedDate, 1004, true);
                    }
                    else
                        this.removeFilterProperty('marcacao__date__lte', 1004, true);
                }
            });
        }

        return this._endDateFilter;
    },

    getCleandateAction: function () {
        if (!this._cleanDate) {
            this._cleanDate = Ext._create('Ext.Button', {
                text: 'Limpar',
                iconCls: 'icon-usefulday icon-usefulday-calendar-remove-button',
                scope: this,
                handler: function () {
                    this.getStartdatefilterAction().setValue();
                    this.getEnddatefilterAction().setValue();
                    this.removeFilterProperty('marcacao__date__gte', 1003, false);
                    this.removeFilterProperty('marcacao__date__lte', 1004, true);
                }
            });
        }

        return this._cleanDate;
    },

    menuFiltroMarcacaoValida: function() {
        this._menuFiltroMarcacaoValida = [
            {
                id: 'todos',
                text: 'Todas',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarMarcacaoValida(chk, 'todos') },
            },
            {
                id: 'valido',
                value: true,
                text: 'Válidas',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarMarcacaoValida(chk, 'valido') },
            },
            {
                id: 'invalido',
                value: false,
                text: 'Inválidas',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarMarcacaoValida(chk, 'invalido') },
            },
        ];
        return this._menuFiltroMarcacaoValida;
    },
    
    filtrarMarcacaoValida: function(chk, opcao) {
        var filtros_aplicar = [];
        if(opcao == 'todos'){
            if(!chk.checked == true){
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != 'todos' && item.checked == true){
                        item.setChecked(false);
                    }
                });
            } else {
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != 'todos' && item.checked == true){
                        filtros_aplicar.push(item.value);
                    }
                });
                if(filtros_aplicar.length == 0){
                    filtros_aplicar.push(true);
                    this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                        if(item.id == 'valido'){ item.setChecked(true); }
                    });
                }
            }
        } else {
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && item.checked == true){
                    item.setChecked(false);
                } else if (
                    (item.id != 'todos' && item.id == opcao && !chk.checked == true) ||
                    (item.id != 'todos' && item.id != opcao && item.checked == true)
                ) {
                    filtros_aplicar.push(item.value);
                }
            });
        }
    
        if(filtros_aplicar.length > 0){
            this.setFilterProperty('marcacao_valida__in', filtros_aplicar, 1005, true);
        } else {
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && !chk.checked == false){
                    item.setChecked(true);
                }
            });
            this.removeFilterProperty('marcacao_valida__in', 1005, true);
        }
    },

    JustificarPorData: function() {
        var servidorRecord = this.observeFn();
        if (!servidorRecord) {
            Ext.Msg.alert('Erro', 'Selecione um servidor na grid superior.');
            return;
        }

        var justificativaWindow = Ext._create('rh.gestorbatida.gestor_batidas.Window', {
            servidorRecord: servidorRecord,
            listeners: {
                close: function() {
                    this.getStore().reload();
                },
                scope: this
            }
        });
    
        justificativaWindow.show();
    },

    
    JustificarPorPeriodo: function() {
        var servidorRecord = this.observeFn();
        if (!servidorRecord) {
            Ext.Msg.alert('Erro', 'Selecione um servidor na grid superior.');
            return;
        }

        var justificativaWindow = Ext._create('rh.gestorbatida.gestor_batidas.PeriodoWindow', {
            servidorRecord: servidorRecord,
            listeners: {
                close: function() {
                    this.getStore().reload();
                },
                scope: this
            }
        });
    
        justificativaWindow.show();
    },

    invalidarMarcacoesSelecionadas: function() {
        var grid = this;
        var selectedRecords = this.getSelectionModel().getSelections();
    
        if (selectedRecords.length === 0) {
            Ext.Msg.alert('Aviso', 'Nenhuma marcação selecionada.');
            return;
        }
    
        var ids = selectedRecords.map(function(record) {
            return record.get('id');
        });

        Ext.Msg.confirm('Confirmação', 'Atenção! Caso tenha um relatório de ponto já enviado, essa ação poderá acarretar em divergências com o relatório. Tem certeza que deseja invalidar as marcações selecionadas?', function(btn) {
            if (btn === 'yes') {
                Ext.Ajax.request({
                    url: core.callAction('RHGestorBatidas', 'invalidar_marcacoes'),
                    method: 'POST',
                    params: {
                        ids: JSON.parse(JSON.stringify(ids))
                    },
                    success: function(response) {
                        var resp = Ext.decode(response.responseText);
                        if (resp.success) {
                            Ext.Msg.alert('Sucesso', 'Marcações invalidadas com sucesso!');
                            grid.getStore().reload();
                        } else {
                            Ext.Msg.alert('Erro', resp.message);
                        }
                    },
                    failure: function(response) {
                        Ext.Msg.alert('Erro', 'Erro ao enviar solicitação ao servidor');
                    }
                });
            }
        });
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        rh.gestorbatida.gestor_batidas.Grid.superclass.constructor.call(this, cfg);
    },

});


core.RestfulGrid.register(
    'rh.gestorbatida.gestor_batidas.Restful',
    'rh.gestorbatida.gestor_batidas.Grid'
);
