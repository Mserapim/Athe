Ext._define('rh.gfp.conference.liquidvalue.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.conference.liquidvalue.Restful',

    hideItemsToolbar: ['edit',],
    hideActions: ['remove', 'copy', 'edit'],

    configOrderToolBar: ['-', 'payroll', '-', '->'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Folha', dataIndex: 'folha_unicode', width: 300},
                    {header: 'Servidor', dataIndex: 'servidor_unicode', id: 'autoExpandColumn'},
                    {header: 'Total líquido ContraCheque', id: 'total_liquido', dataIndex: 'total_liquido', width: 150, renderer: toolkit.util.formatCurrency},
                    {header: 'Total líquido Rúbricas', id: 'total_liquido_lancamentos', dataIndex: 'total_liquido_lancamentos', width: 150, renderer: toolkit.util.formatCurrency},
                ]
            );

        return this._columnModel;
    },

    observePayroll: function(){
        if(this.payroll()){
            this.setParam('folha', this.payroll().pk);
            this.setFilterProperty('folha', this.payroll().pk, 100);
        }
        else{
            this.getStore().removeAll();
            this.setFilterProperty('folha', 0, 100, false);
        }
    },

    payroll: function(value, dispatch){
        dispatch = core.nullValue(dispatch, true);

        if(value !== undefined){
            this._payroll = value;

            if(dispatch) this.observePayroll();
        }
        else
            return this._payroll;
    },

    getCurrentPayroll: function(){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'GFPPayroll',
                'working'
            ),
            method: 'GET',
            success: function(request) {
                var code = Ext.decode(request.responseText);
                if(code.payroll && code.payroll.id){
                    var payrollField = this.getPayrollField();
                    if(payrollField)
                        payrollField.setValue(code.payroll.id);
                }
            },
            scope: this
        });
    },

    getPayrollField: function(cfg) {
        if(!this._payrollField)
            this._payrollField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Folha',
                name: 'payroll',
                rest: 'rh.gfp.payroll.PayrollRestful',
                width: 300,
                comboListeners: {
                    scope: this,
                    changevalid: function(combo, value, oldvalue, valid) {
                        if(valid)
                            this.payroll(combo.store.getById(value).data, true);
                    }
                }
            });

        return this._payrollField;
    },

    getConfigActionsItems: function(cfg){
        if(!this._configActionsItems){
            rh.gfp.paycheck.PayCheckGrid.superclass.getConfigActionsItems.call(this, cfg);
            var _menu = {
                payroll: this.getPayrollField(cfg),
            };
            Ext.apply(this._configActionsItems, _menu);

        }
        return this._configActionsItems;
    },

    postCreate: function(grid){
        this.getCurrentPayroll();
    },

});


core.RestfulGrid.register(
    'rh.gfp.conference.liquidvalue.Restful',
    'rh.gfp.conference.liquidvalue.Grid'
);
