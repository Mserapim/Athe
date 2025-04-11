 Ext._define('rh.gfp.paycheckdifference.difference_payroll.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.paycheckdifference.difference_payroll.Restful',

    restWindow: 'rh.gfp.paycheckdifference.difference_payroll.Window',

    hideItemsToolbar: ['edit','search'],
    hideActions: ['remove', 'copy', 'edit'],

    configOrderToolBar: ['add','-','calculate_all', '-', 'calculate_selected'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Período', dataIndex: 'period', 'maxWidth': 200, id: 'autoExpandColumn'},
                    {header: 'Qtd Diferença', dataIndex: 'qtd_diff', width: 130},
                    {header: 'Qtd Dif. Aplicada', dataIndex: 'qtd_diff_applied', width: 130},
                    {header: 'Qtd Dif. Ignorada', dataIndex: 'qtd_diff_ignored', width: 130},
                    {header: 'Último Cálculo', dataIndex: 'calculate_last_date', width: 120},
                ]
            );

        return this._columnModel;
    },

    _calculatePeriod: function(period_id){
        xt.Msg.show({
            msg: 'Tem certeza que deseja calcular o período selecionado?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPPeriodPayroll','calculate_period'),
                    params: { period_id: period_id },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: Ext.Msg.INFO,
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

    _calculateSelectedPeriods: function(){
        var selecteds = this.getSelectionModel().getSelections().map(function(a){ return a.id; });

        if(selecteds.length == 0){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Escolha pelo menos um período para ser calculado.'
            });
        }else if(selecteds.length > 6){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Escolha no máximo 6 períodos para serem calculados.'
            });
        }else{
            Ext.Msg.show({
                msg: 'Tem certeza que deseja calcular os períodos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (b) {
                    if (b == 'no') return;
    
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('GFPPeriodPayroll','calculate_selected_periods'),
                        params: { periods_ids: selecteds },
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                width:"400px",
                                title: this.title,
                                icon: Ext.Msg.INFO,
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
            });
        }
    },

    _calculateAllPeriods: function(){
        xt.Msg.show({
            msg: 'Tem certeza que deseja calcular todos os períodos?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPPeriodPayroll','calculate_all_periods'),
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: Ext.Msg.INFO,
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
        });
    },

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-core icon-core-run',
                tooltip: 'Calcular',
                scope: this,
                handler: function(action, index){ this._calculatePeriod(action._store.getAt(index).data.pk) },
            },
        ];
    },

    getConfigActionsItems: function(cfg){
        if(!this._configActionsItems){
            rh.gfp.paycheckdifference.difference_payroll.Grid.superclass.getConfigActionsItems.call(this, cfg);
            var _menu = {
                calculate_all:{
                    text: 'Calcular Todos',
                    iconCls: 'icon-fopag icon-arrow-repeat',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Calcular Todos',
                    disabled: false,
                    scope: this,
                    handler: function(){ this._calculateAllPeriods() },
                },
                calculate_selected:{
                    text: 'Calcular Selecionados',
                    iconCls: 'icon-fopag icon-task-select',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Calcular Selecionados',
                    disabled: false,
                    scope: this,
                    handler: function(){ this._calculateSelectedPeriods() },
                },
            };
            Ext.apply(this._configActionsItems, _menu);

        }
        return this._configActionsItems;
    },

});

core.RestfulGrid.register(
    'rh.gfp.paycheckdifference.difference_payroll.Restful',
    'rh.gfp.paycheckdifference.difference_payroll.Grid'
);
