 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.cumulative_exercises_consolidated.Restful',

    restWindow: 'rh.gratifications_manager.cumulative_exercises_consolidated.Window',

    constructor: function(cfg) {
        rh.gratifications_manager.cumulative_exercises_consolidated.Grid.superclass.constructor.call(this, cfg);
    },

    hideActions: ['add','edit','remove', 'copy', 'edit'],

    configOrderToolBar: ['defer_all','-','defer_selected','-','search','->','download'],

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: this.getConfigItemsToolbar(cfg),
            });

            var filterMenu = this.getFilterMenu();
            if(filterMenu && !(cfg || this).hiddenFilter)
                this._toolbar.add([
                    '-',
                    {
                        text: 'Filtro',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: filterMenu
                    }
                ]);

            this._toolbar.add([
                '-',
                {
                    xtype: 'button',
                    text: 'Limpar todos os filtros',
                    iconCls: 'icon-fopag icon-arrow-repeat',
                    handler: function(){ this.setFilterEmpty() },
                    scope: this
                }
            ]);

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

    setFilterEmpty: function(){
        this._configItemsToolbar.forEach(function(item, i){
            if(item.emptyText == 'Motor de buscas'){
                item.setValue('');
            }
        });

        this.removeFilterProperty('paid_out', 1, false);

        this._toolbar.items.items.forEach(function(item, i){
            if(item.text == 'Filtro'){
                item.menu.items.items.forEach(function(item){
                    item.id == 'todos' ? item.setChecked(true) : item.setChecked(false);
                });
            }
        });

        var store = this.getStore();
        store.baseParams.filter = Ext.encode([]);
        store.baseParams.keyword = null;
        store.load({})
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: '', dataIndex: 'icons', width: 65, renderer: toolkit.util.formatStatus},
                    {header: 'Substituto', dataIndex: 'employee_unicode', id: 'autoExpandColumn'},
                    {header: 'Titularidade', dataIndex: 'titularidade', width: 350},
                    {header: 'Qtd Dias', dataIndex: 'days_consolidated', width: 70},
                    {header: 'Valor Calculado', dataIndex: 'value_calculated', width: 120, renderer: toolkit.util.formatCurrency},
                    // {header: 'Período Pgto', dataIndex: 'periodo_pgto', width: 80},
                    // {header: 'Folha Destino', dataIndex: 'payroll_applied', width: 350},
                ]
            );

        return this._columnModel;
    },

    setParamsFilterMenu: function(chk, option){
        var autoLoadPayMonth = (option == 'todos' || !chk.checked == false) ? true : false;
        this.removeFilterProperty('defer', 1, autoLoadPayMonth);

        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
            if(item.id != option){ item.setChecked(false); }

            if(!chk.checked == false && item.id == 'todos'){ item.setChecked(true); }
        });

        if(option == 'deferidos' && !chk.checked == true){
            this.addFilterProperty('defer', true, 1, true);
        }else if(option == 'nao_deferidos' && !chk.checked == true){
            this.addFilterProperty('defer', false, 1, true);
        }
    },

    getFilterMenu: function(){
        this._getFilterMenu = [
            {
                id: 'todos',
                text: 'Todos',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'todos') },
            },
            {
                id: 'deferidos',
                text: 'Somente Deferidos',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'deferidos') },
            },
            {
                id: 'nao_deferidos',
                text: 'Somente Não Deferidos',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'nao_deferidos') },
            },
        ];

        return this._getFilterMenu
    },

    _desconsolidateItem: function(mov_sub_consolidated_id){
        xt.Msg.show({
            msg: 'Tem certeza que deseja desconsolidar este registro?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GMCumulativeExercisesConsolidated','desconsolidated_mov_sub_cons'),
                    params: { mov_sub_consolidated_id: mov_sub_consolidated_id },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: icon,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                        this.getStore().reload();
                    },
                    failure: function() {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                        });
                    },
                    scope: this
                });
            }
        })
    },

    _calculateItem: function(mov_sub_consolidated_id){
        xt.Msg.show({
            msg: 'Tem certeza que deseja calcular?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GMCumulativeExercisesConsolidated','calculate_consolidated'),
                    params: { mov_sub_consolidated_id: mov_sub_consolidated_id },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: icon,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                        this.getStore().reload();
                    },
                    failure: function() {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                        });
                    },
                    scope: this
                });
            }
        })
    },

    _deferConsolidated: function(consolidated_id){
        Ext.Msg.show({
            msg: 'Tem certeza que deseja deferir o consolidado selecionado?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GMCumulativeExercisesConsolidated','defer_consolidated'),
                    params: { consolidated_ids: [consolidated_id] },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR
                        if(obj.success == true){
                            Ext.Msg.show({
                                width:"400px",
                                title: this.title,
                                icon: icon,
                                buttons: Ext.Msg.OK,
                                msg: obj.message
                            });
                            this.getStore().reload();
                        }else{
                            Ext.Msg.show({
                                minWidth: 400,
                                title: this.title,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: obj.message
                            });
                        }
                    },
                    scope: this
                });
            }
        })
    },

    _deferSelectedConsolidateds: function(){
        var selecteds = this.getSelectionModel().getSelections().map(function(a){ return a.id; });

        if(selecteds.length == 0){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Escolha pelo menos um registro para deferir.'
            });
        }else{
            Ext.Msg.show({
                msg: 'Tem certeza que deseja deferir os consolidados selecionados (serão deferidos somente os "calculados")?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (b) {
                    if (b == 'no') return;

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('GMCumulativeExercisesConsolidated','defer_consolidated'),
                        params: { consolidated_ids: selecteds },
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success == true){
                                new rh.gratifications_manager.cumulative_exercises_consolidated.PayrollWindow({
                                    action: 'update',
                                    params: { consolidated_ids: selecteds },
                                }).show();
                            }else{
                                Ext.Msg.show({
                                    minWidth: 400,
                                    title: this.title,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: obj.message
                                });
                            }
                        },
                        scope: this
                    });
                }
            })
        }
    },

    _deferAllConsolidateds: function(){
        Ext.Msg.show({
            msg: 'Tem certeza que deseja deferir todos os consolidados (serão deferidos somente os "calculados")?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GMCumulativeExercisesConsolidated','defer_consolidated'),
                    params: { consolidated_ids: 'all' },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.success == true){
                            new rh.gratifications_manager.cumulative_exercises_consolidated.PayrollWindow({
                                action: 'update',
                                params: { consolidated_ids: ['all'] },
                            }).show();
                        }else{
                            Ext.Msg.show({
                                minWidth: 400,
                                title: this.title,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: obj.message
                            });
                        }
                    },
                    scope: this
                });
            }
        })
    },

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-fopag icon-notebook-minus',
                tooltip: 'Desconsolidar',
                scope: this,
                handler: function(action, index){ this._desconsolidateItem(action._store.getAt(index).data.pk) },
            },
            {
                iconCls: 'icon-16px icon-core icon-core-run',
                tooltip: 'Calcular',
                scope: this,
                handler: function(action, index){ this._calculateItem(action._store.getAt(index).data.pk) },
            },
            {
                iconCls: 'icon-16px icon-fopag icon-medal-arrow',
                tooltip: 'Deferir',
                scope: this,
                handler: function(action, index){ this._deferConsolidated(action._store.getAt(index).data.pk) },
            },
        ];
    },

    getConfigActionsItems: function(cfg){
        var menu = rh.gfp.payroll.EventGrid.superclass.getConfigActionsItems.call(this, cfg);

        menu['defer_all'] = {
            text: 'Deferir Todos',
            iconCls: 'icon-rh icon-core-documents',
            scope: this,
            handler: function(){ this._deferAllConsolidateds() },
        };
        menu['defer_selected'] = {
            text: 'Deferir Selecionados',
            iconCls: 'icon-fopag icon-ui-toolbar-arrow',
            scope: this,
            handler: function(){ this._deferSelectedConsolidateds() },
        };
        
        return menu;
    },
});

core.RestfulGrid.register(
    'rh.gratifications_manager.cumulative_exercises_consolidated.Restful',
    'rh.gratifications_manager.cumulative_exercises_consolidated.Grid'
);
