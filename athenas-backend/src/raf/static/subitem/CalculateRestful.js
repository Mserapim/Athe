Ext._define('raf.subitem.CalculateRestful', {
    extend: 'core.Restful',

    resource: 'RAFSubItemCalculate',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.subitem.CalculateRestful.superclass.getFields.call(this, cfg).concat([
                {
                    name: 'icons'
                },
                {
                    type: "integer",
                    name: "subitem",
                    useNull: true
                },
                {
                    type: "string",
                    name: "subitem_unicode"
                },
                {
                    type: "integer",
                    name: "from_the_sum",
                    useNull: true
                },
                {
                    type: "string",
                    name: "from_the_sum_unicode"
                },
                // {
                //     type: "integer",
                //     name: "affectation",
                //     useNull: true
                // },
                {
                    type: "string",
                    name: "affectation_display"
                },
                {
                    type: "string",
                    name: "affectation"
                },
                {
                    type: "bool",
                    name: "previous_month"
                },
            ]);

        return this._fields;
    }
});
