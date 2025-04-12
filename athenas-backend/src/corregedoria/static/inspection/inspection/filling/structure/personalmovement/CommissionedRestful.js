Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedRestful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'INSPECTIONCommissionedPossessionMovement',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedRestful.superclass.getFields.call(this, cfg).concat([
                { type: 'string', name: 'employee_unicode', },
                { type: 'string', name: 'occupation_unicode', },
            ]);
        return this._fields;
    }

});
