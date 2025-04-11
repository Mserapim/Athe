
Ext._define('judicial.council.DevolutionRecommendationRestful', {
    extend: 'core.Restful',

    resource: 'CouncilDevolutionRecommendation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.council.DevolutionRecommendationRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "date",
                    name: "signed_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "int",
                    name: "shared_with_lawsuit",
                    useNull: true
                },
                {
                    type: "string",
                    name: "shared_with_lawsuit_unicode"
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
                    type: "string",
                    name: "type_part"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "date",
                    name: "modified_at",
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
                },
                {
                    type: "string",
                    name: "justification"
                },
                {
                    type: "int",
                    name: "signed_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "signed_by_unicode"
                },
                {
                    type: "string",
                    name: "partlawsuit_ptr"
                },
                {
                    type: "string",
                    name: "cache_rendered"
                },
                {
                    type: "int",
                    name: "lawsuit",
                    useNull: true
                },
                {
                    type: "string",
                    name: "lawsuit_unicode"
                },

                {
                    type: "int",
                    name: "devolution_to",
                    useNull: true
                },
                {
                    type: "string",
                    name: "devolution_to_unicode"
                }
            ]);

        return this._fields;
    }
});
