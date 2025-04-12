
Ext._define('judicial.parts.DismembermentMultiProcessChunkRestful', {
    extend: 'core.Restful',

    resource: 'EjudDismembermentMultiProcessChunk',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.DismembermentMultiProcessChunkRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "change_title"
                },
                {
                    type: "int",
                    name: "main_matter"
                },
                {
                    type: "string",
                    name: "main_matter_unicode"
                },
                
            ]);

        return this._fields;
    }
});
