
Ext._define('judicial.parts.AdjustmentLawsuitRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EJudAdjustmentLawsuit',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.AdjustmentLawsuitRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "last_title"
                },
                {
                    type: "string",
                    name: "new_title"
                },
                {
                    type: "int",
                    name: "last_acting_zone",
                    useNull: true
                },

                {
                    type: "string",
                    name: "last_acting_zone_unicode"
                },
                {
                    type: "int",
                    name: "new_acting_zone",
                    useNull: true
                },
                {
                    type: "string",
                    name: "new_acting_zone_unicode"
                },
                {
                    type: "int",
                    name: "new_main_matter",
                    useNull: true
                },
                {
                    type: "string",
                    name: "new_main_matter_unicode"
                },
                {
                    type: "int",
                    name: "last_main_matter",
                    useNull: true
                },
                {
                    type: "string",
                    name: "last_main_matter_unicode"
                },
            ]);

        return this._fields;
    }
});
