Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveRestful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'INSPECTIONEffetivePossessionMovement',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveRestful.superclass.getFields.call(this, cfg).concat([
                { type: 'string', name: 'employee_unicode', },
                { type: 'string', name: 'occupation_unicode', },
            ]);
        return this._fields;
    }

});
