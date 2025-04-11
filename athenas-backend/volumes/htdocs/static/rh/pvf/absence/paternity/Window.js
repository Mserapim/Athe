Ext._define('rh.pvf.absence.paternity.Window', {
    extend: 'rh.pvf.absence.maternity.Window',

    rest: 'rh.pvf.absence.paternity.Restful',


    getDays: function (cfg) {
        if (!this._days)
            this._days = Ext._create('Ext.form.NumberField', {
                width: 70,
                hideLabel: true,
                readOnly: cfg.values.type_employee == 'M'?false:true,
                enableKeyEvents: true,
                value:20,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay(cfg);
                    }
                }
            });

        return this._days;
    }, 
});

