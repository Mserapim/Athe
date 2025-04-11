Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationItemRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationItem',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitation.MinuteSolicitationItemRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "item",
                    useNull: true
                },
                {
                    type: "string",
                    name: "item_unicode"
                },

                {
                    type: "int",
                    name: "solicitation",
                    useNull: true
                },
                {
                    type: "string",
                    name: "solicitation_unicode"
                },
                {
                    type: "float",
                    name: "quantity"
                },
                {
                    type: "int",
                    name: "balanced_oid"
                },
                {
                    type: "bool",
                    name: "is_rebalanced"
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
                    type: "float",
                    name: "unit_value"
                }
            ]);

        return this._fields;
    }
});
