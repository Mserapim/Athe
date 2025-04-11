Ext._define('rh.gfp.gcpp.payroll.Restful', {
    extend: 'core.Restful',

    resource: 'GfpGCPPPayrollRestfull',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.gcpp.payroll.Restful.superclass.getFields.call(this, cfg).concat([
                {type: 'int',name: 'id'},
                {type: 'bool', name: 'processado'},
                {type: 'int', name: 'periodo', useNull: true},
                {type: 'string', name: 'periodo_unicode'},
                {type: 'string', name: 'processado_por_unicode'},
                {type: 'int', name: 'status', useNull: true},
                {type: 'string', name: 'status_display'},
                {type: 'string', name: 'fechado_por_unicode'},
                {type: 'int', name: 'tipo_folha', useNull: true},
                {type: 'string', name: 'tipo_folha_unicode'},
                {name: 'icons'},
                {type: 'int', name: 'periodo_ano'},
                {type: 'int', name: 'periodo_mes'},
                {type: 'bool', name: 'is_working'},
                {type: 'string', name: 'complement'},
                {type: 'string', name: 'complement_display'},
                
            ]);

        return this._fields;
    }
});

Ext._define('rh.gfp.gcpp.payroll.OpendedPayrollRestful', {
    extend: 'rh.gfp.gcpp.payroll.Restful',

    resource: 'GFPOpenedPayroll',
});