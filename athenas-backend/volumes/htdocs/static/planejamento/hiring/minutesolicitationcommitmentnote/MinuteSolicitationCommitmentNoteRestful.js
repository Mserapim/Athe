Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationCommitmentNote',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "origin",
                    useNull: true
                },
                {
                    type: "string",
                    name: "origin_display"
                },
                {
                    type: "int",
                    name: "kind",
                    useNull: true
                },
                {
                    type: "string",
                    name: "kind_display"
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
                    type: "int",
                    name: "classification",
                    useNull: true
                },
                {
                    type: "string",
                    name: "classification_display"
                },
                {
                    type: "int",
                    name: "parent",
                    useNull: true
                },
                {
                    type: "string",
                    name: "parent_unicode"
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
                    type: "string",
                    name: "number"
                },
                {
                    type: "float",
                    name: "value",
                    useNull: true
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
                    type: "int",
                    name: "solicitation",
                    useNull: true
                },
                {
                    type: "string",
                    name: "solicitation_unicode"
                },
                {
                    type: "int",
                    name: "reinforcement_reversal",
                    useNull: true
                },
                {
                    type: "string",
                    name: "reinforcement_reversal_display"
                },
                {
                    type: "string",
                    name: "provider_display"
                },
                {
                    type: "string",
                    name: "balance"
                },
            ]);

        return this._fields;
    }
});
