Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationRebalancingRestful', {
    extend: 'core.Restful',

    resource: 'PHMRebalancedSolicitationItem',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitationmanager.MinuteSolicitationRebalancingRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "solicitation_item"
                },
                {
                    type: "string",
                    name: "description"
                },
                {
                    type: "string",
                    name: "brand"
                },
                {
                    type: "string",
                    name: "unit_value"
                }
            ]);

        return this._fields;
    },
});