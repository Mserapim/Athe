Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalRestful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'INSPECTIONExternalPossessionMovement',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalRestful.superclass.getFields.call(this, cfg).concat([
                { type: 'string', name: 'employee_unicode', },
                { type: 'string', name: 'occupation_unicode', },
                { type: 'string', name: 'category', },
            ]);
        return this._fields;
    }

});
