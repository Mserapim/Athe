Ext._define('corregedoria.prontuary.career.movement.promotion.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailPromotion',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.career.movement.promotion.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons" },
                {type: "string", name: "exercise" },
                {type: "string", name: "role" },
                {type: "date", name: "date_initial", dateFormat: "d/m/Y" },
                {type: "date", name: "date_final", dateFormat: "d/m/Y" },
                {type: "string", name: "act_initial" },
                {type: "string", name: "act_final" },
            ]);

        return this._fields;
    }
});
