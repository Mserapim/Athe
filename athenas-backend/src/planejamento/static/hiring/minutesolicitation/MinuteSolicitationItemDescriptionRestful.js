Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationItemDescription',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitation.MinuteSolicitationItemDescriptionRestful.superclass.getFields.call(this, cfg).concat([
                 {
                    type: "int", 
                    name: "solicitation_item"
                },
                {
                    type: "string", 
                    name: "solicitation_item_unicode"
                }, 
                {
                    type: "int",
                    name: "item_description"
                },
                {
                    type: "string", 
                    name: "item_description_unicode"
                }, 
            ]);

        return this._fields;
    }
});
