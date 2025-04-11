Ext._define('raf.typequiz.Restful', {
    extend: 'core.Restful',

    resource: 'RAFTypeQuiz',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.typequiz.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "title" },
                {type: "int", name: "group" },
                {type: "string", name: "group_display" },
                {type: "int", name: "species" },
                {type: "string", name: "species_display" },
            ]);

        return this._fields;
    }
});
