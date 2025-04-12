Ext._define('judicial.parts.GeneralMotionRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EJudGeneralMotion',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.GeneralMotionRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "name"
                },
                {
                    type: "string",
                    name: "content"
                },
                {
                    type: "int",
                    name: "legal_classification",
                    useNull: true,
                },
                {
                    type: "string",
                    name: "legal_classification_unicode"
                }
            ]);

        return this._fields;
    }
});
