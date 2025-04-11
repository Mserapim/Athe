Ext._define('rh.gfp.paycheckdifference.difference_payroll.difference.PayrollGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.paycheckdifference.difference_payroll.difference.PayrollRestful',

    hideItemsToolbar: ['remove','add','edit','search','download'],
    hideActions: ['remove','copy', 'edit'],

    constructor: function (cfg) {  
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            gridAutoLoad: true,
        });

        this.getStore().setBaseParam('periodo_id', 6);
        this.getStore().load();

        rh.gfp.paycheckdifference.difference_payroll.difference.PayrollGrid.superclass.constructor.call(this, cfg);
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: '', dataIndex: 'icons', width: 50, renderer: toolkit.util.rendererIconGrid},
                    {header: 'Tipo de Folha', dataIndex: 'tipo_folha_unicode', width: 200},
                    {header: 'Período', dataIndex: 'periodo_unicode', id: 'autoExpandColumn'},
                    {header: 'Complemento', dataIndex: 'complement_display', width: 100},
                    {header: 'Pagamento em', dataIndex: 'dt_pagamento', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Fechado', dataIndex: 'fechado_por_unicode', width: 170},
                    {header: 'Processado', dataIndex: 'processado_por_unicode', width: 170},
                    {header: 'Folha', dataIndex: 'pendencia_folha', width: 100, renderer: this.rendererPendencies},
                    {header: 'Cont. Interno', dataIndex: 'pendencia_controle', width: 100, renderer: this.rendererPendencies},
                ]
            );

        return this._columnModel;
    },
});


core.RestfulGrid.register(
    'rh.gfp.paycheckdifference.difference_payroll.difference.PayrollRestful',
    'rh.gfp.paycheckdifference.difference_payroll.difference.PayrollGrid'
);