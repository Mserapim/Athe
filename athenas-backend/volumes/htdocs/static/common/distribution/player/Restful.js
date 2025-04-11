Ext._define('common.distribution.player.Restful', {
    extend: 'core.Restful',

    resource: 'CDPlayer',

    getFields: function (cfg) {
        if (!this._fields) {
            this._fields = common.distribution.player.Restful
                               .superclass
                               .getFields
                               .call(this, cfg)
                               .concat([
                {
                    type: "string",
                    name: "title"
                },
                {
                    type: "int",
                    name: "distribution",
                    useNull: true
                },
                {
                    type: "string",
                    name: "distribution_unicode"
                },
                {
                    type: "bool",
                    name: "active"
                },
                {
                    type: "date",
                    name: "modified_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "int",
                    name: "modified_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "modified_by_unicode"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "int",
                    name: "created_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "created_by_unicode"
                }
            ]);
        }
        
        return this._fields;
    }
});
