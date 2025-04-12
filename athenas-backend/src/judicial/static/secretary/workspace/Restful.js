Ext._define('judicial.secretary.workspace.Restful', {
    extend: 'judicial.OutCourtLawsuitRestful',

    resource: 'EJudOutCourtLawsuitSecretary',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = judicial.secretary.workspace.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "date",
                    name: "date_send_secretary",
                    dateFormat: "d/m/Y H:i"
                }

            ]);

        return this._fields;
    },
});
