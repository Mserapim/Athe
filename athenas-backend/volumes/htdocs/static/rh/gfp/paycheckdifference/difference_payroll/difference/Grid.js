Ext._define('rh.gfp.paycheckdifference.difference_payroll.difference.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.paycheckdifference.difference_payroll.difference.Restful',

    hideItemsToolbar: ['remove',],
    hideActions: ['remove','copy', 'edit'],

    configOrderToolBar: ['aplicate_all','-','aplicate_selected','->'],

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            gridAutoLoad: false,
        });

        rh.gfp.paycheckdifference.difference_payroll.difference.Grid.superclass.constructor.call(this, cfg);
        this.setFilterProperty('status__in', ['AVAL']);
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: '', dataIndex: 'icons', width: 80, renderer: toolkit.util.formatStatus},
                    {header: 'Período', dataIndex: 'period_unicode', width: 50},
                    {header: 'Servidor', dataIndex: 'employee_unicode', id: 'autoExpandColumn'},
                    {header: 'Evento Origem', dataIndex: 'event_info', width: 200},
                    {header: 'Folha Origem', dataIndex: 'payroll_event', width: 150},
                    {header: 'Qtd Origem', dataIndex: 'qtd_normalize', width: 80},
                    {header: 'Valor Base - Origem', dataIndex: 'base_value_event', width: 120, 'renderer': toolkit.util.formatCurrency},
                    {header: 'Valor - Origem', dataIndex: 'correct_value_event', width: 100, 'renderer': toolkit.util.formatCurrency},
                    {header: 'Qtd Diferença', dataIndex: 'qtd_diff_normalize', width: 90},
                    {header: 'Valor Base - Diferença', dataIndex: 'base_value_diff', width: 130, 'renderer': toolkit.util.formatCurrency},
                    {header: 'Valor Diferença', dataIndex: 'value_diff', width: 100, 'renderer': toolkit.util.formatCurrency},
                    {header: 'Folha Destino', dataIndex: 'payroll_applied', width: 150},
                    {header: 'Evento Destino', dataIndex: 'event_diff_unicode', width: 200},
                    {header: 'Criado Em', dataIndex: 'created_at', width: 60, hidden: true},
                ]
            );

        return this._columnModel;
    },

    _applicateDifference: function(difference_id){
        xt.Msg.show({
            msg: 'Tem certeza que deseja aplicar a diferença selecionada?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPDifferencePayroll','applicate_difference_validate'),
                    params: { difference_ids: [difference_id] },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.success == true){
                            new rh.gfp.paycheckdifference.difference_payroll.difference.PayrollWindow({
                                action: 'update',
                                params: { difference_ids: [difference_id] },
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

    _applicateSelectedDifference: function(){
        var selecteds = this.getSelectionModel().getSelections().map(function(a){ return a.id; });
        xt.Msg.show({
            msg: 'Tem certeza que deseja aplicar as diferenças selecionadas?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPDifferencePayroll','applicate_difference_validate'),
                    params: { difference_ids: selecteds },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.success == true){
                            new rh.gfp.paycheckdifference.difference_payroll.difference.PayrollWindow({
                                action: 'update',
                                params: { difference_ids: selecteds, period_id: this.params.period },
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

    _applicateAllDifference: function(){
        var period_id = this.params.period
        xt.Msg.show({
            msg: 'Tem certeza que deseja aplicar todas as diferenças em "Avaliar"?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPDifferencePayroll','applicate_all_difference_validate'),
                    params: { period_id: period_id },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.success == true){
                            new rh.gfp.paycheckdifference.difference_payroll.difference.PayrollWindow({
                                action: 'update',
                                params: {
                                    difference_ids: ['all'],
                                    period_id: period_id
                                },
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
    
    _ignorateDifference: function(difference_id){
        xt.Msg.show({
            msg: 'Tem certeza que deseja ignorar a diferença selecionada?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPDifferencePayroll','ignorate_difference'),
                    params: { difference_id: difference_id },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        
                        if(obj.success == true){
                            var icon = Ext.Msg.INFO
                        }else{
                            var icon = Ext.Msg.ERROR
                        }
                        Ext.Msg.show({
                            minWidth: 400,
                            title: this.title,
                            icon: icon,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                        this.getStore().reload();
                    },
                    scope: this
                });
            }
        })
    },

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-fopag icon-medal-arrow',
                tooltip: 'Aplicar',
                scope: this,
                handler: function(action, index){ this._applicateDifference(action._store.getAt(index).data.pk) },
            },
            {
                iconCls: 'icon-16px icon-core icon-core-delete',
                tooltip: 'Ignorar',
                scope: this,
                handler: function(action, index){ this._ignorateDifference(action._store.getAt(index).data.pk) },
            },
        ];
    },

    getConfigActionsItems: function(cfg){
        var menu = rh.gfp.payroll.EventGrid.superclass.getConfigActionsItems.call(this, cfg);

        menu['aplicate_all'] = {
            text: 'Aplicar Todos',
            iconCls: 'icon-rh icon-core-documents',
            scope: this,
            handler: function(){ this._applicateAllDifference() },
        };
        menu['aplicate_selected'] = {
            text: 'Aplicar Selecionados',
            iconCls: 'icon-fopag icon-ui-toolbar-arrow',
            scope: this,
            handler: function(){ this._applicateSelectedDifference() },
        };
        
        return menu;
    },

    setParamsFilterMenu: function(chk, option){
        this._setParamsFilterMenu = core.nullValue(this._setParamsFilterMenu, ['AVAL']);
        if(!chk.checked)
            this._setParamsFilterMenu.push(option)
        else
            this._setParamsFilterMenu.remove(option)

        this.setFilterProperty('status__in', this._setParamsFilterMenu);
    },

    getFilterMenu: function(){
        this._getFilterMenu = [
            {
                text: 'Avaliar',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'AVAL') },
            },
            {
                text: 'Aplicado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'APLI') },
            },
            {
                text: 'Ignorado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'IGNO') },
            }
        ];

        return this._getFilterMenu
    },
});


core.RestfulGrid.register(
    'rh.gfp.paycheckdifference.difference_payroll.difference.Restful',
    'rh.gfp.paycheckdifference.difference_payroll.difference.Grid'
);