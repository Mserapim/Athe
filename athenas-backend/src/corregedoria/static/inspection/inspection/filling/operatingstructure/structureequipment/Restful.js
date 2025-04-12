Ext._define('corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONStructureEquipment',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "equipment"},
                {type: "int", name: "amount", useNull: true},
                {type: "int", name: "status"},
                {type: "string", name: "status_display"},
                {type: "string", name: "observation"},
            ]);

        return this._fields;
    }
});
