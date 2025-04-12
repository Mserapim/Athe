Ext._define('edocs.protocolo.requestform.dependentexclusionitem.Restful', {
    extend: 'core.Restful',

    resource: 'RequestFormDependentExclusionItem',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = edocs.protocolo.requestform.dependentexclusionitem.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "dependent_exclusion", type: "int", useNull: true},
                {name: "dependent_exclusion_unicode", type: "string"},
                {name: "dependent", type: "int", useNull: true},
                {name: "dependent_unicode", type: "string"},
                {name: "income_tax", type: "bool"},
                {name: "post_mortem_pension", type: "bool"}
            ]);

        return this._fields;
    }
});
